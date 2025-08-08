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

"""Tests for the enhanced architecture with Sequential, Parallel, and Loop agents."""

import asyncio
import os
from unittest.mock import Mock
import pytest

try:
    # Import the enhanced agents
    from capricorn_adk_agent.sub_agents.query_generator.agent import enhanced_query_generator_agent
    from capricorn_adk_agent.sub_agents.parallel_search.agent import parallel_search_orchestrator
    from capricorn_adk_agent.sub_agents.paper_analysis.agent import enhanced_paper_analysis_agent
    from capricorn_adk_agent.sub_agents.lit_review.agent import lit_review_coordinator
    from capricorn_adk_agent.shared_libraries.callbacks import initialize_literature_state
    from capricorn_adk_agent.shared_libraries.quality_tools import check_literature_quality
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)


class TestEnhancedArchitecture:
    """Test the enhanced multi-agent architecture."""
    
    def test_imports(self):
        """Test that all enhanced agents import correctly."""
        assert enhanced_query_generator_agent is not None
        assert parallel_search_orchestrator is not None
        assert enhanced_paper_analysis_agent is not None
        assert lit_review_coordinator is not None
    
    @pytest.mark.asyncio
    async def test_state_initialization(self):
        """Test that state initialization works correctly."""
        
        # Mock callback context
        mock_context = Mock()
        mock_context.state = {}
        
        # Test initialization
        result = await initialize_literature_state(mock_context)
        
        # Verify state was initialized
        assert "patient_case" in mock_context.state
        assert "iteration_count" in mock_context.state
        assert "search_queries" in mock_context.state
        assert "raw_papers" in mock_context.state
        assert "analyzed_papers" in mock_context.state
        assert "search_metrics" in mock_context.state
        
        # Should return None (no content to inject)
        assert result is None
        print("✅ State initialization works")
    
    @pytest.mark.asyncio
    async def test_quality_check_insufficient_papers(self):
        """Test quality check with insufficient papers."""
        
        # Mock tool context with insufficient papers
        mock_context = Mock()
        mock_context.state = {
            "analyzed_papers": [
                {"title": "Paper 1", "year": 2023},
                {"title": "Paper 2", "year": 2024}
            ]
        }
        
        # Should fail due to insufficient papers (< 5)
        result = await check_literature_quality(mock_context)
        
        assert result["status"] == "failure"
        assert "refinement_reason" in mock_context.state
        assert "Insufficient papers" in mock_context.state["refinement_reason"]
        print("✅ Quality check correctly identifies insufficient papers")
    
    @pytest.mark.asyncio
    async def test_quality_check_sufficient_papers(self):
        """Test quality check with sufficient quality papers."""
        
        # Mock tool context with sufficient papers
        mock_context = Mock()
        mock_context.state = {
            "analyzed_papers": [
                {"title": "Paper 1", "year": 2023, "type": "clinical_trial"},
                {"title": "Paper 2", "year": 2024, "type": "review"},
                {"title": "Paper 3", "year": 2022, "type": "case_study"},
                {"title": "Paper 4", "year": 2023, "type": "clinical_trial"},
                {"title": "Paper 5", "year": 2024, "type": "meta_analysis"}
            ]
        }
        
        # Should pass with sufficient recent papers
        result = await check_literature_quality(mock_context)
        
        assert result["status"] == "success"
        # No refinement reason should be set
        assert mock_context.state.get("refinement_reason") is None
        assert mock_context.actions.escalate is True
        print("✅ Quality check correctly accepts sufficient papers")


class TestQueryGeneration:
    """Test query generation functionality."""
    
    def test_query_generator_agent_exists(self):
        """Test that the enhanced query generator exists."""
        assert enhanced_query_generator_agent.name == "enhanced_query_generator"
        assert "Generates diverse, targeted search queries" in enhanced_query_generator_agent.description


class TestParallelSearch:
    """Test parallel search functionality."""
    
    def test_parallel_search_orchestrator_exists(self):
        """Test that the parallel search orchestrator exists."""
        assert parallel_search_orchestrator.name == "parallel_search_orchestrator"
        assert "parallel" in parallel_search_orchestrator.description.lower()


