"""JSON file storage operations for mempocket."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from slugify import slugify

from .config import (
    get_mem_home,
    get_entries_dir,
    get_inbox_dir,
    get_proposals_dir,
    get_runs_dir,
    get_index_path,
    Entity,
    Context,
    ProposalStatus,
    LINK_PATTERN,
)
from .models import (
    Entry,
    Proposal,
    RunReport,
    Input,
    Index,
)


def init_storage() -> None:
    """Initialize mempocket storage directories."""
    dirs = [
        get_mem_home(),
        get_entries_dir(),
        get_inbox_dir(),
        get_proposals_dir(),
        get_runs_dir(),
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Initialize index if not exists
    index_path = get_index_path()
    if not index_path.exists():
        save_index(Index())


def _save_json(path: Path, data: dict) -> None:
    """Save data as JSON to file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)


def _load_json(path: Path) -> Optional[dict]:
    """Load JSON from file."""
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============ Entries ============

def save_entry(entry: Entry) -> str:
    """Save an entry to storage."""
    init_storage()
    path = get_entries_dir() / f"{entry.id}.json"
    _save_json(path, entry.model_dump())
    return entry.id


def get_entry(entry_id: str) -> Optional[Entry]:
    """Get an entry by ID."""
    path = get_entries_dir() / f"{entry_id}.json"
    data = _load_json(path)
    if data:
        return Entry.model_validate(data)
    return None


def list_entries(
    entity: Optional[Entity] = None,
    context: Optional[Context] = None,
) -> list[Entry]:
    """List entries, optionally filtered by entity/context."""
    init_storage()
    entries = []
    for path in get_entries_dir().glob("*.json"):
        data = _load_json(path)
        if data:
            entry = Entry.model_validate(data)
            if entity and entry.entity != entity:
                continue
            if context and entry.context != context:
                continue
            entries.append(entry)
    return sorted(entries, key=lambda e: e.updated_at, reverse=True)


def search_entries(
    query: str,
    entity: Optional[Entity] = None,
    context: Optional[Context] = None,
) -> list[Entry]:
    """Search entries by query string."""
    query_lower = query.lower()
    results = []
    for entry in list_entries(entity, context):
        if (
            query_lower in entry.title.lower()
            or query_lower in entry.content.lower()
            or any(query_lower in link.lower() for link in entry.links)
        ):
            results.append(entry)
    return results


def delete_entry(entry_id: str) -> bool:
    """Delete an entry (for admin/testing purposes)."""
    path = get_entries_dir() / f"{entry_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False


# ============ Inputs (Inbox) ============

def save_input(inp: Input) -> str:
    """Save an input to the inbox."""
    init_storage()
    path = get_inbox_dir() / f"{inp.id}.json"
    _save_json(path, inp.model_dump())
    return inp.id


def get_input(input_id: str) -> Optional[Input]:
    """Get an input by ID."""
    path = get_inbox_dir() / f"{input_id}.json"
    data = _load_json(path)
    if data:
        return Input.model_validate(data)
    return None


def list_inputs() -> list[Input]:
    """List all inputs in the inbox."""
    init_storage()
    inputs = []
    for path in get_inbox_dir().glob("*.json"):
        data = _load_json(path)
        if data:
            inputs.append(Input.model_validate(data))
    return sorted(inputs, key=lambda i: i.created_at, reverse=True)


# ============ Proposals ============

def save_proposal(proposal: Proposal) -> str:
    """Save a proposal."""
    init_storage()
    path = get_proposals_dir() / f"{proposal.proposal_id}.json"
    _save_json(path, proposal.model_dump())
    return proposal.proposal_id


def get_proposal(proposal_id: str) -> Optional[Proposal]:
    """Get a proposal by ID."""
    path = get_proposals_dir() / f"{proposal_id}.json"
    data = _load_json(path)
    if data:
        return Proposal.model_validate(data)
    return None


def get_pending_proposals() -> list[Proposal]:
    """Get all pending proposals."""
    init_storage()
    proposals = []
    for path in get_proposals_dir().glob("*.json"):
        data = _load_json(path)
        if data and data.get("status") == ProposalStatus.PENDING.value:
            proposals.append(Proposal.model_validate(data))
    return sorted(proposals, key=lambda p: p.created_at, reverse=True)


def update_proposal_status(
    proposal_id: str,
    status: ProposalStatus,
) -> Optional[Proposal]:
    """Update a proposal's status."""
    proposal = get_proposal(proposal_id)
    if proposal:
        proposal.status = status
        save_proposal(proposal)
        return proposal
    return None


# ============ Run Reports ============

def save_run(run: RunReport) -> str:
    """Save a run report."""
    init_storage()
    path = get_runs_dir() / f"{run.run_id}.json"
    _save_json(path, run.model_dump())
    return run.run_id


def get_run(run_id: str) -> Optional[RunReport]:
    """Get a run report by ID."""
    path = get_runs_dir() / f"{run_id}.json"
    data = _load_json(path)
    if data:
        return RunReport.model_validate(data)
    return None


# ============ Index ============

def save_index(index: Index) -> None:
    """Save the index."""
    # Don't call init_storage here to avoid recursion
    _save_json(get_index_path(), index.model_dump())


def get_index() -> Index:
    """Get the current index."""
    data = _load_json(get_index_path())
    if data:
        return Index.model_validate(data)
    return Index()


def rebuild_index() -> Index:
    """Rebuild the entire index from entries."""
    index = Index()
    entries = list_entries()

    # Build a map of slugified titles to entry IDs for link resolution
    title_to_id: dict[str, str] = {}
    for entry in entries:
        slug = slugify(entry.title)
        title_to_id[slug] = entry.id
        title_to_id[entry.title.lower()] = entry.id

    for entry in entries:
        # Forward links
        linked_ids = []
        for link in entry.links:
            # Try to resolve link to entry ID
            link_slug = slugify(link)
            if link_slug in title_to_id:
                linked_ids.append(title_to_id[link_slug])
            elif link.lower() in title_to_id:
                linked_ids.append(title_to_id[link.lower()])

        if linked_ids:
            index.links[entry.id] = linked_ids

        # Backlinks
        for linked_id in linked_ids:
            if linked_id not in index.backlinks:
                index.backlinks[linked_id] = []
            if entry.id not in index.backlinks[linked_id]:
                index.backlinks[linked_id].append(entry.id)

        # Tags (entity and context)
        for tag in [entry.entity.value, entry.context.value]:
            if tag not in index.tags:
                index.tags[tag] = []
            index.tags[tag].append(entry.id)

    index.updated_at = datetime.utcnow()
    save_index(index)
    return index


def get_links(entry_id: str) -> list[Entry]:
    """Get entries that this entry links to."""
    index = get_index()
    linked_ids = index.links.get(entry_id, [])
    return [e for e in [get_entry(eid) for eid in linked_ids] if e]


def get_backlinks(entry_id: str) -> list[Entry]:
    """Get entries that link to this entry."""
    index = get_index()
    backlink_ids = index.backlinks.get(entry_id, [])
    return [e for e in [get_entry(eid) for eid in backlink_ids] if e]


# ============ Utilities ============

def extract_links(content: str) -> list[str]:
    """Extract [[wiki links]] from content."""
    return re.findall(LINK_PATTERN, content)


def find_entry_by_title(title: str) -> Optional[Entry]:
    """Find an entry by exact or partial title match."""
    title_lower = title.lower()
    slug = slugify(title)

    for entry in list_entries():
        if (
            entry.title.lower() == title_lower
            or slugify(entry.title) == slug
            or entry.id == title
        ):
            return entry
    return None
