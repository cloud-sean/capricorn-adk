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

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool

from .prompt import medical_oncology_agent_instruction
from .sub_agents.lit_review.agent import lit_review_coordinator

root_agent = Agent(
    model="gemini-2.5-pro",
    name="capricorn_medical_oncology_agent",
    description="Medical oncology specialist that analyzes genetic and oncological patient information to provide treatment recommendations with comprehensive literature review capabilities",
    instruction=medical_oncology_agent_instruction,
    tools=[
        AgentTool(agent=lit_review_coordinator),
        # Future: Add custom medical tools like genetic analysis, drug interaction checking, etc.
    ],
)