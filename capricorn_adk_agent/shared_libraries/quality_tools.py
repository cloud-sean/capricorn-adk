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

"""Quality checking tools for the literature review loop."""

from google.adk.tools import ToolContext
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


async def check_literature_quality(
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Check if literature review meets quality standards.
    If quality is sufficient, it signals the loop to terminate.
    """
    
    # Get analyzed papers from state
    papers = tool_context.state.get("analyzed_papers", [])
    
    # Check minimum paper count
    min_papers = 5
    if len(papers) < min_papers:
        tool_context.state["refinement_reason"] = f"Insufficient papers found ({len(papers)} < {min_papers})"
        logger.info(f"Quality check failed: {tool_context.state['refinement_reason']}")
        return {"status": "failure", "message": tool_context.state["refinement_reason"]}
    
    # Check for recent papers (at least 3 from 2022 or later)
    recent_papers = 0
    for paper in papers:
        year = paper.get("year", 0)
        if isinstance(year, str):
            try:
                year = int(year)
            except:
                continue
        if year >= 2022:
            recent_papers += 1
    
    min_recent = 3
    if recent_papers < min_recent:
        tool_context.state["refinement_reason"] = f"Insufficient recent literature ({recent_papers} papers from 2022+, need {min_recent})"
        logger.info(f"Quality check failed: {tool_context.state['refinement_reason']}")
        return {"status": "failure", "message": tool_context.state["refinement_reason"]}
    
    # Check average relevance score if available
    if all("relevance_score" in p for p in papers):
        avg_relevance = sum(p["relevance_score"] for p in papers) / len(papers)
        min_relevance = 7.0
        if avg_relevance < min_relevance:
            tool_context.state["refinement_reason"] = f"Low average relevance score ({avg_relevance:.1f} < {min_relevance})"
            logger.info(f"Quality check failed: {tool_context.state['refinement_reason']}")
            return {"status": "failure", "message": tool_context.state["refinement_reason"]}
    
    # Check for diversity in paper types (if type information is available)
    paper_types = set(p.get("type", "unknown") for p in papers)
    if len(paper_types) < 2 and "unknown" not in paper_types:
        tool_context.state["refinement_reason"] = "Insufficient diversity in evidence types"
        logger.info(f"Quality check failed: {tool_context.state['refinement_reason']}")
        return {"status": "failure", "message": tool_context.state["refinement_reason"]}
    
    # All quality checks passed
    logger.info(f"Quality check passed: {len(papers)} papers with {recent_papers} recent papers")
    tool_context.actions.escalate = True
    return {"status": "success", "message": "Quality standards met, exiting loop."}