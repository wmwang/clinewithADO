# Root Cause Tracing Skill

## Purpose

Trace bugs to their true origin rather than fixing symptoms. Prevents bug recurrence by ensuring fixes address the actual problem.

## Core Principle

Every bug has a root cause. A bug without a traced root cause will recur in a different form.

## When to Use

Announce: "I'm using the Root Cause Tracing skill."

Use when:
- A bug keeps coming back in different forms
- A fix creates new bugs
- The bug seems to move when you fix it
- Multiple related bugs appear around the same time

## The 5 Whys Technique

Ask "why?" five times, following the chain back:

**Example:**
1. Bug: User's cart is empty on checkout
2. Why? → Session data is lost between pages
3. Why? → Session cookie isn't being sent
4. Why? → Cookie domain doesn't match subdomain
5. Why? → Cookie was set on `api.example.com` but read on `www.example.com`
6. **Root Cause:** Cookie domain configuration error

**Rule:** Don't stop at the first "why." The first answer is usually a symptom.

## Tracing Methodology

### Step 1: Identify the Symptom

Precisely define what's going wrong:
- What is the observed behavior?
- What is the expected behavior?
- When does it occur? (always? sometimes? under specific conditions?)

### Step 2: Find the Failure Point

Locate exactly where the system diverges from expected behavior:

Add logging or debugging to narrow down:
```
- Is the data correct at point A?
- Is it correct at point B?
- Something between A and B is wrong
```

Binary search through the code: divide the code in half, check which half has the problem, repeat.

### Step 3: Trace Upstream

Once you find the failure point, ask: what creates the bad data or state that reaches this point?

Trace backwards through:
- Function call chains
- Data transformations
- State changes
- External inputs (API calls, user input, file reads)

### Step 4: Find the Origin

The root cause is the earliest point where the problem is introduced. Ask:
- Where did the bad data come from?
- What decision or assumption caused this?
- Is this a code bug, a data bug, or a specification bug?

### Step 5: Verify the Root Cause

Before fixing, verify your root cause hypothesis:
- Can you consistently reproduce the bug by manipulating the root cause?
- Does removing the root cause prevent the bug?

## Root Cause Categories

**Code bugs:** Logic errors, off-by-one errors, type mismatches
- Fix: Correct the code

**Data bugs:** Invalid or unexpected data entering the system
- Fix: Validate at data entry point + handle in code

**Integration bugs:** Incorrect assumptions about how systems interact
- Fix: Update the integration + add contract tests

**Specification bugs:** The spec was wrong or ambiguous
- Fix: Update both code and specification

**Environment bugs:** Configuration, dependencies, timing
- Fix: Document the required environment + add checks

## Documentation

After finding root cause, document:
```
Root Cause: [One sentence]
Why it happened: [Brief explanation]
Why it went undetected: [Brief explanation]
Fix: [What was changed]
Prevention: [What prevents recurrence]
```

## Anti-Patterns

- Fixing the symptom without asking why it exists
- Stopping at the first cause found
- Assuming the most recent change caused the bug
- Not verifying the root cause hypothesis before fixing
- Fixing the same bug multiple times in different places (find the common root)
