from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    id: str = Field(description="Unique source identifier, e.g., 'S1', 'S2'")
    title: str = Field(default="", description="Title of the source webpage/document")
    url: str = Field(default="", description="Canonical URL of the source")
    snippet: str = Field(default="", description="Cleaned content excerpt used as evidence")
    domain: str = Field(default="", description="Source domain name")
    published_date: Optional[str] = Field(default=None, description="Publication date if available")


class ClaimItem(BaseModel):
    claim: str = Field(description="Extracted factual or analytic statement")
    source_id: str = Field(description="Referenced source tag, e.g., 'S1'")
    evidence_quote: str = Field(description="Direct quotation from the source text supporting the claim")
    category: str = Field(default="fact", description="'fact', 'opinion', or 'disputed'")
    confidence: str = Field(default="high", description="'high', 'medium', or 'low'")


class EvidenceAnalysis(BaseModel):
    claims: List[ClaimItem] = Field(default_factory=list, description="Verified claims extracted from sources")
    contradictions: List[str] = Field(default_factory=list, description="Points of conflict between sources")
    gaps: List[str] = Field(default_factory=list, description="Unanswered questions or missing evidence")
    needs_more_research: bool = Field(default=False, description="Flag indicating if another search round is required")
    new_search_queries: List[str] = Field(default_factory=list, description="Targeted queries for missing information")


class ValidationResult(BaseModel):
    total_citations_found: int = Field(default=0)
    valid_citations: List[str] = Field(default_factory=list)
    invalid_citations: List[str] = Field(default_factory=list)
    passed: bool = Field(default=True)
    notes: str = Field(default="")


class LogEntry(BaseModel):
    agent: str
    message: str
    timestamp: str


class ResearchState(TypedDict):
    """
    Central shared state flowing across all agents in the LangGraph workflow.
    """
    topic: str
    sub_questions: List[str]
    search_queries: List[str]
    sources: Dict[str, Dict[str, Any]]
    analysis: Dict[str, Any]
    loop_count: int
    max_loops: int
    report_markdown: str
    validation: Dict[str, Any]
    status_logs: List[Dict[str, Any]]
