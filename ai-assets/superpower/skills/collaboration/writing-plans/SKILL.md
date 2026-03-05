---
name: superpower-writing-plans
description: Create detailed implementation plans that any engineer can execute without codebase context. Use before implementing a complex feature to enable async work and clear progress tracking.
---

# Writing Plans Skill

## Purpose

Create detailed implementation plans that any engineer can execute without codebase context. Plans enable async work, parallel execution via subagents, and clear progress tracking.

## When to Use

Announce: "I'm using the Writing Plans skill."

Use when:
- About to implement a feature after brainstorming
- The human wants to review the approach before coding
- Work will be handed off to a subagent
- The implementation spans multiple sessions
- Multiple engineers or agents will work in parallel

## Plan Format

### Header (Required)

```markdown
# [Feature Name]

**Goal:** [One sentence describing what this accomplishes]

**Architecture:** [2-3 sentences describing the high-level approach]

**Tech Stack:** [Languages, frameworks, key libraries]

**Principles:** DRY, YAGNI, TDD, commit often
```

### Task List

Each task must be:
- **Single action:** Completable in 2-5 minutes
- **TDD-first:** Test before implementation
- **Atomic:** Independent enough to verify completion
- **Clear:** Someone with zero context can execute it

**Format:**
```markdown
## Phase 1: [Phase Name]

- [ ] 1.1 Create failing test for [specific behavior]
- [ ] 1.2 Implement [specific thing] to make test pass
- [ ] 1.3 Refactor [specific code] for clarity
- [ ] 1.4 Commit: "feat: [what was done]"
```

### Phases

Organize tasks into logical phases:
1. **Setup** - Environment, dependencies, scaffolding
2. **Core Logic** - The main feature implementation
3. **Integration** - Connecting components
4. **Edge Cases** - Error handling, validation
5. **Polish** - Documentation, cleanup

## Granularity Rules

**Too coarse (bad):**
```
- [ ] Implement user authentication
```

**Correct granularity:**
```
- [ ] 1.1 Write failing test: POST /auth/login returns 401 for invalid credentials
- [ ] 1.2 Create auth controller with login endpoint
- [ ] 1.3 Write failing test: POST /auth/login returns token for valid credentials
- [ ] 1.4 Implement credential validation against database
- [ ] 1.5 Write failing test: token expires after 24 hours
- [ ] 1.6 Add JWT generation with expiry
- [ ] 1.7 Commit: "feat: implement login endpoint with JWT"
```

## Execution Handoff

After writing the plan, offer two paths:

**Option A: Subagent execution**
"I can hand this plan to a subagent using the Subagent-Driven Development skill. The subagent will execute tasks in batches of 3, reporting progress at each checkpoint."

**Option B: Continue in this session**
"I can execute this plan now using the Executing Plans skill."

## Quality Checklist

Before presenting the plan:

- [ ] Goal is one sentence (not a paragraph)
- [ ] Architecture is 2-3 sentences (not a wall of text)
- [ ] Each task takes 2-5 minutes (not hours)
- [ ] Every feature task has a corresponding test task before it
- [ ] Commit tasks are included at logical checkpoints
- [ ] Phases are clearly separated
- [ ] No task requires knowledge not in the plan

## Anti-Patterns

- Tasks that take more than 30 minutes
- Implementation tasks without preceding test tasks
- Vague tasks ("update the database logic")
- Plans without a clear goal statement
- Missing commit tasks (leaves work unsaved)
- Over-engineering future requirements (YAGNI)
