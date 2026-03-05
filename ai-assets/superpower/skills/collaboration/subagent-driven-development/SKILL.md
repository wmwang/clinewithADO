# Subagent-Driven Development Skill

## Purpose

Execute implementation plans by spawning focused subagents for parallel or sequential work. Enables complex features to be built efficiently through coordinated specialization.

## When to Use

Announce: "I'm using the Subagent-Driven Development skill."

Use when:
- A plan has been written and is ready for execution
- Tasks can be parallelized across multiple agents
- Work needs to be isolated in separate git worktrees
- The feature is large enough that session context management matters

## Prerequisites

- A written plan exists (from Writing Plans skill)
- The plan has been approved by the human
- The codebase has a working test suite
- Git is configured and working

## Methodology

### Phase 1: Plan Review

Read the full plan before dispatching:
- Understand all phases and dependencies
- Identify which tasks can run in parallel
- Identify blocking dependencies (Task B requires Task A to complete)
- Estimate total scope

### Phase 2: Worktree Setup

For each parallel workstream:
```bash
# Create isolated worktree
git worktree add ../[feature-name]-[workstream] -b [branch-name]

# Verify worktree
cd ../[feature-name]-[workstream]
npm install  # or project equivalent
npm test     # baseline must pass
```

### Phase 3: Task Dispatch

Spawn subagents with:
1. **Context:** The relevant section of the plan
2. **Constraints:** What they cannot change (shared interfaces, APIs)
3. **Success criteria:** How to verify completion
4. **Communication protocol:** How to report blockers

**Dispatch template:**
```
Task: [Task description from plan]
Success: [How to verify completion]
Constraints: [What must stay unchanged]
Report: Complete task X.Y then stop and report status
```

### Phase 4: Progress Monitoring

Track subagent progress:
- [ ] Subagent 1: Tasks 1.1-1.4 (Setup phase)
- [ ] Subagent 2: Tasks 2.1-2.6 (Core logic)
- [ ] Subagent 3: Tasks 3.1-3.3 (Integration)

Check in after each batch of 3 tasks.

### Phase 5: Integration

When parallel workstreams complete:
1. Review each worktree's changes
2. Run tests in each worktree
3. Merge worktrees in dependency order
4. Run full test suite after each merge
5. Resolve conflicts if any

### Phase 6: Verification

After all tasks complete:
- [ ] All tests pass
- [ ] No new warnings
- [ ] Integration points work correctly
- [ ] Plan is 100% complete (no skipped tasks)

Use the Finishing a Development Branch skill to finalize.

## Blocker Protocol

If a subagent hits a blocker:
1. Stop immediately - don't guess or work around
2. Report: what the blocker is, what was tried, what information is needed
3. Wait for resolution from the orchestrating agent or human

## Parallelization Rules

**Can parallelize:**
- Independent features with no shared state
- Tests and documentation
- Different endpoints of an API (if interfaces are pre-defined)

**Cannot parallelize:**
- Tasks with data model dependencies
- Shared configuration changes
- Database migrations

## Anti-Patterns

- Dispatching without a written plan
- Not setting up worktrees (subagents can conflict)
- Dispatching too many agents at once without monitoring
- Not running baseline tests before dispatching
- Skipping the integration phase
- Allowing subagents to work around blockers instead of reporting them
