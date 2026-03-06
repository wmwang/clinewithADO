# OpenSpec Skills (`/opsx-*`)

A self-contained, CLI-free version of OpenSpec implemented as Claude Code skills.

## Installation

Copy the skill folders to your project's `.claude/skills/` directory:

```bash
mkdir -p .claude/skills
cp -r path/to/skills/opsx-* .claude/skills/
```

Then restart Claude Code. The skills will be available automatically.

## Available Commands

| Command | Description |
|---|---|
| `/opsx-propose <name>` | **Start here** - Create a change and generate all artifacts at once |
| `/opsx-apply <name>` | Implement tasks from a change |
| `/opsx-archive <name>` | Archive a completed change |
| `/opsx-sync <name>` | Sync delta specs to main specs |
| `/opsx-verify <name>` | Verify implementation matches artifacts |
| `/opsx-new <name>` | Create a change scaffold (step-by-step mode) |
| `/opsx-continue <name>` | Continue creating artifacts one at a time |
| `/opsx-status [name]` | Show change status and task progress |

## Typical Workflow

```
You: /opsx-propose add-dark-mode
AI:  Creates openspec/changes/add-dark-mode/ with:
     ✓ proposal.md  - why
     ✓ specs/       - what (requirements + scenarios)
     ✓ design.md    - how
     ✓ tasks.md     - implementation checklist

You: /opsx-apply
AI:  Implements each task, marks complete as it goes.
     ✓ 1.1 Add theme context provider
     ✓ 1.2 Create toggle component
     ...

You: /opsx-archive
AI:  Syncs specs if needed, moves to archive/YYYY-MM-DD-add-dark-mode/
```

## File Structure Created

```
openspec/
├── changes/
│   ├── <name>/
│   │   ├── .openspec.yaml     # schema metadata
│   │   ├── proposal.md        # why
│   │   ├── specs/
│   │   │   └── <capability>/
│   │   │       └── spec.md    # what (delta spec)
│   │   ├── design.md          # how
│   │   └── tasks.md           # implementation checklist
│   └── archive/
│       └── YYYY-MM-DD-<name>/ # completed changes
└── specs/
    └── <capability>/
        └── spec.md            # main specs (updated by /opsx-sync)
```

## Project Config (Optional)

Create `openspec/config.yaml` to give context to the AI:

```yaml
schema: spec-driven

context: |
  Tech stack: TypeScript, Node.js, React
  Package manager: npm
  Testing: Jest

rules:
  specs:
    - Include mobile scenarios for UI changes
  tasks:
    - Add tests for all new functionality
```

The AI reads this file when generating artifacts to keep output consistent with your project.
