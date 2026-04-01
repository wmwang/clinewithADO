# PR Template

Use this structure for GitHub or Azure DevOps pull requests created by the skill.

## Title

```text
Fix Java null-safety issue in <module-or-area>
```

## Body

```markdown
## Summary
- Fix <count> confirmed null-safety issue(s) in <module>
- Scope: <changed files or package>

## Findings
1. `<file>:<line>` - <short risk summary>
   - Root cause: <why null can reach the dereference>
   - Fix: <guard clause / fail-fast / optional / branch>

## Verification
- SpotBugs: <command and outcome>
- Tests: <command and outcome>
- Manual reasoning: <any remaining assumptions>

## Notes
- Deferred findings: <none or list>
- Behavior changes: <none or describe>
```

## Authoring Rules

- Keep the summary factual and short.
- Separate confirmed fixes from deferred findings.
- State verification commands exactly when they were run.
- If SpotBugs could not be re-run, say why instead of implying a clean report.
