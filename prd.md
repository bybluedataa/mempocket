# PRD: Context Memory System — Lite Edition

## Vision
A lightweight personal context system: 3 boxes for everything, 2 modes for life. Capture fast, link naturally, search when needed.

---

## Core Philosophy

1. **Don't over-categorize**: Only split when you actually need to
2. **2-second decision**: Every input answers 2 questions, done
3. **Soft relationships**: `[[Wiki Links]]` in content = relationships. Search handles the rest
4. **Append-only**: Never delete, only add. History is preserved
5. **Human approves**: Agent suggests, you confirm
6. **Upgrade later**: Start simple, add complexity only when painful

---

## The Model: 3 Entities + 2 Contexts

### 3 Entities (The Nouns) — "What box does it go in?"

| Entity | What it is | Examples |
|--------|-----------|----------|
| `#project` | Something to finish. Has goal, has end. | "Launch App Q2", "Marathon Training", "Buy House" |
| `#library` | Knowledge & assets. Reference, learn, maintain. | "ReactJS", "Health Records", "Tax Documents", "Cooking" |
| `#people` | Humans & orgs you interact with. | "Alice", "Dr. Chen", "Acme Corp", "Team Engineering" |

### 2 Contexts (The Adjectives) — "Which half of life?"

| Context | What it covers |
|---------|---------------|
| `@work` | Career, money, profession, colleagues |
| `@life` | Health, family, hobbies, personal finance |

> If something is in between, pick whichever dominates your purpose right now.

---

## Data Structure

```
~/.pcms/
├── config.json
├── entries/                    # All notes/entries
│   └── {entry_id}.json
├── inbox/                      # Unprocessed inputs
│   └── {input_id}.json
├── proposals/                  # Agent suggestions awaiting approval
│   └── {proposal_id}.json
├── runs/                       # Pipeline transparency
│   └── {run_id}.json
└── index.json                  # Derived: links, tags (rebuildable)
```

### Entry Schema
```json
{
  "id": "entry_uuid",
  "title": "Launch App Q2",
  "entity": "project|library|people",
  "context": "work|life",
  "content": "Deadline: 30/06\nTeam: [[Alice]], [[Bob]]\nStack: [[ReactJS]]\n\nNotes from kickoff meeting...",
  "links": ["alice", "bob", "reactjs"],
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "source": {
    "type": "manual|file|image|text",
    "ref": "path or null",
    "hash": "sha256 if file"
  },
  "history": [
    {"timestamp": "ISO8601", "action": "created|updated|appended", "by": "user|agent:extractor", "diff": "..."}
  ]
}
```

### Proposal Schema (Agent suggestions)
```json
{
  "proposal_id": "prop_uuid",
  "run_id": "run_uuid",
  "type": "new_entry|update_entry|new_link",
  "suggested": {
    "title": "Dr. Chen",
    "entity": "people",
    "context": "life",
    "content": "Bác sĩ tim mạch tại BV XYZ...",
    "links": ["health-records"]
  },
  "evidence": {
    "source_input": "input_uuid",
    "extracted_from": "Khám tổng quát 2026 notes",
    "span": "line 3-5"
  },
  "confidence": 0.85,
  "reason": "Found new person mentioned: Dr. Chen",
  "status": "pending|approved|rejected"
}
```

### RunReport Schema (Transparency)
```json
{
  "run_id": "run_uuid",
  "started_at": "ISO8601",
  "ended_at": "ISO8601",
  "trigger": "new_input|manual",
  "input": {"type": "text", "content": "...first 200 chars..."},
  "steps": [
    {"stage": "extract", "result": "parsed text, found 3 entities"},
    {"stage": "classify", "result": "entity=project, context=work, confidence=0.9"},
    {"stage": "link_detect", "result": "found links: [[Alice]], [[ReactJS]]"},
    {"stage": "propose", "result": "created proposal prop_abc"}
  ],
  "proposals": ["prop_abc"],
  "flags": []
}
```

---

## Agent Pipeline (Simple)

```
┌─────────────────────────────────────────────┐
│            ORCHESTRATOR AGENT               │
│  1. Receive input                           │
│  2. Run extraction pipeline                 │
│  3. Generate proposals                      │
│  4. Wait for human approval                 │
│  5. Write to entries/                       │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ EXTRACT │ │ CLASSIFY│ │  LINK   │
   │         │ │         │ │ DETECT  │
   │ Parse   │ │ #entity │ │ [[...]] │
   │ OCR     │ │ @context│ │ mentions│
   └─────────┘ └─────────┘ └─────────┘
```

### Pipeline Steps
1. **Extract**: Parse input (text/file/image) → clean content
2. **Classify**: Determine `#entity` + `@context` (with confidence)
3. **Link Detect**: Find `[[wiki links]]` and entity mentions
4. **Propose**: Create proposal for human review

