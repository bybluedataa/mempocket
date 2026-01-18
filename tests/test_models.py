"""Tests for PCMS models."""

import pytest
from datetime import datetime

from pcms.models import (
    Entry,
    Proposal,
    RunReport,
    Input,
    Source,
    HistoryEntry,
    SuggestedEntry,
    Evidence,
    PipelineStep,
    generate_entry_id,
)
from pcms.config import (
    Entity,
    Context,
    ProposalType,
    ProposalStatus,
    InputType,
    HistoryAction,
)


class TestEntry:
    def test_entry_creation(self):
        entry = Entry(
            title="Test Project",
            entity=Entity.PROJECT,
            context=Context.WORK,
            content="Test content with [[Alice]] link",
        )
        assert entry.title == "Test Project"
        assert entry.entity == Entity.PROJECT
        assert entry.context == Context.WORK
        assert "test-project" in entry.id
        assert len(entry.history) == 1
        assert entry.history[0].action == HistoryAction.CREATED

    def test_entry_id_generation(self):
        id1 = generate_entry_id("My Test Project")
        id2 = generate_entry_id("My Test Project")
        assert "my-test-project" in id1
        assert id1 != id2  # UUIDs should differ

    def test_entry_with_links(self):
        entry = Entry(
            title="Test",
            entity=Entity.PROJECT,
            context=Context.WORK,
            links=["alice", "bob"],
        )
        assert entry.links == ["alice", "bob"]


class TestProposal:
    def test_proposal_creation(self):
        suggested = SuggestedEntry(
            title="New Entry",
            entity=Entity.LIBRARY,
            context=Context.LIFE,
            content="Content",
        )
        evidence = Evidence(
            source_input="input_123",
            extracted_from="Test input",
        )
        proposal = Proposal(
            run_id="run_123",
            type=ProposalType.NEW_ENTRY,
            suggested=suggested,
            evidence=evidence,
            confidence=0.9,
            reason="Test reason",
        )
        assert proposal.status == ProposalStatus.PENDING
        assert proposal.confidence == 0.9
        assert "prop_" in proposal.proposal_id


class TestRunReport:
    def test_run_report_creation(self):
        run = RunReport(
            trigger="new_input",
            input_id="input_123",
        )
        assert "run_" in run.run_id
        assert run.trigger == "new_input"
        assert run.ended_at is None

    def test_run_report_with_steps(self):
        run = RunReport(
            trigger="manual",
            input_id="input_123",
        )
        run.steps.append(PipelineStep(stage="extract", result="parsed"))
        run.steps.append(PipelineStep(stage="classify", result="project/work"))
        assert len(run.steps) == 2
        assert run.steps[0].stage == "extract"


class TestInput:
    def test_input_creation(self):
        inp = Input(
            type=InputType.TEXT,
            content="Test content",
        )
        assert "input_" in inp.id
        assert inp.type == InputType.TEXT

    def test_file_input(self):
        inp = Input(
            type=InputType.FILE,
            content="File content",
            file_path="/path/to/file.txt",
        )
        assert inp.file_path == "/path/to/file.txt"
