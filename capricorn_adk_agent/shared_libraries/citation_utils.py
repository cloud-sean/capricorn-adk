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

"""Citation utilities for medical literature references."""

import re
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


def generate_citation_links(paper_data: Any, paper_id: int) -> Dict[str, str]:
    """Generate comprehensive citation links and formatted references for a medical paper.
    
    Now handles various input types robustly to prevent crashes.
    """
    
    citation_links = {
        "pubmed_url": "",
        "doi_url": "",
        "citation_text": "",
        "formatted_reference": ""
    }
    
    # Handle non-dict inputs gracefully
    if isinstance(paper_data, str):
        logger.warning(f"Citation utils received string instead of dict for paper {paper_id}")
        citation_links["citation_text"] = paper_data[:200] if paper_data else "Unknown"
        citation_links["formatted_reference"] = f"[{paper_id}] {paper_data[:100] if paper_data else 'Unknown'}"
        return citation_links
    
    if not isinstance(paper_data, dict):
        logger.error(f"Citation utils received unexpected type: {type(paper_data)} for paper {paper_id}")
        citation_links["formatted_reference"] = f"[{paper_id}] Unknown"
        return citation_links
    
    # Extract paper information safely
    title = paper_data.get("title", "").strip() if paper_data else ""
    authors = paper_data.get("authors", "") if paper_data else ""
    year = paper_data.get("year", "") if paper_data else ""
    journal = paper_data.get("journal", "").strip() if paper_data else ""
    pmid = clean_pmid(paper_data.get("pmid", "")) if paper_data else ""
    doi = clean_doi(paper_data.get("doi", "")) if paper_data else ""
    
    # Generate PubMed URL
    if pmid:
        citation_links["pubmed_url"] = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    
    # Generate DOI URL
    if doi:
        citation_links["doi_url"] = f"https://doi.org/{doi}"
    
    # Format author names for citation
    formatted_authors = format_authors_for_citation(authors)
    
    # Generate standard citation text
    citation_parts = []
    if formatted_authors:
        citation_parts.append(formatted_authors)
    if title:
        citation_parts.append(title)
    if journal:
        citation_parts.append(journal)
    if year:
        citation_parts.append(str(year))
    
    citation_links["citation_text"] = ". ".join(citation_parts) + "."
    
    # Generate formatted reference with markdown formatting
    formatted_ref_parts = [f"[{paper_id}]"]
    if formatted_authors:
        formatted_ref_parts.append(formatted_authors)
    if title:
        formatted_ref_parts.append(title)
    if journal:
        formatted_ref_parts.append(f"*{journal}*")  # Italicize journal name
    if year:
        formatted_ref_parts.append(str(year))
    
    # Add identifiers
    identifiers = []
    if pmid:
        identifiers.append(f"PMID: {pmid}")
    if doi:
        identifiers.append(f"DOI: {doi}")
    
    if identifiers:
        formatted_ref_parts.append(" | ".join(identifiers))
    
    citation_links["formatted_reference"] = ". ".join(formatted_ref_parts) + "."
    
    return citation_links


def clean_pmid(pmid_raw: str) -> str:
    """Clean and validate PubMed ID."""
    if not pmid_raw:
        return ""
    
    # Extract digits only
    pmid = re.sub(r'[^\d]', '', str(pmid_raw))
    
    # Validate PMID format (should be 8-9 digits typically)
    if pmid and len(pmid) >= 6 and pmid.isdigit():
        return pmid
    
    return ""


def clean_doi(doi_raw: str) -> str:
    """Clean and validate DOI."""
    if not doi_raw:
        return ""
    
    doi = str(doi_raw).strip()
    
    # Remove common prefixes
    doi = re.sub(r'^(https?://)?(dx\.)?doi\.org/', '', doi)
    
    # Validate basic DOI format (10.xxxx/yyyy)
    if re.match(r'^10\.\d+/.+', doi):
        return doi
    
    return ""


def format_authors_for_citation(authors_raw: Any) -> str:
    """Format authors for academic citation style."""
    if not authors_raw:
        return ""
    
    # Handle different input formats
    if isinstance(authors_raw, list):
        authors = authors_raw
    elif isinstance(authors_raw, str):
        # Split on common delimiters
        authors = re.split(r'[,;]|\sand\s|\bet\sal\.?', authors_raw)
        authors = [a.strip() for a in authors if a.strip()]
    else:
        return str(authors_raw)
    
    if not authors:
        return ""
    
    # Clean and format authors
    clean_authors = []
    for author in authors[:6]:  # Limit to first 6 authors
        author = author.strip()
        if author:
            # Handle "Last, First" format
            if ',' in author:
                clean_authors.append(author)
            else:
                # Try to convert "First Last" to "Last, First"
                parts = author.split()
                if len(parts) >= 2:
                    clean_authors.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
                else:
                    clean_authors.append(author)
    
    if not clean_authors:
        return ""
    
    # Format author list
    if len(clean_authors) == 1:
        return clean_authors[0]
    elif len(clean_authors) <= 3:
        return ", ".join(clean_authors[:-1]) + f", and {clean_authors[-1]}"
    else:
        return f"{clean_authors[0]}, et al."


def generate_markdown_citation_list(analyzed_papers: list) -> str:
    """Generate a markdown-formatted reference list for all papers."""
    
    if not analyzed_papers:
        return "## References\n\nNo references available.\n"
    
    references = ["## References\n"]
    
    for i, paper in enumerate(analyzed_papers, 1):
        citation_links = paper.get("citation_links", {})
        formatted_ref = citation_links.get("formatted_reference", "")
        pubmed_url = citation_links.get("pubmed_url", "")
        doi_url = citation_links.get("doi_url", "")
        
        if not formatted_ref:
            # Fallback formatting
            title = paper.get("title", "Unknown title")
            authors = paper.get("authors", "Unknown authors")
            formatted_ref = f"[{i}] {authors}. {title}."
        
        reference_line = formatted_ref
        
        # Add clickable links
        links = []
        if pubmed_url:
            links.append(f"[PubMed]({pubmed_url})")
        if doi_url:
            links.append(f"[DOI]({doi_url})")
        
        if links:
            reference_line += f" | {' | '.join(links)}"
        
        references.append(reference_line + "\n")
    
    return "\n".join(references)


def format_inline_citation(paper_data: Any, paper_id: int) -> str:
    """Generate a short inline citation for use within text."""
    
    # Handle non-dict inputs
    if not isinstance(paper_data, dict):
        return f"Reference {paper_id}"
    
    authors = paper_data.get("authors", "") if paper_data else ""
    year = paper_data.get("year", "") if paper_data else ""
    
    # Format first author for inline citation
    first_author = ""
    if isinstance(authors, list) and authors:
        first_author = authors[0].split(',')[0].split()[-1]  # Get last name
    elif isinstance(authors, str) and authors:
        first_author = authors.split(',')[0].split()[-1]
    
    if first_author and year:
        return f"{first_author} et al., {year}"
    elif first_author:
        return f"{first_author} et al."
    else:
        return f"Reference {paper_id}"


# Example usage functions for testing
def test_citation_formatting():
    """Test citation formatting with sample data."""
    
    sample_paper = {
        "title": "Revumenib in relapsed or refractory KMT2A-rearranged acute leukemia",
        "authors": ["Smith, John A", "Johnson, Mary B", "Davis, Robert C"],
        "year": 2024,
        "journal": "New England Journal of Medicine",
        "pmid": "38754448",
        "doi": "10.1056/NEJMoa2402245"
    }
    
    citation_links = generate_citation_links(sample_paper, 1)
    
    print("Citation Links Test:")
    for key, value in citation_links.items():
        print(f"  {key}: {value}")
    
    print(f"\nInline citation: {format_inline_citation(sample_paper, 1)}")
    
    return citation_links


if __name__ == "__main__":
    test_citation_formatting()