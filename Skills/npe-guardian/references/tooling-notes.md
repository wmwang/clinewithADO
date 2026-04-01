# Tooling Notes

## Analyzer Positioning

### SpotBugs

SpotBugs is the default and only analyzer targeted by this skill. It usually works on existing Java projects with lower adoption cost and does not require repository-wide nullness annotations. It also emits machine-friendly XML that is easy to parse and review.

Best for:

- legacy repos
- quick PR-oriented scans
- low-friction auto-fix workflows

## Recommended Mode Mapping

- `fast`: SpotBugs

## Merge Guidance

This skill does not merge findings across NullAway or Checker Framework. Instead:

- Treat SpotBugs as the machine-generated entry point.
- Use source inspection to confirm whether the reported path is a real NPE risk.
- Prefer runtime-safe local code fixes over tooling- or policy-driven fixes.

## Skill boundary

This skill is intentionally centered on:

- SpotBugs-based null-safety detection
- source-aware triage
- conservative code fixes that do not rely on annotation campaigns
- verification
- PR preparation

It is not meant to perform a whole-repo nullness migration in one run.
