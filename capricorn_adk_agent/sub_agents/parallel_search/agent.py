# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Parallel search agent for concurrent Google searches across multiple queries."""

from google.adk.agents import Agent, ParallelAgent
from google.adk.tools import google_search
from google.adk.agents import callback_context as callback_context_module
from google.genai import types
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def create_query_search_agent(query_obj: Dict[str, Any]) -> Agent:
    """Create a search agent for a specific query."""
    
    query_id = query_obj.get("id", 0)
    query_text = query_obj.get("query", "")
    query_type = query_obj.get("type", "general")
    
    # Create tailored search instruction based on query type
    instruction = f"""
    Execute this medical literature search query: "{query_text}"
    Query type: {query_type}
    
    Search Strategy:
    - Use Google search to find relevant medical literature
    - Focus on peer-reviewed publications, clinical trials, and medical journals
    - Look for papers from 2022-2024 when possible
    - Include PubMed articles, clinical trial reports, and medical journal articles
    
    Extract the following information from search results:
    - Paper title
    - Authors (if available)  
    - Publication year
    - Journal/source
    - Abstract or summary (if available)
    - PMID (if PubMed article)
    - DOI (if available)
    - Study type (clinical trial, review, case report, etc.)
    
    Format results as a structured list of papers found.
    Focus on the most relevant and recent results.
    """
    
    async def store_search_results(
        callback_context: callback_context_module.CallbackContext
    ) -> Optional[types.Content]:
        """Store search results in parallel_search_results state."""
        
        # Access output from the agent's execution through state
        # The output_key f"search_results_query_{query_id}" should be set by the agent
        search_results = callback_context.state.get(f"search_results_query_{query_id}")
        
        if search_results:
            # Initialize parallel_search_results if not exists
            if "parallel_search_results" not in callback_context.state:
                callback_context.state["parallel_search_results"] = {}
            
            # Store results under query ID
            callback_context.state["parallel_search_results"][f"query_{query_id}"] = search_results
            logger.info(f"Stored search results for query {query_id}: {query_text[:50]}...")
        
        return None
    
    return Agent(
        model=MODEL,
        name=f"search_query_{query_id}",
        description=f"Search for query {query_id}: {query_text[:50]}...",
        instruction=instruction,
        tools=[google_search],
        after_agent_callback=store_search_results,
        output_key=f"search_results_query_{query_id}"
    )


async def create_parallel_search_from_state(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Create parallel search agents dynamically based on queries in state."""
    
    queries = callback_context.state.get("search_queries", [])
    
    if not queries:
        logger.warning("No search queries found in state for parallel search")
        return None
    
    # Create individual search agents for each query
    search_agents = []
    for query_obj in queries:
        if isinstance(query_obj, dict) and "query" in query_obj:
            search_agent = create_query_search_agent(query_obj)
            search_agents.append(search_agent)
    
    if not search_agents:
        logger.warning("No valid queries found for parallel search")
        return None
    
    # Store the parallel agents in context for execution
    callback_context.state["parallel_search_agents"] = search_agents
    logger.info(f"Created {len(search_agents)} parallel search agents")
    
    return None


class ParallelSearchOrchestrator:
    """Orchestrates parallel searches across multiple queries."""
    
    def __init__(self):
        self.search_agents = []
    
    def create_parallel_agent_from_queries(self, queries: list) -> ParallelAgent:
        """Create a ParallelAgent with individual search agents for each query."""
        
        search_agents = []
        for query_obj in queries:
            if isinstance(query_obj, dict) and "query" in query_obj:
                search_agent = create_query_search_agent(query_obj)
                search_agents.append(search_agent)
        
        return ParallelAgent(
            name="parallel_query_searches",
            description=f"Execute {len(search_agents)} literature searches in parallel",
            sub_agents=search_agents
        )


async def orchestrate_parallel_search(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Create and execute parallel search based on queries in state."""
    
    queries = callback_context.state.get("search_queries", [])
    
    if not queries:
        logger.warning("No search queries found for parallel search")
        return types.Content(parts=[types.Part(text="No queries available for search")])
    
    # Ensure queries is a list
    if not isinstance(queries, list):
        logger.error(f"Invalid queries format: {type(queries)}")
        # Use fallback queries
        queries = [
            {"id": 1, "query": "KMT2A AML revumenib resistance", "type": "treatment"},
            {"id": 2, "query": "menin inhibitor relapse HSCT", "type": "clinical"},
            {"id": 3, "query": "CD33 CD123 AML therapy", "type": "immunotherapy"}
        ]
        callback_context.state["search_queries"] = queries
    
    logger.info(f"Orchestrating parallel search for {len(queries)} queries")
    
    # Create individual search agents for each query
    search_agents = []
    query_texts = []
    
    for query_obj in queries:
        if isinstance(query_obj, dict) and "query" in query_obj:
            search_agent = create_query_search_agent(query_obj)
            search_agents.append(search_agent)
            query_texts.append(query_obj.get("query", "Unknown query"))
        elif isinstance(query_obj, str):
            # Handle case where queries are plain strings
            query_dict = {"id": len(search_agents) + 1, "query": query_obj, "type": "general"}
            search_agent = create_query_search_agent(query_dict)
            search_agents.append(search_agent)
            query_texts.append(query_obj)
    
    # Store the agents for the parallel execution
    callback_context.state["parallel_search_agents"] = search_agents
    
    if query_texts:
        return types.Content(
            parts=[types.Part(
                text=f"Prepared {len(search_agents)} search agents for parallel execution:\n" +
                     "\n".join([f"- {q}" for q in query_texts[:10]]) +
                     (f"\n... and {len(query_texts) - 10} more" if len(query_texts) > 10 else "")
            )]
        )
    else:
        return types.Content(
            parts=[types.Part(text=f"Prepared {len(search_agents)} search agents")]
        )


# The main orchestrator agent
parallel_search_orchestrator = Agent(
    model=MODEL,
    name="parallel_search_orchestrator", 
    description="Coordinates parallel literature searches across multiple queries",
    instruction="""
    You are orchestrating parallel medical literature searches.
    
    Based on the search queries in the context:
    1. Acknowledge the queries to be searched
    2. Execute searches across all queries simultaneously using Google Search
    3. Each query will search for peer-reviewed medical literature
    4. Return structured results from all parallel searches
    
    Focus on finding relevant papers, clinical trials, and medical research.
    """,
    before_agent_callback=orchestrate_parallel_search,
    output_key="parallel_search_results"
)