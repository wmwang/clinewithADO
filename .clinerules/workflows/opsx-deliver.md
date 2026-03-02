# OPSX: Deliver

Delegation workflow: run propose → apply → archive via Skill tool

This workflow is intentionally thin to avoid duplicate maintenance.

IMPORTANT: workflow files cannot directly "invoke another workflow" by name.
To delegate reliably, this workflow must call skills via the Skill tool:
- `openspec-propose`
- `openspec-apply`
- `openspec-archive`

---

**Input**: Optional argument after `/opsx:deliver`:
- existing change name, OR
- feature/fix description

## Steps

1. **Resolve input once**
   - If input is missing, ask user what they want to build/deliver.
   - Keep the same resolved input for downstream steps.

2. **Delegate to propose (Skill tool)**
   - Use Skill tool to invoke `openspec-propose` with the resolved input.
   - Let that skill own all propose rules and artifact generation behavior.

3. **Delegate to apply (Skill tool)**
   - Use Skill tool to invoke `openspec-apply` for the resolved/created change.
   - Let that skill own all implementation rules, pause conditions, and task updates.

4. **Delegate to archive (Skill tool)**
   - Use Skill tool to invoke `openspec-archive` for the same change.
   - Let that skill own all confirmation gates and sync/archive guardrails.

5. **Summarize**
   - Show high-level status for propose/apply/archive.
   - If paused or blocked in any delegated step, stop and report where/why.

---

## Guardrails

- Do not re-implement logic from propose/apply/archive in this file.
- Use delegated skill behavior as the single source of truth.
- If delegated workflows require user confirmation (especially archive), do not bypass.
- Stop immediately on blocker and ask user how to proceed.
