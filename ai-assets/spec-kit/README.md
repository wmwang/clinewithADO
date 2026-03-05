# Spec Kit

Specification-driven development methodology from GitHub. Write specs, plans, and tasks before writing code.

**Source:** [github/spec-kit](https://github.com/github/spec-kit)

## Philosophy

Spec-driven development (SDD) inverts traditional development: specifications generate code, not the other way around.

> "Maintaining software means evolving specifications."

## Workflow

```
/speckit.specify → define what to build (spec.md)
/speckit.plan    → define how to build it (plan.md)
/speckit.tasks   → break into actionable steps (tasks.md)
/speckit.implement → execute tasks with TDD
```

## Templates

| Template | Purpose |
|----------|---------|
| `spec-template.md` | User scenarios and requirements |
| `plan-template.md` | Technical approach and architecture |
| `tasks-template.md` | Granular implementation tasks |
| `constitution-template.md` | Project governance principles |

## Commands

| Command | Action |
|---------|--------|
| `/speckit.specify` | Create specification from requirements |
| `/speckit.plan` | Create technical plan from spec |
| `/speckit.tasks` | Generate task list from plan |
| `/speckit.implement` | Execute tasks with TDD |

## Project Structure After Installation

```
.specify/
├── memory/
│   └── constitution.md      # Project principles
└── templates/               # Template files
spec.md                      # Current specification
plan.md                      # Technical plan
tasks.md                     # Implementation tasks
```

## Installation

Use the repo's `install.sh` to set up Spec Kit in your project.
