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

"""Utility functions for parsing LLM outputs in ADK agents."""

import json
import re
import logging
from typing import Any, Union, List, Dict, Optional

logger = logging.getLogger(__name__)


def parse_llm_json_output(
    raw_output: Any, 
    expected_key: Optional[str] = None,
    context_name: str = "LLM output"
) -> Union[List, Dict, None]:
    """
    Robustly parse LLM output into structured data.
    
    ADK's output_key feature stores the raw LLM response in state, which is often
    a string containing JSON (possibly wrapped in markdown). This function handles
    various formats the LLM might return.
    
    Args:
        raw_output: The raw output from the LLM (could be string, list, dict, etc.)
        expected_key: If provided, will look for this key in parsed dict results
        context_name: Name for logging context (e.g., "analyzed_papers", "search_queries")
    
    Returns:
        Parsed data as list or dict, or None if parsing fails
    """
    
    # Case 1: Already properly structured
    if isinstance(raw_output, (list, dict)):
        if expected_key and isinstance(raw_output, dict):
            return raw_output.get(expected_key, raw_output)
        return raw_output
    
    # Case 2: String output (most common with LLMs)
    if isinstance(raw_output, str) and raw_output.strip():
        logger.debug(f"Parsing string output from LLM for {context_name}")
        
        try:
            # Step 1: Extract JSON from markdown blocks if present
            json_str = extract_json_from_markdown(raw_output)
            
            # Step 2: Validate it looks like JSON
            if not json_str.strip().startswith(("{", "[")):
                logger.error(f"{context_name}: String doesn't appear to be JSON. Snippet: {json_str[:100]}...")
                return None
            
            # Step 3: Parse JSON
            parsed_data = json.loads(json_str)
            
            # Step 4: Extract expected key if provided
            if expected_key and isinstance(parsed_data, dict):
                if expected_key in parsed_data:
                    logger.debug(f"{context_name}: Extracted '{expected_key}' from parsed JSON")
                    return parsed_data[expected_key]
                else:
                    logger.warning(f"{context_name}: Expected key '{expected_key}' not found in parsed JSON")
                    # Return the whole dict anyway, caller can decide what to do
                    return parsed_data
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"{context_name}: Failed to parse as JSON: {e}")
            logger.debug(f"{context_name}: Raw output snippet: {raw_output[:500]}...")
            return None
        except Exception as e:
            logger.error(f"{context_name}: Unexpected error during parsing: {e}")
            return None
    
    # Case 3: Empty or unexpected type
    if raw_output:
        logger.warning(f"{context_name}: Received unexpected type: {type(raw_output)}")
    else:
        logger.debug(f"{context_name}: Received empty output")
    
    return None


def extract_json_from_markdown(text: str) -> str:
    """
    Extract JSON content from markdown code blocks.
    
    Handles formats like:
    ```json
    {...}
    ```
    
    Args:
        text: String that might contain markdown-wrapped JSON
    
    Returns:
        Extracted JSON string or original text if no markdown blocks found
    """
    # Try to find JSON in markdown code blocks
    # Use re.DOTALL to allow . to match newlines
    patterns = [
        r"```json\s*(.*?)\s*```",  # ```json ... ```
        r"```JSON\s*(.*?)\s*```",  # ```JSON ... ```
        r"```\s*(.*?)\s*```",      # ``` ... ``` (generic code block)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            # Verify it looks like JSON before returning
            if extracted and extracted[0] in "{[":
                logger.debug("Successfully extracted JSON from markdown block")
                return extracted
    
    # No markdown blocks found, return original
    return text.strip()


def validate_paper_structure(paper: Any, index: int = 0) -> Optional[Dict]:
    """
    Validate and clean a paper object to ensure it has the expected structure.
    
    Args:
        paper: Paper data (could be dict, string, or other)
        index: Index for logging
    
    Returns:
        Validated paper dict or None if invalid
    """
    if not isinstance(paper, dict):
        logger.warning(f"Paper {index} is not a dictionary: {type(paper)}")
        return None
    
    # Ensure minimum required fields
    if not paper.get("title") and not paper.get("query"):
        logger.warning(f"Paper {index} missing title or query field")
        return None
    
    # Clean and validate
    cleaned_paper = {
        "title": paper.get("title", "Unknown Title"),
        "authors": paper.get("authors", ""),
        "year": paper.get("year", ""),
        "journal": paper.get("journal", ""),
        "pmid": paper.get("pmid", ""),
        "doi": paper.get("doi", ""),
        "abstract": paper.get("abstract", paper.get("summary", "")),
    }
    
    # Preserve any additional fields
    for key, value in paper.items():
        if key not in cleaned_paper:
            cleaned_paper[key] = value
    
    return cleaned_paper


def validate_query_structure(query: Any, index: int = 0) -> Optional[Dict]:
    """
    Validate and clean a query object to ensure it has the expected structure.
    
    Args:
        query: Query data (could be dict, string, or other)
        index: Index for logging and ID generation
    
    Returns:
        Validated query dict or None if invalid
    """
    # Handle string queries
    if isinstance(query, str):
        return {
            "id": index,
            "query": query,
            "type": "general",
            "priority": "medium"
        }
    
    if not isinstance(query, dict):
        logger.warning(f"Query {index} is not a dictionary or string: {type(query)}")
        return None
    
    # Ensure minimum required fields
    if not query.get("query"):
        logger.warning(f"Query {index} missing 'query' field")
        return None
    
    # Clean and validate
    cleaned_query = {
        "id": query.get("id", index),
        "query": query.get("query"),
        "type": query.get("type", "general"),
        "priority": query.get("priority", "medium"),
        "focus": query.get("focus", "")
    }
    
    return cleaned_query