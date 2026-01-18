# mempocket

A lightweight personal context memory system: 3 boxes for everything, 2 modes for life.

## Core Philosophy

- **Don't over-categorize**: Only split when you actually need to
- **2-second decision**: Every input answers 2 questions, done
- **Soft relationships**: `[[Wiki Links]]` in content = relationships
- **Append-only**: Never delete, only add. History is preserved
- **Human approves**: Agent suggests, you confirm

## The Model

### 3 Entities (What box does it go in?)

| Entity | What it is | Examples |
|--------|-----------|----------|
| `#project` | Something to finish. Has goal, has end. | "Launch App Q2", "Marathon Training" |
| `#library` | Knowledge & assets. Reference, learn, maintain. | "ReactJS", "Health Records" |
| `#people` | Humans & orgs you interact with. | "Alice", "Dr. Chen", "Acme Corp" |

### 2 Contexts (Which half of life?)

| Context | What it covers |
|---------|---------------|
| `@work` | Career, money, profession, colleagues |
| `@life` | Health, family, hobbies, personal finance |

## Installation

```bash
pip install -e .
```

## Usage

### Quick Add (Agent Classifies)

```bash
pcms add "Meeting with Alice about Q2 launch, deadline June 30"
pcms add --file ./notes.md
```

### Manual Add (You Classify)

```bash
pcms new "Launch App Q2" --project --work
pcms new "Dr. Chen" --people --life
pcms new "ReactJS Notes" --library --work
```

### Review Agent Suggestions

```bash
pcms pending              # List all proposals
pcms show <proposal_id>   # See details + evidence
pcms approve <proposal_id>
pcms reject <proposal_id> "Wrong classification"
```

### Query

```bash
pcms search "Alice Q2"
pcms list --project --work
pcms list --people
pcms get <entry_id>
```

### Update Existing

```bash
pcms append <entry_id> "New update: deadline moved to July 15"
pcms edit <entry_id>      # Open in $EDITOR
```

### Links

```bash
pcms links <entry_id>     # Show what this entry links to
pcms backlinks <entry_id> # Show what links TO this entry
```

## Data Storage

All data is stored in `~/.pcms/` (override with `PCMS_HOME` env var):

```
~/.pcms/
├── config.json
├── entries/           # All notes/entries
├── inbox/             # Unprocessed inputs
├── proposals/         # Agent suggestions awaiting approval
├── runs/              # Pipeline transparency logs
└── index.json         # Derived links index (rebuildable)
```

## Requirements

- Python 3.11+
- Claude Code CLI (uses your Claude subscription - no API key needed)
  ```bash
  npm install -g @anthropic-ai/claude-code
  claude login
  ```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT
