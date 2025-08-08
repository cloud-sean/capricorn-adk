#!/usr/bin/env python
"""
CLI test script for Capricorn ADK Agent.
Runs the agent with example input and validates it executes without errors.
"""

import asyncio
import sys
import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from google.adk import runners
from google.adk.sessions import InMemorySessionService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.genai import types
from capricorn_adk_agent import agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentTestRunner:
    """Test runner for ADK agents."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the test runner."""
        self.verbose = verbose
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        self.session_service = InMemorySessionService()
        self.credential_service = InMemoryCredentialService()
        self.runner = None
        self.test_results = {
            "passed": [],
            "failed": [],
            "errors": []
        }
    
    async def setup(self):
        """Set up the test environment."""
        logger.info("Setting up test environment...")
        
        self.runner = runners.Runner(
            app_name="capricorn_test_cli",
            agent=agent.root_agent,
            session_service=self.session_service,
            credential_service=self.credential_service
        )
        
        logger.info("Test environment ready")
    
    async def run_test_case(self, test_name: str, input_text: str) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            test_name: Name of the test
            input_text: Input text for the agent
            
        Returns:
            Test result dictionary
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*60}")
        
        result = {
            "test_name": test_name,
            "status": "unknown",
            "response": None,
            "error": None,
            "events": [],
            "duration_ms": 0
        }
        
        try:
            # Create session first
            session_id = f"test_{test_name}"
            await self.session_service.create_session(
                session_id=session_id,
                app_name="capricorn_test_cli",
                user_id="test_user"
            )
            
            # Create user content with the actual patient case
            # Make sure we're sending the actual input text
            logger.debug(f"Sending input text ({len(input_text)} chars): {input_text[:200]}...")
            user_content = types.Content(
                parts=[types.Part(text=input_text)]
            )
            
            # Run the agent using the correct Runner API
            import time
            start_time = time.time()
            
            response_text = ""
            event_count = 0
            
            async for event in self.runner.run_async(
                user_id="test_user",
                session_id=session_id,
                new_message=user_content
            ):
                event_count += 1
                
                # Collect event information
                event_info = {
                    "type": type(event).__name__,
                    "author": getattr(event, 'author', 'unknown')
                }
                
                # Extract text from event
                if hasattr(event, 'text'):
                    event_text = event.text
                    response_text += event_text
                    event_info["text_length"] = len(event_text)
                    if self.verbose:
                        logger.debug(f"[{event_info['author']}]: {event_text[:200]}...")
                elif hasattr(event, 'content'):
                    content = event.content
                    if hasattr(content, 'parts'):
                        for part in content.parts:
                            if hasattr(part, 'text'):
                                response_text += part.text
                                event_info["text_length"] = len(part.text)
                
                result["events"].append(event_info)
            
            end_time = time.time()
            result["duration_ms"] = int((end_time - start_time) * 1000)
            
            # Check if we got a response
            if response_text:
                result["status"] = "passed"
                result["response"] = response_text[:500] + "..." if len(response_text) > 500 else response_text
                logger.info(f"✅ Test passed - Got response with {len(response_text)} characters")
                logger.info(f"   Processed {event_count} events in {result['duration_ms']}ms")
                self.test_results["passed"].append(test_name)
            else:
                result["status"] = "failed"
                result["error"] = "No response generated"
                logger.error(f"❌ Test failed - No response generated")
                self.test_results["failed"].append(test_name)
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"❌ Test error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            self.test_results["errors"].append(test_name)
        
        return result
    
    async def run_all_tests(self):
        """Run all configured tests."""
        await self.setup()
        
        # Test 1: Simple test with a basic query
        simple_test = """45-year-old female with invasive ductal carcinoma, ER+/PR+/HER2-, 
        BRCA1 mutation, T2N1M0. What are the treatment options?"""
        
        result1 = await self.run_test_case("simple_case", simple_test)
        
        # Test 2: Complex test with example_input.txt
        example_file = Path("example_input.txt")
        if example_file.exists():
            with open(example_file, "r") as f:
                complex_test = f.read()
            result2 = await self.run_test_case("complex_case", complex_test)
        else:
            logger.warning("example_input.txt not found, skipping complex test")
            result2 = None
        
        # Test 3: Edge case - empty input
        result3 = await self.run_test_case("empty_input", "")
        
        # Print summary
        self.print_summary([result1, result2, result3])
    
    def print_summary(self, results):
        """Print test summary."""
        logger.info(f"\n{'='*60}")
        logger.info("TEST SUMMARY")
        logger.info(f"{'='*60}")
        
        total_tests = len([r for r in results if r])
        passed = len(self.test_results["passed"])
        failed = len(self.test_results["failed"])
        errors = len(self.test_results["errors"])
        
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"⚠️  Errors: {errors}")
        
        if passed == total_tests:
            logger.info("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            logger.error(f"\n❌ {failed + errors} test(s) failed")
            sys.exit(1)


async def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Capricorn ADK Agent")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-i", "--input", type=str, help="Custom input file to test")
    parser.add_argument("-t", "--test", type=str, help="Specific test to run (simple, complex, empty)")
    
    args = parser.parse_args()
    
    runner = AgentTestRunner(verbose=args.verbose)
    
    if args.input:
        # Run with custom input file
        with open(args.input, "r") as f:
            input_text = f.read()
        result = await runner.run_test_case(Path(args.input).stem, input_text)
        runner.print_summary([result])
    elif args.test:
        # Run specific test
        await runner.setup()
        if args.test == "simple":
            test_input = "45-year-old female with breast cancer, ER+/PR+/HER2-, BRCA1 mutation"
            result = await runner.run_test_case("simple_case", test_input)
        elif args.test == "complex":
            with open("example_input.txt", "r") as f:
                test_input = f.read()
            result = await runner.run_test_case("complex_case", test_input)
        elif args.test == "empty":
            result = await runner.run_test_case("empty_input", "")
        else:
            logger.error(f"Unknown test: {args.test}")
            sys.exit(1)
        runner.print_summary([result])
    else:
        # Run all tests
        await runner.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)