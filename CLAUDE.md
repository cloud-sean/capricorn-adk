# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Capricorn ADK Agent - a research prototype demonstrating Google's Agent Development Kit (ADK) for complex healthcare AI workflows, specifically medical oncology case analysis with advanced literature review capabilities.

## Key Commands

### Development
```bash
# Install dependencies (from project root)
poetry install

# Run interactive web UI (recommended for development)
poetry run adk web

# Run agent via CLI (from capricorn_adk_agent/ directory)
cd capricorn_adk_agent/
poetry run adk run .

# Start API server for integration
poetry run adk api_server capricorn_adk_agent --allow_origins="*"
```

### Testing & Validation
```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_enhanced_architecture.py -v

# Validate multi-agent architecture
python misc/validate_architecture.py

# Format code
poetry run black .
```

## Architecture Overview

### Multi-Agent Hierarchy
The system uses a sophisticated nested agent architecture with ADK's coordination patterns:

```
root_agent (Agent) - Main medical oncology specialist
└── lit_review_coordinator (LoopAgent) - Iterative quality assurance (max 3 iterations)
    └── literature_review_pipeline (SequentialAgent) - Core processing pipeline
        ├── enhanced_query_generator_agent (Agent) - Generates 5-7 diverse PubMed queries
        ├── parallel_search_orchestrator (ParallelAgent) - Concurrent Google searches
        └── enhanced_paper_analysis_agent (Agent) - Scores and selects papers
```

### Key Agent Coordination Patterns

1. **LoopAgent** (`lit_review_coordinator`): Provides iterative refinement with quality checks
2. **SequentialAgent** (`literature_review_pipeline`): Ensures ordered workflow execution
3. **ParallelAgent** (`parallel_search_orchestrator`): Enables concurrent processing
4. **Callback System**: State management through `before_agent_callback` and `after_agent_callback`

### Shared Libraries Architecture

The `shared_libraries/` directory contains critical cross-agent utilities:

- **callbacks.py**: State initialization and result aggregation functions
  - `initialize_literature_state()`: Sets up shared context
  - `track_iteration()`: Monitors pipeline progress
  - `aggregate_parallel_results()`: Combines search results
  - `save_final_results()`: Persists final output

- **quality_tools.py**: Quality assessment functions
  - `check_literature_quality()`: Validates paper relevance and quality

- **citation_utils.py**: Citation formatting and management

### Agent Models Strategy

Different models optimized for specific tasks:
- **gemini-2.5-pro**: Complex reasoning (root agent, paper analysis)
- **gemini-2.5-flash**: High-speed operations (query generation, search)

## Environment Configuration

Required `.env` file setup:
```bash
cp .env.example .env
```

