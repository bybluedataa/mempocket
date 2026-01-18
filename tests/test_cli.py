"""Tests for mempocket CLI."""

import os
import tempfile
import pytest
from click.testing import CliRunner

from mem.cli import cli
from mem.store import init_storage, save_entry
from mem.models import Entry
from mem.config import Entity, Context


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_mem_home(monkeypatch):
    """Create a temporary mempocket home directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("MEM_HOME", tmpdir)
        init_storage()
        yield tmpdir


class TestNewCommand:
    def test_new_project(self, runner, temp_mem_home):
        result = runner.invoke(cli, [
            "new", "Test Project",
            "--project", "--work"
        ])
        assert result.exit_code == 0
        assert "Created entry" in result.output

    def test_new_without_entity(self, runner, temp_mem_home):
        result = runner.invoke(cli, [
            "new", "Test", "--work"
        ])
        assert result.exit_code == 0
        assert "Specify --project" in result.output

    def test_new_without_context(self, runner, temp_mem_home):
        result = runner.invoke(cli, [
            "new", "Test", "--project"
        ])
        assert result.exit_code == 0
        assert "Specify --work or --life" in result.output


class TestListCommand:
    def test_list_empty(self, runner, temp_mem_home):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No entries found" in result.output

    def test_list_with_entries(self, runner, temp_mem_home):
        entry = Entry(
            title="Test Entry",
            entity=Entity.PROJECT,
            context=Context.WORK,
        )
        save_entry(entry)

        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Test Entry" in result.output

    def test_list_filter_entity(self, runner, temp_mem_home):
        entry1 = Entry(title="Project", entity=Entity.PROJECT, context=Context.WORK)
        entry2 = Entry(title="Person", entity=Entity.PEOPLE, context=Context.LIFE)
        save_entry(entry1)
        save_entry(entry2)

        result = runner.invoke(cli, ["list", "--project"])
        assert result.exit_code == 0
        assert "Project" in result.output
        assert "Person" not in result.output


class TestSearchCommand:
    def test_search(self, runner, temp_mem_home):
        entry = Entry(
            title="Meeting with Alice",
            entity=Entity.PROJECT,
            context=Context.WORK,
            content="Discuss Q2 goals",
        )
        save_entry(entry)

        result = runner.invoke(cli, ["search", "Alice"])
        assert result.exit_code == 0
        assert "Alice" in result.output

    def test_search_no_results(self, runner, temp_mem_home):
        result = runner.invoke(cli, ["search", "nonexistent"])
        assert result.exit_code == 0
        assert "No results found" in result.output


class TestGetCommand:
    def test_get_entry(self, runner, temp_mem_home):
        entry = Entry(
            title="Test Entry",
            entity=Entity.PROJECT,
            context=Context.WORK,
            content="Test content",
        )
        entry_id = save_entry(entry)

        result = runner.invoke(cli, ["get", entry_id])
        assert result.exit_code == 0
        assert "Test Entry" in result.output
        assert "Test content" in result.output

    def test_get_not_found(self, runner, temp_mem_home):
        result = runner.invoke(cli, ["get", "nonexistent"])
        assert result.exit_code == 0
        assert "not found" in result.output


class TestStatusCommand:
    def test_status(self, runner, temp_mem_home):
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "mempocket Status" in result.output
        assert "Total entries" in result.output


class TestPendingCommand:
    def test_pending_empty(self, runner, temp_mem_home):
        result = runner.invoke(cli, ["pending"])
        assert result.exit_code == 0
        assert "No pending proposals" in result.output
