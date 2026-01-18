"""Claude agent orchestrator for PCMS.

This module provides the agent interface for processing inputs
and interacting with the PCMS system.

For the MVP, the agent functionality is primarily embedded in the
pipeline module, which uses Claude for classification.
"""

from typing import Optional

from .config import InputType
from .models import Input
from .store import save_input, init_storage
from .pipeline import run_pipeline


def quick_add(content: str) -> dict:
    """
    Quick add content - agent classifies and proposes.

    This is the main entry point for agent-assisted input.

    Args:
        content: Raw text content to add

    Returns:
        Dict with run_id, proposal_id, and summary
    """
    init_storage()

    # Create input
    inp = Input(
        type=InputType.TEXT,
        content=content,
    )
    input_id = save_input(inp)

    # Run pipeline
    run = run_pipeline(input_id)

    # Build summary
    result = {
        "run_id": run.run_id,
        "input_id": input_id,
        "proposals": run.proposals,
        "steps": [],
        "flags": run.flags,
    }

    for step in run.steps:
        result["steps"].append({
            "stage": step.stage,
            "result": step.result,
        })

    return result


def add_file_input(file_path: str) -> dict:
    """
    Add a file for agent processing.

    Args:
        file_path: Path to the file

    Returns:
        Dict with run_id, proposal_id, and summary
    """
    from pathlib import Path

    init_storage()

    path = Path(file_path)
    content = ""

    if path.exists():
        # Read text files
        if path.suffix.lower() in [".txt", ".md", ".json", ".yaml", ".yml"]:
            content = path.read_text(encoding="utf-8")
        else:
            content = f"[File: {path.name}]"
    else:
        return {
            "error": f"File not found: {file_path}",
            "run_id": None,
            "proposals": [],
        }

    # Create input
    inp = Input(
        type=InputType.FILE,
        content=content,
        file_path=str(path.absolute()),
    )
    input_id = save_input(inp)

    # Run pipeline
    run = run_pipeline(input_id)

    return {
        "run_id": run.run_id,
        "input_id": input_id,
        "proposals": run.proposals,
        "steps": [{"stage": s.stage, "result": s.result} for s in run.steps],
        "flags": run.flags,
    }


def get_system_status() -> dict:
    """
    Get current system status.

    Returns:
        Dict with counts of entries, pending proposals, etc.
    """
    from .store import list_entries, get_pending_proposals, list_inputs

    entries = list_entries()
    proposals = get_pending_proposals()
    inputs = list_inputs()

    # Count by entity
    by_entity = {"project": 0, "library": 0, "people": 0}
    for entry in entries:
        by_entity[entry.entity.value] += 1

    # Count by context
    by_context = {"work": 0, "life": 0}
    for entry in entries:
        by_context[entry.context.value] += 1

    return {
        "total_entries": len(entries),
        "by_entity": by_entity,
        "by_context": by_context,
        "pending_proposals": len(proposals),
        "inbox_items": len(inputs),
    }
