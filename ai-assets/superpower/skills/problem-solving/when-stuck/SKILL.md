# When Stuck Skill

## Purpose

Break through mental blocks and find new approaches when progress stalls. Provides structured techniques to escape tunnel vision and find the path forward.

## When to Use

Announce: "I'm using the When Stuck skill."

Use when:
- 2+ attempts at the same approach have failed
- The solution seems to be just around the corner but keeps moving
- Spinning on a problem without making progress
- The code is getting more complex with each attempt

## Core Insight

When stuck, you're usually stuck on a **wrong assumption**. The techniques below help identify and escape that assumption.

## Technique 1: Restate the Problem

Stop working. State the problem in plain language as if explaining to someone with no context:

- "I'm trying to make X happen"
- "The current behavior is Y"
- "I've tried Z and it didn't work because..."
- "The constraint I'm working within is..."

Often, restating the problem reveals the misunderstanding.

## Technique 2: Question Your Assumptions

List every assumption you're making:

- "I assumed the API returns X format"
- "I assumed the library handles Y automatically"
- "I assumed the error is on the client side"

Then question each one. Which assumption could be wrong?

## Technique 3: Inversion

Flip the problem. Instead of "how do I make X work?", ask "how would I reliably make X fail?"

This often reveals:
- Edge cases you haven't considered
- Dependencies you haven't accounted for
- The real root cause of the issue

## Technique 4: Simplify Aggressively

Strip the problem to its minimal reproducible form:

1. Can you reproduce the issue in isolation (no framework, no database)?
2. What's the smallest code change that makes the problem appear/disappear?
3. Does the problem exist in a fresh project?

The minimal case often makes the root cause obvious.

## Technique 5: Check the Basics

Before complex debugging:
- Is the right file being loaded?
- Are environment variables set correctly?
- Is the correct version of the dependency installed?
- Is there a cache that needs clearing?
- Are you looking at the right environment (staging vs production)?

## Technique 6: Fresh Eyes

Stop for 5 minutes. Then read the error message again as if you've never seen it.

- Read it literally, word by word
- What is it actually saying? Not what you expect it to say?

## Technique 7: Ask for Help

When to involve the human:
- After 3+ failed attempts
- When you can't form a hypothesis about root cause
- When you've exhausted all techniques above

How to ask effectively:
1. What you're trying to accomplish
2. What you've tried and what happened
3. What you think might be wrong (even if uncertain)
4. The relevant code and error message

## Red Flags - Stop Immediately

- Making changes without knowing why they might help
- Adding more complexity to fix a complexity problem
- "Let me try this and see what happens"
- Copy-pasting Stack Overflow answers without understanding them

**If you're doing any of these: stop, use Technique 1, then continue.**

## Anti-Patterns

- Continuing to try variations of the same wrong approach
- Assuming the problem is in the last thing you changed
- Debugging by adding more code instead of removing code
- Not reading the full error message
- Skipping the "simplify aggressively" step because "that's not the problem"
