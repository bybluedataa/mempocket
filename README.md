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

## Configuration

mempocket supports two modes for AI classification:

### Mode 1: Claude CLI (Default)
Uses your Claude subscription via Claude Code CLI. No API key needed.

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code
claude login

# Use mempocket (default mode)
mem add "Meeting with Alice about Q2 launch"
```

### Mode 2: Anthropic API
Uses Anthropic API directly with an API key.

```bash
# Set environment variables
export MEM_MODE=api
export ANTHROPIC_API_KEY=sk-ant-...

# Use mempocket
mem add "Meeting with Alice about Q2 launch"
```

## Usage

### Quick Add (Agent Classifies)

```bash
mem add "Meeting with Alice about Q2 launch, deadline June 30"
mem add --file ./notes.md
```

### Manual Add (You Classify)

```bash
mem new "Launch App Q2" --project --work
mem new "Dr. Chen" --people --life
mem new "ReactJS Notes" --library --work
```

### Review Agent Suggestions

```bash
mem pending              # List all proposals
mem show <proposal_id>   # See details + evidence
mem approve <proposal_id>
mem reject <proposal_id> "Wrong classification"
```

### Query

```bash
mem search "Alice Q2"
mem list --project --work
mem list --people
mem get <entry_id>
```

### Update Existing

```bash
mem append <entry_id> "New update: deadline moved to July 15"
mem edit <entry_id>      # Open in $EDITOR
```

### Links

```bash
mem links <entry_id>     # Show what this entry links to
mem backlinks <entry_id> # Show what links TO this entry
```

### Status

```bash
mem status               # Show system status and current mode
```

## Data Storage

All data is stored in `~/.mempocket/` (override with `MEM_HOME` env var):

```
~/.mempocket/
├── config.json
├── entries/           # All notes/entries
├── inbox/             # Unprocessed inputs
├── proposals/         # Agent suggestions awaiting approval
├── runs/              # Pipeline transparency logs
└── index.json         # Derived links index (rebuildable)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEM_HOME` | Data storage directory | `~/.mempocket` |
| `MEM_MODE` | `cli` for Claude CLI, `api` for API key | `cli` |
| `ANTHROPIC_API_KEY` | API key (required if MEM_MODE=api) | - |

## Requirements

- Python 3.11+
- One of:
  - Claude Code CLI (`npm install -g @anthropic-ai/claude-code`) for CLI mode
  - Anthropic API key for API mode

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT
