# Tooling Notes

## Analyzer Positioning

### SpotBugs

SpotBugs is the best default entry point for this skill because it usually works on existing Java projects with less adoption cost than NullAway or Checker Framework. It also emits machine-friendly XML that is easy to parse and review.

Best for:

- legacy repos
- quick PR-oriented scans
- low-friction auto-fix workflows

### NullAway

NullAway is strongest when a codebase is ready to adopt consistent nullness annotations and Error Prone in the build. It can be a follow-on evolution for teams that want stricter prevention, but it is not the lowest-friction first step for an autonomous repair workflow.

Best for:

- compile-time contract enforcement
- teams already using Error Prone
- prevention-oriented strict mode

### Checker Framework

Checker Framework can provide deeper type-level guarantees, but it typically requires more annotation work and broader developer buy-in. Treat it as a strategic migration tool, not the first-line engine for this skill.

Best for:

- teams that already accept annotation-heavy workflows
- deeper type-level guarantees
- deep mode where accuracy matters more than friction

## Recommended Mode Mapping

- `fast`: SpotBugs
- `strict`: SpotBugs + NullAway
- `deep`: SpotBugs + NullAway + Checker Framework

Prefer escalation only when the repository is already prepared for it.

## Merge Guidance

When multiple analyzers report similar issues:

- Merge by file, line, symbol, and dereference target when possible.
- Treat agreement across tools as confidence amplification, not automatic approval to refactor aggressively.
- Let SpotBugs contribute path-based evidence.
- Let NullAway contribute contract and annotation evidence.
- Let Checker Framework contribute stronger type-system evidence.

If only one tool reports the issue, use source inspection to decide whether that tool is seeing a real bug or a policy mismatch.

## Skill boundary

This skill is intentionally centered on:

- multi-tool null-safety detection
- source-aware triage
- conservative code fixes
- verification
- PR preparation

It is not meant to perform a whole-repo nullness migration in one run.
