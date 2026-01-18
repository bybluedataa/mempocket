# mempocket

A lightweight personal context memory system: 3 boxes for everything, 2 modes for life.

## Quick Start

### Option 1: Using Claude CLI (Recommended - No API Key Needed)

```bash
# 1. Install Claude Code CLI and login
npm install -g @anthropic-ai/claude-code
claude login

# 2. Clone and install mempocket
git clone https://github.com/bybluedataa/mempocket.git
cd mempocket
pip install -e .

# 3. Start using it!
mem new "My First Project" --project --work
mem add "Meeting with Alice about Q3 budget planning"
mem pending
mem approve <proposal_id>
mem list
```

### Option 2: Using Anthropic API Key

```bash
# 1. Clone and install mempocket
git clone https://github.com/bybluedataa/mempocket.git
cd mempocket
pip install -e .

# 2. Set environment variables
export MEM_MODE=api
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Start using it!
mem add "Meeting with Alice about Q3 budget planning"
```

### Verify Installation

```bash
mem status
```

You should see:
```
mempocket Status
  Home: /Users/you/.mempocket
  Mode: cli (set MEM_MODE to change)

Total entries: 0
...
```

---

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

## Web UI

mempocket includes a web-based dashboard for visual management of your entries and proposals.

### Running the Web UI

```bash
# 1. Install dependencies (first time only)
pip install -e .
cd web && npm install && cd ..

# 2. Start the backend API (Terminal 1)
uvicorn api.main:app --port 8000

# 3. Start the frontend (Terminal 2)
cd web && npm run dev

# 4. Open in browser
open http://localhost:3000
```

### Features

- **Dashboard** - Overview with stats, pending proposals, and recent entries
- **Entries** - Browse, filter, and manage all entries
- **Proposals** - Review and approve/reject AI-suggested entries
- **Quick Add** - Press `Cmd+K` to quickly add new content
- **Search** - Full-text search across all entries

## Configuration

### Two Modes for AI Classification

| Mode | How to Enable | Description |
|------|---------------|-------------|
| **CLI** (default) | `MEM_MODE=cli` or unset | Uses Claude Code CLI with your Claude subscription |
| **API** | `MEM_MODE=api` | Uses Anthropic API directly (requires `ANTHROPIC_API_KEY`) |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MEM_HOME` | Data storage directory | `~/.mempocket` |
| `MEM_MODE` | `cli` for Claude CLI, `api` for API key | `cli` |
| `ANTHROPIC_API_KEY` | API key (required if MEM_MODE=api) | - |

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

## Requirements

- Python 3.11+
- One of:
  - **Claude Code CLI** for CLI mode: `npm install -g @anthropic-ai/claude-code`
  - **Anthropic API key** for API mode

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT
