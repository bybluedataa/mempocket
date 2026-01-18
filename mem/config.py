"""Configuration and constants for mempocket."""

import json
import os
from pathlib import Path
from enum import Enum
from typing import Optional

# Global config file location (user's home directory)
GLOBAL_CONFIG_FILE = Path.home() / ".mempocketrc"


def _load_global_config() -> dict:
    """Load global config from ~/.mempocketrc if it exists."""
    if GLOBAL_CONFIG_FILE.exists():
        try:
            with open(GLOBAL_CONFIG_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def _save_global_config(config: dict) -> None:
    """Save global config to ~/.mempocketrc."""
    with open(GLOBAL_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


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
    """Get mempocket home directory.

    Priority:
    1. MEM_HOME environment variable
    2. mem_home from ~/.mempocketrc config file
    3. Default: ~/.mempocket
    """
    # Check environment variable first
    if os.environ.get("MEM_HOME"):
        return Path(os.environ["MEM_HOME"])

    # Check config file
    config = _load_global_config()
    if config.get("mem_home"):
        return Path(config["mem_home"])

    # Default
    return Path.home() / ".mempocket"


def set_mem_home(path: Path) -> None:
    """Set mempocket home directory in config file."""
    config = _load_global_config()
    config["mem_home"] = str(path.resolve())
    _save_global_config(config)


def is_initialized() -> bool:
    """Check if mempocket has been initialized."""
    return GLOBAL_CONFIG_FILE.exists() or get_mem_home().exists()


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
