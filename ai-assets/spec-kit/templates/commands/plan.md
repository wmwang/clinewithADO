---
description: "Create a technical implementation plan from a specification"
---

# /speckit.plan

Create a technical implementation plan for $ARGUMENTS based on the existing specification.

## Instructions

You are acting as a senior architect. Read `spec.md` before starting.

### Step 1: Constitution Check

Read the project constitution (if it exists). For each principle:
- [ ] Does this plan comply?
- [ ] If not, document justification

### Step 2: Research Existing Code

Before designing:
1. Find similar existing patterns in the codebase
2. Identify reusable components or services
3. Note constraints from existing architecture
4. Check what testing patterns are used

### Step 3: Define Data Models

For each entity in the spec:
- Fields and types
- Relationships to other entities
- Validation rules
- Storage approach (database, cache, file)

### Step 4: Define API Contracts

For each user scenario, define:
- Endpoint or function signature
- Input format (request body, parameters)
- Output format (response, return value)
- Error cases (what errors can occur, how they're surfaced)

Document contracts BEFORE writing implementation tasks.

### Step 5: Write the Plan

Create `plan.md` using the plan template. Include:

**Technical Context:**
- Language, runtime, framework versions
- Key dependencies
- Existing patterns to follow

**Implementation Phases:**
- Phase 0: Setup and research
- Phase 1: Data models
- Phase 2: API contracts
- Phase 3: Implementation (point to tasks.md)

**Repository Structure:**
- Where new files will be created
- Follow existing project conventions

### Step 6: Review

Before finalizing:
- [ ] Plan follows constitution principles
- [ ] All spec scenarios have a technical path
- [ ] No new dependencies without justification
- [ ] Complexity is justified

### Output

Create or update: `plan.md`

Say when done: "Plan complete. Review `plan.md` then run `/speckit.tasks` to generate implementation tasks."
