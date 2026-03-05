# Executing Plans Skill

## Purpose

Execute a written implementation plan systematically with checkpoints, progress reports, and blocker handling.

## When to Use

Announce: "I'm using the Executing Plans skill."

Use when:
- A written plan exists (from Writing Plans skill)
- Starting implementation after planning/brainstorming
- Resuming work from a previous session
- Executing tasks from a subagent assignment

## Methodology

### Step 1: Load and Review

Read the complete plan before starting:
- Understand all phases and their dependencies
- Identify the current state (which tasks are done, which are pending)
- Note any blockers or prerequisites
- Confirm you have access to everything needed

### Step 2: Execute in Batches

Execute **3 tasks per batch** by default:

For each task:
1. Read the task description carefully
2. Execute it (TDD: write test first if it's an implementation task)
3. Verify completion (run relevant tests)
4. Mark task complete in the plan file: `- [x] 1.1 ...`
5. Commit if task includes a commit step

After 3 tasks: report progress and continue.

**Batch report format:**
```
Batch complete (tasks X.X - X.X):
✓ X.X [Task description]
✓ X.X [Task description]
✓ X.X [Task description]

Next batch: X.X - X.X
Continuing...
```

### Step 3: Blocker Handling

Stop immediately on any blocker:
- Missing dependency (package not installed, API not available)
- Test fails in unexpected way
- Unclear instruction (ambiguous acceptance criteria)
- Architectural conflict (plan doesn't match codebase reality)

**Blocker report format:**
```
BLOCKED on task X.X: [Task description]

Issue: [Specific problem]
Tried: [What was attempted]
Need: [What information or resource is needed]

Awaiting input before continuing.
```

Do NOT:
- Work around a blocker by skipping the task
- Make assumptions that might be wrong
- Continue to the next task while blocked

### Step 4: Progress Reporting

After each phase completion, report:
```
Phase [N] complete.
Tasks completed: [list]
Tests: [X passing, Y failing]
Next phase: [description]
```

### Step 5: Final Report

When all tasks are complete:
```
Plan execution complete.

Summary:
- Tasks completed: X/X
- Tests passing: X
- Commits: [list of commit messages]

Suggested next step: [e.g., "Use Finishing a Development Branch skill to prepare for PR"]
```

## Rules

- **3 tasks per batch** by default (unless human specifies otherwise)
- **Stop on blockers** - never work around them silently
- **Verify each task** - don't just execute, confirm it worked
- **Commit regularly** - follow commit tasks in the plan
- **Announce the skill** - say "I'm using the Executing Plans skill"

## Integration

This skill pairs with:
- **Writing Plans skill** - to create the plan being executed
- **Finishing a Development Branch skill** - after execution is complete
- **Subagent-Driven Development skill** - for parallel execution

## Anti-Patterns

- Executing multiple phases without reporting
- Continuing past a blocker
- Not running tests after implementation tasks
- Skipping commit tasks
- Executing without first reviewing the full plan
