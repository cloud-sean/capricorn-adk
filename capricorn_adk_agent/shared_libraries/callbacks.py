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

"""Callback functions for state management across the literature review pipeline."""

from google.adk.agents import callback_context as callback_context_module
from typing import Optional, Dict, Any, List
from google.genai import types
import json
import logging
from datetime import datetime
from .parsing_utils import parse_llm_json_output, validate_paper_structure

logger = logging.getLogger(__name__)


async def initialize_literature_state(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Initialize state for literature review pipeline."""
    
    callback_context.state["patient_case"] = {}
    callback_context.state["iteration_count"] = 0
    callback_context.state["search_queries"] = []
    callback_context.state["raw_papers"] = []
    callback_context.state["analyzed_papers"] = []
    callback_context.state["refinement_history"] = []
    callback_context.state["search_metrics"] = {
        "total_queries": 0,
        "successful_searches": 0,
        "papers_found": 0
    }
    
    logger.info("Initialized literature review state")
    return None


async def track_iteration(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Track loop iterations and refinement history."""
    
    iteration = callback_context.state.get("iteration_count", 0) + 1
    callback_context.state["iteration_count"] = iteration
    
    if callback_context.state.get("refinement_reason"):
        callback_context.state["refinement_history"].append({
            "iteration": iteration,
            "reason": callback_context.state["refinement_reason"],
            "timestamp": datetime.now().isoformat()
        })
    
    logger.info(f"Literature review iteration {iteration}")
    return None


async def before_query_generation(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Prepare context for query generation, including refinement feedback."""
    
    if callback_context.state.get("refinement_reason"):
        # Provide feedback for refinement
        feedback = f"Previous search was insufficient: {callback_context.state['refinement_reason']}. Generate more targeted queries."
        return types.Content(
            parts=[types.Part(text=feedback)]
        )
    return None


async def after_query_generation(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Store generated queries in state."""
    
    # Access output from the agent's execution through state
    # The output_key "search_queries" should be set by the agent
    queries = callback_context.state.get("search_queries", [])
    if queries:
        callback_context.state["search_metrics"]["total_queries"] = len(queries)
        logger.info(f"Generated {len(queries)} search queries")
    
    return None


async def aggregate_parallel_results(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Aggregate results from parallel searches."""
    
    all_papers = []
    search_metrics = callback_context.state.get("search_metrics", {})
    successful_searches = 0
    
    # Get parallel search results from state
    parallel_results = callback_context.state.get("parallel_search_results", {})
    
    # Process each query result
    for query_id, raw_papers in parallel_results.items():
        if not raw_papers:
            continue
            
        # Parse the raw output if it's a string
        parsed_papers = parse_llm_json_output(
            raw_papers,
            expected_key="papers",
            context_name=f"search_{query_id}"
        )
        
        # Handle different result formats
        papers_list = []
        if isinstance(parsed_papers, list):
            papers_list = parsed_papers
        elif isinstance(parsed_papers, dict):
            # Try common keys where papers might be stored
            for key in ["papers", "results", "search_results", "items"]:
                if key in parsed_papers and isinstance(parsed_papers[key], list):
                    papers_list = parsed_papers[key]
                    break
        
        # Validate and add papers
        valid_papers = []
        for i, paper in enumerate(papers_list):
            validated = validate_paper_structure(paper, i)
            if validated:
                valid_papers.append(validated)
        
        if valid_papers:
            successful_searches += 1
            search_metrics["papers_found"] = search_metrics.get("papers_found", 0) + len(valid_papers)
            all_papers.extend(valid_papers)
            logger.debug(f"Query {query_id}: Found {len(valid_papers)} valid papers")
    
    # Remove duplicates based on title
    unique_papers = []
    seen_titles = set()
    for paper in all_papers:
        title = paper.get("title", "").lower().strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_papers.append(paper)
    
    # Update state
    callback_context.state["raw_papers"] = unique_papers
    search_metrics["successful_searches"] = successful_searches
    callback_context.state["search_metrics"] = search_metrics
    
    logger.info(f"Aggregated {len(unique_papers)} unique papers from {successful_searches} searches")
    return None


async def save_final_results(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Save final literature review results with citation information."""
    
    analyzed_papers = callback_context.state.get("analyzed_papers", [])
    formatted_references = callback_context.state.get("formatted_references", "")
    
    results = {
        "patient_case": callback_context.state.get("patient_case"),
        "total_iterations": callback_context.state.get("iteration_count", 1),
        "refinement_history": callback_context.state.get("refinement_history", []),
        "search_metrics": callback_context.state.get("search_metrics", {}),
        "final_papers": analyzed_papers,
        "queries_used": callback_context.state.get("search_queries", []),
        "formatted_references": formatted_references,
        "citation_summary": {
            "total_references": len(analyzed_papers),
            "papers_with_pmid": sum(1 for p in analyzed_papers if p.get("citation_links", {}).get("pubmed_url")),
            "papers_with_doi": sum(1 for p in analyzed_papers if p.get("citation_links", {}).get("doi_url")),
        }
    }
    
    # Save detailed results to JSON file
    output_file = "literature_review_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Save markdown references to separate file for easy copy-paste
    if formatted_references:
        references_file = "formatted_references.md"
        with open(references_file, "w") as f:
            f.write(formatted_references)
        logger.info(f"Saved formatted references to {references_file}")
    
    logger.info(
        f"Saved literature review results to {output_file}: "
        f"{len(results['final_papers'])} papers with citations after {results['total_iterations']} iterations"
    )
    
    return None


async def prepare_parallel_search_context(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Prepare context for parallel search execution."""
    
    queries = callback_context.state.get("search_queries", [])
    
    if not queries:
        logger.warning("No queries available for parallel search")
        return None
    
    # Initialize storage for parallel results
    callback_context.state["parallel_search_results"] = {}
    
    logger.info(f"Prepared context for parallel search of {len(queries)} queries")
    return None