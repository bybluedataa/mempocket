"""CLI interface for PCMS."""

import json
import os
import subprocess
import tempfile
from typing import Optional

import click

from .config import Entity, Context, ProposalStatus, get_pcms_home
from .store import (
    init_storage,
    get_entry,
    list_entries,
    search_entries,
    save_entry,
    get_proposal,
    get_pending_proposals,
    update_proposal_status,
    get_run,
    get_links,
    get_backlinks,
    rebuild_index,
    extract_links,
    find_entry_by_title,
)
from .models import Entry, HistoryEntry, Source
from .config import HistoryAction, InputType
from .agent import quick_add, add_file_input, get_system_status
from .tools import approve as approve_proposal


@click.group()
@click.version_option(version="0.1.0", prog_name="pcms")
def cli():
    """PCMS - Personal Context Memory System

    A lightweight personal context system: 3 boxes for everything, 2 modes for life.
    """
    init_storage()


# ============ Quick Add Commands ============

@cli.command()
@click.argument("content", required=False)
@click.option("--file", "-f", "file_path", help="Add from file")
def add(content: Optional[str], file_path: Optional[str]):
    """Quick add - agent classifies automatically.

    Examples:
        pcms add "Meeting with Alice about Q2 launch"
        pcms add --file ./notes.md
    """
    if file_path:
        result = add_file_input(file_path)
    elif content:
        result = quick_add(content)
    else:
        click.echo("Error: Provide content or --file", err=True)
        return

    if result.get("error"):
        click.echo(f"Error: {result['error']}", err=True)
        return

    click.echo(f"Pipeline {result['run_id']}:")
    for step in result.get("steps", []):
        click.echo(f"  ✓ {step['stage']}: {step['result']}")

    if result.get("proposals"):
        click.echo(f"  → Created proposal {result['proposals'][0]}")
        click.echo("\nRun 'pcms pending' to review")


# ============ Manual Add Commands ============

@cli.command()
@click.argument("title")
@click.option("--project", "entity", flag_value="project", help="Mark as project")
@click.option("--library", "entity", flag_value="library", help="Mark as library")
@click.option("--people", "entity", flag_value="people", help="Mark as people")
@click.option("--work", "context", flag_value="work", help="Work context")
@click.option("--life", "context", flag_value="life", help="Life context")
@click.option("--content", "-c", default="", help="Entry content")
def new(title: str, entity: Optional[str], context: Optional[str], content: str):
    """Manually create an entry with explicit classification.

    Examples:
        pcms new "Launch App Q2" --project --work
        pcms new "Dr. Chen" --people --life
        pcms new "ReactJS Notes" --library --work -c "Notes about React..."
    """
    if not entity:
        click.echo("Error: Specify --project, --library, or --people", err=True)
        return
    if not context:
        click.echo("Error: Specify --work or --life", err=True)
        return

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

    click.echo(f"✓ Created entry: {entry_id}")
    click.echo(f"  #{entity} @{context}")
    if links:
        click.echo(f"  Links: {', '.join(links)}")


# ============ Proposal Commands ============

@cli.command()
def pending():
    """List all pending proposals."""
    proposals = get_pending_proposals()

    if not proposals:
        click.echo("No pending proposals")
        return

    for p in proposals:
        entity = p.suggested.entity.value
        context = p.suggested.context.value
        title = p.suggested.title[:50]
        links = ", ".join(p.suggested.links[:3])
        if len(p.suggested.links) > 3:
            links += "..."

        click.echo(f"[{p.proposal_id}] NEW #{entity} @{context}")
        click.echo(f"  \"{title}\"")
        if links:
            click.echo(f"  Links: {links}")
        click.echo(f"  Confidence: {p.confidence:.2f}")
        click.echo()


@cli.command()
@click.argument("proposal_id")
def show(proposal_id: str):
    """Show proposal details."""
    proposal = get_proposal(proposal_id)

    if not proposal:
        click.echo(f"Proposal not found: {proposal_id}", err=True)
        return

    click.echo(f"Proposal: {proposal.proposal_id}")
    click.echo(f"Status: {proposal.status.value}")
    click.echo(f"Type: {proposal.type.value}")
    click.echo(f"Run: {proposal.run_id}")
    click.echo()
    click.echo("Suggested Entry:")
    click.echo(f"  Title: {proposal.suggested.title}")
    click.echo(f"  Entity: #{proposal.suggested.entity.value}")
    click.echo(f"  Context: @{proposal.suggested.context.value}")
    click.echo(f"  Links: {', '.join(proposal.suggested.links) or 'none'}")
    click.echo()
    click.echo("Content:")
    click.echo(proposal.suggested.content[:500])
    if len(proposal.suggested.content) > 500:
        click.echo("...")
    click.echo()
    click.echo("Evidence:")
    click.echo(f"  Source: {proposal.evidence.source_input}")
    click.echo(f"  From: {proposal.evidence.extracted_from}")
    click.echo()
    click.echo(f"Confidence: {proposal.confidence:.2f}")
    click.echo(f"Reason: {proposal.reason}")


