"""Agent pipeline for processing inputs.

Supports two modes:
- CLI mode: Uses Claude Code CLI (subscription-based, no API key needed)
- API mode: Uses Anthropic API directly (requires ANTHROPIC_API_KEY)

Set MEM_MODE=api to use API mode, otherwise CLI mode is default.
"""

import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

from .config import (
    Entity,
    Context,
    ProposalType,
    InputType,
    ClaudeMode,
    CLAUDE_MODEL,
    get_claude_mode,
    has_api_key,
)
from .models import (
    Input,
    RunReport,
    PipelineStep,
    Proposal,
    SuggestedEntry,
    Evidence,
    ClassificationResult,
)
from .store import (
    get_input,
    save_run,
    save_proposal,
    extract_links,
)


CLASSIFICATION_PROMPT = """You are a personal knowledge assistant helping categorize information.

Given the following content, classify it according to these rules:

## Entity (what box does it go in?):
- "project": Something to finish. Has a goal and an end. Examples: "Launch App Q2", "Marathon Training", "Buy House"
- "library": Knowledge & assets. Reference, learn, maintain. Examples: "ReactJS", "Health Records", "Tax Documents", "Cooking"
- "people": Humans & organizations you interact with. Examples: "Alice", "Dr. Chen", "Acme Corp", "Team Engineering"

## Context (which half of life?):
- "work": Career, money, profession, colleagues
- "life": Health, family, hobbies, personal finance

If something is in between, pick whichever dominates the purpose.

## Content to classify:
{content}

## Response format:
Respond ONLY with a valid JSON object (no markdown, no explanation):
{{
    "entity": "project" | "library" | "people",
    "context": "work" | "life",
    "confidence": 0.0-1.0,
    "reason": "Brief explanation of classification",
    "suggested_title": "A concise title for this entry"
}}"""


def extract_content(inp: Input) -> tuple[str, str]:
    """
    Extract clean content from input.
    Returns (content, extraction_note).
    """
    if inp.type == InputType.TEXT or inp.type == InputType.MANUAL:
        return inp.content, "parsed text input"

    if inp.type == InputType.FILE and inp.file_path:
        path = Path(inp.file_path)
        if path.exists():
            # For MVP, only handle text files
            if path.suffix in [".txt", ".md", ".json", ".yaml", ".yml"]:
                content = path.read_text(encoding="utf-8")
                return content, f"read file: {path.name}"
            else:
                return inp.content, f"file reference: {path.name}"

    return inp.content, "raw content"


def _parse_json_response(response_text: str) -> dict:
    """Parse JSON from Claude response, handling markdown code blocks."""
    # Handle potential markdown code blocks
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    elif "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()

    # Try to find JSON object in response
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    if json_start >= 0 and json_end > json_start:
        response_text = response_text[json_start:json_end]

    return json.loads(response_text)


