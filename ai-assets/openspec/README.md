# OpenSpec

Spec-driven development framework. Agree on what to build before writing any code.

**Source:** [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)

## Philosophy

> fluid not rigid → iterative not waterfall → easy not complex

## How It Works

Each feature gets its own folder:

```
openspec/changes/<feature-name>/
├── proposal.md    # Why + what's changing
├── specs/         # Requirements and scenarios
│   └── <capability>/spec.md
├── design.md      # Technical approach (optional)
└── tasks.md       # Implementation checklist
```

When done, changes are archived and `openspec/specs/` becomes the source of truth.

## Commands

| Command | Action |
|---------|--------|
| `/opsx:propose <idea>` | Start a new feature with proposal + specs + design + tasks |
| `/opsx:apply` | Implement pending tasks |
| `/opsx:archive` | Archive completed changes to specs |

## Templates

| Template | Purpose |
|----------|---------|
| `proposal.md` | Why + what changes |
| `spec.md` | Requirements in WHEN/THEN format |
| `design.md` | Technical decisions |
| `tasks.md` | Implementation checklist |

## Installation

Use the repo's `install.sh` to set up OpenSpec in your project.

**Project setup creates:**
```
openspec/
├── changes/     # Active feature work
└── specs/       # System source of truth
AGENTS.md        # AI instructions
```
