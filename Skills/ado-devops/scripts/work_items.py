#!/usr/bin/env python3
"""
Azure DevOps work item operations.

Usage:
  python work_items.py get <id>
      Get full details of a work item.

  python work_items.py list [--state STATE] [--type TYPE] [--assignee ASSIGNEE]
                             [--title KEYWORD] [--sprint current] [--top N]
      Query work items with filters. Combine filters as needed.

  python work_items.py create --type TYPE --title TITLE [--assign EMAIL]
                               [--priority 1-4] [--description TEXT]
                               [--field "Field.Name" VALUE]
      Create a new work item.

  python work_items.py mine [--include-closed] [--top N]
      List work items assigned to the authenticated user.

  python work_items.py sprint-items [--sprint current|PATH] [--team TEAM] [--top N]
      List work items in a sprint (uses @CurrentIteration by default).

  python work_items.py update <id> [--state STATE] [--title TITLE]
                               [--assign EMAIL] [--priority 1-4]
                               [--field "Field.Name" VALUE]
      Update one or more fields on a work item.

  python work_items.py comment <id> <text>
      Add a comment to a work item.

  python work_items.py comments <id>
      List recent comments on a work item.

  python work_items.py children <id>
      List all direct child work items under a parent.

  python work_items.py link <id> --parent PARENT_ID
      Link an existing work item to a parent (sets the Hierarchy-Reverse relation).

Environment variables:
  ADO_PAT, ADO_ORG, ADO_PROJECT  (required)
  HTTP_PROXY / HTTPS_PROXY        (optional)
"""

import argparse
import json
import os
import re
import sys

# Allow importing ado_client from the same directory
sys.path.insert(0, os.path.dirname(__file__))
from ado_client import get_client


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|li|tr|h[1-6])>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text.replace("&amp;", "&").replace("&lt;", "<")
                  .replace("&gt;", ">").replace("&nbsp;", " ")
                  .replace("&quot;", '"').replace("&#39;", "'")).strip()


def format_work_item(item):
    f = item.get("fields", {})

    # Extract parent / children from relations (only present when $expand=all)
    parent_id = None
    child_ids = []
    for r in item.get("relations", []) or []:
        rel = r.get("rel", "")
        url = r.get("url", "")
        wi_id = url.rstrip("/").split("/")[-1]
        if not wi_id.isdigit():
            continue
        if rel == "System.LinkTypes.Hierarchy-Reverse":
            parent_id = int(wi_id)
        elif rel == "System.LinkTypes.Hierarchy-Forward":
            child_ids.append(int(wi_id))

    return {
        "id": item["id"],
        "type": f.get("System.WorkItemType", ""),
        "title": f.get("System.Title", ""),
        "state": f.get("System.State", ""),
        "assignee": (f.get("System.AssignedTo") or {}).get("displayName", "Unassigned"),
        "priority": f.get("Microsoft.VSTS.Common.Priority", ""),
        "area": f.get("System.AreaPath", ""),
        "iteration": f.get("System.IterationPath", ""),
        "parent_id": parent_id,
        "child_ids": child_ids,
        "created_by": (f.get("System.CreatedBy") or {}).get("displayName", ""),
        "created_date": f.get("System.CreatedDate", "")[:10] if f.get("System.CreatedDate") else "",
        "changed_date": f.get("System.ChangedDate", "")[:10] if f.get("System.ChangedDate") else "",
        "description": strip_html(f.get("System.Description", "")),
        "tags": f.get("System.Tags", ""),
        "url": item.get("_links", {}).get("html", {}).get("href", ""),
    }


def cmd_get(client, args):
    item = client.get_work_item(args.id)
    print(json.dumps(format_work_item(item), ensure_ascii=False, indent=2))


def cmd_list(client, args):
    project = client.project
    conditions = [f"[System.TeamProject] = '{project}'"]

    if args.type:
        conditions.append(f"[System.WorkItemType] = '{args.type}'")
    if args.state:
        conditions.append(f"[System.State] = '{args.state}'")
    if args.assignee:
        if args.assignee.lower() == "me":
            conditions.append("[System.AssignedTo] = @Me")
        else:
            conditions.append(f"[System.AssignedTo] CONTAINS '{args.assignee}'")
    if args.title:
        conditions.append(f"[System.Title] CONTAINS '{args.title}'")
    if args.sprint:
        if args.sprint.lower() == "current":
            conditions.append("[System.IterationPath] = @CurrentIteration")
        else:
            conditions.append(f"[System.IterationPath] CONTAINS '{args.sprint}'")

    where_clause = " AND ".join(conditions)
    top = args.top or 50
    query = (
        f"SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo] "
        f"FROM WorkItems WHERE {where_clause} "
        f"ORDER BY [System.ChangedDate] DESC"
    )

    result = client.wiql(query)
    ids = [item["id"] for item in result.get("workItems", [])[:top]]
    if not ids:
        print(json.dumps({"count": 0, "items": []}))
        return

    batch = client.get_work_items_batch(ids)
    items = [format_work_item(i) for i in batch.get("value", [])]
    print(json.dumps({"count": len(items), "items": items}, ensure_ascii=False, indent=2))


