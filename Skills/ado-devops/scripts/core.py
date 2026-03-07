#!/usr/bin/env python3
"""
Azure DevOps organization / project / team operations (Core API).

Usage:
  python core.py whoami
      Show the authenticated user info. Useful for verifying connection settings.

  python core.py projects
      List all projects in the organization.

  python core.py project [PROJECT_NAME]
      Get details for a project (defaults to ADO_PROJECT env var).

  python core.py teams [--project PROJECT_NAME]
      List all teams in a project.

  python core.py members <TEAM_NAME> [--project PROJECT_NAME]
      List members of a team.

  python core.py sprints [--team TEAM_NAME] [--project PROJECT_NAME] [--current]
      List sprints / iterations for a team.
      Use --current to show only the active sprint.

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


def cmd_whoami(client, args):
    url = f"{client.base_url}/_apis/connectionData"
    result = client.request(url)
    user = result.get("authenticatedUser", {})
    props = user.get("properties", {})

    # Try to extract a readable account name
    def prop_val(key):
        entry = props.get(key, {})
        return entry.get("$value", "")

    print(json.dumps({
        "display_name": user.get("providerDisplayName", ""),
        "account": prop_val("Account"),
        "mail": prop_val("Mail"),
        "id": user.get("id", ""),
        "org": client.org,
        "project": client.project,
    }, ensure_ascii=False, indent=2))


def cmd_projects(client, args):
    url = f"{client.base_url}/_apis/projects?$top=100&api-version=7.1"
    result = client.request(url)
    projects = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "state": p.get("state"),
            "visibility": p.get("visibility"),
            "last_update": (p.get("lastUpdateTime", "")[:10] if p.get("lastUpdateTime") else ""),
        }
        for p in result.get("value", [])
    ]
    print(json.dumps({"count": len(projects), "projects": projects}, ensure_ascii=False, indent=2))


def cmd_project(client, args):
    project = args.project or client.project
    project_enc = urllib.parse.quote(project, safe="")
    url = f"{client.base_url}/_apis/projects/{project_enc}?includeCapabilities=true&api-version=7.1"
    p = client.request(url)
    caps = p.get("capabilities", {})
    process_name = caps.get("processTemplate", {}).get("templateName", "")
    src_ctrl = caps.get("versioncontrol", {}).get("sourceControlType", "")
    print(json.dumps({
        "id": p.get("id"),
        "name": p.get("name"),
        "description": p.get("description", ""),
        "state": p.get("state"),
        "visibility": p.get("visibility"),
        "process_template": process_name,
        "source_control": src_ctrl,
        "default_team": p.get("defaultTeam", {}).get("name", ""),
    }, ensure_ascii=False, indent=2))


def cmd_teams(client, args):
    project = args.project or client.project
    project_enc = urllib.parse.quote(project, safe="")
    url = f"{client.base_url}/_apis/projects/{project_enc}/teams?$top=100&api-version=7.1"
    result = client.request(url)
    teams = [
        {
            "id": t.get("id"),
            "name": t.get("name"),
            "description": t.get("description", ""),
        }
        for t in result.get("value", [])
    ]
    print(json.dumps({"count": len(teams), "project": project, "teams": teams},
                     ensure_ascii=False, indent=2))


def cmd_members(client, args):
    project = args.project or client.project
    project_enc = urllib.parse.quote(project, safe="")
    team_enc = urllib.parse.quote(args.team, safe="")
    url = (
        f"{client.base_url}/_apis/projects/{project_enc}/teams/{team_enc}/members"
        f"?api-version=7.1"
    )
    result = client.request(url)
    members = [
        {
            "display_name": m.get("identity", {}).get("displayName", ""),
            "unique_name": m.get("identity", {}).get("uniqueName", ""),
            "id": m.get("identity", {}).get("id", ""),
            "is_team_admin": m.get("isTeamAdmin", False),
        }
        for m in result.get("value", [])
    ]
    print(json.dumps({"count": len(members), "team": args.team, "members": members},
                     ensure_ascii=False, indent=2))


def cmd_sprints(client, args):
    project = args.project or client.project
    project_enc = urllib.parse.quote(project, safe="")

    # If no team specified, try to get the default team name first
    team = args.team
    if not team:
        try:
            p_enc = urllib.parse.quote(project, safe="")
            p_url = f"{client.base_url}/_apis/projects/{p_enc}?api-version=7.1"
            p_data = client.request(p_url)
            team = p_data.get("defaultTeam", {}).get("name", project)
        except Exception:
            team = project  # fallback: ADO often accepts project name as team name

    team_enc = urllib.parse.quote(team, safe="")
    timeframe = "?$timeframe=current" if args.current else ""
    url = (
        f"{client.base_url}/{project_enc}/{team_enc}/_apis/work/teamsettings/iterations"
        f"{timeframe}&api-version=7.1"
    )
    result = client.request(url)

    sprints = []
    for it in result.get("value", []):
        attrs = it.get("attributes", {})
        sprints.append({
            "id": it.get("id"),
            "name": it.get("name"),
            "path": it.get("path"),
            "start_date": (attrs.get("startDate", "") or "")[:10],
            "finish_date": (attrs.get("finishDate", "") or "")[:10],
            "time_frame": attrs.get("timeFrame", ""),  # past / current / future
        })

    print(json.dumps({
        "count": len(sprints),
        "project": project,
        "team": team,
        "sprints": sprints,
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Azure DevOps Core (org/project/team) operations")
    sub = parser.add_subparsers(dest="command", required=True)

    # whoami
    sub.add_parser("whoami", help="Show authenticated user info")

    # projects
    sub.add_parser("projects", help="List all projects in the organization")

    # project
    p_project = sub.add_parser("project", help="Get project details")
    p_project.add_argument("project", nargs="?", help="Project name (default: ADO_PROJECT)")

    # teams
    p_teams = sub.add_parser("teams", help="List teams in a project")
    p_teams.add_argument("--project", help="Project name (default: ADO_PROJECT)")

    # members
    p_members = sub.add_parser("members", help="List team members")
    p_members.add_argument("team", help="Team name")
    p_members.add_argument("--project", help="Project name (default: ADO_PROJECT)")

    # sprints
    p_sprints = sub.add_parser("sprints", help="List sprints / iterations")
    p_sprints.add_argument("--team", help="Team name (default: project default team)")
    p_sprints.add_argument("--project", help="Project name (default: ADO_PROJECT)")
    p_sprints.add_argument("--current", action="store_true", help="Show only the current sprint")

    args = parser.parse_args()
    client = get_client()

    try:
        if args.command == "whoami":
            cmd_whoami(client, args)
        elif args.command == "projects":
            cmd_projects(client, args)
        elif args.command == "project":
            cmd_project(client, args)
        elif args.command == "teams":
            cmd_teams(client, args)
        elif args.command == "members":
            cmd_members(client, args)
        elif args.command == "sprints":
            cmd_sprints(client, args)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
