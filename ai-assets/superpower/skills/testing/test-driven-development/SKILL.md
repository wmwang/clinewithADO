# Test-Driven Development Skill

## Purpose

Write tests first, watch them fail, then write minimal code to make them pass. TDD prevents over-engineering, ensures testability, and creates a safety net for refactoring.

## Core Rule

**No production code without a corresponding failing test first.**

No exceptions without explicit permission from your human partner.

## When to Use

Announce: "I'm using the Test-Driven Development skill."

Use for:
- All new features
- All bug fixes
- All refactors

## The Red-Green-Refactor Cycle

### RED - Write a Failing Test

Write the test for functionality that doesn't exist yet.

```
test('describes the behavior clearly', async () => {
  // Arrange: set up the scenario
  // Act: trigger the behavior
  // Assert: verify the outcome
});
```

**Verify it fails:** Run the test. Watch it fail. Confirm it fails for the right reason (missing feature, not a typo).

If the test passes immediately: you're testing the wrong thing or the feature already exists.

### GREEN - Write Minimal Code

Write the minimum code needed to make the test pass.

- Don't add features not tested
- Don't add error handling not tested
- Resist the urge to "do it right" before it works

**Verify it passes:** Run the test. It must pass. If it doesn't: debug, don't guess.

### REFACTOR - Clean Up

With tests passing:
- Remove duplication
- Improve naming
- Simplify logic
- Extract well-named functions

**Verify still green:** Run tests after every refactor change.

## Rationalizations to Reject

| Rationalization | Truth |
|----------------|-------|
| "Too simple to test" | Nothing is too simple. Tests document expected behavior. |
| "I'll add tests after" | You won't. After = never. Write them first. |
| "Already manually tested" | Manual tests don't run automatically. They won't catch regressions. |
| "Deleting code is wasteful" | Code written before tests is wrong by definition. Delete it. |
| "TDD will slow me down" | TDD is faster than debugging. Measure it. |
| "This is different because..." | It isn't. Write the test first. |
| "I need to explore first" | Fine. Throw away your exploration. Start with TDD. |
| "Test hard = design unclear" | Listen to the test. Hard to test = hard to use. Simplify. |

## Red Flags - STOP and Start Over

- Code written before test
- Test added after implementation
- Test passes immediately without code changes
- Can't explain why the test failed
- "I'll add tests later"
- Rationalizing "just this once"
- "I already manually tested it"
- "Keep as reference" when asked to delete pre-test code

**All of these mean: Delete the code. Start over with TDD.**

## Bug Fix Protocol

Bugs get tests too:

**RED:**
```typescript
test('rejects empty email', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```

**Verify RED:** Run test. It fails (bug is reproduced).

**GREEN:** Fix the bug.

**Verify GREEN:** Test passes. Regression is prevented forever.

## When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write the wished-for API. Write the assertion first. Ask your human partner. |
| Test too complicated | Your design is too complicated. Simplify the interface. |
| Must mock everything | Code is too coupled. Use dependency injection. |
| Test setup is huge | Extract setup helpers. Still complex? Simplify the design. |

## Verification Checklist

Before marking work complete:

- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for the expected reason (missing feature, not a syntax error)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass
- [ ] No warnings or errors in output
- [ ] Tests use real code paths (mocks only when unavoidable)
- [ ] Edge cases and error paths covered

Can't check all boxes? You skipped TDD. Start over.

## Final Rule

```
Production code ← test exists and failed first
Otherwise ← not TDD
```

No exceptions without your human partner's explicit permission.