---

## Tools (Claude Agent SDK)

```python
# Input
add_input(content: str, type: str) -> input_id
add_file(path: str) -> input_id

# Pipeline
run_pipeline(input_id: str) -> run_id
get_run(run_id: str) -> RunReport

# Proposals
get_pending() -> list[Proposal]
approve(proposal_id: str) -> entry_id
reject(proposal_id: str, reason: str)

# Entries
get_entry(entry_id: str) -> Entry
search(query: str, entity: str = None, context: str = None) -> list[Entry]
list_entries(entity: str = None, context: str = None) -> list[Entry]

# Manual operations
create_entry(title, entity, context, content) -> entry_id
update_entry(entry_id, content) -> entry_id
append_entry(entry_id, content) -> entry_id
```

---

## CLI Interface

```bash
# Quick add (agent classifies)
pcms add "Meeting với Alice về dự án Q2, deadline 30/06"
pcms add --file ./contract.pdf
pcms add --image ./whiteboard.jpg

# Manual add (you classify)
pcms new "Launch App Q2" --project --work
pcms new "Dr. Chen" --people --life
pcms new "ReactJS Notes" --library --work

# Review agent suggestions
pcms pending                    # List all proposals
pcms show <proposal_id>         # See details + evidence
pcms approve <proposal_id>
pcms reject <proposal_id> "Wrong classification"
pcms run <run_id>               # See full pipeline trace

# Query
pcms search "Alice Q2"
pcms list --project --work      # All work projects
pcms list --people              # All people
pcms get <entry_id>

# Update existing
pcms append <entry_id> "New update: deadline moved to 15/07"
pcms edit <entry_id>            # Open in $EDITOR

# Links
pcms links <entry_id>           # Show what this entry links to
pcms backlinks <entry_id>       # Show what links TO this entry
```

---

## Example Workflow

### 1. Quick capture
```bash
$ pcms add "Họp với Alice và Bob về launch app. Deadline 30/06. Dùng ReactJS."
```

### 2. Agent processes & proposes
```
Pipeline run_abc123:
  ✓ Extract: parsed text
  ✓ Classify: #project @work (confidence: 0.92)
  ✓ Links: [[Alice]], [[Bob]], [[ReactJS]]
  → Created proposal prop_xyz
```

### 3. Review & approve
```bash
$ pcms pending
  [prop_xyz] NEW #project @work "Họp với Alice và Bob..."
             Links: Alice, Bob, ReactJS
             Confidence: 0.92

$ pcms approve prop_xyz
  ✓ Created entry entry_abc
```

### 4. Later, search naturally
```bash
$ pcms search "Alice deadline"
  [entry_abc] #project @work "Họp với Alice và Bob..."
              Deadline: 30/06

$ pcms backlinks alice
  [entry_abc] "Họp với Alice và Bob..."
  [entry_def] "1-on-1 với Alice về performance..."
```

---

## MVP Scope

### Must Have
- [ ] Entry storage with entity/context/links
- [ ] Inbox for raw inputs
- [ ] Pipeline: Extract → Classify → Link Detect → Propose
- [ ] Proposal approval/rejection flow
- [ ] RunReport for every pipeline run
- [ ] CLI: add, new, pending, approve, reject, search, list, get
- [ ] Basic link extraction from `[[wiki syntax]]`
- [ ] File-based JSON storage

### Deferred
- [ ] Image/vision input (OCR)
- [ ] Backlinks index
- [ ] Smart entity mention detection (without `[[]]`)
- [ ] Web UI
- [ ] Export to Obsidian/Notion format

---

## Implementation Structure

```
pcms/
├── pyproject.toml
├── pcms/
│   ├── __init__.py
│   ├── cli.py                  # Click CLI
│   ├── config.py               # Paths, settings
│   ├── models.py               # Pydantic: Entry, Proposal, RunReport
│   ├── store.py                # JSON file operations
│   ├── pipeline.py             # Orchestrator + stages
│   ├── tools.py                # Claude SDK tool definitions
│   └── agent.py                # Claude Agent setup
└── tests/
    ├── test_store.py
    ├── test_pipeline.py
    └── test_cli.py
```

---

## Technical Notes

- **Python 3.11+**
- **anthropic** SDK for agents
- **Pydantic v2** for models
- **Click** for CLI
- Storage: `~/.pcms/` (override with `PCMS_HOME`)
- Model: `claude-sonnet-4-20250514`
- Links extracted via regex: `\[\[([^\]]+)\]\]`
- Entry IDs derived from slugified title + short uuid

---

## The 2-Second Rule

When adding anything, you (or the agent) only answer:

1. **What box?** → `#project` / `#library` / `#people`
2. **Which life?** → `@work` / `@life`

That's it. Links emerge naturally from content. Search finds everything else.