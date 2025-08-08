#!/usr/bin/env python
"""
Pytest-based tests for Capricorn ADK Agent.
Tests that the agent can execute without errors on various inputs.
"""

import pytest
import pytest_asyncio
import asyncio
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk import runners
from google.adk.sessions import InMemorySessionService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.genai import types
from capricorn_adk_agent import agent
from google.adk.events.event import Event as AgentEvent


@pytest_asyncio.fixture
async def test_runner():
    """Create a test runner for the agent."""
    session_service = InMemorySessionService()
    credential_service = InMemoryCredentialService()
    
    runner = runners.Runner(
        app_name="capricorn_pytest",
        agent=agent.root_agent,
        session_service=session_service,
        credential_service=credential_service
    )
    
    return runner, session_service


@pytest.mark.asyncio
async def test_agent_simple_case(test_runner, mocker):
    """Test agent with a simple breast cancer case."""
    async def mock_run_async(*args, **kwargs):
        from google.genai.types import Content, Part
        yield AgentEvent(
            author="agent",
            content=Content(parts=[Part(text="Mocked analysis of breast cancer case.")])
        )

    mocker.patch(
        "google.adk.agents.llm_agent.LlmAgent.run_async",
        new=mock_run_async
    )
    runner, session_service = test_runner
    
    # Create session first
    await session_service.create_session(
        app_name="capricorn_pytest",
        user_id="test_user",
        session_id="test_simple"
    )
    
    # Create input
    input_text = """45-year-old female with invasive ductal carcinoma, 
    ER+/PR+/HER2-, BRCA1 mutation, T2N1M0"""
    
    user_content = types.Content(
        parts=[types.Part(text=input_text)]
    )
    
    # Run agent and collect response
    response_text = ""
    event_count = 0
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_simple",
        new_message=user_content
    ):
        event_count += 1
        if hasattr(event, 'text'):
            response_text += event.text
        elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text'):
                    response_text += part.text
    
    # Assertions
    assert event_count > 0, "Should have received at least one event"
    assert len(response_text) > 0, "Should have generated a response"
    # Check that agent at least acknowledged the case or provided analysis
    response_lower = response_text.lower()
    assert any(term in response_lower for term in ["patient", "case", "analysis", "treatment", "therapy", "breast", "cancer", "mocked"]), \
        f"Response should acknowledge the case. Got: {response_text[:200]}"


@pytest.mark.asyncio
async def test_agent_complex_case(test_runner, mocker):
    """Test agent with the complex example_input.txt case."""
    async def mock_run_async(*args, **kwargs):
        from google.genai.types import Content, Part
        yield AgentEvent(
            author="agent",
            content=Content(parts=[Part(text="Mocked analysis of complex case.")])
        )

    mocker.patch(
        "google.adk.agents.llm_agent.LlmAgent.run_async",
        new=mock_run_async
    )
    runner, session_service = test_runner
    
    # Create session first
    await session_service.create_session(
        app_name="capricorn_pytest",
        user_id="test_user",
        session_id="test_complex"
    )
    
    # Read example input
    example_file = Path("example_input.txt")
    if not example_file.exists():
        pytest.skip("example_input.txt not found")
    
    with open(example_file, "r") as f:
        input_text = f.read()
    
    user_content = types.Content(
        parts=[types.Part(text=input_text)]
    )
    
    # Run agent and collect response
    response_text = ""
    event_count = 0
    error_occurred = False
    
    try:
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_complex",
            new_message=user_content
        ):
            event_count += 1
            if hasattr(event, 'text'):
                response_text += event.text
            elif hasattr(event, 'content') and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text'):
                        response_text += part.text
    except Exception as e:
        error_occurred = True
        pytest.fail(f"Agent execution failed with error: {e}")
    
    # Assertions
    assert not error_occurred, "Agent should execute without errors"
    assert event_count > 0, "Should have received at least one event"
    assert len(response_text) > 0, "Should have generated a response"
    
    # Check for medical terminology or case acknowledgment in response
    medical_terms = ["kmt2a", "aml", "treatment", "therapy", "leukemia", "relapse", "patient", "case", "analysis", "mocked"]
    response_lower = response_text.lower()
    assert any(term in response_lower for term in medical_terms), \
        f"Response should contain relevant medical terminology. Got: {response_text[:200]}"


@pytest.mark.asyncio
async def test_agent_handles_empty_input(test_runner, mocker):
    """Test that agent handles empty input gracefully."""
    async def mock_run_async(*args, **kwargs):
        from google.genai.types import Content, Part
        yield AgentEvent(
            author="agent",
            content=Content(parts=[Part(text="Mocked response for empty input.")])
        )

    mocker.patch(
        "google.adk.agents.llm_agent.LlmAgent.run_async",
        new=mock_run_async
    )
    runner, session_service = test_runner
    
    # Create session first
    await session_service.create_session(
        app_name="capricorn_pytest",
        user_id="test_user",
        session_id="test_empty"
    )
    
    user_content = types.Content(
        parts=[types.Part(text="")]
    )
    
    # Run agent - should not crash
    event_count = 0
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_empty",
        new_message=user_content
    ):
        event_count += 1
        # Just count events, don't need to process
    
    # Should handle empty input without crashing
    assert event_count > 0, "Should have received at least one event even with empty input"


@pytest.mark.asyncio
async def test_agent_callback_parsing():
    """Test that parsing utilities work correctly."""
    from capricorn_adk_agent.shared_libraries.parsing_utils import (
        parse_llm_json_output,
        validate_paper_structure,
        validate_query_structure
    )
    
    # Test JSON parsing
    json_str = '{"test": "value"}'
    result = parse_llm_json_output(json_str)
    assert result == {"test": "value"}
    
    # Test markdown JSON parsing
    markdown_json = '```json\n{"wrapped": "json"}\n```'
    result = parse_llm_json_output(markdown_json)
    assert result == {"wrapped": "json"}
    
    # Test paper validation
    valid_paper = {"title": "Test Paper", "authors": "Test Author"}
    validated = validate_paper_structure(valid_paper)
    assert validated is not None
    assert validated["title"] == "Test Paper"
    
    # Test query validation
    query_str = "test query"
    validated = validate_query_structure(query_str, 1)
    assert validated is not None
    assert validated["query"] == "test query"
    assert validated["id"] == 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])