"""Tests for mempocket store operations."""

import os
import pytest
import tempfile
from pathlib import Path

from mem.config import Entity, Context, ProposalStatus, ProposalType, InputType
from mem.models import Entry, Proposal, Input, SuggestedEntry, Evidence
from mem.store import (
    init_storage,
    save_entry,
    get_entry,
    list_entries,
    search_entries,
    delete_entry,
    save_input,
    get_input,
    save_proposal,
    get_proposal,
    get_pending_proposals,
    update_proposal_status,
    extract_links,
    rebuild_index,
    get_links,
    get_backlinks,
)


@pytest.fixture
def temp_mem_home(monkeypatch):
    """Create a temporary mempocket home directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("MEM_HOME", tmpdir)
        init_storage()
        yield Path(tmpdir)


class TestEntryOperations:
    def test_save_and_get_entry(self, temp_mem_home):
        entry = Entry(
            title="Test Entry",
            entity=Entity.PROJECT,
            context=Context.WORK,
            content="Test content",
        )
        entry_id = save_entry(entry)

        retrieved = get_entry(entry_id)
        assert retrieved is not None
        assert retrieved.title == "Test Entry"
        assert retrieved.entity == Entity.PROJECT

    def test_list_entries(self, temp_mem_home):
        # Create multiple entries
        for i in range(3):
            entry = Entry(
                title=f"Entry {i}",
                entity=Entity.PROJECT if i < 2 else Entity.LIBRARY,
                context=Context.WORK,
            )
            save_entry(entry)

        # List all
        entries = list_entries()
        assert len(entries) == 3

        # Filter by entity
        projects = list_entries(entity=Entity.PROJECT)
        assert len(projects) == 2

    def test_search_entries(self, temp_mem_home):
        entry1 = Entry(
            title="Meeting with Alice",
            entity=Entity.PROJECT,
            context=Context.WORK,
            content="Discuss Q2 goals",
        )
        entry2 = Entry(
            title="Doctor Appointment",
            entity=Entity.PEOPLE,
            context=Context.LIFE,
            content="Annual checkup",
        )
        save_entry(entry1)
        save_entry(entry2)

        # Search by title
        results = search_entries("Alice")
        assert len(results) == 1
        assert results[0].title == "Meeting with Alice"

        # Search by content
        results = search_entries("Q2")
        assert len(results) == 1

    def test_delete_entry(self, temp_mem_home):
        entry = Entry(
            title="To Delete",
            entity=Entity.LIBRARY,
            context=Context.LIFE,
        )
        entry_id = save_entry(entry)

        assert delete_entry(entry_id)
        assert get_entry(entry_id) is None


class TestInputOperations:
    def test_save_and_get_input(self, temp_mem_home):
        inp = Input(
            type=InputType.TEXT,
            content="Test input content",
        )
        input_id = save_input(inp)

        retrieved = get_input(input_id)
        assert retrieved is not None
        assert retrieved.content == "Test input content"


class TestProposalOperations:
    def test_save_and_get_proposal(self, temp_mem_home):
        suggested = SuggestedEntry(
            title="New Entry",
            entity=Entity.PROJECT,
            context=Context.WORK,
        )
        evidence = Evidence(
            source_input="input_123",
            extracted_from="Test",
        )
        proposal = Proposal(
            run_id="run_123",
            type=ProposalType.NEW_ENTRY,
            suggested=suggested,
            evidence=evidence,
            confidence=0.9,
            reason="Test",
        )
        proposal_id = save_proposal(proposal)

        retrieved = get_proposal(proposal_id)
        assert retrieved is not None
        assert retrieved.status == ProposalStatus.PENDING

    def test_get_pending_proposals(self, temp_mem_home):
        for i in range(3):
            suggested = SuggestedEntry(
                title=f"Entry {i}",
                entity=Entity.PROJECT,
                context=Context.WORK,
            )
            evidence = Evidence(source_input=f"input_{i}", extracted_from="Test")
            proposal = Proposal(
                run_id=f"run_{i}",
                type=ProposalType.NEW_ENTRY,
                suggested=suggested,
                evidence=evidence,
                confidence=0.9,
                reason="Test",
            )
            save_proposal(proposal)

        pending = get_pending_proposals()
        assert len(pending) == 3

    def test_update_proposal_status(self, temp_mem_home):
        suggested = SuggestedEntry(
            title="Test",
            entity=Entity.PROJECT,
            context=Context.WORK,
        )
        evidence = Evidence(source_input="input_1", extracted_from="Test")
        proposal = Proposal(
            run_id="run_1",
            type=ProposalType.NEW_ENTRY,
            suggested=suggested,
            evidence=evidence,
            confidence=0.9,
            reason="Test",
        )
        proposal_id = save_proposal(proposal)

        updated = update_proposal_status(proposal_id, ProposalStatus.APPROVED)
        assert updated.status == ProposalStatus.APPROVED


class TestLinkExtraction:
    def test_extract_links(self):
        content = "Meeting with [[Alice]] and [[Bob]] about [[Project Q2]]"
        links = extract_links(content)
        assert links == ["Alice", "Bob", "Project Q2"]

    def test_extract_no_links(self):
        content = "Plain text without any links"
        links = extract_links(content)
        assert links == []


class TestIndex:
    def test_rebuild_index(self, temp_mem_home):
        # Create entries with links
        alice = Entry(
            title="Alice",
            entity=Entity.PEOPLE,
            context=Context.WORK,
        )
        alice_id = save_entry(alice)

        project = Entry(
            title="Project Q2",
            entity=Entity.PROJECT,
            context=Context.WORK,
            content="Working with [[Alice]]",
            links=["Alice"],
        )
        project_id = save_entry(project)

        # Rebuild index
        index = rebuild_index()

        # Check links
        assert project_id in index.links

    def test_backlinks(self, temp_mem_home):
        alice = Entry(
            title="Alice",
            entity=Entity.PEOPLE,
            context=Context.WORK,
        )
        alice_id = save_entry(alice)

        project = Entry(
            title="Meeting",
            entity=Entity.PROJECT,
            context=Context.WORK,
            content="With [[Alice]]",
            links=["Alice"],
        )
        save_entry(project)

        rebuild_index()

        # Get backlinks to Alice
        backlinks = get_backlinks(alice_id)
        assert len(backlinks) == 1
