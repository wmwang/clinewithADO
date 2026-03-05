---
description: "Generate granular implementation tasks from a plan"
---

# /speckit.tasks

Generate implementation tasks for $ARGUMENTS based on `plan.md` and `spec.md`.

## Instructions

You are creating a task list that any developer can execute without additional context. Read both `spec.md` and `plan.md` before starting.

### Task Quality Rules

Each task must be:
- **Completable in one session** (30-90 minutes)
- **Independently verifiable** (you know when it's done)
- **TDD-first** (test tasks before implementation tasks)
- **Specific** (includes file names and what to do)

### Task Format

```
- [ ] [ID] [Priority] [Story reference] Description
  - File: `path/to/file.ts`
  - Details: specific implementation notes
```

### Ordering Rules

1. **Setup tasks first** (branch, baseline tests)
2. **Foundational tasks next** (data models, shared utilities)
3. **P1 stories** in dependency order
4. **P2 stories** after P1 complete
5. **P3 stories** after P2 validated

### TDD Task Pairs

Every implementation task needs a test task before it:

```
- [ ] [F4] [P1] Write failing test: [specific behavior]
  - File: src/[feature]/[feature].test.ts
  - Test: describe('[behavior]', () => { it('[assertion]', ...) })
- [ ] [F5] [P1] Implement [function/endpoint]
  - File: src/[feature]/[feature].ts
  - Makes test F4 pass
```

### Granularity Check

**Too coarse (rewrite):**
```
- [ ] Implement user authentication
```

**Correct:**
```
- [ ] Write failing test: POST /auth/login returns 401 for wrong password
- [ ] Implement credential validation in AuthService.login()
- [ ] Write failing test: POST /auth/login returns JWT for valid credentials
- [ ] Add JWT generation to AuthService.login()
- [ ] Commit: feat: implement login endpoint
```

### Parallel Execution

Identify tasks that can run in parallel and note them:
- Tasks that don't share files
- Tasks for different features/modules
- Test writing and documentation

### Output

Create or update: `tasks.md`

Structure:
- Phase 1: Setup
- Phase 2: Foundational
- Phase 3: P1 Stories (one section per story)
- Phase 4: P2 Stories
- Phase 5: P3 Stories
- Testing Checklist

Say when done: "Tasks complete. Review `tasks.md` then begin implementation with `/speckit.implement`."
