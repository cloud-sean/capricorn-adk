# Capricorn ADK Agent - Medical Oncology Treatment Advisor

A medical oncology specialist agent built with Google's Agent Development Kit (ADK) that analyzes genetic and oncological patient information to provide evidence-based treatment recommendations.

## Overview

This agent serves as a medical oncology specialist that:
- Analyzes patient genetic profiles and tumor characteristics
- Provides structured treatment recommendations using medical terminology
- Follows evidence-based protocols and current clinical guidelines
- Considers personalized medicine approaches based on molecular profiling

## Features

- **Genetic Analysis**: Processes germline and somatic mutations, biomarkers, and molecular profiles
- **Treatment Strategy**: Recommends first-line and subsequent therapy options
- **Clinical Guidelines**: Follows NCCN, ESMO, and ASCO treatment protocols
- **Precision Medicine**: Incorporates targeted therapies and immunotherapy eligibility
- **Monitoring Plans**: Provides response assessment and toxicity management protocols
- **Literature Review**: Comprehensive medical literature search and analysis for complex cases
  - Generates targeted search queries based on patient-specific factors
  - Retrieves and analyzes recent medical literature (2022-2024)
  - Selects top 5 most relevant papers for treatment decision-making
  - Integrates literature findings into treatment recommendations

## Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- Google Cloud Project with Vertex AI enabled
- Google Cloud credentials configured

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

## Usage

### CLI Mode
Run the agent in command-line interface:
```bash
cd capricorn_adk_agent/
poetry run adk run .
```

### Web UI Mode
Launch the interactive web interface:
```bash
poetry run adk web
```
Then open your browser to the provided URL and select the agent from the dropdown.

### API Server Mode
Start a local FastAPI server:
```bash
poetry run adk api_server capricorn_adk_agent --allow_origins="*"
```
Access the API at `http://127.0.0.1:8000` with docs at `http://127.0.0.1:8000/docs`

## Input Format

Provide patient information including:

**Genetic Information:**
- Germline mutations (BRCA1/2, Lynch syndrome genes, p53, etc.)
- Somatic mutations and tumor markers
- Microsatellite instability (MSI) status
- Tumor mutational burden (TMB)
- PD-L1 expression levels

**Clinical Information:**
- Primary tumor type, stage, and histology
- Metastatic sites and patterns
- Prior treatment history and responses
- Performance status and comorbidities

## Output Format

The agent provides structured recommendations including:

1. **Molecular Profile Summary**: Key genetic alterations and clinical significance
2. **Treatment Strategy**: Recommended therapies with rationale and alternatives
3. **Monitoring Plan**: Response assessment and toxicity management
4. **Additional Considerations**: Genetic counseling, clinical trials, palliative care

## Example Interactions

### Basic Treatment Recommendation
```
Input: "45-year-old female with invasive ductal carcinoma, ER+/PR+/HER2-, BRCA1 mutation, T2N1M0"

Output: 
- Molecular Profile: BRCA1 pathogenic variant, hormone receptor positive, HER2 negative
- Treatment Strategy: Neoadjuvant chemotherapy with carboplatin-based regimen, followed by surgery
- Monitoring: Response assessment q3 cycles, genetic counseling for family
- Considerations: Fertility preservation discussion, PARP inhibitor maintenance
```

### Complex Case with Literature Review
```
Input: "A now almost 4-year-old female diagnosed with KMT2A-rearranged AML and CNS2 involvement exhibited refractory disease after NOPHO DBH AML 2012 protocol. Post-MEC and ADE, MRD remained at 35% and 53%. Vyxeos-clofarabine therapy reduced MRD to 18%. Third-line FLAG-Mylotarg lowered MRD to 3.5% (flow) and 1% (molecular). After a cord blood HSCT in December 2022, she relapsed 10 months later with 3% MRD and femoral extramedullary disease. After the iLTB discussion, in November 2023 the patient was enrolled in the SNDX5613 trial, receiving revumenib for three months, leading to a reduction in KMT2A MRD to 0.1% by PCR. Subsequently, the patient underwent a second allogeneic HSCT using cord blood with treosulfan, thiotepa, and fludarabine conditioning, followed by revumenib maintenance. In August 2024, 6.5 months after the second HSCT, the patient experienced a bone marrow relapse with 33% blasts. The patient is currently in very good clinical condition."

Expected Agent Response:
1. Agent recognizes this as a complex, rare case requiring literature review
2. Invokes Literature Review Coordinator to:
   - Generate targeted queries: "KMT2A rearranged AML pediatric treatment", "revumenib KMT2A AML clinical trial", "relapsed refractory KMT2A AML second transplant", etc.
   - Search for recent papers (2022-2024) on KMT2A-rearranged AML treatments
   - Analyze and select top 5 most relevant papers
3. Integrates literature findings with case analysis to provide:
   - Updated treatment options based on recent trials
   - Novel combination approaches
   - Evidence-based recommendations for this specific scenario
```

## Testing

Run unit tests:
```bash
pytest
```

## Deployment

Deploy to Vertex AI Agent Engine:
```bash
cd deployment/
python deploy.py --create
```

## Important Notes

- **Educational/Research Use Only**: All recommendations are for educational and research purposes
- **Clinical Validation Required**: Recommendations require multidisciplinary tumor board review
- **Human Oversight**: Always involve qualified oncologists in treatment decisions
- **Genetic Counseling**: Recommend professional genetic counseling for hereditary syndromes

## Architecture

This is a single-agent system built with:
- **Agent Type**: `Agent` with Gemini 2.5 Pro model
- **Framework**: Google ADK v1.0.0
- **Deployment**: Vertex AI Agent Engine compatible

## License

Apache License 2.0 - See LICENSE file for details.

## Contributing

Please ensure all medical recommendations follow evidence-based guidelines and include appropriate disclaimers for clinical use.