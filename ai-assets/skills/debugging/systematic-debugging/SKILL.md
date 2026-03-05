---
name: superpower-systematic-debugging
description: Debug complex issues using a structured hypothesis-driven approach. Use when facing hard-to-reproduce bugs, performance issues, or complex system failures.
---

# Systematic Debugging Skill

## Purpose

Debug issues methodically by identifying root causes before attempting fixes. Prevents the "random change" debugging trap that wastes hours.

## Core Law

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

A fix without a root cause is a guess. Guesses create new bugs.

## When to Use

Announce: "I'm using the Systematic Debugging skill."

Use when:
- A test is failing
- Something isn't working as expected
- A previous fix didn't work
- You're about to make a third attempt at fixing something

## Methodology

### Phase 1: Root Cause Investigation

**Read the error carefully:**
- Read the full error message - don't skim
- Note the file, line number, and error type
- Understand what the error is literally saying before interpreting it

**Reproduce consistently:**
- Can you make it fail every time?
- What's the minimal case that triggers it?
- What changed recently? (git log, git diff)

**Examine the code:**
- What is the code actually doing vs. what you expect?
- Add logging/debugging to verify assumptions
- Check inputs at every stage

### Phase 2: Pattern Analysis

**Compare against reference:**
- Find a working similar case in the codebase
- Compare working vs. broken line by line
- What's different?

**Identify the gap:**
- What assumption is wrong?
- What invariant is violated?
- Is this a timing issue? A type issue? A missing edge case?

### Phase 3: Hypothesis and Testing

**Form a hypothesis:**
- "I believe the bug is X because Y"
- If you can't complete this sentence, you don't know the root cause

**Test with single variables:**
- Change one thing at a time
- Verify your hypothesis is correct before moving on
- If your fix doesn't work, your hypothesis was wrong - go back to Phase 1

### Phase 4: Implementation

1. Write a failing test that reproduces the bug
2. Implement the minimal fix
3. Verify the test passes
4. Check no other tests broke
5. Review the fix - is it addressing root cause or symptom?

## Red Flags - Return to Phase 1

If you've made 3+ fix attempts without success:
- **Stop.** Your hypothesis is wrong.
- Question the architecture, not just the implementation
- Consider if the problem is upstream from where you're looking
- Ask the human for additional context

Other red flags:
- You're not sure why the fix worked
- The fix feels hacky
- You're adding special cases instead of fixing the core logic

## Results

Applying this skill achieves:
- 15-30 minute resolution (vs 2-3 hours random debugging)
- 95% first-time fix rate
- Fixes that don't create new bugs

## Anti-Patterns

- Trying a fix before understanding the root cause
- Making multiple changes simultaneously
- Hoping a change will work without knowing why
- Continuing to guess after 3+ failures
- Fixing symptoms instead of root causes
