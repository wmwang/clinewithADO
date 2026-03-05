# Finishing a Development Branch Skill

## Purpose

Ensure a development branch is truly complete before merging: tests pass, code is clean, PR is well-documented, and all loose ends are tied up.

## When to Use

Announce: "I'm using the Finishing a Development Branch skill."

Use when:
- Feature implementation appears complete
- Preparing to open a pull request
- Handing off work to another engineer or agent

## Methodology

### Phase 1: Verification

Run the full test suite:
```bash
# Run all tests
npm test  # or your project's test command

# Verify no warnings in output
# Verify coverage hasn't dropped
```

Check for:
- [ ] All tests pass
- [ ] No new warnings or errors
- [ ] No commented-out code left behind
- [ ] No debug logging left in production code
- [ ] No TODO comments that should be issues

### Phase 2: Code Quality

Review your changes:

```bash
git diff main...HEAD
```

Check each changed file:
- [ ] No unnecessary changes beyond the feature
- [ ] Variable and function names are descriptive
- [ ] Complex logic has comments explaining WHY (not what)
- [ ] Error handling is appropriate
- [ ] No magic numbers - use named constants

### Phase 3: Commit History

Review commits:
```bash
git log main...HEAD --oneline
```

- [ ] Commits tell a coherent story
- [ ] Each commit is atomic (one logical change)
- [ ] Commit messages follow project conventions
- [ ] No "WIP" or "fix fix fix" commits (squash if needed)

If commits need cleanup:
```bash
git rebase -i main
```

### Phase 4: Documentation

Update relevant documentation:
- [ ] README updated if new setup steps required
- [ ] API documentation updated if endpoints changed
- [ ] CHANGELOG entry added (if project uses one)
- [ ] Migration guide if breaking changes

### Phase 5: PR Description

Write a clear PR description:

```markdown
## What
[One paragraph describing what this PR does]

## Why
[One paragraph explaining the motivation]

## How
[Brief technical description of the approach]

## Testing
[How to verify the changes work]

## Screenshots (if UI changes)
```

### Phase 6: Final Checklist

- [ ] Branch is up to date with main (`git rebase main`)
- [ ] No merge conflicts
- [ ] CI pipeline passing
- [ ] PR description written
- [ ] Reviewers assigned
- [ ] Labels added

## Common Issues

**Tests fail after rebase:**
- Run `npm install` first (dependencies may have changed)
- Check if test fixtures need updating

**Conflicts in generated files:**
- Regenerate the file from source, don't manually merge

**Old code left in comments:**
- Delete it. Git history preserves it if needed.

## Anti-Patterns

- Merging without running the full test suite
- PR descriptions that just repeat the commit message
- Leaving debug code "just in case"
- Merging with known failing tests "to fix in follow-up"
- Not updating documentation for API changes
