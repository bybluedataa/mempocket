"""Pydantic models for PCMS data structures."""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field
from slugify import slugify

from .config import (
    Entity,
    Context,
    ProposalType,
    ProposalStatus,
    InputType,
    HistoryAction,
)


def generate_id(prefix: str = "") -> str:
    """Generate a short UUID."""
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def generate_entry_id(title: str) -> str:
    """Generate entry ID from title + short UUID."""
    slug = slugify(title, max_length=30)
    short_uuid = uuid.uuid4().hex[:8]
    return f"{slug}-{short_uuid}" if slug else short_uuid


class Source(BaseModel):
    """Source information for an entry."""
    type: InputType = InputType.MANUAL
    ref: Optional[str] = None  # Path or reference
    hash: Optional[str] = None  # SHA256 if file


class HistoryEntry(BaseModel):
    """A single history entry tracking changes."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: HistoryAction
    by: str = "user"  # "user" or "agent:<name>"
    diff: Optional[str] = None


class Entry(BaseModel):
    """A memory entry - the core data unit."""
    id: str = Field(default_factory=lambda: generate_id("entry_"))
    title: str
    entity: Entity
    context: Context
    content: str = ""
    links: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: Source = Field(default_factory=Source)
    history: list[HistoryEntry] = Field(default_factory=list)

    def model_post_init(self, __context) -> None:
        """Generate ID from title if using default."""
        if self.id.startswith("entry_"):
            self.id = generate_entry_id(self.title)
        if not self.history:
            self.history = [
                HistoryEntry(action=HistoryAction.CREATED, by="user")
            ]


class SuggestedEntry(BaseModel):
    """Suggested entry data in a proposal."""
    title: str
    entity: Entity
    context: Context
    content: str = ""
    links: list[str] = Field(default_factory=list)


class Evidence(BaseModel):
    """Evidence supporting a proposal."""
    source_input: str  # input_id
    extracted_from: str  # Description
    span: Optional[str] = None  # e.g., "line 3-5"


class Proposal(BaseModel):
    """Agent proposal awaiting human approval."""
    proposal_id: str = Field(default_factory=lambda: generate_id("prop_"))
    run_id: str
    type: ProposalType
    suggested: SuggestedEntry
    evidence: Evidence
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Input(BaseModel):
    """Raw input before processing."""
    id: str = Field(default_factory=lambda: generate_id("input_"))
    type: InputType
    content: str
    file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PipelineStep(BaseModel):
    """A single step in the pipeline run."""
    stage: str  # "extract", "classify", "link_detect", "propose"
    result: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RunReport(BaseModel):
    """Report of a pipeline run for transparency."""
    run_id: str = Field(default_factory=lambda: generate_id("run_"))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    trigger: str = "new_input"  # "new_input" or "manual"
    input_summary: str = ""  # First 200 chars of input
    input_id: str = ""
    steps: list[PipelineStep] = Field(default_factory=list)
    proposals: list[str] = Field(default_factory=list)  # proposal_ids
    flags: list[str] = Field(default_factory=list)


class Index(BaseModel):
    """Derived index for links and tags (rebuildable)."""
    links: dict[str, list[str]] = Field(default_factory=dict)  # entry_id -> linked entry_ids
    backlinks: dict[str, list[str]] = Field(default_factory=dict)  # entry_id -> entries linking to it
    tags: dict[str, list[str]] = Field(default_factory=dict)  # tag -> entry_ids
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ClassificationResult(BaseModel):
    """Result from Claude classification."""
    entity: Entity
    context: Context
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    suggested_title: Optional[str] = None
