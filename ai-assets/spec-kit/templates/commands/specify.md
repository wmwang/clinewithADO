---
description: "Create a specification for a new feature based on user requirements"
---

# /speckit.specify

Create a comprehensive specification for $ARGUMENTS.

## Instructions

You are acting as a product manager and architect helping define what to build.

### Step 1: Clarify Requirements

Ask these questions if not already answered:
1. Who are the primary users of this feature?
2. What problem does this solve for them?
3. What does success look like? (measurable outcome)
4. What are the constraints? (technical, timeline, resources)
5. What is explicitly out of scope?

### Step 2: Write the Specification

Create `spec.md` using the spec template. Include:

**User Scenarios (ordered by priority):**
- P1: Must have - the feature is useless without these
- P2: Should have - significantly improves the feature
- P3: Nice to have - polish and edge cases

Each scenario must be:
- Independently testable
- Described as user-visible behavior (not implementation)
- Written in Given/When/Then format

**Requirements:**
- Functional: What the system must do
- Non-functional: Performance, security, reliability targets

**Key Entities:**
- Data structures and their relationships
- State transitions (if applicable)

**Success Criteria:**
- Measurable outcomes that confirm the feature is working

### Step 3: Review

Before finalizing:
- [ ] Every P1 scenario has clear acceptance criteria
- [ ] Non-functional requirements have numeric targets
- [ ] Out of scope is explicitly defined
- [ ] Open questions are listed

### Output

Create or update: `spec.md`

Say when done: "Specification complete. Review `spec.md` then run `/speckit.plan` to create the technical approach."