def _classify_via_cli(content: str) -> ClassificationResult:
    """Classify content using Claude Code CLI."""
    claude_path = shutil.which("claude")
    if not claude_path:
        return ClassificationResult(
            entity=Entity.LIBRARY,
            context=Context.LIFE,
            confidence=0.5,
            reason="Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code",
            suggested_title=content[:50],
        )

    prompt = CLASSIFICATION_PROMPT.format(content=content[:2000])

    try:
        result = subprocess.run(
            [claude_path, "-p", prompt, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            return ClassificationResult(
                entity=Entity.LIBRARY,
                context=Context.LIFE,
                confidence=0.5,
                reason=f"Claude CLI error: {result.stderr[:100]}",
                suggested_title=content[:50],
            )

        data = _parse_json_response(result.stdout.strip())
        return ClassificationResult(
            entity=Entity(data["entity"]),
            context=Context(data["context"]),
            confidence=float(data.get("confidence", 0.8)),
            reason=data.get("reason", ""),
            suggested_title=data.get("suggested_title"),
        )

    except subprocess.TimeoutExpired:
        return ClassificationResult(
            entity=Entity.LIBRARY,
            context=Context.LIFE,
            confidence=0.5,
            reason="Classification timed out",
            suggested_title=content[:50],
        )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return ClassificationResult(
            entity=Entity.LIBRARY,
            context=Context.LIFE,
            confidence=0.5,
            reason=f"Classification failed: {e}. Defaulting to library/life.",
            suggested_title=content[:50],
        )


def _classify_via_api(content: str) -> ClassificationResult:
    """Classify content using Anthropic API."""
    try:
        import anthropic
    except ImportError:
        return ClassificationResult(
            entity=Entity.LIBRARY,
            context=Context.LIFE,
            confidence=0.5,
            reason="anthropic package not installed. Run: pip install anthropic",
            suggested_title=content[:50],
        )

    if not has_api_key():
        return ClassificationResult(
            entity=Entity.LIBRARY,
            context=Context.LIFE,
            confidence=0.5,
            reason="ANTHROPIC_API_KEY not set. Set it or use MEM_MODE=cli",
            suggested_title=content[:50],
        )

    prompt = CLASSIFICATION_PROMPT.format(content=content[:2000])

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        data = _parse_json_response(message.content[0].text.strip())
        return ClassificationResult(
            entity=Entity(data["entity"]),
            context=Context(data["context"]),
            confidence=float(data.get("confidence", 0.8)),
            reason=data.get("reason", ""),
            suggested_title=data.get("suggested_title"),
        )

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return ClassificationResult(
            entity=Entity.LIBRARY,
            context=Context.LIFE,
            confidence=0.5,
            reason=f"Classification failed: {e}. Defaulting to library/life.",
            suggested_title=content[:50],
        )


def classify_content(content: str) -> ClassificationResult:
    """
    Classify content into entity + context using Claude.

    Uses CLI mode by default (Claude Code subscription).
    Set MEM_MODE=api to use Anthropic API key instead.
    """
    mode = get_claude_mode()

    if mode == ClaudeMode.API:
        return _classify_via_api(content)
    else:
        return _classify_via_cli(content)


def detect_links(content: str) -> list[str]:
    """Extract [[wiki links]] from content."""
    return extract_links(content)


def create_proposal(
    run_id: str,
    inp: Input,
    content: str,
    classification: ClassificationResult,
    links: list[str],
) -> Proposal:
    """Create a proposal from pipeline results."""
    title = classification.suggested_title or content[:50].strip()

    suggested = SuggestedEntry(
        title=title,
        entity=classification.entity,
        context=classification.context,
        content=content,
        links=links,
    )

    evidence = Evidence(
        source_input=inp.id,
        extracted_from=title,
        span=None,
    )

    return Proposal(
        run_id=run_id,
        type=ProposalType.NEW_ENTRY,
        suggested=suggested,
        evidence=evidence,
        confidence=classification.confidence,
        reason=classification.reason,
    )


def run_pipeline(input_id: str) -> RunReport:
    """
    Run the full pipeline on an input.

    Pipeline steps:
    1. Extract - Parse input content
    2. Classify - Determine entity + context
    3. Link Detect - Find [[wiki links]]
    4. Propose - Create proposal for review
    """
    # Initialize run report
    run = RunReport(
        trigger="new_input",
        input_id=input_id,
    )

    # Get input
    inp = get_input(input_id)
    if not inp:
        run.flags.append(f"Input not found: {input_id}")
        run.ended_at = datetime.utcnow()
        save_run(run)
        return run

    run.input_summary = inp.content[:200]

    # Step 1: Extract
    content, extract_note = extract_content(inp)
    run.steps.append(PipelineStep(
        stage="extract",
        result=extract_note,
    ))

    # Step 2: Classify
    classification = classify_content(content)
    run.steps.append(PipelineStep(
        stage="classify",
        result=f"entity={classification.entity.value}, context={classification.context.value}, confidence={classification.confidence:.2f}",
    ))

    # Step 3: Link Detect
    links = detect_links(content)
    run.steps.append(PipelineStep(
        stage="link_detect",
        result=f"found {len(links)} links: {', '.join(links[:5])}{'...' if len(links) > 5 else ''}",
    ))

    # Step 4: Propose
    proposal = create_proposal(run.run_id, inp, content, classification, links)
    proposal_id = save_proposal(proposal)
    run.proposals.append(proposal_id)
    run.steps.append(PipelineStep(
        stage="propose",
        result=f"created proposal {proposal_id}",
    ))

    # Complete run
    run.ended_at = datetime.utcnow()
    save_run(run)

    return run
