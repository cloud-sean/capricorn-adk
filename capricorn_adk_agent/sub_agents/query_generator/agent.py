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
from typing import Optional, Any
import logging

from . import prompt
from .enhanced_prompt import ENHANCED_QUERY_GENERATOR_PROMPT
from ...shared_libraries.callbacks import before_query_generation, after_query_generation

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


# Enhanced query generator with multiple query generation
enhanced_query_generator_agent = Agent(
    model=MODEL,
    name="enhanced_query_generator",
    description="Generates diverse, targeted search queries with refinement capability for comprehensive literature coverage",
    instruction=ENHANCED_QUERY_GENERATOR_PROMPT,
    before_agent_callback=before_query_generation,
    after_agent_callback=after_query_generation,
    output_key="search_queries"
)

# Keep original for backward compatibility
query_generator_agent = enhanced_query_generator_agent