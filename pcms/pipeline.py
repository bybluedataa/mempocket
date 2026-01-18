"""Agent pipeline for processing inputs."""

import json
from datetime import datetime
from pathlib import Path

import anthropic

from .config import (
    CLAUDE_MODEL,
    Entity,
    Context,
    ProposalType,
    InputType,
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


def classify_content(content: str) -> ClassificationResult:
    """
    Use Claude to classify content into entity + context.
    """
    client = anthropic.Anthropic()

    prompt = CLASSIFICATION_PROMPT.format(content=content[:2000])

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()

    # Parse JSON response
    try:
        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        data = json.loads(response_text)
        return ClassificationResult(
            entity=Entity(data["entity"]),
            context=Context(data["context"]),
            confidence=float(data.get("confidence", 0.8)),
            reason=data.get("reason", ""),
            suggested_title=data.get("suggested_title"),
        )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Default fallback
        return ClassificationResult(
            entity=Entity.LIBRARY,
            context=Context.LIFE,
            confidence=0.5,
            reason=f"Classification failed: {e}. Defaulting to library/life.",
            suggested_title=content[:50],
        )


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
