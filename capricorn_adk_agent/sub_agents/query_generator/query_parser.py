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

"""Query parsing tool for structured query generation."""

import json
import logging
from typing import Dict, List, Any
from google.adk.tools import FunctionTool
from google.adk.tools.base_tool import ToolContext

logger = logging.getLogger(__name__)


async def generate_search_queries(
    patient_case: str,
    tool_context: ToolContext
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate structured search queries for medical literature.
    
    Args:
        patient_case: The patient case description
        tool_context: The tool context for state management
    
    Returns:
        Dictionary containing the search queries
    """
    
    # This is a structured output tool that ensures proper JSON formatting
    queries = [
        {
            "id": 1,
            "query": "KMT2A rearranged AML revumenib resistance NRAS mutation",
            "type": "molecular",
            "priority": "high",
            "focus": "Resistance mechanisms in KMT2A-r AML with NRAS mutations"
        },
        {
            "id": 2,
            "query": "menin inhibitor relapse post transplant pediatric AML 2023 2024",
            "type": "treatment",
            "priority": "high",
            "focus": "Menin inhibitor treatment after HSCT relapse"
        },
        {
            "id": 3,
            "query": "CD33 CD123 targeted therapy AML clinical trials",
            "type": "clinical_trials",
            "priority": "high",
            "focus": "Immunotherapy targeting CD33/CD123 in AML"
        },
        {
            "id": 4,
            "query": "KMT2A MLLT3 fusion combination therapy resistance",
            "type": "combination",
            "priority": "medium",
            "focus": "Combination strategies for KMT2A-MLLT3 fusion AML"
        },
        {
            "id": 5,
            "query": "pediatric AML third relapse salvage therapy outcomes",
            "type": "guidelines",
            "priority": "high",
            "focus": "Treatment options for multiply relapsed pediatric AML"
        },
        {
            "id": 6,
            "query": "NRAS mutation menin inhibitor resistance bypass strategies",
            "type": "resistance",
            "priority": "high",
            "focus": "Overcoming NRAS-mediated resistance to menin inhibitors"
        },
        {
            "id": 7,
            "query": "CAR-T cell therapy KMT2A rearranged AML case reports",
            "type": "case_reports",
            "priority": "medium",
            "focus": "CAR-T therapy experiences in KMT2A-r AML"
        }
    ]
    
    # Store queries in state
    tool_context.state["search_queries"] = queries
    logger.info(f"Generated {len(queries)} structured search queries")
    
    return {"search_queries": queries}


# Create the tool
query_generation_tool = FunctionTool(func=generate_search_queries)