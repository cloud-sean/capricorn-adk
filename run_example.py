#!/usr/bin/env python
"""Script to run the Capricorn ADK Agent with example input."""

import asyncio
from google.adk import runners
from google.adk.sessions import InMemorySessionService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from capricorn_adk_agent import agent

async def main():
    """Run the agent with example input."""
    
    # Read the example input
    with open("example_input.txt", "r") as f:
        patient_case = f.read()
    
    # Create services
    session_service = InMemorySessionService()
    credential_service = InMemoryCredentialService()
    
    # Create a runner for the agent
    runner = runners.Runner(
        app_name="capricorn_medical_agent",
        agent=agent.root_agent,
        session_service=session_service,
        credential_service=credential_service
    )
    
    # Run the agent with the input
    print("Running Capricorn Medical Oncology Agent with example patient case...")
    print("=" * 80)
    
    # Create an invocation context
    invocation_context = runners.InvocationContext(
        initial_message=patient_case,
        session_id="test_session"
    )
    
    async for event in runner.run_async(invocation_context):
        if hasattr(event, 'text'):
            print(f"[{event.author}]: {event.text}")
        elif hasattr(event, 'content'):
            print(f"[{event.author}]: {event.content}")
    
    print("=" * 80)
    print("Agent execution completed.")

if __name__ == "__main__":
    asyncio.run(main())