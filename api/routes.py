"""API routes for mempocket."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from mem.config import Entity, Context, ProposalStatus
from mem.models import Entry
from mem.store import (
    init_storage,
    save_entry,
    get_entry,
    list_entries,
    search_entries,
    delete_entry,
    get_pending_proposals,
    get_proposal,
    update_proposal_status,
    get_links,
    get_backlinks,
    append_to_entry,
)
from mem.agent import quick_add, get_system_status

router = APIRouter()

# Initialize storage on startup
init_storage()


# Request/Response models
class CreateEntryRequest(BaseModel):
    title: str
    entity: str  # "project", "library", "people"
    context: str  # "work", "life"
    content: Optional[str] = ""


class UpdateEntryRequest(BaseModel):
    content: str


class QuickAddRequest(BaseModel):
    content: str


class RejectRequest(BaseModel):
    reason: Optional[str] = None


# Entry endpoints
@router.get("/entries")
async def list_all_entries(
    entity: Optional[str] = None,
    context: Optional[str] = None,
):
    """List all entries with optional filters."""
    entity_filter = Entity(entity) if entity else None
    context_filter = Context(context) if context else None

    entries = list_entries(entity=entity_filter, context=context_filter)
    return {
        "entries": [
            {
                "id": e.id,
                "title": e.title,
                "entity": e.entity.value,
                "context": e.context.value,
                "content": e.content,
                "links": e.links,
                "created_at": e.created_at.isoformat(),
                "updated_at": e.updated_at.isoformat(),
            }
            for e in entries
        ]
    }


@router.get("/entries/{entry_id}")
async def get_entry_detail(entry_id: str):
    """Get a single entry by ID."""
    entry = get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {
        "id": entry.id,
        "title": entry.title,
        "entity": entry.entity.value,
        "context": entry.context.value,
        "content": entry.content,
        "links": entry.links,
        "created_at": entry.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat(),
        "history": [
            {
                "action": h.action.value,
                "timestamp": h.timestamp.isoformat(),
                "details": h.details,
            }
            for h in entry.history
        ],
    }


@router.post("/entries")
async def create_entry(request: CreateEntryRequest):
    """Create a new entry manually."""
    entry = Entry(
        title=request.title,
        entity=Entity(request.entity),
        context=Context(request.context),
        content=request.content or "",
    )
    entry_id = save_entry(entry)
    return {"id": entry_id, "message": "Entry created"}


@router.put("/entries/{entry_id}")
async def update_entry(entry_id: str, request: UpdateEntryRequest):
    """Append content to an entry."""
    entry = append_to_entry(entry_id, request.content)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"id": entry_id, "message": "Entry updated"}


@router.delete("/entries/{entry_id}")
async def remove_entry(entry_id: str):
    """Delete an entry."""
    if delete_entry(entry_id):
        return {"message": "Entry deleted"}
    raise HTTPException(status_code=404, detail="Entry not found")


# Quick Add (AI classification)
@router.post("/add")
async def add_with_ai(request: QuickAddRequest):
    """Quick add with AI classification."""
    result = quick_add(request.content)
    return result


# Proposals endpoints
@router.get("/proposals")
async def list_proposals():
    """List all pending proposals."""
    proposals = get_pending_proposals()
    return {
        "proposals": [
            {
                "id": p.proposal_id,
                "type": p.type.value,
                "status": p.status.value,
                "confidence": p.confidence,
                "reason": p.reason,
                "created_at": p.created_at.isoformat(),
                "suggested": {
                    "title": p.suggested.title,
                    "entity": p.suggested.entity.value,
                    "context": p.suggested.context.value,
                    "content": p.suggested.content,
                },
                "evidence": {
                    "source_input": p.evidence.source_input,
                    "extracted_from": p.evidence.extracted_from,
                },
            }
            for p in proposals
        ]
    }


@router.get("/proposals/{proposal_id}")
async def get_proposal_detail(proposal_id: str):
    """Get a single proposal by ID."""
    proposal = get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    return {
        "id": proposal.proposal_id,
        "type": proposal.type.value,
        "status": proposal.status.value,
        "confidence": proposal.confidence,
        "reason": proposal.reason,
        "created_at": proposal.created_at.isoformat(),
        "suggested": {
            "title": proposal.suggested.title,
            "entity": proposal.suggested.entity.value,
            "context": proposal.suggested.context.value,
            "content": proposal.suggested.content,
        },
        "evidence": {
            "source_input": proposal.evidence.source_input,
            "extracted_from": proposal.evidence.extracted_from,
        },
    }


@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(proposal_id: str):
    """Approve a proposal and create the entry."""
    proposal = get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if proposal.status != ProposalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Proposal is not pending")

    # Create entry from proposal
    entry = Entry(
        title=proposal.suggested.title,
        entity=proposal.suggested.entity,
        context=proposal.suggested.context,
        content=proposal.suggested.content or "",
        links=proposal.suggested.links or [],
    )
    entry_id = save_entry(entry)

    # Update proposal status
    update_proposal_status(proposal_id, ProposalStatus.APPROVED)

    return {"message": "Proposal approved", "entry_id": entry_id}


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: str, request: RejectRequest):
    """Reject a proposal."""
    proposal = get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if proposal.status != ProposalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Proposal is not pending")

    update_proposal_status(
        proposal_id,
        ProposalStatus.REJECTED,
        rejection_reason=request.reason
    )

    return {"message": "Proposal rejected"}


# Search endpoint
@router.get("/search")
async def search(q: str):
    """Search entries by query."""
    results = search_entries(q)
    return {
        "query": q,
        "results": [
            {
                "id": e.id,
                "title": e.title,
                "entity": e.entity.value,
                "context": e.context.value,
                "content": e.content[:200] if e.content else "",
            }
            for e in results
        ]
    }


# Links endpoints
@router.get("/entries/{entry_id}/links")
async def get_entry_links(entry_id: str):
    """Get links from an entry."""
    entry = get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    links = get_links(entry_id)
    return {"links": links}


@router.get("/entries/{entry_id}/backlinks")
async def get_entry_backlinks(entry_id: str):
    """Get backlinks to an entry."""
    entry = get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    backlinks = get_backlinks(entry_id)
    return {"backlinks": backlinks}


# Status endpoint
@router.get("/status")
async def get_status():
    """Get system status."""
    return get_system_status()
