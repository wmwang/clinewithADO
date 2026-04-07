#!/usr/bin/env python3
"""
Post AI code review comments to an Azure DevOps PR.

Reads a JSON review plan from a file and posts each selected comment as an
inline thread (file + line) or a general PR-level thread (summary).

Usage:
  python pr_comment.py <repo> <pr_id> --from-file /tmp/review.json

JSON schema for the review file:
  {
    "summary": "Overall PR review summary (posted as a general PR comment)",
    "comments": [
      {
        "id": 1,
        "severity": "BLOCKER",        // BLOCKER | MAJOR | MINOR | SUGGESTION
        "file": "/src/.../Foo.java",  // null for PR-level comments
        "line": 45,                   // null for PR-level comments
        "message": "Issue description and suggestion"
      }
    ]
  }

  Pass --ids 1 3 5 to post only specific comment IDs.
  Pass --min-severity MAJOR to post only BLOCKER and MAJOR findings.
  Omit both to post all comments.

Environment variables:
  ADO_PAT, ADO_ORG, ADO_PROJECT  (required)
  HTTP_PROXY / HTTPS_PROXY        (optional)
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ado_client import get_client

SEVERITY_RANK = {"BLOCKER": 4, "MAJOR": 3, "MINOR": 2, "SUGGESTION": 1}

SEVERITY_PREFIX = {
    "BLOCKER":    "🔴 **[BLOCKER]**",
    "MAJOR":      "🟠 **[MAJOR]**",
    "MINOR":      "🟡 **[MINOR]**",
    "SUGGESTION": "💡 **[SUGGESTION]**",
}

REVIEW_FOOTER = "\n\n---\n*由 AI Code Review 自動建立*"


def build_comment_body(severity, message):
    prefix = SEVERITY_PREFIX.get(severity, f"**[{severity}]**")
    return f"{prefix}\n\n{message}{REVIEW_FOOTER}"


def build_summary_body(summary_text, stats):
    lines = ["## 📋 AI Code Review 總結\n"]
    lines.append(summary_text)
    lines.append("\n\n---\n**發現問題統計：**\n")
    for sev in ("BLOCKER", "MAJOR", "MINOR", "SUGGESTION"):
        count = stats.get(sev, 0)
        icon = SEVERITY_PREFIX[sev].split(" ")[0]
        lines.append(f"- {icon} {sev}: {count} 項\n")
    lines.append(REVIEW_FOOTER)
    return "".join(lines)


def post_comments(client, repo, pr_id, review_data, selected_ids=None, min_severity=None):
    comments = review_data.get("comments", [])
    summary  = review_data.get("summary", "")

    # Filter by ID whitelist
    if selected_ids:
        comments = [c for c in comments if c["id"] in selected_ids]

    # Filter by minimum severity rank
    if min_severity:
        min_rank = SEVERITY_RANK.get(min_severity.upper(), 0)
        comments = [c for c in comments if SEVERITY_RANK.get(c["severity"].upper(), 0) >= min_rank]

    posted = []
    errors = []

    # Post inline / file-level comments
    for c in comments:
        body     = build_comment_body(c["severity"], c["message"])
        file_path = c.get("file")
        line      = c.get("line")
        try:
            client.create_pr_thread(repo, pr_id, body,
                                    file_path=file_path, line=line)
            posted.append({
                "id":       c["id"],
                "severity": c["severity"],
                "file":     file_path,
                "line":     line,
                "status":   "posted",
            })
        except Exception as e:
            errors.append({
                "id":    c["id"],
                "error": str(e),
            })

    # Post summary comment if summary text is present
    summary_status = None
    if summary:
        stats = {}
        for c in review_data.get("comments", []):
            sev = c.get("severity", "SUGGESTION")
            stats[sev] = stats.get(sev, 0) + 1
        summary_body = build_summary_body(summary, stats)
        try:
            client.create_pr_thread(repo, pr_id, summary_body)
            summary_status = "posted"
        except Exception as e:
            summary_status = f"error: {e}"

    return {
        "posted_count":   len(posted),
        "error_count":    len(errors),
        "summary_status": summary_status,
        "posted":         posted,
        "errors":         errors,
    }


def main():
    parser = argparse.ArgumentParser(description="Post AI review comments to ADO PR")
    parser.add_argument("repo",   help="Repository name")
    parser.add_argument("pr_id",  type=int, help="Pull request ID")
    parser.add_argument("--from-file", required=True, metavar="PATH",
                        help="Path to review JSON file")
    parser.add_argument("--ids", nargs="+", type=int, metavar="ID",
                        help="Post only specific comment IDs")
    parser.add_argument("--min-severity", metavar="SEVERITY",
                        choices=["SUGGESTION", "MINOR", "MAJOR", "BLOCKER"],
                        help="Post only findings at or above this severity")
    args = parser.parse_args()

    if not os.path.exists(args.from_file):
        print(json.dumps({"error": f"File not found: {args.from_file}"}))
        sys.exit(1)

    with open(args.from_file, encoding="utf-8") as f:
        review_data = json.load(f)

    client = get_client()
    result = post_comments(
        client, args.repo, args.pr_id, review_data,
        selected_ids=args.ids,
        min_severity=args.min_severity,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
