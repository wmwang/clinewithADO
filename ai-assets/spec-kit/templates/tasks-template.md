# [Feature Name] Tasks

> **Purpose:** Granular, actionable implementation tasks. Generated from `plan.md`. Each task should be completable in one session.

## Phase 1: Setup

- [ ] [S1] [P1] Create feature branch: `git checkout -b feat/[feature-name]`
- [ ] [S2] [P1] Verify test suite baseline: run `[test command]`, all pass
- [ ] [S3] [P1] Install required dependencies: `[install command]`
- [ ] [S4] [P1] Create directory structure per plan.md

## Phase 2: Foundational

### Data Layer

- [ ] [F1] [P1] [Story: Data models] Create migration for [entity] table
  - File: `[path/to/migration.sql]`
  - Fields: [list key fields]
- [ ] [F2] [P1] [Story: Data models] Verify migration applies cleanly
- [ ] [F3] [P1] [Story: Data models] Create TypeScript types for [entity]
  - File: `[path/to/types.ts]`

### Service Layer

- [ ] [F4] [P1] [Story: Core service] Write failing test: [specific behavior]
  - File: `[path/to/test.ts]`
  - Test: `[describe what the test asserts]`
- [ ] [F5] [P1] [Story: Core service] Implement [ServiceName].[method]()
  - File: `[path/to/service.ts]`
  - Implements: [what it does]
- [ ] [F6] [P1] Commit: `feat: add [feature] data layer`

## Phase 3: User Stories P1

### Story: [Story name from spec]

> **Goal:** [One sentence from spec]

- [ ] [P1.1] [P1] Write failing test: [specific API behavior]
  - File: `[path/to/test.ts]`
  - Test: `[describe the assertion]`
- [ ] [P1.2] [P1] Implement [endpoint/function]: [brief description]
  - File: `[path/to/implementation]`
  - Input: `[input format]`
  - Output: `[output format]`
- [ ] [P1.3] [P1] Write failing test: [edge case]
- [ ] [P1.4] [P1] Handle [edge case] in implementation
- [ ] [P1.5] [P1] Commit: `feat: implement [story name]`

### Story: [Next P1 story]

- [ ] [P1.6] [P1] Write failing test: [behavior]
- [ ] [P1.7] [P1] Implement [component]
- [ ] [P1.8] [P1] Commit: `feat: [story name]`

## Phase 4: User Stories P2

### Story: [P2 story from spec]

> Complete after all P1 stories are done and deployed.

- [ ] [P2.1] [P2] Write failing test: [behavior]
- [ ] [P2.2] [P2] Implement [feature]
- [ ] [P2.3] [P2] Commit: `feat: [story name]`

## Phase 5: User Stories P3

> Complete after P2 stories are validated with users.

- [ ] [P3.1] [P3] [Task description]

## Parallel Execution Notes

The following tasks can run in parallel:
- [Task group A] - independent of [Task group B]
- [Task group B] - can start after [prerequisite]

## Testing Checklist

Before considering implementation complete:
- [ ] All P1 scenario tests pass
- [ ] All P2 scenario tests pass
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] Performance test: [specific target]
- [ ] No console errors or warnings

## Deliverables

At completion, the following are independently testable and deployable:
- [ ] [P1 deliverable - specific feature]
- [ ] [P2 deliverable - specific feature]
