#!/usr/bin/env python3
"""
Azure DevOps full-text search (Search API).

Note: The Search API uses a different hostname (almsearch.dev.azure.com),
but authentication is the same — use the same PAT.

Usage:
  python search.py code <KEYWORD> [--repo REPO_NAME] [--branch BRANCH]
                                   [--path PATH_PREFIX] [--top N] [--skip N]
      Full-text search across file contents in all repositories.

  python search.py workitem <KEYWORD> [--type TYPE] [--state STATE]
                                       [--assignee EMAIL] [--area AREA_PATH]
                                       [--top N] [--skip N]
      Full-text search across work item titles, descriptions, and comments.

  python search.py wiki <KEYWORD> [--wiki WIKI_ID] [--top N] [--skip N]
      Full-text search across wiki page contents.

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


def fmt_code_result(r):
    file_info = r.get("path", "")
    repo = (r.get("repository") or {}).get("name", "")
    branch = ""
    versions = r.get("versions", [])
    if versions:
        branch = versions[0].get("branchName", "")

    # Collect matching snippets
    snippets = []
    for match in (r.get("matches") or {}).get("content", []):
        for fragment in match.get("charOffset", []):
            pass  # charOffset based — not readable; use contentId instead
    # Use the hits array if available
    content_hits = (r.get("matches") or {}).get("content", [])
    snippet_lines = []
    for hit in content_hits[:3]:
        line = hit.get("line", "")
        if line:
            snippet_lines.append(line.strip())

    return {
        "repo": repo,
        "branch": branch,
        "path": file_info,
        "snippets": snippet_lines,
    }


def fmt_workitem_result(r):
    fields = r.get("fields", {})
    return {
        "id": fields.get("system.id", ""),
        "type": fields.get("system.workitemtype", ""),
        "title": fields.get("system.title", ""),
        "state": fields.get("system.state", ""),
        "assignee": fields.get("system.assignedto", ""),
        "area": fields.get("system.areapath", ""),
        "url": r.get("url", ""),
    }


def fmt_wiki_result(r):
    return {
        "wiki": (r.get("wiki") or {}).get("name", ""),
        "path": r.get("path", ""),
        "collection": (r.get("collection") or {}).get("name", ""),
        "hits": [h.get("content", "")[:200] for h in (r.get("hits") or [])[:2]],
    }


def cmd_code(client, args):
    result = client.search_code(
        text=args.text,
        repo=args.repo,
        branch=args.branch,
        path=args.path,
        top=args.top,
        skip=args.skip,
    )
    count = result.get("count", 0)
    results = [fmt_code_result(r) for r in result.get("results", [])]
    print(json.dumps({
        "total": count,
        "returned": len(results),
        "query": args.text,
        "results": results,
    }, ensure_ascii=False, indent=2))


def cmd_workitem(client, args):
    result = client.search_workitem(
        text=args.text,
        work_item_type=args.type,
        state=args.state,
        assignee=args.assignee,
        area_path=args.area,
        top=args.top,
        skip=args.skip,
    )
    count = result.get("count", 0)
    results = [fmt_workitem_result(r) for r in result.get("results", [])]
    print(json.dumps({
        "total": count,
        "returned": len(results),
        "query": args.text,
        "results": results,
    }, ensure_ascii=False, indent=2))


def cmd_wiki(client, args):
    result = client.search_wiki(
        text=args.text,
        wiki=args.wiki,
        top=args.top,
        skip=args.skip,
    )
    count = result.get("count", 0)
    results = [fmt_wiki_result(r) for r in result.get("results", [])]
    print(json.dumps({
        "total": count,
        "returned": len(results),
        "query": args.text,
        "results": results,
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Azure DevOps Search")
    sub = parser.add_subparsers(dest="command", required=True)

    # code
    p_code = sub.add_parser("code", help="Search code across repositories")
    p_code.add_argument("text", help="Search text")
    p_code.add_argument("--repo", help="Filter by repository name")
    p_code.add_argument("--branch", help="Filter by branch name")
    p_code.add_argument("--path", help="Filter by file path prefix, e.g. /src")
    p_code.add_argument("--top", type=int, default=25, help="Max results (default 25)")
    p_code.add_argument("--skip", type=int, default=0, help="Skip N results (for pagination)")

    # workitem
    p_wi = sub.add_parser("workitem", help="Search work items by text")
    p_wi.add_argument("text", help="Search text")
    p_wi.add_argument("--type", help='Filter by type, e.g. "Bug", "Task"')
    p_wi.add_argument("--state", help='Filter by state, e.g. "Active"')
    p_wi.add_argument("--assignee", help="Filter by assignee email or display name")
    p_wi.add_argument("--area", help="Filter by area path")
    p_wi.add_argument("--top", type=int, default=25, help="Max results (default 25)")
    p_wi.add_argument("--skip", type=int, default=0, help="Skip N results (for pagination)")

    # wiki
    p_wiki = sub.add_parser("wiki", help="Search wiki pages")
    p_wiki.add_argument("text", help="Search text")
    p_wiki.add_argument("--wiki", help="Filter by wiki identifier or name")
    p_wiki.add_argument("--top", type=int, default=25, help="Max results (default 25)")
    p_wiki.add_argument("--skip", type=int, default=0, help="Skip N results (for pagination)")

    args = parser.parse_args()
    client = get_client()

    try:
        if args.command == "code":
            cmd_code(client, args)
        elif args.command == "workitem":
            cmd_workitem(client, args)
        elif args.command == "wiki":
            cmd_wiki(client, args)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
