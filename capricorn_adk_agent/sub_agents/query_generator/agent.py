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

"""Query generator agent for creating targeted medical literature search queries."""

from google.adk.agents import Agent
from google.adk.agents import callback_context as callback_context_module
from google.genai import types
from typing import Optional, Any, List, Dict
import logging

from . import prompt
from .enhanced_prompt import ENHANCED_QUERY_GENERATOR_PROMPT
from ...models import PubMedQuery
from ...shared_libraries.callbacks import before_query_generation
from ...shared_libraries.parsing_utils import parse_llm_json_output, validate_query_structure
from .query_parser import query_generation_tool

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


async def parse_and_store_queries(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Parse the generated queries and store them properly in state."""
    
    # Get the raw output from the agent
    raw_output = callback_context.state.get("search_queries", "")
    
    # Robustly parse the LLM output
    parsed_data = parse_llm_json_output(
        raw_output,
        expected_key="search_queries",
        context_name="query_generation"
    )
    
    # Extract queries from parsed data
    if isinstance(parsed_data, list):
        queries = parsed_data
    elif isinstance(parsed_data, dict) and "search_queries" in parsed_data:
        queries = parsed_data["search_queries"]
    else:
        queries = None
    
    # Validate and clean queries
    validated_queries = []
    if queries and isinstance(queries, list):
        for i, query in enumerate(queries, 1):
            validated_query = validate_query_structure(query, i)
            if validated_query:
                validated_queries.append(validated_query)
        logger.info(f"Validated {len(validated_queries)} queries from {len(queries)} raw queries")
    
    # Use fallback queries if parsing/validation failed
    if not validated_queries:
        logger.warning("No valid queries parsed, using fallback queries for KMT2A AML case")
        validated_queries = [
            {
                "id": 1,
                "query": "KMT2A rearranged AML revumenib resistance 2024",
                "type": "molecular",
                "priority": "high",
                "focus": "Resistance mechanisms in KMT2A-r AML"
            },
            {
                "id": 2, 
                "query": "menin inhibitor relapse post HSCT pediatric AML",
                "type": "treatment",
                "priority": "high",
                "focus": "Menin inhibitor treatment after transplant"
            },
            {
                "id": 3,
                "query": "CD33 CD123 targeted therapy AML clinical trials",
                "type": "immunotherapy",
                "priority": "high",
                "focus": "Immunotherapy targeting CD33/CD123"
            },
            {
                "id": 4,
                "query": "NRAS mutation menin inhibitor resistance AML",
                "type": "resistance",
                "priority": "high",
                "focus": "NRAS-mediated resistance mechanisms"
            },
            {
                "id": 5,
                "query": "pediatric AML third relapse treatment options",
                "type": "guidelines",
                "priority": "high",
                "focus": "Treatment strategies for multiply relapsed AML"
            }
        ]
    
    # Store the validated queries
    callback_context.state["search_queries"] = validated_queries
    logger.info(f"Stored {len(validated_queries)} validated search queries")
    
    # Update metrics
    if "search_metrics" in callback_context.state:
        callback_context.state["search_metrics"]["total_queries"] = len(validated_queries)
    
    return None


# Enhanced query generator with structured output
enhanced_query_generator_agent = Agent(
    model=MODEL,
    name="enhanced_query_generator",
    description="Generates diverse, targeted search queries with refinement capability for comprehensive literature coverage",
    instruction=ENHANCED_QUERY_GENERATOR_PROMPT,
    before_agent_callback=before_query_generation,
    after_agent_callback=parse_and_store_queries,
    output_key="search_queries",
    # Note: Could use output_schema with list[PubMedQuery] if needed for stricter validation
)

# Keep original for backward compatibility
query_generator_agent = enhanced_query_generator_agent