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

"""Fixed parallel search agent that actually executes searches."""

from google.adk.agents import Agent, ParallelAgent
from google.adk.tools import google_search
from google.adk.agents import callback_context as callback_context_module
from google.genai import types
from typing import Optional, List, Dict, Any
import logging
from ...shared_libraries.parsing_utils import parse_llm_json_output, validate_paper_structure

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"

# Create 5 generic search agents that can be reused
search_agent_1 = Agent(
    model=MODEL,
    name="search_agent_1",
    description="Execute medical literature search query 1",
    instruction="""Search for medical literature using Google Search. 
    Find peer-reviewed publications, clinical trials, and medical journals.
    Extract paper title, authors, year, journal, abstract, PMID, DOI if available.""",
    tools=[google_search],
    output_key="search_1_results"
)

search_agent_2 = Agent(
    model=MODEL,
    name="search_agent_2", 
    description="Execute medical literature search query 2",
    instruction="""Search for medical literature using Google Search.
    Focus on recent publications from 2022-2024.
    Extract paper title, authors, year, journal, abstract, PMID, DOI if available.""",
    tools=[google_search],
    output_key="search_2_results"
)

search_agent_3 = Agent(
    model=MODEL,
    name="search_agent_3",
    description="Execute medical literature search query 3",
    instruction="""Search for medical literature using Google Search.
    Look for clinical trials and treatment outcomes.
    Extract paper title, authors, year, journal, abstract, PMID, DOI if available.""",
    tools=[google_search],
    output_key="search_3_results"
)

search_agent_4 = Agent(
    model=MODEL,
    name="search_agent_4",
    description="Execute medical literature search query 4",
    instruction="""Search for medical literature using Google Search.
    Find systematic reviews and meta-analyses.
    Extract paper title, authors, year, journal, abstract, PMID, DOI if available.""",
    tools=[google_search],
    output_key="search_4_results"
)

search_agent_5 = Agent(
    model=MODEL,
    name="search_agent_5",
    description="Execute medical literature search query 5",
    instruction="""Search for medical literature using Google Search.
    Look for case reports and treatment guidelines.
    Extract paper title, authors, year, journal, abstract, PMID, DOI if available.""",
    tools=[google_search],
    output_key="search_5_results"
)


async def prepare_search_context(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Prepare search queries for parallel execution."""
    
    queries = callback_context.state.get("search_queries", [])
    
    if not queries:
        logger.warning("No search queries found for parallel search")
        return None
    
    # Store individual queries for each agent
    for i, query_obj in enumerate(queries[:5], 1):  # Limit to 5 queries
        if isinstance(query_obj, dict):
            query_text = query_obj.get("query", "")
        else:
            query_text = str(query_obj)
        
        callback_context.state[f"query_{i}"] = query_text
        logger.info(f"Set query_{i}: {query_text[:50]}...")
    
    # Initialize results storage
    callback_context.state["parallel_search_results"] = {}
    
    return types.Content(
        parts=[types.Part(
            text=f"Executing {min(len(queries), 5)} parallel searches for medical literature"
        )]
    )


async def aggregate_search_results(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Aggregate results from parallel searches."""
    
    all_papers = []
    
    # Collect results from each search agent
    for i in range(1, 6):
        results_key = f"search_{i}_results"
        if results_key in callback_context.state:
            raw_results = callback_context.state[results_key]
            if not raw_results:
                continue
            
            # Parse the raw output if it's a string
            parsed_results = parse_llm_json_output(
                raw_results,
                expected_key="papers",
                context_name=f"search_{i}"
            )
            
            # Store in parallel_search_results for compatibility
            callback_context.state["parallel_search_results"][f"query_{i}"] = parsed_results or raw_results
            
            # Extract papers from parsed results
            papers_list = []
            if isinstance(parsed_results, list):
                papers_list = parsed_results
            elif isinstance(parsed_results, dict):
                # Try common keys where papers might be stored
                for key in ["papers", "results", "search_results", "items"]:
                    if key in parsed_results and isinstance(parsed_results[key], list):
                        papers_list = parsed_results[key]
                        break
                # If still no list found, wrap dict as single item
                if not papers_list and parsed_results:
                    papers_list = [parsed_results]
            
            # Validate papers before adding
            for j, paper in enumerate(papers_list):
                validated = validate_paper_structure(paper, j)
                if validated:
                    all_papers.append(validated)
    
    # Store aggregated papers
    callback_context.state["raw_papers"] = all_papers
    
    logger.info(f"Aggregated {len(all_papers)} validated papers from parallel searches")
    
    return None


# Create the actual ParallelAgent
parallel_search_executor = ParallelAgent(
    name="parallel_search_executor",
    description="Execute up to 5 literature searches in parallel",
    sub_agents=[
        search_agent_1,
        search_agent_2,
        search_agent_3,
        search_agent_4,
        search_agent_5
    ],
    before_agent_callback=prepare_search_context,
    after_agent_callback=aggregate_search_results
)


# Create a wrapper agent that uses the parallel executor
enhanced_parallel_search = Agent(
    model=MODEL,
    name="enhanced_parallel_search",
    description="Coordinates and executes parallel literature searches",
    instruction="""You are coordinating parallel medical literature searches.
    
    The search queries have been prepared. Execute parallel searches to find:
    - Recent peer-reviewed publications (2022-2024)
    - Clinical trials and treatment outcomes
    - Systematic reviews and meta-analyses
    - Case reports and treatment guidelines
    - Papers relevant to the specific patient case
    
    Each search should return structured paper information including:
    - Title, authors, year, journal
    - Abstract or summary
    - PMID and DOI when available
    - Study type and relevance
    """,
    sub_agents=[parallel_search_executor],
    output_key="parallel_search_results"
)