"""Configuration and constants for mempocket."""

import os
from pathlib import Path
from enum import Enum


class Entity(str, Enum):
    """Entity types - what box does it go in?"""
    PROJECT = "project"  # Something to finish. Has goal, has end.
    LIBRARY = "library"  # Knowledge & assets. Reference, learn, maintain.
    PEOPLE = "people"    # Humans & orgs you interact with.


class Context(str, Enum):
    """Context types - which half of life?"""
    WORK = "work"  # Career, money, profession, colleagues
    LIFE = "life"  # Health, family, hobbies, personal finance


class ProposalType(str, Enum):
    """Types of proposals the agent can make."""
    NEW_ENTRY = "new_entry"
    UPDATE_ENTRY = "update_entry"
    NEW_LINK = "new_link"


class ProposalStatus(str, Enum):
    """Status of a proposal."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class InputType(str, Enum):
    """Types of input sources."""
    MANUAL = "manual"
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"


class HistoryAction(str, Enum):
    """Actions recorded in entry history."""
    CREATED = "created"
    UPDATED = "updated"
    APPENDED = "appended"


class ClaudeMode(str, Enum):
    """Mode for Claude API access."""
    CLI = "cli"      # Use Claude Code CLI (subscription)
    API = "api"      # Use Anthropic API key


# Storage paths
def get_mem_home() -> Path:
    """Get mempocket home directory, respecting MEM_HOME env var."""
    return Path(os.environ.get("MEM_HOME", Path.home() / ".mempocket"))


def get_entries_dir() -> Path:
    return get_mem_home() / "entries"


def get_inbox_dir() -> Path:
    return get_mem_home() / "inbox"


def get_proposals_dir() -> Path:
    return get_mem_home() / "proposals"


def get_runs_dir() -> Path:
    return get_mem_home() / "runs"


def get_config_path() -> Path:
    return get_mem_home() / "config.json"


def get_index_path() -> Path:
    return get_mem_home() / "index.json"


# Claude configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"


def get_claude_mode() -> ClaudeMode:
    """
    Get Claude mode from environment.

    Set MEM_MODE=api to use Anthropic API key (requires ANTHROPIC_API_KEY)
    Set MEM_MODE=cli to use Claude Code CLI (default, uses subscription)
    """
    mode = os.environ.get("MEM_MODE", "cli").lower()
    if mode == "api":
        return ClaudeMode.API
    return ClaudeMode.CLI


def has_api_key() -> bool:
    """Check if Anthropic API key is available."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


# Link extraction pattern
LINK_PATTERN = r'\[\[([^\]]+)\]\]'
