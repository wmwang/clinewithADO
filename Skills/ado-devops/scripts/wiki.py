#!/usr/bin/env python3
"""
Azure DevOps Wiki operations.

Usage:
  python wiki.py list
      List all wikis in the project.

  python wiki.py pages <wiki> [--path PATH] [--recursive]
      List wiki pages. Defaults to root level; use --recursive for full tree.

  python wiki.py get <wiki> <page-path>
      Get the Markdown content of a wiki page.

  python wiki.py create <wiki> <page-path> --content "Markdown text"
                                            [--content-file FILE]
      Create a new wiki page. Use --content-file to read content from a file.

  python wiki.py update <wiki> <page-path> --content "Markdown text"
                                            [--content-file FILE]
      Update (overwrite) an existing wiki page.

  python wiki.py delete <wiki> <page-path>
      Delete a wiki page.

Arguments:
  <wiki>       Wiki identifier — use the wiki name (e.g. "MyProject.wiki")
               or its GUID. Run "list" to see available wikis.
  <page-path>  Page path starting with "/" (e.g. "/Architecture/Overview").
               Spaces are allowed; the script handles URL encoding.

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


# ── Formatters ────────────────────────────────────────────────────────────────

def fmt_wiki(w):
    return {
        "id": w.get("id", ""),
        "name": w.get("name", ""),
        "type": w.get("type", ""),
        "url": w.get("remoteUrl", "") or w.get("url", ""),
        "mapped_path": w.get("mappedPath", ""),
    }


def fmt_page(p, include_content=False):
    result = {
        "id": p.get("id"),
        "path": p.get("path", ""),
        "order": p.get("order"),
        "is_parent_page": p.get("isParentPage", False),
        "url": (p.get("_links") or {}).get("self", {}).get("href", ""),
    }
    if include_content:
        result["content"] = p.get("content", "")
    sub_pages = p.get("subPages") or []
    if sub_pages:
        result["sub_pages"] = [fmt_page(sp, include_content) for sp in sub_pages]
    return result


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_list(client, _args):
    result = client.list_wikis()
    wikis = [fmt_wiki(w) for w in result.get("value", [])]
    print(json.dumps({"count": len(wikis), "wikis": wikis}, ensure_ascii=False, indent=2))


def cmd_pages(client, args):
    result = client.get_wiki_pages(
        wiki_identifier=args.wiki,
        path=args.path or "/",
        recursive=args.recursive,
        include_content=False,
    )
    page = fmt_page(result)
    print(json.dumps(page, ensure_ascii=False, indent=2))


def cmd_get(client, args):
    result = client.get_wiki_page(
        wiki_identifier=args.wiki,
        path=args.page,
        include_content=True,
    )
    output = {
        "path": result.get("path", ""),
        "id": result.get("id"),
        "url": (result.get("_links") or {}).get("self", {}).get("href", ""),
        "content": result.get("content", ""),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def _resolve_content(args):
    """Return the content string from --content or --content-file."""
    if args.content_file:
        with open(args.content_file, encoding="utf-8") as f:
            return f.read()
    if args.content:
        return args.content
    print(json.dumps({"error": "Provide --content or --content-file"}))
    sys.exit(1)


def cmd_create(client, args):
    content = _resolve_content(args)
    result = client.create_wiki_page(
        wiki_identifier=args.wiki,
        path=args.page,
        content=content,
    )
    print(json.dumps({
        "created": True,
        "path": result.get("path", args.page),
        "id": result.get("id"),
    }, ensure_ascii=False, indent=2))


def cmd_update(client, args):
    content = _resolve_content(args)
    result = client.update_wiki_page(
        wiki_identifier=args.wiki,
        path=args.page,
        content=content,
    )
    print(json.dumps({
        "updated": True,
        "path": result.get("path", args.page),
        "id": result.get("id"),
    }, ensure_ascii=False, indent=2))


def cmd_delete(client, args):
    client.delete_wiki_page(wiki_identifier=args.wiki, path=args.page)
    print(json.dumps({"deleted": True, "path": args.page}, ensure_ascii=False, indent=2))


# ── Argument parser ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Azure DevOps Wiki operations")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    sub.add_parser("list", help="List all wikis in the project")

    # pages
    p_pages = sub.add_parser("pages", help="List wiki pages")
    p_pages.add_argument("wiki", help="Wiki name or GUID")
    p_pages.add_argument("--path", default="/", help='Starting path (default "/")')
    p_pages.add_argument("--recursive", action="store_true",
                         help="Recursively list all sub-pages")

    # get
    p_get = sub.add_parser("get", help="Get wiki page content")
    p_get.add_argument("wiki", help="Wiki name or GUID")
    p_get.add_argument("page", help='Page path, e.g. "/Architecture/Overview"')

    # create
    p_create = sub.add_parser("create", help="Create a new wiki page")
    p_create.add_argument("wiki", help="Wiki name or GUID")
    p_create.add_argument("page", help='Page path, e.g. "/Architecture/NewPage"')
    p_create.add_argument("--content", help="Markdown content string")
    p_create.add_argument("--content-file", metavar="FILE",
                          help="Read Markdown content from this file")

    # update
    p_update = sub.add_parser("update", help="Update (overwrite) an existing wiki page")
    p_update.add_argument("wiki", help="Wiki name or GUID")
    p_update.add_argument("page", help='Page path, e.g. "/Architecture/Overview"')
    p_update.add_argument("--content", help="New Markdown content string")
    p_update.add_argument("--content-file", metavar="FILE",
                          help="Read new Markdown content from this file")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a wiki page")
    p_delete.add_argument("wiki", help="Wiki name or GUID")
    p_delete.add_argument("page", help='Page path to delete')

    args = parser.parse_args()
    client = get_client()

    try:
        dispatch = {
            "list": cmd_list,
            "pages": cmd_pages,
            "get": cmd_get,
            "create": cmd_create,
            "update": cmd_update,
            "delete": cmd_delete,
        }
        dispatch[args.command](client, args)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