@cli.command()
@click.argument("proposal_id")
def approve(proposal_id: str):
    """Approve a proposal and create the entry."""
    entry_id = approve_proposal(proposal_id)

    if entry_id:
        click.echo(f"✓ Created entry: {entry_id}")
    else:
        click.echo(f"Failed to approve: {proposal_id}", err=True)


@cli.command()
@click.argument("proposal_id")
@click.argument("reason", default="")
def reject(proposal_id: str, reason: str):
    """Reject a proposal."""
    proposal = update_proposal_status(proposal_id, ProposalStatus.REJECTED)

    if proposal:
        click.echo(f"✓ Rejected: {proposal_id}")
    else:
        click.echo(f"Proposal not found: {proposal_id}", err=True)


@cli.command()
@click.argument("run_id")
def run(run_id: str):
    """Show pipeline run details."""
    report = get_run(run_id)

    if not report:
        click.echo(f"Run not found: {run_id}", err=True)
        return

    click.echo(f"Run: {report.run_id}")
    click.echo(f"Trigger: {report.trigger}")
    click.echo(f"Input: {report.input_id}")
    click.echo(f"Started: {report.started_at}")
    click.echo(f"Ended: {report.ended_at}")
    click.echo()
    click.echo("Steps:")
    for step in report.steps:
        click.echo(f"  ✓ {step.stage}: {step.result}")
    click.echo()
    if report.proposals:
        click.echo(f"Proposals: {', '.join(report.proposals)}")
    if report.flags:
        click.echo(f"Flags: {', '.join(report.flags)}")


# ============ Query Commands ============

@cli.command()
@click.argument("query")
@click.option("--project", "entity", flag_value="project", help="Filter by project")
@click.option("--library", "entity", flag_value="library", help="Filter by library")
@click.option("--people", "entity", flag_value="people", help="Filter by people")
@click.option("--work", "context", flag_value="work", help="Filter by work")
@click.option("--life", "context", flag_value="life", help="Filter by life")
def search(query: str, entity: Optional[str], context: Optional[str]):
    """Search entries by query string.

    Examples:
        pcms search "Alice"
        pcms search "Q2 deadline" --project --work
    """
    entity_enum = Entity(entity) if entity else None
    context_enum = Context(context) if context else None

    results = search_entries(query, entity_enum, context_enum)

    if not results:
        click.echo("No results found")
        return

    for entry in results:
        _print_entry_summary(entry)


@cli.command("list")
@click.option("--project", "entity", flag_value="project", help="Filter by project")
@click.option("--library", "entity", flag_value="library", help="Filter by library")
@click.option("--people", "entity", flag_value="people", help="Filter by people")
@click.option("--work", "context", flag_value="work", help="Filter by work")
@click.option("--life", "context", flag_value="life", help="Filter by life")
def list_cmd(entity: Optional[str], context: Optional[str]):
    """List entries with optional filters.

    Examples:
        pcms list
        pcms list --project --work
        pcms list --people
    """
    entity_enum = Entity(entity) if entity else None
    context_enum = Context(context) if context else None

    entries = list_entries(entity_enum, context_enum)

    if not entries:
        click.echo("No entries found")
        return

    for entry in entries:
        _print_entry_summary(entry)


@cli.command()
@click.argument("entry_id")
def get(entry_id: str):
    """Get entry details.

    The entry_id can be the full ID or a partial title match.
    """
    entry = get_entry(entry_id)
    if not entry:
        entry = find_entry_by_title(entry_id)

    if not entry:
        click.echo(f"Entry not found: {entry_id}", err=True)
        return

    click.echo(f"ID: {entry.id}")
    click.echo(f"Title: {entry.title}")
    click.echo(f"Entity: #{entry.entity.value}")
    click.echo(f"Context: @{entry.context.value}")
    click.echo(f"Created: {entry.created_at}")
    click.echo(f"Updated: {entry.updated_at}")
    if entry.links:
        click.echo(f"Links: {', '.join(entry.links)}")
    click.echo()
    click.echo("Content:")
    click.echo(entry.content or "(empty)")


# ============ Update Commands ============

