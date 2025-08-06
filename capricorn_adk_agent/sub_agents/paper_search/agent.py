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

"""Paper search agent for retrieving medical literature using Google Search."""

from google.adk.agents import Agent
from google.adk.tools import google_search

from . import prompt

MODEL = "gemini-2.5-flash"

paper_search_agent = Agent(
    model=MODEL,
    name="medical_paper_search",
    description="Searches for medical literature using Google Search based on generated queries",
    instruction=prompt.PAPER_SEARCH_PROMPT,
    output_key="retrieved_papers",
    tools=[google_search],
)