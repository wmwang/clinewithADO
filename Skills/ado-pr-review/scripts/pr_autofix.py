#!/usr/bin/env python3
"""
Auto-fix support for AI code review: scan for "fix it" replies and push file fixes.

Subcommands:
  scan <repo> <pr_id>
      Scan PR threads for user replies that indicate they want a fix applied.
      Returns a list of fixable threads with their review comment, file, and line.

  push <repo> <branch> --file PATH --content-file FILE [--message MSG] [--new-file]
      Commit a modified file to the given branch via ADO Git Push API.
      Reads new content from --content-file (write your fixed version there first).

  reply <repo> <pr_id> <thread_id> <text>
      Post a reply to a PR thread (e.g. "Fix applied in commit abc1234").

  resolve <repo> <pr_id> <thread_id>
      Mark a PR thread as resolved (fixed).

Environment variables:
  ADO_PAT, ADO_ORG, ADO_PROJECT  (required)
  HTTP_PROXY / HTTPS_PROXY        (optional)
"""

import argparse
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from ado_client import get_client

# Keywords that indicate the user wants the fix applied.
# Case-insensitive substring match.
FIX_KEYWORDS = [
    "fix it", "fix this", "please fix", "apply fix", "apply it",
    "apply the fix", "apply the suggestion", "apply suggestion",
    "go ahead", "lgtm fix", "ok fix", "okay fix", "sounds good",
    "修一下", "幫我修", "修掉", "修正", "套用", "apply",
    "好", "ok", "同意",
]


def _wants_fix(text: str) -> bool:
    """Return True if the comment text is a request to apply the fix."""
    lower = text.lower().strip()
    return any(kw in lower for kw in FIX_KEYWORDS)


# ── scan ─────────────────────────────────────────────────────────────────────

def cmd_scan(args):
    """Find PR threads that have a 'fix it' reply and are not yet resolved."""
    client = get_client()
    result = client.list_pr_threads(args.repo, args.pr_id)
    threads = result.get("value", [])

    fixable = []
    for thread in threads:
        if thread.get("isDeleted"):
            continue

        # Skip already-resolved threads
        if thread.get("status") in ("fixed", "wontFix", "byDesign", "closed"):
            continue

        comments = thread.get("comments", [])
        if len(comments) < 2:
            continue  # No reply yet

        # First comment (parentCommentId == 0) is the original AI review
        original = next((c for c in comments if c.get("parentCommentId") == 0), None)
        if not original:
            continue

        # Look for a "fix it" reply in subsequent comments
        fix_reply = None
        for c in comments[1:]:
            if _wants_fix(c.get("content", "")):
                fix_reply = c
                break

        if not fix_reply:
            continue

        thread_context = thread.get("threadContext") or {}
        file_path = thread_context.get("filePath")
        right_start = thread_context.get("rightFileStart") or {}
        line = right_start.get("line")

        fixable.append({
            "thread_id":      thread["id"],
            "file":           file_path,       # None for PR-level comments
            "line":           line,
            "review_comment": original.get("content", ""),
            "fix_reply":      fix_reply.get("content", ""),
            "fix_reply_by":   (fix_reply.get("author") or {}).get("displayName", ""),
        })

    print(json.dumps({
        "pr_id":           args.pr_id,
        "fixable_count":   len(fixable),
        "fixable_threads": fixable,
    }, ensure_ascii=False, indent=2))


# ── push ─────────────────────────────────────────────────────────────────────

def cmd_push(args):
    """Commit a fixed file to the branch using ADO Git Push API."""
    client = get_client()

    if not os.path.exists(args.content_file):
        print(json.dumps({"error": f"Content file not found: {args.content_file}"}))
        sys.exit(1)

    with open(args.content_file, encoding="utf-8") as f:
        new_content = f.read()

    # Get current HEAD of the branch (needed as oldObjectId)
    try:
        ref = client.get_branch_ref(args.repo, args.branch)
        old_object_id = ref["objectId"]
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    change_type = "add" if args.new_file else "edit"
    commit_message = args.message or (
        f"fix: apply code review suggestion for {os.path.basename(args.file)}"
    )

    repo_enc = urllib.parse.quote(args.repo, safe="")
    body = {
        "refUpdates": [{
            "name":        f"refs/heads/{args.branch}",
            "oldObjectId": old_object_id,
        }],
        "commits": [{
            "comment": commit_message,
            "changes": [{
                "changeType": change_type,
                "item":       {"path": args.file},
                "newContent": {
                    "content":     new_content,
                    "contentType": "rawtext",
                },
            }],
        }],
    }

    url = (
        f"{client.base_url}/{client.project_encoded}/_apis/git/repositories/{repo_enc}"
        f"/pushes?api-version=7.1"
    )
    try:
        result = client.request(url, "POST", body)
        commits = result.get("commits", [])
        commit_id = commits[0].get("commitId", "")[:8] if commits else ""
        print(json.dumps({
            "pushed":         True,
            "branch":         args.branch,
            "file":           args.file,
            "commit_id":      commit_id,
            "commit_message": commit_message,
        }, ensure_ascii=False, indent=2))
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


# ── reply ─────────────────────────────────────────────────────────────────────

def cmd_reply(args):
    client = get_client()
    try:
        client.reply_to_thread(args.repo, args.pr_id, args.thread_id, args.text)
        print(json.dumps({"replied": True, "thread_id": args.thread_id}))
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


# ── resolve ───────────────────────────────────────────────────────────────────

def cmd_resolve(args):
    client = get_client()
    try:
        client.update_pr_thread_status(args.repo, args.pr_id, args.thread_id, "fixed")
        print(json.dumps({"resolved": True, "thread_id": args.thread_id}))
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Auto-fix support for AI code review")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="Find threads with 'fix it' replies")
    p_scan.add_argument("repo")
    p_scan.add_argument("pr_id", type=int)

    p_push = sub.add_parser("push", help="Commit a fixed file to ADO branch")
    p_push.add_argument("repo")
    p_push.add_argument("branch")
    p_push.add_argument("--file",         required=True, metavar="PATH",
                        help="File path in repo (e.g. /src/main/java/com/example/Foo.java)")
    p_push.add_argument("--content-file", required=True, metavar="PATH",
                        help="Local temp file containing the new file content")
    p_push.add_argument("--message",      metavar="MSG",
                        help="Commit message (auto-generated if omitted)")
    p_push.add_argument("--new-file",     action="store_true",
                        help="Use changeType=add (for newly created files)")

    p_reply = sub.add_parser("reply", help="Post a reply to a PR thread")
    p_reply.add_argument("repo")
    p_reply.add_argument("pr_id",     type=int)
    p_reply.add_argument("thread_id", type=int)
    p_reply.add_argument("text")

    p_resolve = sub.add_parser("resolve", help="Mark a PR thread as resolved")
    p_resolve.add_argument("repo")
    p_resolve.add_argument("pr_id",     type=int)
    p_resolve.add_argument("thread_id", type=int)

    args = parser.parse_args()
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "push":
        cmd_push(args)
    elif args.command == "reply":
        cmd_reply(args)
    elif args.command == "resolve":
        cmd_resolve(args)


if __name__ == "__main__":
    main()
