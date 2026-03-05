# OpenSpec - AI Agent Instructions

This project uses OpenSpec for spec-driven development. Follow these guidelines when working on features.

## Workflow Overview

```
/opsx:propose → creates proposal + specs + design + tasks
/opsx:apply   → implements pending tasks
/opsx:archive → archives completed changes to specs
```

## Directory Structure

```
openspec/
├── changes/         # Active feature work
│   └── <change>/
│       ├── proposal.md    # Why + what changes
│       ├── specs/         # Requirements and scenarios
│       ├── design.md      # Technical approach
│       └── tasks.md       # Implementation checklist
└── specs/           # Current system state (source of truth)
    └── <capability>/
        └── spec.md
```

## Key Rules

### Before Implementing Any Feature
1. A proposal must exist in `openspec/changes/<feature-name>/proposal.md`
2. Specs must be written in `openspec/changes/<feature-name>/specs/`
3. Tasks must be defined in `openspec/changes/<feature-name>/tasks.md`

### During Implementation
- Work through tasks in order unless blocked
- Mark tasks complete as you finish them: `- [x] 1.1 ...`
- If blocked, stop and report - don't work around blockers

### After Implementation
- All tasks must be checked before considering the feature done
- Archive with `/opsx:archive` to update `openspec/specs/`

## Spec Format

Requirements use SHALL/MUST for normative language:

```markdown
## ADDED Requirements

### Requirement: User can export data
The system SHALL allow users to export their data in CSV format.

#### Scenario: Successful export
- **WHEN** user clicks "Export" button
- **THEN** system downloads a CSV file with all user data
```

## What Belongs Where

- **proposal.md** - Why we're building this and what changes at a high level
- **specs/** - WHAT the system should do (observable behavior)
- **design.md** - HOW to implement it (technical decisions)
- **tasks.md** - Implementation checklist (actionable steps)

## Philosophy

> fluid not rigid → iterative not waterfall → easy not complex