Key variables:
- `GOOGLE_GENAI_USE_VERTEXAI=1`: Use Vertex AI backend
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_CLOUD_LOCATION`: Region (typically us-central1)
- `MODEL`: Default model (gemini-2.5-pro)
- `STAGING_BUCKET`: For deployment (optional)

## Development Workflow

### Adding New Sub-Agents
1. Create directory: `capricorn_adk_agent/sub_agents/new_agent/`
2. Required files:
   - `__init__.py`: Export agent
   - `agent.py`: Agent configuration with ADK classes
   - `prompt.py`: Agent-specific prompts

### Modifying Agent Coordination
- For sequential workflows: Use `SequentialAgent`
- For parallel processing: Use `ParallelAgent`
- For iterative refinement: Wrap in `LoopAgent`
- State sharing: Implement callbacks in `shared_libraries/callbacks.py`

### Testing Multi-Agent Interactions
The `validate_architecture.py` script verifies:
- All agents import correctly
- Agent hierarchy is properly configured
- Callback functions are accessible
- Model assignments are correct

## Google ADK Integration Points

### Core ADK Components Used
- `google.adk.agents.Agent`: Base agent class
- `google.adk.agents.SequentialAgent`: Ordered workflow execution
- `google.adk.agents.ParallelAgent`: Concurrent processing
- `google.adk.agents.LoopAgent`: Iterative refinement
- `google.adk.tools.FunctionTool`: Custom tool integration
- `google.adk.tools.agent_tool.AgentTool`: Agent-as-tool pattern

### Agent Communication
Agents communicate through:
1. **Tool Context State**: Shared state dictionary
2. **Callbacks**: Before/after execution hooks
3. **AgentTool Wrapping**: Agents callable as tools by other agents

## Medical Domain Considerations

This prototype focuses on oncology research workflows:
- Genetic profile analysis integration points
- Literature review for evidence-based recommendations
- Multi-modal data processing (clinical, genetic, literature)
- HIPAA-compliant design patterns (research use only)

## Important Notes

- This is a **research prototype** - not for clinical deployment
- All medical outputs require expert validation
- Focus on demonstrating ADK multi-agent patterns for healthcare
- Extensible architecture for additional medical specialties

## ADK Best Practices Guide

### Agent Type Selection

Choose the appropriate agent type based on your use case:

1. **Agent** - Basic coordination with sub-agents and tools
   ```python
   agent = Agent(
       model="gemini-2.5-pro",
       sub_agents=[agent1, agent2],
       tools=[tool1, tool2]
   )
   ```

2. **LlmAgent** - Coordinator/dispatcher pattern with AgentTool delegation
   ```python
   coordinator = LlmAgent(
       model="gemini-2.5-pro",
       tools=[
           AgentTool(agent=specialist_1),
           AgentTool(agent=specialist_2)
       ]
   )
   ```

3. **SequentialAgent** - Ordered workflow execution
   ```python
   pipeline = SequentialAgent(
       name="processing_pipeline",
       sub_agents=[step1_agent, step2_agent, step3_agent]
   )
   ```

4. **ParallelAgent** - Concurrent execution for independent tasks
   ```python
   parallel_processor = ParallelAgent(
       name="parallel_searches",
       sub_agents=[search_agent_1, search_agent_2, search_agent_3]
   )
   ```

5. **LoopAgent** - Iterative refinement with termination conditions
   ```python
   loop = LoopAgent(
       name="refinement_loop",
       sub_agents=[process_agent, checker_agent],
       max_iterations=3,
       before_agent_callback=initialize_state
   )
   ```

### State Management Patterns

#### Inter-Agent Communication
```python
# Setting output keys for explicit state passing
agent = Agent(
    name="analyzer",
    output_key="analysis_results"  # Results available as state["analysis_results"]
)

# Accessing shared state in tools
async def custom_tool(input: str, tool_context: ToolContext):
    previous_results = tool_context.state.get("analysis_results", {})
    # Process and update state
    tool_context.state["processed_data"] = process(input, previous_results)
```

#### Callback Implementation
```python
def initialize_literature_state(callback_context: CallbackContext):
    """Initialize state before agent execution."""
    if "search_results" not in callback_context.state:
        callback_context.state["search_results"] = []
        callback_context.state["iteration_count"] = 0
    
def aggregate_results(callback_context: CallbackContext):
    """Process results after agent execution."""
    results = callback_context.state.get("raw_results", [])
    callback_context.state["aggregated_results"] = aggregate(results)
```

### Tool Development Best Practices

#### Custom Tool Structure
```python
from google.adk.tools import FunctionTool
from google.adk.tools.base_tool import ToolContext

async def advanced_analysis_tool(
    query: str,
    max_results: int = 10,
    tool_context: ToolContext = None
) -> dict:
    """Tool with proper typing and context management."""
    # Access shared state
    config = tool_context.state.get("analysis_config", {})
    
    # Perform operation
    results = await perform_analysis(query, max_results, config)
    
    # Update state for downstream agents
    tool_context.state["latest_analysis"] = results
    
    return {"status": "success", "results": results}

# Register as FunctionTool
analysis_tool = FunctionTool(func=advanced_analysis_tool)
```

#### AgentTool for Sub-Agent Invocation
```python
from google.adk.tools.agent_tool import AgentTool

async def invoke_specialist(request: str, tool_context: ToolContext):
    """Programmatically invoke another agent as a tool."""
    specialist = AgentTool(agent=specialist_agent)
    result = await specialist.run_async(
        args={"request": request},
        tool_context=tool_context
    )
    return result
```

### Multi-Agent Coordination Patterns

#### Pattern 1: Hierarchical Delegation
```python
# Main coordinator delegates to specialists
root_agent = LlmAgent(
    model="gemini-2.5-pro",
    instruction="Analyze the case and delegate to appropriate specialists",
    tools=[
        AgentTool(agent=oncologist_agent),
        AgentTool(agent=radiologist_agent),
        AgentTool(agent=pathologist_agent)
    ]
)
```

#### Pattern 2: Sequential Pipeline with State
```python
# Each stage processes and enriches shared state
pipeline = SequentialAgent(
    sub_agents=[
        data_extraction_agent,  # Extracts raw data
        analysis_agent,         # Analyzes extracted data
        report_generation_agent # Generates final report
    ],
    before_agent_callback=initialize_pipeline_state,
    after_agent_callback=save_pipeline_results
)
```

#### Pattern 3: Parallel Processing with Aggregation
```python
# Concurrent execution with result merging
parallel_search = ParallelAgent(
    sub_agents=[
        pubmed_search_agent,
        arxiv_search_agent,
        google_scholar_agent
    ]
)

