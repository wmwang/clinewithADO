#!/usr/bin/env python3
"""
Fetch PR info and changed file contents for AI code review.

Usage:
  python pr_fetch.py <repo> <pr_id>
      Fetch PR metadata + full content of all reviewable changed files.
      Outputs structured JSON to stdout.

  python pr_fetch.py <repo> <pr_id> --files-only
      List changed files without fetching content (quick overview).

  python pr_fetch.py <repo> <pr_id> --file /src/main/java/Foo.java
      Fetch a single specific file from the PR source branch.

  python pr_fetch.py <repo> <pr_id> --max-lines 800
      Truncate files longer than N lines (default: 1000).

Environment variables:
  ADO_PAT, ADO_ORG, ADO_PROJECT  (required — same as ado-devops skill)
  HTTP_PROXY / HTTPS_PROXY        (optional)
"""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from ado_client import get_client

# File extensions considered reviewable source code
REVIEWABLE_EXTENSIONS = {
    ".java", ".kt", ".groovy",           # JVM source
    ".xml",                               # Spring config, pom.xml
    ".yml", ".yaml",                      # application.yml, docker-compose
    ".properties",                        # application.properties
    ".sql",                               # migrations
    ".json",                              # config / API contracts
}

SEVERITY_ICONS = {
    "BLOCKER": "🔴",
    "MAJOR": "🟠",
    "MINOR": "🟡",
    "SUGGESTION": "💡",
}


# ── ADO API helpers ───────────────────────────────────────────────────────────

def _build_raw_opener(client):
    """Build a URL opener that uses the same auth + proxy as ADOClient."""
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    handlers = [urllib.request.HTTPSHandler(context=ssl_ctx)]
    if client._proxy:
        handlers.insert(0, urllib.request.ProxyHandler({
            "http": client._proxy, "https": client._proxy,
        }))
    return urllib.request.build_opener(*handlers)


def get_latest_iteration(client, repo, pr_id):
    """Return the latest iteration ID for a PR."""
    repo_enc = urllib.parse.quote(repo, safe="")
    url = (
        f"{client.base_url}/{client.project_encoded}/_apis/git/repositories/{repo_enc}"
        f"/pullrequests/{pr_id}/iterations?api-version=7.1"
    )
    result = client.request(url)
    iterations = result.get("value", [])
    if not iterations:
        raise RuntimeError(f"No iterations found for PR #{pr_id}")
    return max(it["id"] for it in iterations)


def get_changed_files(client, repo, pr_id, iteration_id):
    """Return list of {path, change_type} for blobs changed in a PR iteration."""
    repo_enc = urllib.parse.quote(repo, safe="")
    url = (
        f"{client.base_url}/{client.project_encoded}/_apis/git/repositories/{repo_enc}"
        f"/pullrequests/{pr_id}/iterations/{iteration_id}/changes?api-version=7.1"
    )
    result = client.request(url)
    files = []
    for entry in result.get("changeEntries", []):
        item = entry.get("item", {})
        path = item.get("path", "")
        # gitObjectType may be absent; include anything with a file path (has extension)
        if path and "." in os.path.basename(path):
            files.append({
                "path": path,
                "change_type": entry.get("changeType", "unknown"),
            })
    return files


def fetch_file_content(client, repo, branch, file_path, max_lines=1000):
    """
    Fetch raw text content of a file from a specific branch.
    Returns a line-numbered string, truncated at max_lines.
    """
    repo_enc = urllib.parse.quote(repo, safe="")
    path_enc = urllib.parse.quote(file_path, safe="/")
    branch_enc = urllib.parse.quote(branch, safe="")
    url = (
        f"{client.base_url}/{client.project_encoded}/_apis/git/repositories/{repo_enc}"
        f"/items?path={path_enc}"
        f"&versionDescriptor.version={branch_enc}"
        f"&versionDescriptor.versionType=branch"
        f"&$format=text"
        f"&api-version=7.1"
    )
    opener = _build_raw_opener(client)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {client._token}",
        "Accept": "text/plain",
    })
    try:
        with opener.open(req) as resp:
            content = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}: unable to fetch file content]"
    except Exception as e:
        return f"[Error fetching file: {e}]"

    lines = content.splitlines()
    total_lines = len(lines)
    truncated = total_lines > max_lines
    if truncated:
        lines = lines[:max_lines]

    numbered = "\n".join(f"{i + 1:5d}  {line}" for i, line in enumerate(lines))
    if truncated:
        numbered += f"\n      ... [truncated: showing {max_lines} of {total_lines} lines]"
    return numbered


def is_reviewable(file_path):
    """True if the file extension is in the reviewable set."""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in REVIEWABLE_EXTENSIONS


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch PR data for AI code review")
    parser.add_argument("repo",          help="Repository name")
    parser.add_argument("pr_id",  type=int, help="Pull request ID")
    parser.add_argument("--files-only",  action="store_true",
                        help="List changed files without fetching content")
    parser.add_argument("--file",        metavar="PATH",
                        help="Fetch only a specific file from the PR source branch")
    parser.add_argument("--max-lines",   type=int, default=1000,
                        help="Max lines per file before truncation (default: 1000)")
    args = parser.parse_args()

    client = get_client()

    # ── PR metadata ──────────────────────────────────────────────────────────
    pr_raw = client.get_pr(args.repo, args.pr_id)
    pr_info = {
        "id":            pr_raw.get("pullRequestId"),
        "title":         pr_raw.get("title", ""),
        "description":   pr_raw.get("description", ""),
        "source_branch": pr_raw.get("sourceRefName", "").replace("refs/heads/", ""),
        "target_branch": pr_raw.get("targetRefName", "").replace("refs/heads/", ""),
        "created_by":    (pr_raw.get("createdBy") or {}).get("displayName", ""),
        "status":        pr_raw.get("status", ""),
    }
    source_branch = pr_info["source_branch"]

    # ── Changed files ────────────────────────────────────────────────────────
    iteration_id = get_latest_iteration(client, args.repo, args.pr_id)
    changed_files = get_changed_files(client, args.repo, args.pr_id, iteration_id)

    if args.files_only:
        print(json.dumps({
            "pr":           pr_info,
            "iteration_id": iteration_id,
            "changed_files": changed_files,
        }, ensure_ascii=False, indent=2))
        return

    # ── Fetch file contents ──────────────────────────────────────────────────
    result_files = []
    for f in changed_files:
        path        = f["path"]
        change_type = f["change_type"]  # edit / add / delete / rename

        # Skip deleted files (nothing to review)
        if change_type == "delete":
            result_files.append({
                "path": path, "change_type": change_type,
                "skipped": True, "skip_reason": "deleted",
            })
            continue

        # If a specific file was requested, skip all others
        if args.file and path != args.file:
            continue

        # Skip non-reviewable file types (binaries, lock files, etc.)
        if not is_reviewable(path):
            result_files.append({
                "path": path, "change_type": change_type,
                "skipped": True, "skip_reason": "non-reviewable extension",
            })
            continue

        content = fetch_file_content(client, args.repo, source_branch, path, args.max_lines)
        result_files.append({
            "path":        path,
            "change_type": change_type,
            "skipped":     False,
            "content":     content,
        })

    print(json.dumps({
        "pr":            pr_info,
        "iteration_id":  iteration_id,
        "source_branch": source_branch,
        "files":         result_files,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
