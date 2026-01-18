"""Claude SDK tool definitions for PCMS agent."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import (
    Entity,
    Context,
    ProposalStatus,
    InputType,
    HistoryAction,
)
from .models import (
    Input,
    Entry,
    HistoryEntry,
    Source,
)
from .store import (
    save_input,
    save_entry,
    get_entry,
    list_entries,
    search_entries,
    get_pending_proposals,
    get_proposal,
    update_proposal_status,
    get_run,
    get_links,
    get_backlinks,
    rebuild_index,
    extract_links,
)
from .pipeline import run_pipeline


# ============ Input Tools ============

def add_input(content: str, input_type: str = "text") -> str:
    """
    Add raw input for processing.

    Args:
        content: The text content to add
        input_type: Type of input (text, manual)

    Returns:
        The input ID
    """
    inp = Input(
        type=InputType(input_type),
        content=content,
    )
    return save_input(inp)


def add_file(path: str) -> str:
    """
    Add a file as input.

    Args:
        path: Path to the file

    Returns:
        The input ID
    """
    file_path = Path(path)
    content = ""
    if file_path.exists():
        if file_path.suffix in [".txt", ".md"]:
            content = file_path.read_text(encoding="utf-8")
        else:
            content = f"[File: {file_path.name}]"

    inp = Input(
        type=InputType.FILE,
        content=content,
        file_path=str(file_path.absolute()),
    )
    return save_input(inp)


# ============ Pipeline Tools ============

def process_input(input_id: str) -> dict:
    """
    Run the pipeline on an input.

    Args:
        input_id: The input ID to process

    Returns:
        Run report summary
    """
    run = run_pipeline(input_id)
    return {
        "run_id": run.run_id,
        "steps": [{"stage": s.stage, "result": s.result} for s in run.steps],
        "proposals": run.proposals,
        "flags": run.flags,
    }


def get_run_report(run_id: str) -> Optional[dict]:
    """
    Get a pipeline run report.

    Args:
        run_id: The run ID

    Returns:
        Run report details or None
    """
    run = get_run(run_id)
    if run:
        return run.model_dump()
    return None


# ============ Proposal Tools ============

def get_pending() -> list[dict]:
    """
    Get all pending proposals.

    Returns:
        List of pending proposals
    """
    proposals = get_pending_proposals()
    return [p.model_dump() for p in proposals]


def approve(proposal_id: str) -> Optional[str]:
    """
    Approve a proposal and create the entry.

    Args:
        proposal_id: The proposal ID to approve

    Returns:
        The created entry ID or None
    """
    proposal = get_proposal(proposal_id)
    if not proposal:
        return None

    if proposal.status != ProposalStatus.PENDING:
        return None

    # Create entry from proposal
    entry = Entry(
        title=proposal.suggested.title,
        entity=proposal.suggested.entity,
        context=proposal.suggested.context,
        content=proposal.suggested.content,
        links=proposal.suggested.links,
        source=Source(type=InputType.TEXT, ref=proposal.evidence.source_input),
        history=[
            HistoryEntry(
                action=HistoryAction.CREATED,
                by=f"agent:pipeline",
                diff=f"Approved from proposal {proposal_id}",
            )
        ],
    )
    entry_id = save_entry(entry)

    # Update proposal status
    update_proposal_status(proposal_id, ProposalStatus.APPROVED)

    # Rebuild index
    rebuild_index()

    return entry_id


def reject(proposal_id: str, reason: str = "") -> bool:
    """
    Reject a proposal.

    Args:
        proposal_id: The proposal ID to reject
        reason: Reason for rejection

    Returns:
        True if rejected successfully
    """
    proposal = update_proposal_status(proposal_id, ProposalStatus.REJECTED)
    return proposal is not None


# ============ Entry Tools ============

def get_entry_details(entry_id: str) -> Optional[dict]:
    """
    Get entry details.

    Args:
        entry_id: The entry ID

    Returns:
        Entry details or None
    """
    entry = get_entry(entry_id)
    if entry:
        return entry.model_dump()
    return None


def search(
    query: str,
    entity: Optional[str] = None,
    context: Optional[str] = None,
) -> list[dict]:
    """
    Search entries.

    Args:
        query: Search query
        entity: Filter by entity (project/library/people)
        context: Filter by context (work/life)

    Returns:
        List of matching entries
    """
    entity_enum = Entity(entity) if entity else None
    context_enum = Context(context) if context else None
    entries = search_entries(query, entity_enum, context_enum)
    return [e.model_dump() for e in entries]


def list_all(
    entity: Optional[str] = None,
    context: Optional[str] = None,
) -> list[dict]:
    """
    List entries.

    Args:
        entity: Filter by entity (project/library/people)
        context: Filter by context (work/life)

    Returns:
        List of entries
    """
    entity_enum = Entity(entity) if entity else None
    context_enum = Context(context) if context else None
    entries = list_entries(entity_enum, context_enum)
    return [
        {
            "id": e.id,
            "title": e.title,
            "entity": e.entity.value,
            "context": e.context.value,
            "links": e.links,
            "updated_at": str(e.updated_at),
        }
        for e in entries
    ]


# ============ Manual Entry Tools ============

def create_entry(
    title: str,
    entity: str,
    context: str,
    content: str = "",
) -> str:
    """
    Manually create an entry.

    Args:
        title: Entry title
        entity: Entity type (project/library/people)
        context: Context (work/life)
        content: Entry content

    Returns:
        The created entry ID
    """
    links = extract_links(content)
    entry = Entry(
        title=title,
        entity=Entity(entity),
        context=Context(context),
        content=content,
        links=links,
    )
    entry_id = save_entry(entry)
    rebuild_index()
    return entry_id


def update_entry(entry_id: str, content: str) -> Optional[str]:
    """
    Update an entry's content (replace).

    Args:
        entry_id: The entry ID
        content: New content

    Returns:
        The entry ID or None
    """
    entry = get_entry(entry_id)
    if not entry:
        return None

    entry.content = content
    entry.links = extract_links(content)
    entry.updated_at = datetime.utcnow()
    entry.history.append(
        HistoryEntry(action=HistoryAction.UPDATED, by="user")
    )
    save_entry(entry)
    rebuild_index()
    return entry_id


def append_entry(entry_id: str, content: str) -> Optional[str]:
    """
    Append content to an entry.

    Args:
        entry_id: The entry ID
        content: Content to append

    Returns:
        The entry ID or None
    """
    entry = get_entry(entry_id)
    if not entry:
        return None

    entry.content = f"{entry.content}\n\n{content}".strip()
    entry.links = extract_links(entry.content)
    entry.updated_at = datetime.utcnow()
    entry.history.append(
        HistoryEntry(action=HistoryAction.APPENDED, by="user")
    )
    save_entry(entry)
    rebuild_index()
    return entry_id


# ============ Link Tools ============

def get_entry_links(entry_id: str) -> list[dict]:
    """
    Get entries that this entry links to.

    Args:
        entry_id: The entry ID

    Returns:
        List of linked entries
    """
    entries = get_links(entry_id)
    return [{"id": e.id, "title": e.title} for e in entries]


def get_entry_backlinks(entry_id: str) -> list[dict]:
    """
    Get entries that link to this entry.

    Args:
        entry_id: The entry ID

    Returns:
        List of entries linking to this one
    """
    entries = get_backlinks(entry_id)
    return [{"id": e.id, "title": e.title} for e in entries]