@cli.command()
@click.argument("entry_id")
@click.argument("content")
def append(entry_id: str, content: str):
    """Append content to an entry.

    Example:
        pcms append abc123 "New update: deadline moved to 15/07"
    """
    entry = get_entry(entry_id)
    if not entry:
        entry = find_entry_by_title(entry_id)

    if not entry:
        click.echo(f"Entry not found: {entry_id}", err=True)
        return

    from datetime import datetime

    entry.content = f"{entry.content}\n\n{content}".strip()
    entry.links = extract_links(entry.content)
    entry.updated_at = datetime.utcnow()
    entry.history.append(
        HistoryEntry(action=HistoryAction.APPENDED, by="user")
    )
    save_entry(entry)
    rebuild_index()

    click.echo(f"✓ Updated: {entry.id}")


@cli.command()
@click.argument("entry_id")
def edit(entry_id: str):
    """Edit an entry in $EDITOR."""
    entry = get_entry(entry_id)
    if not entry:
        entry = find_entry_by_title(entry_id)

    if not entry:
        click.echo(f"Entry not found: {entry_id}", err=True)
        return

    editor = os.environ.get("EDITOR", "vim")

    # Create temp file with content
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(f"# {entry.title}\n\n")
        f.write(entry.content)
        temp_path = f.name

    try:
        subprocess.run([editor, temp_path], check=True)

        # Read back
        with open(temp_path, "r") as f:
            new_content = f.read()

        # Parse - skip title line if present
        lines = new_content.split("\n")
        if lines and lines[0].startswith("# "):
            new_content = "\n".join(lines[1:]).strip()

        from datetime import datetime

        entry.content = new_content
        entry.links = extract_links(entry.content)
        entry.updated_at = datetime.utcnow()
        entry.history.append(
            HistoryEntry(action=HistoryAction.UPDATED, by="user")
        )
        save_entry(entry)
        rebuild_index()

        click.echo(f"✓ Updated: {entry.id}")

    finally:
        os.unlink(temp_path)


# ============ Link Commands ============

@cli.command()
@click.argument("entry_id")
def links(entry_id: str):
    """Show what this entry links to."""
    entry = get_entry(entry_id)
    if not entry:
        entry = find_entry_by_title(entry_id)

    if not entry:
        click.echo(f"Entry not found: {entry_id}", err=True)
        return

    linked = get_links(entry.id)

    click.echo(f"Links from: {entry.title}")
    click.echo(f"Raw links in content: {', '.join(entry.links) or 'none'}")
    click.echo()

    if linked:
        click.echo("Resolved to entries:")
        for e in linked:
            click.echo(f"  [{e.id}] {e.title}")
    else:
        click.echo("No resolved entry links")


@cli.command()
@click.argument("entry_id")
def backlinks(entry_id: str):
    """Show what links TO this entry."""
    entry = get_entry(entry_id)
    if not entry:
        entry = find_entry_by_title(entry_id)

    if not entry:
        click.echo(f"Entry not found: {entry_id}", err=True)
        return

    linking = get_backlinks(entry.id)

    click.echo(f"Backlinks to: {entry.title}")
    click.echo()

    if linking:
        for e in linking:
            click.echo(f"  [{e.id}] {e.title}")
    else:
        click.echo("No entries link to this")


# ============ Utility Commands ============

@cli.command()
def status():
    """Show system status."""
    stats = get_system_status()

    click.echo("PCMS Status")
    click.echo(f"  Home: {get_pcms_home()}")
    click.echo()
    click.echo(f"Total entries: {stats['total_entries']}")
    click.echo()
    click.echo("By entity:")
    for entity, count in stats['by_entity'].items():
        click.echo(f"  #{entity}: {count}")
    click.echo()
    click.echo("By context:")
    for context, count in stats['by_context'].items():
        click.echo(f"  @{context}: {count}")
    click.echo()
    click.echo(f"Pending proposals: {stats['pending_proposals']}")
    click.echo(f"Inbox items: {stats['inbox_items']}")


@cli.command()
def reindex():
    """Rebuild the index."""
    index = rebuild_index()
    click.echo(f"✓ Index rebuilt")
    click.echo(f"  Links: {len(index.links)} entries with outgoing links")
    click.echo(f"  Backlinks: {len(index.backlinks)} entries with incoming links")


def _print_entry_summary(entry: Entry):
    """Print a one-line entry summary."""
    entity = entry.entity.value
    context = entry.context.value
    title = entry.title[:40]
    if len(entry.title) > 40:
        title += "..."

    click.echo(f"[{entry.id}] #{entity} @{context}")
    click.echo(f"  {title}")
    if entry.links:
        links = ", ".join(entry.links[:3])
        if len(entry.links) > 3:
            links += "..."
        click.echo(f"  Links: {links}")
    click.echo()


if __name__ == "__main__":
    cli()
