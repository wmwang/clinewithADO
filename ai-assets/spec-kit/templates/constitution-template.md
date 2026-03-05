# Project Constitution

> **Purpose:** Define the governing principles and development guidelines for this project. This document takes precedence over all other guidance. All AI agents and human developers must follow these principles.

## Core Principles

### Principle 1: [Name]

**Statement:** [One sentence describing the principle]

**Description:** [2-3 sentences explaining what this means in practice]

**Examples:**
- Good: [Example of following this principle]
- Bad: [Example of violating this principle]

### Principle 2: [Name]

**Statement:** [One sentence]

**Description:** [2-3 sentences]

### Principle 3: [Name]

**Statement:** [One sentence]

**Description:** [2-3 sentences]

### Principle 4: [Name]

**Statement:** [One sentence]

**Description:** [2-3 sentences]

### Principle 5: [Name]

**Statement:** [One sentence]

**Description:** [2-3 sentences]

## Additional Constraints

### Technology Constraints
- [Required technology or library]
- [Prohibited technology or pattern]

### Process Constraints
- [Required workflow step]
- [Required review or approval]

### Quality Constraints
- [Minimum test coverage requirement]
- [Performance requirement]
- [Security requirement]

## Development Workflow

### Feature Development
1. Spec first: Write `spec.md` before any code
2. Plan second: Write `plan.md` with technical approach
3. Tasks third: Break into granular `tasks.md`
4. Implement: Follow TDD for all implementation
5. Review: All code reviewed before merge

### Quality Gates
- [ ] Specification approved before development starts
- [ ] Plan reviewed by architect before implementation
- [ ] All tests pass before PR is opened
- [ ] No new technical debt without documented justification
- [ ] Performance targets verified before merge

### Commit Standards
- Format: `type(scope): description`
- Types: feat, fix, docs, refactor, test, chore
- One logical change per commit
- Tests committed with the code they test

## Governance

### Amendment Process
1. Propose change with written rationale
2. Discuss in team meeting
3. Vote: requires unanimous agreement for core principles
4. Update this document with change and reason

### Conflict Resolution
When work conflicts with this constitution:
1. Stop work
2. Document the conflict
3. Raise with team immediately
4. Do not work around the principle without team agreement

### Exceptions
Exceptions to these principles require:
- Written justification
- Tech lead approval
- Documentation in the relevant `plan.md`

---

*Constitution version: 1.0*
*Last updated: [date]*
*Approved by: [team/individuals]*