def cmd_create(client, args):
    ops = [
        {"op": "add", "path": "/fields/System.Title", "value": args.title},
    ]
    if args.assign:
        ops.append({"op": "add", "path": "/fields/System.AssignedTo", "value": args.assign})
    if args.priority:
        ops.append({"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": args.priority})
    if args.description:
        ops.append({"op": "add", "path": "/fields/System.Description", "value": args.description})
    if args.field:
        for i in range(0, len(args.field), 2):
            if i + 1 < len(args.field):
                ops.append({"op": "add", "path": f"/fields/{args.field[i]}", "value": args.field[i + 1]})
    if args.parent:
        parent_url = (
            f"{client.base_url}/{client.project_encoded}/_apis/wit/workitems/{args.parent}"
        )
        ops.append({
            "op": "add",
            "path": "/relations/-",
            "value": {"rel": "System.LinkTypes.Hierarchy-Reverse", "url": parent_url},
        })

    result = client.create_work_item(args.type, ops)
    created = format_work_item(result)
    print(json.dumps({"created": True, "work_item": created}, ensure_ascii=False, indent=2))


def cmd_mine(client, args):
    project = client.project
    conditions = [
        f"[System.TeamProject] = '{project}'",
        "[System.AssignedTo] = @Me",
    ]
    if not args.include_closed:
        conditions.append("[System.State] <> 'Closed'")

    query = (
        f"SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType] "
        f"FROM WorkItems WHERE {' AND '.join(conditions)} "
        f"ORDER BY [System.ChangedDate] DESC"
    )
    result = client.wiql(query)
    ids = [item["id"] for item in result.get("workItems", [])[:args.top]]
    if not ids:
        print(json.dumps({"count": 0, "items": []}))
        return
    batch = client.get_work_items_batch(ids)
    items = [format_work_item(i) for i in batch.get("value", [])]
    print(json.dumps({"count": len(items), "items": items}, ensure_ascii=False, indent=2))


def cmd_sprint_items(client, args):
    project = client.project
    sprint = args.sprint or "current"

    if sprint.lower() == "current":
        iteration_condition = "[System.IterationPath] = @CurrentIteration"
        if args.team:
            iteration_condition = f"[System.IterationPath] = @CurrentIteration('[{project}]\\{args.team}')"
    else:
        iteration_condition = f"[System.IterationPath] UNDER '{sprint}'"

    query = (
        f"SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [System.WorkItemType] "
        f"FROM WorkItems "
        f"WHERE [System.TeamProject] = '{project}' AND {iteration_condition} "
        f"ORDER BY [System.WorkItemType], [System.State]"
    )
    result = client.wiql(query)
    ids = [item["id"] for item in result.get("workItems", [])[:args.top]]
    if not ids:
        print(json.dumps({"count": 0, "sprint": sprint, "items": []}))
        return
    batch = client.get_work_items_batch(ids)
    items = [format_work_item(i) for i in batch.get("value", [])]
    print(json.dumps({"count": len(items), "sprint": sprint, "items": items},
                     ensure_ascii=False, indent=2))


def cmd_update(client, args):
    ops = []

    if args.state:
        ops.append({"op": "add", "path": "/fields/System.State", "value": args.state})
    if args.title:
        ops.append({"op": "add", "path": "/fields/System.Title", "value": args.title})
    if args.assign:
        ops.append({"op": "add", "path": "/fields/System.AssignedTo", "value": args.assign})
    if args.priority:
        ops.append({"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": args.priority})
    # --field "Field.Name" "value" pairs
    if args.field:
        for i in range(0, len(args.field), 2):
            if i + 1 < len(args.field):
                ops.append({"op": "add", "path": f"/fields/{args.field[i]}", "value": args.field[i + 1]})

    if not ops:
        print(json.dumps({"error": "No update fields specified. Use --state, --title, --assign, --priority, or --field"}))
        sys.exit(1)

    result = client.update_work_item(args.id, ops)
    updated = format_work_item(result)
    print(json.dumps({"updated": True, "work_item": updated}, ensure_ascii=False, indent=2))


def cmd_comment(client, args):
    result = client.add_comment(args.id, args.text)
    print(json.dumps({
        "comment_id": result.get("id"),
        "work_item_id": args.id,
        "text": args.text,
        "created_by": (result.get("createdBy") or {}).get("displayName", ""),
    }, ensure_ascii=False, indent=2))


def cmd_children(client, args):
    query = (
        f"SELECT [System.Id], [System.Title], [System.State], "
        f"[System.WorkItemType], [System.AssignedTo] "
        f"FROM WorkItems WHERE [System.Parent] = {args.id} "
        f"ORDER BY [System.WorkItemType], [System.State]"
    )
    result = client.wiql(query)
    ids = [item["id"] for item in result.get("workItems", [])]
    if not ids:
        print(json.dumps({"count": 0, "parent_id": args.id, "children": []}))
        return
    batch = client.get_work_items_batch(ids)
    items = [format_work_item(i) for i in batch.get("value", [])]
    print(json.dumps({"count": len(items), "parent_id": args.id, "children": items},
                     ensure_ascii=False, indent=2))