# Wrap in sequential pipeline for aggregation
search_pipeline = SequentialAgent(
    sub_agents=[
        query_generator,
        parallel_search,
        result_aggregator
    ]
)
```

#### Pattern 4: Iterative Refinement Loop
```python
def check_quality(tool_context: ToolContext) -> bool:
    """Termination condition for loop."""
    score = tool_context.state.get("quality_score", 0)
    if score >= 0.9:
        tool_context.actions.escalate = True  # Terminate loop
        return True
    return False

quality_loop = LoopAgent(
    sub_agents=[
        generation_agent,
        evaluation_agent  # Sets quality_score in state
    ],
    max_iterations=5
)
```

### Model Selection Strategy

```python
import os

# Performance tiers
FAST_MODEL = "gemini-2.5-flash"      # For simple tasks, high speed
BALANCED_MODEL = "gemini-2.5-pro"    # For complex reasoning
ADVANCED_MODEL = "gemini-2.5-pro"    # For critical decisions

# Environment-based configuration
MODEL = os.getenv("AGENT_MODEL", BALANCED_MODEL)

# Task-specific model selection
query_agent = Agent(model=FAST_MODEL)      # Fast, simple queries
analysis_agent = Agent(model=BALANCED_MODEL) # Complex analysis
decision_agent = Agent(model=ADVANCED_MODEL) # Critical decisions
```

### Error Handling and Validation

```python
def validate_before_tool(
    tool: BaseTool, 
    args: Dict[str, Any], 
    tool_context: ToolContext
) -> Optional[Dict]:
    """Pre-execution validation callback."""
    # Input validation
    if not args.get("patient_id"):
        return {"error": "Patient ID required"}
    
    # Business rule enforcement
    if tool.name == "prescribe_medication":
        if not tool_context.state.get("diagnosis_confirmed"):
            return {"error": "Diagnosis must be confirmed before prescription"}
    
    return None  # Proceed with execution

agent = Agent(
    before_tool_callback=validate_before_tool
)
```

### Performance Optimization

#### Rate Limiting
```python
import time

def rate_limit_callback(callback_context: CallbackContext, llm_request):
    """Implement rate limiting for API calls."""
    last_call = callback_context.state.get("last_api_call", 0)
    min_interval = 1.0  # Minimum seconds between calls
    
    elapsed = time.time() - last_call
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    
    callback_context.state["last_api_call"] = time.time()
```

#### Caching Strategy
```python
def cache_results(tool_context: ToolContext, key: str, value: Any, ttl: int = 3600):
    """Cache results with TTL."""
    cache = tool_context.state.setdefault("cache", {})
    cache[key] = {
        "value": value,
        "expires": time.time() + ttl
    }

def get_cached(tool_context: ToolContext, key: str) -> Optional[Any]:
    """Retrieve cached value if not expired."""
    cache = tool_context.state.get("cache", {})
    if key in cache:
        entry = cache[key]
        if time.time() < entry["expires"]:
            return entry["value"]
    return None
```

### Testing and Validation

```python
# Agent architecture validation
def validate_agent_hierarchy(root_agent):
    """Validate agent configuration."""
    assert hasattr(root_agent, 'name'), "Agent must have name"
    assert hasattr(root_agent, 'model'), "Agent must specify model"
    
    if hasattr(root_agent, 'sub_agents'):
        for sub_agent in root_agent.sub_agents:
            validate_agent_hierarchy(sub_agent)
    
    return True

# Run validation
validate_agent_hierarchy(root_agent)
```

### ADK Development Workflow

1. **Design Phase**: Choose appropriate agent types and coordination patterns
2. **Implementation**: Follow consistent structure (prompts, tools, sub-agents in separate modules)
3. **State Management**: Define clear state keys and data flow
4. **Testing**: Validate architecture and test multi-agent interactions
5. **Optimization**: Implement caching, rate limiting, and appropriate model selection

### Common Pitfalls to Avoid

- **State Key Conflicts**: Use namespaced keys (e.g., `"lit_review.results"` vs just `"results"`)
- **Missing Callbacks**: Initialize state before agent execution to avoid KeyErrors
- **Blocking Operations**: Use async/await for I/O operations in tools
- **Model Overuse**: Don't use expensive models for simple tasks
- **Tight Coupling**: Keep agents modular and communication through state