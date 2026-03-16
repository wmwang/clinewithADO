#!/usr/bin/env python3
"""Grade all skill-manual-writer eval runs against their assertions."""

import json
import os
import re
import time

BASE = "/Users/isosoman/Documents/repo/deepwiki_claude/clinewithADO/Skills/skill-manual-writer-workspace/iteration-1"

EVALS = [
    {
        "eval_id": 0,
        "eval_name": "ado-devops",
        "assertions": [
            {"name": "manual_md_exists", "text": "manual.md file is created in the outputs directory", "check": "file_exists", "target": "manual.md"},
            {"name": "has_ascii_box_diagram", "text": "Output contains ASCII box-drawing characters (┌ ─ ┐ │ └ ┘ etc.)", "check": "content_contains_regex", "pattern": r"[┌─┐│└┘├┤┬┴]"},
            {"name": "all_7_scripts_mentioned", "text": "All 7 ado-devops scripts are referenced (work_items, repos, core, search, setup, ado_client, wiki)", "check": "content_contains_all", "patterns": ["work_items", "repos.py", "core.py", "search.py", "setup.py", "ado_client", "wiki.py"]},
            {"name": "has_flow_arrows", "text": "Output contains flow direction symbols (▼ or →) indicating a flowchart", "check": "content_contains_regex", "pattern": r"[▼→]"},
            {"name": "has_cli_examples", "text": "Output contains real CLI command examples referencing python and scripts/", "check": "content_contains_regex", "pattern": r"python.*scripts"},
            {"name": "has_error_section", "text": "Output contains an error handling or troubleshooting section", "check": "content_contains_any", "patterns": ["錯誤", "Error", "error", "troubleshoot", "問題"]},
        ],
        "timing": {"ado-devops/with_skill": 200.8, "ado-devops/without_skill": 205.6}
    },
    {
        "eval_id": 1,
        "eval_name": "tech-article-writer",
        "assertions": [
            {"name": "manual_md_exists", "text": "manual.md file is created in the outputs directory", "check": "file_exists", "target": "manual.md"},
            {"name": "has_flow_diagram", "text": "Output contains a flowchart or workflow diagram even though the skill has no scripts", "check": "content_contains_regex", "pattern": r"[▼→┌─┐│└┘]"},
            {"name": "has_trigger_examples", "text": "Output includes trigger phrases or keyword examples for when the skill activates", "check": "content_contains_any", "patterns": ["觸發", "trigger", "寫一篇", "科技文章", "AI 教學"]},
            {"name": "no_phantom_scripts", "text": "Output does NOT reference scripts/ directory (this skill has no scripts)", "check": "content_not_contains", "pattern": "scripts/"},
        ],
        "timing": {"tech-article-writer/with_skill": 143.3, "tech-article-writer/without_skill": 96.3}
    },
    {
        "eval_id": 2,
        "eval_name": "gitnexus-exploring",
        "assertions": [
            {"name": "manual_md_exists", "text": "manual.md file is created in the outputs directory", "check": "file_exists", "target": "manual.md"},
            {"name": "gitnexus_tools_mentioned", "text": "Both main GitNexus tools are referenced: gitnexus_query and gitnexus_context", "check": "content_contains_all", "patterns": ["gitnexus_query", "gitnexus_context"]},
            {"name": "workflow_steps_present", "text": "The workflow is represented (mentions gitnexus:// resources or step structure)", "check": "content_contains_any", "patterns": ["gitnexus://", "Step 1", "步驟", "Workflow", "流程"]},
            {"name": "not_over_padded", "text": "The manual is not excessively long (word count < 2000 words)", "check": "max_word_count", "max_words": 2000},
        ],
        "timing": {"gitnexus-exploring/with_skill": 114.9, "gitnexus-exploring/without_skill": 70.6}
    }
]

CONFIGS = ["with_skill", "without_skill"]


def read_output(eval_name, config):
    path = os.path.join(BASE, eval_name, config, "outputs", "manual.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def grade_assertion(assertion, content):
    check = assertion["check"]
    if check == "file_exists":
        passed = content is not None
        evidence = "manual.md found in outputs/" if passed else "manual.md not found in outputs/"
    elif check == "content_contains_regex":
        if content is None:
            return False, "File not found"
        matches = re.findall(assertion["pattern"], content)
        passed = len(matches) > 0
        evidence = f"Found {len(matches)} matches for pattern '{assertion['pattern']}'" if passed else f"No matches found for pattern '{assertion['pattern']}'"
    elif check == "content_contains_all":
        if content is None:
            return False, "File not found"
        missing = [p for p in assertion["patterns"] if p not in content]
        passed = len(missing) == 0
        evidence = "All patterns found" if passed else f"Missing: {missing}"
    elif check == "content_contains_any":
        if content is None:
            return False, "File not found"
        found = [p for p in assertion["patterns"] if p in content]
        passed = len(found) > 0
        evidence = f"Found: {found}" if passed else f"None of {assertion['patterns']} found"
    elif check == "content_not_contains":
        if content is None:
            return False, "File not found"
        found = assertion["pattern"] in content
        passed = not found
        evidence = f"Pattern '{assertion['pattern']}' correctly absent" if passed else f"Pattern '{assertion['pattern']}' found — should not be present"
    elif check == "max_word_count":
        if content is None:
            return False, "File not found"
        wc = len(content.split())
        passed = wc <= assertion["max_words"]
        evidence = f"Word count: {wc} ({'OK' if passed else 'EXCEEDS limit of ' + str(assertion['max_words'])})"
    else:
        return False, f"Unknown check type: {check}"
    return passed, evidence


results = {}

for eval_info in EVALS:
    eval_name = eval_info["eval_name"]
    results[eval_name] = {}
    for config in CONFIGS:
        content = read_output(eval_name, config)
        graded = []
        for a in eval_info["assertions"]:
            passed, evidence = grade_assertion(a, content)
            graded.append({
                "text": a["text"],
                "passed": passed,
                "evidence": evidence
            })
        total = len(graded)
        passed_count = sum(1 for g in graded if g["passed"])
        grading = {
            "expectations": graded,
            "summary": {
                "passed": passed_count,
                "failed": total - passed_count,
                "total": total,
                "pass_rate": round(passed_count / total, 2) if total else 0
            }
        }
        # Save grading.json
        grading_path = os.path.join(BASE, eval_name, config, "grading.json")
        with open(grading_path, "w", encoding="utf-8") as f:
            json.dump(grading, f, indent=2, ensure_ascii=False)
        results[eval_name][config] = grading["summary"]
        print(f"[{eval_name}/{config}] {passed_count}/{total} passed ({grading['summary']['pass_rate']*100:.0f}%)")

print("\n=== Summary ===")
for eval_name, configs in results.items():
    for config, summary in configs.items():
        print(f"  {eval_name}/{config}: {summary['passed']}/{summary['total']} = {summary['pass_rate']*100:.0f}%")
