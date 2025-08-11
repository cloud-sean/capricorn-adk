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

"""Structured output models for the Capricorn ADK Agent."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class PubMedQuery(BaseModel):
    """Model representing a specific PubMed search query."""
    
    query: str = Field(
        description="A highly specific and targeted query for PubMed literature search."
    )
    rationale: str = Field(
        description="Brief explanation of why this query is relevant to the medical case."
    )
    expected_papers: int = Field(
        default=5,
        description="Expected number of relevant papers from this query."
    )


class PaperRelevance(BaseModel):
    """Model for evaluating individual paper relevance to a medical case."""
    
    paper_id: str = Field(
        description="Unique identifier for the paper (PMID or DOI)."
    )
    title: str = Field(
        description="Full title of the paper."
    )
    relevance_score: float = Field(
        ge=0.0, le=1.0,
        description="Relevance score between 0 and 1."
    )
    key_findings: list[str] = Field(
        description="List of key findings relevant to the medical case."
    )
    clinical_impact: str = Field(
        description="How this paper's findings could impact clinical decision-making."
    )


class LiteratureQualityAssessment(BaseModel):
    """Model for comprehensive literature review quality assessment."""
    
    grade: Literal["excellent", "good", "adequate", "insufficient"] = Field(
        description="Overall quality grade of the literature review."
    )
    total_papers_reviewed: int = Field(
        description="Total number of papers reviewed."
    )
    high_relevance_papers: int = Field(
        description="Number of papers with relevance score > 0.7."
    )
    coverage_assessment: str = Field(
        description="Assessment of how well the literature covers the medical case aspects."
    )
    gaps_identified: Optional[list[str]] = Field(
        default=None,
        description="Specific gaps in the literature review that need addressing."
    )
    follow_up_queries: Optional[list[PubMedQuery]] = Field(
        default=None,
        description="Additional queries needed to fill identified gaps."
    )
    confidence_level: float = Field(
        ge=0.0, le=1.0,
        description="Confidence level in the completeness of the review."
    )


class ClinicalRecommendation(BaseModel):
    """Model for structured clinical recommendations based on literature."""
    
    recommendation: str = Field(
        description="Specific clinical recommendation."
    )
    evidence_level: Literal["high", "moderate", "low", "very_low"] = Field(
        description="Level of evidence supporting this recommendation."
    )
    supporting_papers: list[str] = Field(
        description="List of paper IDs supporting this recommendation."
    )
    contraindications: Optional[list[str]] = Field(
        default=None,
        description="Known contraindications or cautions."
    )
    patient_specific_considerations: Optional[str] = Field(
        default=None,
        description="Considerations specific to the patient's case."
    )


class LiteratureReviewReport(BaseModel):
    """Model for the final literature review report structure."""
    
    case_summary: str = Field(
        description="Brief summary of the medical case being reviewed."
    )
    search_strategy: list[PubMedQuery] = Field(
        description="Search queries used in the literature review."
    )
    papers_analyzed: list[PaperRelevance] = Field(
        description="List of papers analyzed with relevance scores."
    )
    key_findings: list[str] = Field(
        description="Major findings from the literature review."
    )
    clinical_recommendations: list[ClinicalRecommendation] = Field(
        description="Evidence-based clinical recommendations."
    )
    quality_assessment: LiteratureQualityAssessment = Field(
        description="Quality assessment of the literature review."
    )
    limitations: Optional[list[str]] = Field(
        default=None,
        description="Limitations of the current literature review."
    )


class CitationMetadata(BaseModel):
    """Model for tracking citation metadata and confidence."""
    
    source_id: str = Field(
        description="Unique identifier for the source (e.g., 'src-1')."
    )
    title: str = Field(
        description="Title of the source."
    )
    authors: Optional[list[str]] = Field(
        default=None,
        description="List of authors."
    )
    journal: Optional[str] = Field(
        default=None,
        description="Journal name."
    )
    year: Optional[int] = Field(
        default=None,
        description="Publication year."
    )
    doi: Optional[str] = Field(
        default=None,
        description="Digital Object Identifier."
    )
    pmid: Optional[str] = Field(
        default=None,
        description="PubMed ID."
    )
    url: str = Field(
        description="URL to the source."
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in the source's reliability."
    )
    supported_claims: list[dict] = Field(
        default_factory=list,
        description="List of claims supported by this source with confidence scores."
    )