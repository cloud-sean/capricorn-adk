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

"""Paper analysis agent for evaluating medical literature relevance to patient cases."""

from google.adk.agents import Agent
from google.adk.agents import callback_context as callback_context_module
from google.genai import types
from typing import Optional, Any, List, Dict
import logging

from . import prompt
from .enhanced_prompt import ENHANCED_PAPER_ANALYSIS_PROMPT
from ...shared_libraries.citation_utils import generate_citation_links, generate_markdown_citation_list
from ...shared_libraries.parsing_utils import parse_llm_json_output, validate_paper_structure

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-pro"


async def prepare_papers_for_analysis(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Prepare papers from parallel search results for analysis."""
    
    # Get all papers from parallel search results
    parallel_results = callback_context.state.get("parallel_search_results", {})
    all_papers = []
    
    for query_id, results in parallel_results.items():
        if isinstance(results, list):
            for paper in results:
                if isinstance(paper, dict):
                    # Add source query information
                    paper["source_query"] = query_id
                    all_papers.append(paper)
        elif isinstance(results, dict) and "papers" in results:
            # Handle case where results are wrapped in a papers key
            for paper in results["papers"]:
                if isinstance(paper, dict):
                    paper["source_query"] = query_id
                    all_papers.append(paper)
    
    callback_context.state["raw_papers"] = all_papers
    logger.info(f"Prepared {len(all_papers)} papers for analysis from {len(parallel_results)} query results")
    
    if all_papers:
        # Provide context about papers to analyze
        return types.Content(
            parts=[types.Part(
                text=f"Analyze these {len(all_papers)} papers retrieved from literature search:\n\n" +
                     "\n".join([f"- {p.get('title', 'Untitled')}" for p in all_papers[:10]]) +
                     (f"\n... and {len(all_papers) - 10} more papers" if len(all_papers) > 10 else "")
            )]
        )
    
    return None


async def store_analyzed_papers(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Store analyzed papers in state with enhanced citation information."""
    
    # Access raw output from the agent's execution through state
    raw_output = callback_context.state.get("analyzed_papers", [])
    
    # Robustly parse the LLM output
    parsed_data = parse_llm_json_output(
        raw_output, 
        expected_key="analyzed_papers",
        context_name="paper_analysis"
    )
    
    # Ensure we have a list
    if isinstance(parsed_data, dict) and "analyzed_papers" in parsed_data:
        analyzed_papers = parsed_data["analyzed_papers"]
    elif isinstance(parsed_data, list):
        analyzed_papers = parsed_data
    else:
        analyzed_papers = []
        if parsed_data:
            logger.warning(f"Unexpected parsed data structure: {type(parsed_data)}")
    
    enhanced_papers = []
    if analyzed_papers:
        # Enhance papers with citation links
        for i, paper in enumerate(analyzed_papers, 1):
            # Validate paper structure
            validated_paper = validate_paper_structure(paper, i)
            if not validated_paper:
                logger.warning(f"Skipping invalid paper {i}")
                continue
            
            # Generate citation links if not already present
            if "citation_links" not in validated_paper or not validated_paper.get("citation_links"):
                try:
                    citation_links = generate_citation_links(validated_paper, i)
                    validated_paper["citation_links"] = citation_links
                except Exception as e:
                    logger.error(f"Error generating citations for paper {i}: {e}")
                    validated_paper["citation_links"] = {
                        "formatted_reference": f"[{i}] {validated_paper.get('title', 'Unknown')}"
                    }
            
            enhanced_papers.append(validated_paper)
    
    # Store enhanced/cleaned papers back
    callback_context.state["analyzed_papers"] = enhanced_papers
    
    if enhanced_papers:
        # Generate markdown reference list for easy copy-paste
        try:
            markdown_references = generate_markdown_citation_list(enhanced_papers)
            callback_context.state["formatted_references"] = markdown_references
        except Exception as e:
            logger.error(f"Error generating markdown references: {e}")
            callback_context.state["formatted_references"] = ""
        
        # Update search metrics
        if "search_metrics" in callback_context.state:
            callback_context.state["search_metrics"]["papers_analyzed"] = len(enhanced_papers)
            callback_context.state["search_metrics"]["references_generated"] = len(enhanced_papers)
        
        logger.info(f"Stored {len(enhanced_papers)} analyzed papers with citation links in state")
    else:
        logger.warning("No valid papers were processed after analysis step")
    
    return None


# Enhanced paper analysis agent with scoring
enhanced_paper_analysis_agent = Agent(
    model=MODEL,
    name="enhanced_medical_paper_analyzer",
    description="Analyzes and scores medical papers for relevance, then selects the most applicable studies",
    instruction=ENHANCED_PAPER_ANALYSIS_PROMPT,
    before_agent_callback=prepare_papers_for_analysis,
    after_agent_callback=store_analyzed_papers,
    output_key="analyzed_papers"
)

# Keep the original for backward compatibility
paper_analysis_agent = enhanced_paper_analysis_agent