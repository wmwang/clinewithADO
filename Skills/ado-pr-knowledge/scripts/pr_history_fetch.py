#!/usr/bin/env python3
"""
Fetch completed PR threads from an ADO repo for knowledge extraction.

Reads repo and options from config.json (sibling of SKILL.md), or from CLI overrides.

Usage:
  python pr_history_fetch.py
      Use settings from config.json.

  python pr_history_fetch.py --repo my-repo --max-prs 200
      Override config values from CLI.

  python pr_history_fetch.py --config /path/to/config.json
      Use a different config file.

  python pr_history_fetch.py --batch-size 50 --batch 0
      Fetch only batch 0 (PRs 0–49). Useful for incremental processing.

Output (stdout): JSON with PR metadata and their review threads.

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

# Thread statuses considered "informative" for knowledge extraction
INFORMATIVE_STATUSES = {"active", "fixed", "wontFix", "byDesign", "pending"}

# Skip comments that are pure noise
NOISE_PATTERNS = [
    "lgtm", "+1", "👍", "looks good", "approved", "ship it",
    "ok", "okay", "sure", "thanks", "thank you", "nice",
    "great", "good job", "合併", "approve", "可以",
]


def _is_noise(text: str) -> bool:
    stripped = text.strip().lower()
    # Very short and matches noise pattern exactly
    if len(stripped) <= 15 and any(stripped == p for p in NOISE_PATTERNS):
        return True
    # Essentially empty
    if len(stripped) < 3:
        return True
    return False


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        return {}
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def fetch_pr_list(client, repo: str, max_prs: int) -> list:
    """Fetch all completed PRs (paged)."""
    prs = []
    skip = 0
    page_size = 100

    while len(prs) < max_prs:
        to_fetch = min(page_size, max_prs - len(prs))
        import urllib.parse
        repo_enc = urllib.parse.quote(repo, safe="")
        url = (
            f"{client.base_url}/{client.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/pullrequests"
            f"?searchCriteria.status=completed"
            f"&$top={to_fetch}&$skip={skip}"
            f"&api-version=7.1"
        )
        result = client.request(url)
        page = result.get("value", [])
        if not page:
            break
        prs.extend(page)
        skip += len(page)
        if len(page) < to_fetch:
            break  # No more pages

    return prs


def fetch_threads_for_pr(client, repo: str, pr_id: int,
                          include_wont_fix: bool) -> list:
    """Return informative threads for a PR, filtering noise."""
    result = client.list_pr_threads(repo, pr_id)
    threads = result.get("value", [])

    informative = []
    for t in threads:
        if t.get("isDeleted"):
            continue

        status = t.get("status", "unknown")

        # Skip purely system-generated threads
        if status == "unknown":
            continue

        # Optionally skip wontFix
        if not include_wont_fix and status == "wontFix":
            continue

        comments = t.get("comments", [])
        # Get the first real comment (the review comment itself)
        first = next((c for c in comments
                      if c.get("parentCommentId") == 0
                      and not c.get("isDeleted")), None)
        if not first:
            continue

        content = first.get("content", "").strip()
        if _is_noise(content):
            continue

        thread_context = t.get("threadContext") or {}
        informative.append({
            "thread_id":  t["id"],
            "status":     status,          # fixed | wontFix | byDesign | active
            "file":       thread_context.get("filePath"),
            "line":       (thread_context.get("rightFileStart") or {}).get("line"),
            "comment":    content,
            "reply_count": len([c for c in comments if c.get("parentCommentId", 0) > 0]),
        })

    return informative


def fmt_pr(pr: dict) -> dict:
    return {
        "id":            pr.get("pullRequestId"),
        "title":         pr.get("title", ""),
        "created_by":    (pr.get("createdBy") or {}).get("displayName", ""),
        "creation_date": (pr.get("creationDate", "")[:10] if pr.get("creationDate") else ""),
        "close_date":    (pr.get("closedDate", "")[:10] if pr.get("closedDate") else ""),
        "source_branch": pr.get("sourceRefName", "").replace("refs/heads/", ""),
        "target_branch": pr.get("targetRefName", "").replace("refs/heads/", ""),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fetch PR review threads for knowledge extraction"
    )
    # Config file — default is config.json next to SKILL.md (one level up from scripts/)
    default_config = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.json"
    )
    parser.add_argument("--config",     default=default_config, metavar="PATH",
                        help=f"Config file path (default: {default_config})")
    parser.add_argument("--repo",       metavar="REPO",
                        help="Override config: repo name")
    parser.add_argument("--max-prs",    type=int, metavar="N",
                        help="Override config: max PRs to fetch")
    parser.add_argument("--batch-size", type=int, default=50,
                        help="PRs per batch output (default: 50)")
    parser.add_argument("--batch",      type=int, default=None,
                        help="Output only this batch index (0-based). Omit for all.")
    parser.add_argument("--no-threads", action="store_true",
                        help="Only list PR metadata without fetching threads (fast overview)")
    args = parser.parse_args()

    config = load_config(args.config)

    repo            = args.repo or config.get("repo", "")
    max_prs         = args.max_prs or config.get("max_prs", 800)
    include_wont_fix = config.get("include_wont_fix", True)

    if not repo:
        print(json.dumps({"error": "repo not specified. Set in config.json or --repo"}))
        sys.exit(1)

    client = get_client()

    sys.stderr.write(f"Fetching up to {max_prs} completed PRs from repo '{repo}'...\n")
    pr_list = fetch_pr_list(client, repo, max_prs)
    sys.stderr.write(f"Found {len(pr_list)} PRs.\n")

    if args.no_threads:
        print(json.dumps({
            "repo":    repo,
            "pr_count": len(pr_list),
            "prs":     [fmt_pr(p) for p in pr_list],
        }, ensure_ascii=False, indent=2))
        return

    # Determine which batch to output
    batch_size = args.batch_size
    total_batches = (len(pr_list) + batch_size - 1) // batch_size
    batch_indices = [args.batch] if args.batch is not None else list(range(total_batches))

    all_batches = []
    for bi in batch_indices:
        start = bi * batch_size
        end   = min(start + batch_size, len(pr_list))
        batch_prs = pr_list[start:end]

        sys.stderr.write(
            f"Batch {bi}/{total_batches - 1}: fetching threads for PRs {start}–{end - 1}...\n"
        )

        pr_records = []
        for pr in batch_prs:
            pr_id  = pr.get("pullRequestId")
            meta   = fmt_pr(pr)
            threads = fetch_threads_for_pr(client, repo, pr_id, include_wont_fix)
            if threads:  # Only include PRs that have informative threads
                pr_records.append({**meta, "threads": threads})

        all_batches.append({
            "batch":       bi,
            "total_batches": total_batches,
            "repo":        repo,
            "pr_count":    len(pr_records),
            "prs":         pr_records,
        })

    # Output single batch directly, or array if multiple
    if len(all_batches) == 1:
        print(json.dumps(all_batches[0], ensure_ascii=False, indent=2))
    else:
        print(json.dumps(all_batches, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
