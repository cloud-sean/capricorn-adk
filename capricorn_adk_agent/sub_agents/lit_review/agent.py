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

"""Enhanced Literature Review coordinator with Sequential, Parallel, and Loop agents."""

from google.adk.agents import Agent, SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools import FunctionTool
from google.adk.agents import callback_context as callback_context_module
from google.genai import types
from typing import Optional
import logging

from . import prompt
from ..query_generator.agent import enhanced_query_generator_agent
from ..parallel_search.fixed_agent import enhanced_parallel_search
from ..paper_analysis.agent import enhanced_paper_analysis_agent
from ...shared_libraries.callbacks import (
    initialize_literature_state,
    track_iteration,
    aggregate_parallel_results,
    save_final_results
)
from ...shared_libraries.quality_tools import check_literature_quality

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-pro"


# Create the quality check tool for the loop
quality_check_tool = FunctionTool(
    func=check_literature_quality
)


# Step 1: Core Sequential Pipeline
literature_review_pipeline = SequentialAgent(
    name="literature_review_pipeline",
    description="Sequential pipeline: Query Generation → Parallel Search → Paper Analysis",
    sub_agents=[
        enhanced_query_generator_agent,   # Generate 5-7 diverse queries
        enhanced_parallel_search,         # Execute parallel searches (fixed version)
        enhanced_paper_analysis_agent     # Analyze and score papers
    ],
    before_agent_callback=track_iteration,
    after_agent_callback=aggregate_parallel_results
)


# Create the quality check agent
quality_check_agent = Agent(
    name="quality_check_agent",
    model=MODEL,
    instruction="""You must call the `check_literature_quality` tool.""",
    tools=[quality_check_tool],
    include_contents='none',
)


# Step 2: Wrap in Loop for Quality Assurance  
lit_review_coordinator = LoopAgent(
    name="literature_review_coordinator",
    description="Literature review with iterative refinement until quality standards are met",
    sub_agents=[
        literature_review_pipeline,
        quality_check_agent
    ],
    max_iterations=3,
    before_agent_callback=initialize_literature_state,
    after_agent_callback=save_final_results
)