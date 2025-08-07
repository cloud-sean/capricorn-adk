#!/usr/bin/env python
"""Test script for Capricorn ADK Agent with example input."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from google.adk.sessions import InMemorySessionService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk import runners
from capricorn_adk_agent import agent


async def test_agent():
    """Test the agent with example input."""
    
    # Read the example input
    with open("example_input.txt", "r") as f:
        patient_case = f.read()
    
    print("=" * 80)
    print("CAPRICORN MEDICAL ONCOLOGY AGENT - TEST RUN")
    print("=" * 80)
    print("Patient Case:")
    print(patient_case)
    print("=" * 80)
    print("\nInitializing agent...")
    
    # Create services
    session_service = InMemorySessionService()
    credential_service = InMemoryCredentialService()
    
    # Create runner
    runner = runners.Runner(
        app_name="capricorn_test",
        agent=agent.root_agent,
        session_service=session_service,
        credential_service=credential_service
    )
    
    # Create session
    session = await session_service.create_session(
        session_id="test_session",
        app_name="capricorn_test",
        user_id="test_user"
    )
    
    # Create invocation context with all required fields
    from google.genai import types
    
    # Create user content
    user_content = types.Content(
        parts=[types.Part(text=patient_case)]
    )
    
    invocation_context = runners.InvocationContext(
        session_service=session_service,
        invocation_id="test_invocation",
        agent=agent.root_agent,
        session=session,
        user_content=user_content
    )
    
    print("Running agent...")
    print("=" * 80)
    
    # Run the agent
    response_text = ""
    async for event in runner.run_async(invocation_context):
        if hasattr(event, 'text'):
            print(f"[{getattr(event, 'author', 'agent')}]: {event.text}")
            response_text += event.text
        elif hasattr(event, 'content'):
            content = event.content
            if hasattr(content, 'parts'):
                for part in content.parts:
                    if hasattr(part, 'text'):
                        print(f"[{getattr(event, 'author', 'agent')}]: {part.text}")
                        response_text += part.text
    
    print("=" * 80)
    print("Agent execution completed successfully!")
    
    # Check if output files were created
    output_files = ["literature_review_results.json", "formatted_references.md"]
    for file in output_files:
        if Path(file).exists():
            print(f"✓ Created: {file}")
    
    return response_text


if __name__ == "__main__":
    try:
        asyncio.run(test_agent())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()