# Capricorn ADK Agent - Medical Oncology Research Prototype

> ⚠️ **IMPORTANT DISCLAIMER**  
> This is an **experimental research prototype** developed by the Google Cloud Healthcare and Life Sciences Customer Engineering Team. This code sample is intended **solely for research and development purposes** and is **not designed or intended to be deployed in clinical settings** or used for actual patient care. Users acknowledge they bear sole responsibility and liability for any use of this system.

## Overview

This experimental prototype demonstrates the capabilities of Google's Agent Development Kit (ADK) for complex healthcare AI workflows. The system showcases a multi-agent architecture for medical oncology case analysis, featuring:

- **Genetic profile analysis** with molecular profiling integration
- **Evidence-based treatment exploration** following clinical protocols
- **Literature review coordination** with automated medical research
- **Multi-agent coordination** patterns for complex healthcare workflows

**Research Focus Areas:**
- Agent orchestration patterns for healthcare AI
- Multi-modal medical data processing with LLMs
- Automated literature review and synthesis workflows
- Clinical decision support system architectures

## Technical Features

This prototype demonstrates several advanced ADK capabilities:

### Core Agent Architecture
- **Literature Review Coordinator**: Multi-agent orchestration for medical research workflows
- **Paper Search & Analysis**: Specialized agents for PubMed and medical literature processing
- **Query Generation**: LLM-powered search query optimization for medical contexts
- **Parallel Processing**: Concurrent literature analysis and synthesis

### Healthcare AI Workflows
- **Genetic Profile Processing**: Molecular profiling and biomarker analysis workflows
- **Treatment Protocol Exploration**: Integration with clinical guideline databases (NCCN, ESMO, ASCO)
- **Evidence Synthesis**: Automated literature review and recommendation generation
- **Multi-Modal Data**: Support for clinical, genetic, and imaging data integration

### Google Cloud Integration
- **Vertex AI**: Powered by Gemini 2.5 Pro for advanced medical reasoning
- **BigQuery**: Healthcare data analytics and storage patterns
- **Cloud Healthcare API**: FHIR-compliant data processing demonstrations

## Prerequisites

**Development Environment:**
- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- Git for version control

**Google Cloud Setup:**
- Google Cloud Project with the following APIs enabled:
  - Vertex AI API
  - Cloud Healthcare API (optional, for FHIR demonstrations)
  - BigQuery API (optional, for data analytics examples)
- Google Cloud credentials configured (`gcloud auth application-default login`)
- Appropriate IAM permissions for Vertex AI model access

## Setup

1. **Navigate to the agent directory:**
   ```bash
   cd capricorn-adk-agent
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your values:
   # - GOOGLE_CLOUD_PROJECT: Your GCP project ID
   # - GOOGLE_CLOUD_LOCATION: GCP region (e.g., us-central1)
   # - STAGING_BUCKET: Your GCS bucket for deployments
   ```

4. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth application-default login
   ```

## Running the Prototype

### Interactive Development (Recommended)
Launch the web-based development interface:
```bash
poetry run adk web
```
Navigate to the provided URL and select the agent from the dropdown menu.

### Command Line Testing
Run the agent via CLI for automated testing:
```bash
cd capricorn_adk_agent/
poetry run adk run .
```

### API Integration
Start a local FastAPI server for integration testing:
```bash
poetry run adk api_server capricorn_adk_agent --allow_origins="*"
```
- API endpoint: `http://127.0.0.1:8000`
- Interactive documentation: `http://127.0.0.1:8000/docs`

## Research Use Cases

This prototype supports various healthcare AI research scenarios:

### 1. Multi-Agent Coordination Research
- **Literature Review Orchestration**: Complex workflows with multiple specialized agents
- **Parallel Processing**: Concurrent analysis of medical literature and data
- **Agent Communication**: State management and information sharing between agents

### 2. Medical NLP and Reasoning
- **Clinical Text Processing**: Analysis of medical case descriptions and patient histories
- **Evidence Synthesis**: Automated synthesis of medical literature findings
- **Structured Output Generation**: Clinical reasoning and recommendation formatting