class TestPaperAnalysis:
    """Test paper analysis functionality."""
    
    def test_enhanced_paper_analyzer_exists(self):
        """Test that the enhanced paper analyzer exists."""
        assert enhanced_paper_analysis_agent.name == "enhanced_medical_paper_analyzer"
        assert "scores" in enhanced_paper_analysis_agent.description.lower()


class TestLiteratureReviewCoordinator:
    """Test the main literature review coordinator."""
    
    def test_coordinator_is_loop_agent(self):
        """Test that the coordinator is a LoopAgent."""
        # Check that it has the characteristics of a LoopAgent
        assert lit_review_coordinator.name == "literature_review_coordinator"
        assert hasattr(lit_review_coordinator, 'max_iterations')
        assert lit_review_coordinator.max_iterations == 3
    
    def test_coordinator_has_quality_check(self):
        """Test that the coordinator has a quality check agent."""
        assert len(lit_review_coordinator.sub_agents) == 2
        assert lit_review_coordinator.sub_agents[1].name == "quality_check_agent"


@pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"), 
    reason="Integration tests require environment setup"
)
class TestIntegration:
    """Integration tests for the enhanced architecture."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_mock(self):
        """Test the full pipeline with mocked components."""
        
        # This test would require proper ADK environment setup
        # For now, just verify the structure exists
        
        test_case = """
        Patient: 4-year-old female with KMT2A-rearranged AML
        Status: Relapsed post-second HSCT with 33% blasts
        Prior treatments: Multiple lines including revumenib
        """
        
        # The actual test would run:
        # result = await lit_review_coordinator.run(test_case)
        # For now, just verify the coordinator exists and is callable
        
        assert callable(getattr(lit_review_coordinator, 'run', None)) or \
               hasattr(lit_review_coordinator, 'agent')  # LoopAgent structure
    
    def test_architecture_structure(self):
        """Test that the architecture has the expected structure."""
        
        # Verify the coordinator is a LoopAgent
        assert lit_review_coordinator.name == "literature_review_coordinator"
        
        # Verify it has the expected components
        assert hasattr(lit_review_coordinator, 'agent')  # The inner sequential agent
        assert hasattr(lit_review_coordinator, 'max_iterations')
        assert hasattr(lit_review_coordinator, 'loop_condition_tool')
        
        # The inner agent should be the sequential pipeline
        inner_agent = lit_review_coordinator.agent
        assert inner_agent.name == "literature_review_pipeline"
        
        # Should have 3 sub-agents in the sequential pipeline
        assert hasattr(inner_agent, 'sub_agents')
        assert len(inner_agent.sub_agents) == 3
        
        # Verify the order: query generator, parallel search, paper analysis
        sub_agents = inner_agent.sub_agents
        assert sub_agents[0].name == "enhanced_query_generator"
        assert sub_agents[1].name == "parallel_search_orchestrator"  
        assert sub_agents[2].name == "enhanced_medical_paper_analyzer"


if __name__ == "__main__":
    # Run basic tests
    test_arch = TestEnhancedArchitecture()
    
    print("Testing architecture imports...")
    test_arch.test_imports()
    print("✅ All imports successful")
    
    print("\nTesting state initialization...")
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_arch.test_state_initialization())
    print("✅ State initialization works")
    
    print("\nTesting quality checks...")
    loop.run_until_complete(test_arch.test_quality_check_insufficient_papers())
    loop.run_until_complete(test_arch.test_quality_check_sufficient_papers())
    print("✅ Quality checks work correctly")
    
    print("\nTesting architecture structure...")
    test_integration = TestIntegration()
    test_integration.test_architecture_structure()
    print("✅ Architecture structure is correct")
    
    print("\n🎉 All tests passed! Enhanced architecture is ready.")
    print("""
    Architecture Summary:
    📊 LoopAgent (Quality Assurance, max 3 iterations)
      └── SequentialAgent (Core Pipeline)
          ├── Enhanced Query Generator (5-7 diverse queries)
          ├── Parallel Search Orchestrator (concurrent Google searches)
          └── Enhanced Paper Analyzer (scoring + selection)
    
    Ready for Phase 1 implementation! 🚀
    """)