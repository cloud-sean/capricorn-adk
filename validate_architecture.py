#!/usr/bin/env python3
"""Simple validation script to verify the enhanced architecture is working."""

def main():
    print("🔍 Validating Enhanced Architecture...")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from capricorn_adk_agent.sub_agents.query_generator.agent import enhanced_query_generator_agent
        from capricorn_adk_agent.sub_agents.parallel_search.agent import parallel_search_orchestrator
        from capricorn_adk_agent.sub_agents.paper_analysis.agent import enhanced_paper_analysis_agent
        from capricorn_adk_agent.sub_agents.lit_review.agent import lit_review_coordinator
        print("   ✅ All agent imports successful")
        
        # Test shared libraries
        from capricorn_adk_agent.shared_libraries.callbacks import initialize_literature_state
        from capricorn_adk_agent.shared_libraries.quality_tools import check_literature_quality
        print("   ✅ Shared libraries import successful")
        
        # Validate agent structure
        print("\n2. Validating agent structure...")
        
        # Check query generator
        assert enhanced_query_generator_agent.name == "enhanced_query_generator"
        assert enhanced_query_generator_agent.model == "gemini-2.5-flash"
        print("   ✅ Query generator configured correctly")
        
        # Check parallel search orchestrator
        assert parallel_search_orchestrator.name == "parallel_search_orchestrator"
        print("   ✅ Parallel search orchestrator configured correctly")
        
        # Check paper analyzer
        assert enhanced_paper_analysis_agent.name == "enhanced_medical_paper_analyzer"
        assert enhanced_paper_analysis_agent.model == "gemini-2.5-pro"
        print("   ✅ Paper analyzer configured correctly")
        
        # Check literature review coordinator (LoopAgent)
        assert lit_review_coordinator.name == "literature_review_coordinator"
        assert hasattr(lit_review_coordinator, 'max_iterations')
        assert lit_review_coordinator.max_iterations == 3
        print("   ✅ Literature review coordinator (LoopAgent) configured correctly")
        
        # Check the inner sequential agent
        inner_agent = lit_review_coordinator.sub_agents[0]  # LoopAgent has sub_agents
        assert inner_agent.name == "literature_review_pipeline"
        assert hasattr(inner_agent, 'sub_agents')
        assert len(inner_agent.sub_agents) == 3
        print("   ✅ Inner sequential pipeline has 3 sub-agents")
        
        # Validate the sequence order
        sub_agents = inner_agent.sub_agents
        assert sub_agents[0].name == "enhanced_query_generator"
        assert sub_agents[1].name == "parallel_search_orchestrator"
        assert sub_agents[2].name == "enhanced_medical_paper_analyzer"
        print("   ✅ Agent sequence is correct: Query Gen → Parallel Search → Paper Analysis")
        
        print("\n3. Architecture Summary:")
        print("   📊 LoopAgent (Quality Assurance, max 3 iterations)")
        print("     └── SequentialAgent (Core Pipeline)")
        print("         ├── Enhanced Query Generator (5-7 diverse queries)")
        print("         ├── Parallel Search Orchestrator (concurrent Google searches)")
        print("         └── Enhanced Paper Analyzer (scoring + selection)")
        
        print("\n🎉 Architecture Validation Complete!")
        print("✅ All components are correctly configured and integrated")
        print("🚀 Ready for Phase 1 implementation!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)