### 3. Healthcare Data Integration
- **Multi-Modal Analysis**: Integration of genetic, clinical, and literature data
- **FHIR Compatibility**: Healthcare data standard processing demonstrations
- **Real-Time Processing**: Live literature search and analysis workflows

## Example Research Scenarios

### Simple Case Analysis
```
Input: "45-year-old female with invasive ductal carcinoma, ER+/PR+/HER2-, BRCA1 mutation, T2N1M0"

Prototype demonstrates:
- Genetic profile interpretation workflows
- Treatment protocol database integration
- Evidence-based reasoning patterns
- Clinical decision support architectures
```

### Complex Multi-Agent Literature Review
```
Input: Complex pediatric oncology case with rare genetic markers

Prototype workflow:
1. Case complexity assessment and routing
2. Multi-agent literature search coordination
3. Parallel paper analysis and ranking
4. Evidence synthesis and integration
5. Structured recommendation generation
```

## Development and Testing

### Running Tests
Execute the prototype's test suite:
```bash
pytest
```

### Architecture Validation
Verify the multi-agent system architecture:
```bash
python validate_architecture.py
```

### Evaluation Framework
This prototype includes evaluation capabilities for research assessment:
```bash
# Run evaluation tests (when available)
python eval/test_eval.py
```

## Deployment (Research Only)

For research environments, deploy to Vertex AI Agent Engine:
```bash
cd deployment/
python deploy.py --create
```
> **Note**: Deployment is intended only for controlled research environments with appropriate security and privacy safeguards.

## Research Ethics and Responsible AI

This prototype is developed following Google Cloud's AI principles and responsible AI practices:

### Ethical Guidelines
- **Research Purpose Only**: This system is designed exclusively for research and development
- **No Clinical Deployment**: Not intended for actual patient care or clinical decision-making
- **Human Oversight Required**: All outputs require expert medical review and validation
- **Privacy by Design**: Implements data protection and privacy safeguards for research data

### Limitations and Considerations
- **Experimental Nature**: This is a research prototype with inherent limitations
- **Validation Required**: All AI-generated content requires medical expert review
- **Bias Awareness**: May reflect biases present in training data and medical literature
- **Scope Limitations**: Focused on oncology research scenarios, not comprehensive medical care

## Technical Architecture

**Multi-Agent System Components:**
- **Root Agent**: Main coordination and patient case analysis
- **Literature Review Coordinator**: Orchestrates complex literature search workflows
- **Specialized Sub-Agents**: Paper search, analysis, and query generation agents
- **Shared Libraries**: Common utilities for quality assessment and callback management

**Google Cloud Integration:**
- **Framework**: Google ADK v1.0.0 with Gemini 2.5 Pro
- **Platform**: Vertex AI Agent Engine compatible
- **Deployment**: Cloud-native architecture for scalable research applications

## Contributing to Healthcare AI Research

Researchers interested in extending this prototype should:

1. **Follow Responsible AI Principles**: Ensure all modifications adhere to ethical AI development practices
2. **Maintain Research Focus**: Keep the experimental nature and appropriate disclaimers
3. **Document Thoroughly**: Provide comprehensive documentation for research reproducibility
4. **Engage Domain Experts**: Collaborate with healthcare professionals for medical accuracy

## Support and Resources

**Google Cloud Resources:**
- [Healthcare and Life Sciences on Google Cloud](https://cloud.google.com/solutions/healthcare-life-sciences)
- [Vertex AI Agent Engine Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agents)
- [Responsible AI Practices](https://ai.google/responsibility/principles/)

**Community:**
- Report issues or contribute to the Google ADK samples repository
- Engage with the Google Cloud Healthcare and Life Sciences community

---

*This research prototype is maintained by the Google Cloud Healthcare and Life Sciences Customer Engineering Team as part of ongoing research into AI applications in healthcare workflows.*