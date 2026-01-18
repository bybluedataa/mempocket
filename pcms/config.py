"""Configuration and constants for PCMS."""

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


# Storage paths
def get_pcms_home() -> Path:
    """Get PCMS home directory, respecting PCMS_HOME env var."""
    return Path(os.environ.get("PCMS_HOME", Path.home() / ".pcms"))


def get_entries_dir() -> Path:
    return get_pcms_home() / "entries"


def get_inbox_dir() -> Path:
    return get_pcms_home() / "inbox"


def get_proposals_dir() -> Path:
    return get_pcms_home() / "proposals"


def get_runs_dir() -> Path:
    return get_pcms_home() / "runs"


def get_config_path() -> Path:
    return get_pcms_home() / "config.json"


def get_index_path() -> Path:
    return get_pcms_home() / "index.json"


# Claude model configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Link extraction pattern
LINK_PATTERN = r'\[\[([^\]]+)\]\]'
