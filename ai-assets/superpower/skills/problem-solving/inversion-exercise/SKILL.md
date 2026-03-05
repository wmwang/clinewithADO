---
name: superpower-inversion-exercise
description: Solve problems by inverting them: identify what would cause failure, then avoid those paths. Use when stuck on a difficult design decision or architecture choice.
---

# Inversion Exercise Skill

## Purpose

Break through stuck thinking by inverting assumptions. Find solutions by first understanding how to guarantee failure.

## When to Use

Announce: "I'm using the Inversion Exercise skill."

Use when:
- Stuck on a design problem
- Need to identify risks before building
- Current approach feels forced but can't see why
- Need to stress-test a solution

## Core Technique

Instead of asking "how do I make X succeed?", ask "how do I reliably make X fail?"

Then examine the failure conditions - they reveal what you need to prevent or address.

## Methodology

### Step 1: Identify Core Assumptions

List the assumptions in your current approach:
- "Users will have fast connections"
- "The API will respond within 500ms"
- "Users will enter valid data"

### Step 2: Reverse Each Assumption

For each assumption, ask: "what if the opposite is true?"

- "Users have slow, unreliable connections"
- "The API will be slow or unavailable"
- "Users will enter garbage data"

### Step 3: Examine Implications

For each reversal, ask: "what would the system need to handle this?"

**Slow connections →** Lazy loading, progressive enhancement, offline support
**Slow API →** Timeouts, fallbacks, optimistic updates
**Invalid data →** Validation at every boundary, meaningful error messages

### Step 4: Test Valid Inversions

Some inversions reveal that "strategic failure" is actually better:

**Example: Performance**
- Normal assumption: Everything should be fast
- Inversion: What if we made some things deliberately slow?
- Insight: Debouncing, rate limiting, lazy loading - strategic slowness improves UX

Apply inversions that reveal genuinely better approaches.

## Application to Architecture

**When designing a system:**
1. How would I make this system unreliable? → Reveals redundancy requirements
2. How would I make this system insecure? → Reveals security requirements
3. How would I make this impossible to maintain? → Reveals maintainability requirements

## Warning Signs in Your Thinking

Stop and apply inversion when you hear yourself saying:
- "There's only one way to do this"
- "This solution is forced by the requirements"
- "I can't explain why, but this is the right approach"
- "That's just how it's done"

## Example Walkthrough

**Problem:** API endpoint is slow

**Normal approach:** Optimize the endpoint

**Inversion:**
- How would I make this endpoint maximally slow?
  - Add complex database queries
  - Compute expensive operations synchronously
  - Call multiple downstream services serially
  - Hold locks for a long time

**Insights from inversion:**
- Move complex queries to background jobs
- Cache expensive computations
- Parallelize downstream service calls
- Minimize lock duration

**Result:** Better understanding of performance levers than "just optimize it"

## Anti-Patterns

- Inverting without examining implications
- Stopping at one level of inversion (invert the inversions too)
- Using inversion to justify doing nothing ("what if requirements change?")
- Treating all inversions as valid (filter for useful insights)