def cmd_link(client, args):
    result = client.add_relation(
        item_id=args.id,
        rel_type="System.LinkTypes.Hierarchy-Reverse",
        target_id=args.parent,
    )
    updated = format_work_item(result)
    print(json.dumps({"linked": True, "work_item": updated}, ensure_ascii=False, indent=2))


def cmd_comments(client, args):
    result = client.get_comments(args.id)
    comments = []
    for c in result.get("comments", []):
        comments.append({
            "id": c.get("id"),
            "text": strip_html(c.get("text", "")),
            "created_by": (c.get("createdBy") or {}).get("displayName", ""),
            "created_date": (c.get("createdDate", "")[:10] if c.get("createdDate") else ""),
        })
    print(json.dumps({"count": len(comments), "comments": comments}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Azure DevOps work item operations")
    sub = parser.add_subparsers(dest="command", required=True)

    # get
    p_get = sub.add_parser("get", help="Get work item details")
    p_get.add_argument("id", type=int, help="Work item ID")

    # list
    p_list = sub.add_parser("list", help="Query work items")
    p_list.add_argument("--state", help='e.g. "Active", "To Do", "Done"')
    p_list.add_argument("--type", help='e.g. "Bug", "Task", "User Story"')
    p_list.add_argument("--assignee", help='Email, display name, or "me"')
    p_list.add_argument("--title", help="Keyword to search in title")
    p_list.add_argument("--sprint", help='Sprint path or "current"')
    p_list.add_argument("--top", type=int, default=50, help="Max results (default 50)")

    # update
    p_update = sub.add_parser("update", help="Update work item fields")
    p_update.add_argument("id", type=int, help="Work item ID")
    p_update.add_argument("--state", help="New state value")
    p_update.add_argument("--title", help="New title")
    p_update.add_argument("--assign", help="Assign to (email or display name)")
    p_update.add_argument("--priority", type=int, choices=[1, 2, 3, 4], help="Priority (1=highest)")
    p_update.add_argument("--field", nargs="+", metavar="NAME_OR_VALUE",
                          help='Custom field pairs: --field "Field.Name" "value"')

    # create
    p_create = sub.add_parser("create", help="Create a new work item")
    p_create.add_argument("--type", required=True, help='Work item type, e.g. "Bug", "Task", "User Story"')
    p_create.add_argument("--title", required=True, help="Title of the new work item")
    p_create.add_argument("--assign", help="Assign to (email or display name)")
    p_create.add_argument("--priority", type=int, choices=[1, 2, 3, 4], help="Priority (1=highest)")
    p_create.add_argument("--description", help="Description (plain text or HTML)")
    p_create.add_argument("--field", nargs="+", metavar="NAME_OR_VALUE",
                          help='Extra field pairs: --field "Field.Name" "value"')
    p_create.add_argument("--parent", type=int, metavar="ID",
                          help="Parent work item ID — links this new item as a child")

    # mine
    p_mine = sub.add_parser("mine", help="List work items assigned to me")
    p_mine.add_argument("--include-closed", action="store_true", help="Include Closed items")
    p_mine.add_argument("--top", type=int, default=50, help="Max results (default 50)")

    # sprint-items
    p_sprint = sub.add_parser("sprint-items", help="List work items in a sprint")
    p_sprint.add_argument("--sprint", help='Sprint path or "current" (default: current)', default="current")
    p_sprint.add_argument("--team", help="Team name (for @CurrentIteration scoping)")
    p_sprint.add_argument("--top", type=int, default=100, help="Max results (default 100)")

    # comment
    p_comment = sub.add_parser("comment", help="Add a comment")
    p_comment.add_argument("id", type=int, help="Work item ID")
    p_comment.add_argument("text", help="Comment text (plain text or HTML)")

    # comments
    p_comments = sub.add_parser("comments", help="List comments on a work item")
    p_comments.add_argument("id", type=int, help="Work item ID")

    # children
    p_children = sub.add_parser("children", help="List direct child work items")
    p_children.add_argument("id", type=int, help="Parent work item ID")

    # link
    p_link = sub.add_parser("link", help="Link a work item to a parent")
    p_link.add_argument("id", type=int, help="Work item ID to link")
    p_link.add_argument("--parent", type=int, required=True, metavar="ID",
                        help="Parent work item ID")

    args = parser.parse_args()
    client = get_client()

    try:
        if args.command == "get":
            cmd_get(client, args)
        elif args.command == "list":
            cmd_list(client, args)
        elif args.command == "create":
            cmd_create(client, args)
        elif args.command == "mine":
            cmd_mine(client, args)
        elif args.command == "sprint-items":
            cmd_sprint_items(client, args)
        elif args.command == "update":
            cmd_update(client, args)
        elif args.command == "comment":
            cmd_comment(client, args)
        elif args.command == "comments":
            cmd_comments(client, args)
        elif args.command == "children":
            cmd_children(client, args)
        elif args.command == "link":
            cmd_link(client, args)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
