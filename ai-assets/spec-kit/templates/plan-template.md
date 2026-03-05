# [Feature Name] Implementation Plan

> **Purpose:** Define the technical approach for implementing [feature name]. Architects are responsible for this document.

## Technical Context

### Stack
- **Language:** [e.g., TypeScript 5.x / Python 3.11]
- **Runtime:** [e.g., Node.js 20.x / Python]
- **Framework:** [e.g., Next.js 14 / FastAPI]
- **Database:** [e.g., PostgreSQL 15]
- **Testing:** [e.g., Vitest / pytest]
- **Key Dependencies:** [List key libraries]

### Existing Architecture

[Brief description of relevant existing architecture]

## Constitution Check

Before proceeding, verify compliance with project constitution:
- [ ] Solution uses existing libraries before introducing new ones
- [ ] CLI interfaces preferred over complex UIs for internal tools
- [ ] Tests are written before implementation (TDD)
- [ ] Solution is as simple as possible
- [ ] No unnecessary abstractions

If any check fails, document the justification below:

**Justification for exceptions:** [If none, write "None"]

## Implementation Phases

### Phase 0: Research & Setup

**Goal:** Validate approach and prepare environment

Tasks:
- [ ] Review existing code patterns in [relevant files]
- [ ] Confirm all required dependencies available
- [ ] Set up feature branch: `git checkout -b feat/[feature-name]`
- [ ] Verify test suite passes: `[test command]`

**Research Findings:**
<!-- Complete before Phase 1 -->

### Phase 1: Data Models

**Goal:** Define the data layer

Tasks:
- [ ] Design schema for [entity 1]
- [ ] Design schema for [entity 2]
- [ ] Create migration files
- [ ] Verify migration runs cleanly

**Schema Decisions:**
<!-- Document key schema choices and rationale -->

### Phase 2: API Contracts

**Goal:** Define interfaces before implementation

Tasks:
- [ ] Define API endpoints (request/response shapes)
- [ ] Define service interfaces
- [ ] Define event/message contracts (if applicable)
- [ ] Review contracts with team

**API Contracts:**

```
POST /api/[endpoint]
Request: { ... }
Response: { ... }
Errors: 400 (validation), 401 (auth), 500 (server)
```

### Phase 3: Implementation Tasks

> See `tasks.md` for detailed task breakdown

**Generated from:** Phase 2 API contracts

## Repository Structure

### Single Project
```
src/
├── [feature]/
│   ├── [feature].controller.ts
│   ├── [feature].service.ts
│   ├── [feature].repository.ts
│   └── [feature].test.ts
└── types/
    └── [feature].types.ts
```

### Web Application (Frontend + Backend)
```
frontend/
└── src/features/[feature]/
backend/
└── src/[feature]/
```

## Complexity Justifications

Track any violations of the simplicity principle:

| Decision | Justification | Approved By |
|----------|---------------|-------------|
| [Complex choice] | [Why needed] | [Who approved] |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk description] | Low/Med/High | Low/Med/High | [How to mitigate] |

## Definition of Done

- [ ] All P1 scenarios from spec pass automated tests
- [ ] P2 scenarios implemented and tested
- [ ] No new technical debt without documented justification
- [ ] Documentation updated
- [ ] Performance targets verified
- [ ] Security review completed (if applicable)
- [ ] Code reviewed and merged to main
