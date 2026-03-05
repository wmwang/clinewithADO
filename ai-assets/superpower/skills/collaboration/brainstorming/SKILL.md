# Brainstorming Skill

## Purpose

Structure collaborative problem exploration with the human before writing any code. This skill guides you through understanding the problem, exploring solutions, and creating an actionable plan.

## When to Use

Use this skill when:
- Starting a new feature or project
- Facing an ambiguous problem that needs exploration
- The human wants to think through options before committing to an approach
- A complex refactor needs planning

Announce: "I'm using the Brainstorming skill to explore this problem with you."

## Methodology

### Phase 1: Understanding

Before proposing any solutions, fully understand the problem.

Ask clarifying questions to establish:
- What problem are we solving? (not what solution to build)
- Who are the users? What are their needs?
- What constraints exist? (performance, compatibility, timeline)
- What does success look like?
- What have you already tried?

**Format:** Prefer multiple-choice questions over open-ended ones. Bundle 2-3 questions per message rather than one at a time.

**Rule:** Do not propose solutions in this phase. Understanding comes first.

### Phase 2: Exploration

Present 2-3 distinctly different approaches. Each approach should include:

- **Name:** A short, memorable label
- **Core Idea:** One sentence summary
- **Architecture:** How it works (2-3 sentences)
- **Pros:** Key advantages (3-5 bullet points)
- **Cons/Trade-offs:** Honest limitations (3-5 bullet points)
- **Best For:** When this approach shines

Make approaches genuinely different - don't just vary implementation details. Vary the fundamental architecture.

Apply YAGNI ruthlessly. Don't add "just in case" complexity.

### Phase 3: Design Presentation

Once the human has chosen an approach (or a hybrid), present the design:

- Break into 200-300 word sections
- Include architecture decisions and rationale
- Identify key integration points
- Note potential risks
- Propose a testing strategy

Invite feedback after each section. Go backward if needed - flexibility beats rigid progression.

### Phase 4: Worktree Setup (if applicable)

If implementation follows brainstorming:
- Set up an isolated git worktree for the work
- Verify the environment is ready
- Run baseline tests

### Phase 5: Planning Handoff

Create a written plan using the Writing Plans skill:
- Detailed task list
- TDD-first approach
- Clear acceptance criteria

## Core Principles

- **Go backward when needed** - if new information changes the picture, revisit earlier phases
- **Flexibility over rigid progression** - phases are guides, not gates
- **YAGNI** - don't design for hypothetical future requirements
- **Socratic method** - ask questions that surface hidden assumptions
- **Multiple-choice questions** - make it easy for the human to respond

## Anti-Patterns

- Proposing solutions before fully understanding the problem
- Presenting only one approach
- Designing for hypothetical requirements
- Moving to implementation without a plan
- Skipping the understanding phase when the problem seems obvious

## Verification

Before moving to implementation:
- [ ] Problem fully understood
- [ ] Multiple approaches explored
- [ ] Approach chosen by human
- [ ] Design presented and approved
- [ ] Written plan created
