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
from typing import Optional, Any
import logging

from . import prompt
from .enhanced_prompt import ENHANCED_PAPER_ANALYSIS_PROMPT

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
    callback_context: callback_context_module.CallbackContext,
    result: Any
) -> Optional[types.Content]:
    """Store analyzed papers in state."""
    
    if result and isinstance(result, dict):
        analyzed_papers = result.get("analyzed_papers", [])
        callback_context.state["analyzed_papers"] = analyzed_papers
        
        # Update search metrics
        if "search_metrics" in callback_context.state:
            callback_context.state["search_metrics"]["papers_analyzed"] = len(analyzed_papers)
        
        logger.info(f"Stored {len(analyzed_papers)} analyzed papers in state")
    
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