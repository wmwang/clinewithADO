#!/usr/bin/env python3
"""
Azure DevOps repository operations.

Usage:
  python repos.py list
      List all repositories in the project.

  python repos.py prs <repo> [--status active|all|completed|abandoned] [--top N]
      List pull requests for a repository.

  python repos.py pr <repo> <pr_id>
      Get details of a specific pull request.

  python repos.py create-pr <repo> --source BRANCH --target BRANCH --title TITLE
                             [--description TEXT] [--draft] [--work-items ID [ID ...]]
      Create a new pull request.

  python repos.py branches <repo> [--filter PREFIX]
      List branches (optionally filter by prefix, e.g. "feature/").

  python repos.py create-branch <repo> --name NEW_BRANCH --from SOURCE_BRANCH
      Create a new branch from an existing branch.

  python repos.py update-pr <repo> <pr_id> [--title TITLE] [--description TEXT]
                              [--status active|abandoned|completed] [--draft] [--undraft]
      Update PR properties.

  python repos.py threads <repo> <pr_id>
      List all comment threads on a PR.

  python repos.py comment-pr <repo> <pr_id> <content> [--file PATH] [--line N]
      Create a new comment thread on a PR (optionally on a specific file/line).

  python repos.py reply <repo> <pr_id> <thread_id> <content>
      Reply to an existing PR thread.

  python repos.py resolve-thread <repo> <pr_id> <thread_id>
      Mark a PR thread as resolved (fixed).

  python repos.py ls <repo> [--path PATH] [--branch BRANCH] [--recursive]
      List files and directories in a repository path.

  python repos.py commits <repo> [--branch BRANCH] [--top N]
      List recent commits (default top 20).

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


def fmt_repo(r):
    return {
        "id": r.get("id", ""),
        "name": r.get("name", ""),
        "default_branch": r.get("defaultBranch", "").replace("refs/heads/", ""),
        "size_kb": r.get("size", 0),
        "url": r.get("remoteUrl", ""),
        "web_url": r.get("_links", {}).get("web", {}).get("href", ""),
    }


def fmt_pr(pr):
    reviewers = [
        {"name": rv.get("displayName", ""), "vote": rv.get("vote", 0)}
        for rv in pr.get("reviewers", [])
    ]
    return {
        "id": pr.get("pullRequestId"),
        "title": pr.get("title", ""),
        "status": pr.get("status", ""),
        "source_branch": pr.get("sourceRefName", "").replace("refs/heads/", ""),
        "target_branch": pr.get("targetRefName", "").replace("refs/heads/", ""),
        "created_by": (pr.get("createdBy") or {}).get("displayName", ""),
        "creation_date": (pr.get("creationDate", "")[:10] if pr.get("creationDate") else ""),
        "reviewers": reviewers,
        "merge_status": pr.get("mergeStatus", ""),
        "description": pr.get("description", ""),
    }


def fmt_branch(ref):
    name = ref.get("name", "").replace("refs/heads/", "")
    creator = (ref.get("creator") or {}).get("displayName", "")
    return {
        "name": name,
        "commit": ref.get("objectId", "")[:8],
        "creator": creator,
    }


def fmt_commit(c):
    return {
        "id": c.get("commitId", "")[:8],
        "full_id": c.get("commitId", ""),
        "author": (c.get("author") or {}).get("name", ""),
        "date": (c.get("author") or {}).get("date", "")[:10],
        "message": (c.get("comment") or "").split("\n")[0],
        "url": c.get("url", ""),
    }


def cmd_list(client, args):
    result = client.list_repos()
    repos = [fmt_repo(r) for r in result.get("value", [])]
    print(json.dumps({"count": len(repos), "repos": repos}, ensure_ascii=False, indent=2))


def cmd_prs(client, args):
    result = client.list_prs(args.repo, status=args.status, top=args.top)
    prs = [fmt_pr(pr) for pr in result.get("value", [])]
    print(json.dumps({"count": len(prs), "repo": args.repo, "status": args.status, "prs": prs},
                     ensure_ascii=False, indent=2))


def cmd_pr(client, args):
    result = client.get_pr(args.repo, args.pr_id)
    print(json.dumps(fmt_pr(result), ensure_ascii=False, indent=2))


def cmd_create_pr(client, args):
    result = client.create_pr(
        repo=args.repo,
        source_branch=args.source,
        target_branch=args.target,
        title=args.title,
        description=args.description or "",
        work_item_ids=args.work_items,
        is_draft=args.draft,
    )
    pr = fmt_pr(result)
    pr["url"] = (
        f"https://dev.azure.com/{client.org}/{client.project}"
        f"/_git/{args.repo}/pullrequest/{pr['id']}"
    )
    print(json.dumps({"created": True, "pr": pr}, ensure_ascii=False, indent=2))


def cmd_create_branch(client, args):
    result = client.create_branch(args.repo, args.name, args.from_branch)
    # result is a list of ref update results
    updates = result if isinstance(result, list) else result.get("value", [result])
    success = all(u.get("success", True) for u in updates)
    print(json.dumps({
        "created": success,
        "repo": args.repo,
        "branch": args.name,
        "from": args.from_branch,
        "updates": updates,
    }, ensure_ascii=False, indent=2))


def cmd_update_pr(client, args):
    result = client.update_pr(
        repo=args.repo,
        pr_id=args.pr_id,
        title=args.title,
        description=args.description,
        status=args.status,
        target_branch=args.target,
        is_draft=True if args.draft else (False if args.undraft else None),
    )
    print(json.dumps({"updated": True, "pr": fmt_pr(result)}, ensure_ascii=False, indent=2))


def fmt_thread(t):
    comments = []
    for c in t.get("comments", []):
        if c.get("commentType") == 256:  # system comment, skip
            continue
        comments.append({
            "id": c.get("id"),
            "author": (c.get("author") or {}).get("displayName", ""),
            "content": c.get("content", ""),
            "date": (c.get("publishedDate", "")[:10] if c.get("publishedDate") else ""),
        })
    ctx = t.get("threadContext") or {}
    return {
        "thread_id": t.get("id"),
        "status": t.get("status", ""),
        "file": ctx.get("filePath", ""),
        "line": (ctx.get("rightFileStart") or {}).get("line", ""),
        "comments": comments,
    }


def cmd_threads(client, args):
    result = client.list_pr_threads(args.repo, args.pr_id)
    threads = [fmt_thread(t) for t in result.get("value", [])
               if t.get("comments")]  # skip empty system threads
    print(json.dumps({"count": len(threads), "threads": threads}, ensure_ascii=False, indent=2))


def cmd_comment_pr(client, args):
    result = client.create_pr_thread(
        repo=args.repo,
        pr_id=args.pr_id,
        content=args.content,
        file_path=args.file,
        line=args.line,
    )
    print(json.dumps({"created": True, "thread": fmt_thread(result)}, ensure_ascii=False, indent=2))


def cmd_reply(client, args):
    result = client.reply_to_thread(args.repo, args.pr_id, args.thread_id, args.content)
    print(json.dumps({
        "replied": True,
        "comment_id": result.get("id"),
        "author": (result.get("author") or {}).get("displayName", ""),
        "content": result.get("content", ""),
    }, ensure_ascii=False, indent=2))


def cmd_resolve_thread(client, args):
    result = client.update_pr_thread_status(args.repo, args.pr_id, args.thread_id, "fixed")
    print(json.dumps({"resolved": True, "thread_id": args.thread_id,
                      "status": result.get("status", "")}, ensure_ascii=False, indent=2))


def cmd_ls(client, args):
    result = client.list_directory(
        repo=args.repo,
        path=args.path or "/",
        branch=args.branch or "",
        recursive=args.recursive,
    )
    items = []
    for item in result.get("value", []):
        items.append({
            "path": item.get("path", ""),
            "type": "tree" if item.get("isFolder") else "blob",
            "size": item.get("size", 0) if not item.get("isFolder") else None,
            "commit": (item.get("commitId") or "")[:8],
        })
    print(json.dumps({"count": len(items), "repo": args.repo,
                      "path": args.path or "/", "items": items},
                     ensure_ascii=False, indent=2))


def cmd_branches(client, args):
    result = client.list_branches(args.repo, filter_prefix=args.filter or "")
    branches = [fmt_branch(r) for r in result.get("value", [])]
    print(json.dumps({"count": len(branches), "repo": args.repo, "branches": branches},
                     ensure_ascii=False, indent=2))


def cmd_commits(client, args):
    result = client.list_commits(args.repo, branch=args.branch or "", top=args.top)
    commits = [fmt_commit(c) for c in result.get("value", [])]
    print(json.dumps({"count": len(commits), "repo": args.repo, "commits": commits},
                     ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Azure DevOps repository operations")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List all repositories")

    # prs
    p_prs = sub.add_parser("prs", help="List pull requests")
    p_prs.add_argument("repo", help="Repository name or ID")
    p_prs.add_argument("--status", default="active",
                       choices=["active", "all", "completed", "abandoned"],
                       help="PR status filter (default: active)")
    p_prs.add_argument("--top", type=int, default=50, help="Max results (default 50)")

    # pr (single)
    p_pr = sub.add_parser("pr", help="Get a specific pull request")
    p_pr.add_argument("repo", help="Repository name or ID")
    p_pr.add_argument("pr_id", type=int, help="Pull request ID")

    # create-pr
    p_cpr = sub.add_parser("create-pr", help="Create a pull request")
    p_cpr.add_argument("repo", help="Repository name or ID")
    p_cpr.add_argument("--source", required=True, help="Source branch name")
    p_cpr.add_argument("--target", required=True, help="Target branch name")
    p_cpr.add_argument("--title", required=True, help="PR title")
    p_cpr.add_argument("--description", help="PR description")
    p_cpr.add_argument("--draft", action="store_true", help="Create as draft PR")
    p_cpr.add_argument("--work-items", type=int, nargs="+", metavar="ID",
                       help="Work item IDs to link to this PR")

    # create-branch
    p_cb = sub.add_parser("create-branch", help="Create a new branch")
    p_cb.add_argument("repo", help="Repository name or ID")
    p_cb.add_argument("--name", required=True, help="New branch name")
    p_cb.add_argument("--from", dest="from_branch", required=True,
                      help="Source branch to branch from")

    # update-pr
    p_upr = sub.add_parser("update-pr", help="Update pull request properties")
    p_upr.add_argument("repo", help="Repository name or ID")
    p_upr.add_argument("pr_id", type=int, help="Pull request ID")
    p_upr.add_argument("--title", help="New PR title")
    p_upr.add_argument("--description", help="New PR description")
    p_upr.add_argument("--status", choices=["active", "abandoned", "completed"],
                       help="New PR status")
    p_upr.add_argument("--target", help="Change target branch")
    p_upr.add_argument("--draft", action="store_true", help="Convert to draft")
    p_upr.add_argument("--undraft", action="store_true", help="Publish draft PR")

    # threads
    p_threads = sub.add_parser("threads", help="List PR comment threads")
    p_threads.add_argument("repo", help="Repository name or ID")
    p_threads.add_argument("pr_id", type=int, help="Pull request ID")

    # comment-pr
    p_cmt = sub.add_parser("comment-pr", help="Add a comment thread to a PR")
    p_cmt.add_argument("repo", help="Repository name or ID")
    p_cmt.add_argument("pr_id", type=int, help="Pull request ID")
    p_cmt.add_argument("content", help="Comment text")
    p_cmt.add_argument("--file", help="File path to comment on (for inline comments)")
    p_cmt.add_argument("--line", type=int, help="Line number for inline comment")

    # reply
    p_reply = sub.add_parser("reply", help="Reply to a PR thread")
    p_reply.add_argument("repo", help="Repository name or ID")
    p_reply.add_argument("pr_id", type=int, help="Pull request ID")
    p_reply.add_argument("thread_id", type=int, help="Thread ID to reply to")
    p_reply.add_argument("content", help="Reply text")

    # resolve-thread
    p_resolve = sub.add_parser("resolve-thread", help="Resolve a PR thread")
    p_resolve.add_argument("repo", help="Repository name or ID")
    p_resolve.add_argument("pr_id", type=int, help="Pull request ID")
    p_resolve.add_argument("thread_id", type=int, help="Thread ID to resolve")

    # ls
    p_ls = sub.add_parser("ls", help="List files in a repository directory")
    p_ls.add_argument("repo", help="Repository name or ID")
    p_ls.add_argument("--path", help="Directory path (default: /)", default="/")
    p_ls.add_argument("--branch", help="Branch name (default: repo default)")
    p_ls.add_argument("--recursive", action="store_true", help="List all files recursively")

    # branches
    p_branches = sub.add_parser("branches", help="List branches")
    p_branches.add_argument("repo", help="Repository name or ID")
    p_branches.add_argument("--filter", help='Filter prefix, e.g. "feature/"', default="")

    # commits
    p_commits = sub.add_parser("commits", help="List recent commits")
    p_commits.add_argument("repo", help="Repository name or ID")
    p_commits.add_argument("--branch", help="Branch name (default: repo default branch)")
    p_commits.add_argument("--top", type=int, default=20, help="Number of commits (default 20)")

    args = parser.parse_args()
    client = get_client()

    try:
        if args.command == "list":
            cmd_list(client, args)
        elif args.command == "prs":
            cmd_prs(client, args)
        elif args.command == "pr":
            cmd_pr(client, args)
        elif args.command == "create-pr":
            cmd_create_pr(client, args)
        elif args.command == "update-pr":
            cmd_update_pr(client, args)
        elif args.command == "threads":
            cmd_threads(client, args)
        elif args.command == "comment-pr":
            cmd_comment_pr(client, args)
        elif args.command == "reply":
            cmd_reply(client, args)
        elif args.command == "resolve-thread":
            cmd_resolve_thread(client, args)
        elif args.command == "ls":
            cmd_ls(client, args)
        elif args.command == "branches":
            cmd_branches(client, args)
        elif args.command == "create-branch":
            cmd_create_branch(client, args)
        elif args.command == "commits":
            cmd_commits(client, args)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
