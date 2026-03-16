# ado-devops Skill — Comprehensive Manual

> A Claude Code skill for interacting with Azure DevOps via natural language. No SDK or az CLI required — pure Python stdlib.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Component Reference](#component-reference)
4. [Setup and Configuration](#setup-and-configuration)
5. [Work Items](#work-items)
6. [Repository Operations](#repository-operations)
7. [Wiki Operations](#wiki-operations)
8. [Full-Text Search](#full-text-search)
9. [Core / Org Operations](#core--org-operations)
10. [Error Reference](#error-reference)
11. [Developer Guide](#developer-guide)
12. [Quick-Reference Cheat Sheet](#quick-reference-cheat-sheet)

---

## Overview

`ado-devops` is a Claude Code skill that wraps the Azure DevOps REST API (API version 7.1) into a set of Python CLI scripts. Every script is self-contained and relies only on the Python standard library (`urllib`, `json`, `ssl`, `argparse`). No `pip install` is needed.

### Key capabilities

| Domain | Operations |
|--------|-----------|
| Work Items | get, list, create, update, mine, sprint-items, comment, comments, children, link |
| Repositories | list, ls, branches, create-branch, commits, prs, pr, create-pr, update-pr |
| PR Review | threads, comment-pr, reply, resolve-thread |
| Wiki | list, pages, get, create, update, delete |
| Search | code, workitem, wiki |
| Core | whoami, projects, project, teams, members, sprints |
| Setup | status, save, clear |

### Design principles

- **Zero dependencies** — only Python standard library modules
- **Cross-platform** — Windows (`python`), macOS/Linux (`python3`)
- **Enterprise-ready** — built-in SSL bypass (`verify=False`), HTTP/HTTPS proxy support with both uppercase and lowercase env-var variants
- **Credential persistence** — credentials written once to `~/.ado-devops.env` (permissions `600` on Unix); no need to re-enter each session
- **JSON output** — every command outputs valid JSON for easy parsing or display

---

## Architecture

### Component diagram

```
  User / Claude Agent
         |
         | natural language request
         v
  +------+------+
  |  SKILL.md   |  <-- skill definition, triggers, setup flow
  +------+------+
         |
         | invokes CLI scripts
         v
  +------------------------------------------------------------+
  |                   scripts/                                 |
  |                                                            |
  |  setup.py      work_items.py   repos.py                    |
  |  (config mgr)  (WIT ops)       (Git ops)                   |
  |                                                            |
  |  core.py       search.py       wiki.py                     |
  |  (org/proj)    (full-text)     (wiki CRUD)                 |
  |                                                            |
  |  +-------------------------------------------------+       |
  |  |              ado_client.py                      |       |
  |  |  ADOClient — shared HTTP, auth, proxy, SSL      |       |
  |  +-------------------------------------------------+       |
  +------------------------------------------------------------+
         |
         | HTTPS (Basic auth via PAT)
         v
  +--------------------+     +-----------------------------+
  | dev.azure.com      |     | almsearch.dev.azure.com     |
  | (ADO REST API v7.1)|     | (Search API — code/WI/wiki) |
  +--------------------+     +-----------------------------+
```

### Credential resolution order

```
  1. Environment variables (ADO_PAT, ADO_ORG, ADO_PROJECT, HTTP_PROXY ...)
         |
         | if any var is missing
         v
  2. ~/.ado-devops.env config file
         |
         | if still missing
         v
  3. Error — exit with JSON {"error": "Missing credentials: ..."}
```

### Request lifecycle

```
  Script entry point
       |
       v
  get_client()                    [ado_client.py]
   - load ~/.ado-devops.env
   - merge with env vars
   - validate PAT / ORG / PROJECT
   - return ADOClient instance
       |
       v
  ADOClient.__init__()
   - build base64 PAT header
   - create ssl.SSLContext (check_hostname=False, CERT_NONE)
   - if proxy: add ProxyHandler
   - build urllib opener
       |
       v
  ADOClient.request(url, method, data)
   - set Authorization / Content-Type / Accept headers
   - encode body as JSON
   - open request via custom opener
   - decode response and return parsed JSON
   - on HTTPError: raise RuntimeError("HTTP <code> ...")
       |
       v
  Script formats result as JSON
       |
       v
  print() to stdout
```

---

## Component Reference

### `ado_client.py` — Shared HTTP client

The foundation module used by every other script. Instantiated via `get_client()`.

**Class: `ADOClient`**

| Method | Description |
|--------|-------------|
| `__init__(pat, org, project, proxy)` | Initialises auth token, SSL context, optional proxy handler |
| `request(url, method, data, content_type, extra_headers)` | Executes an HTTP request and returns parsed JSON |
| `wiql(query_str)` | Executes a WIQL query against the project |
| `get_work_item(id, expand)` | Fetches a single work item with `$expand=all` by default |
| `get_work_items_batch(ids)` | Fetches up to 200 work items by ID list |
| `update_work_item(id, operations)` | PATCH using JSON Patch operations |
| `add_comment(id, text)` | Posts a discussion comment on a work item |
| `get_comments(id)` | Lists discussion comments on a work item |
| `create_work_item(type, operations)` | POST to create a new work item |
| `add_relation(id, rel_type, target_id)` | Adds a hierarchy link to a work item |
| `list_repos()` | Lists all repos in the project |
| `get_repo(repo)` | Gets metadata for a single repo |
| `list_prs(repo, status, top)` | Lists pull requests by status |
| `get_pr(repo, pr_id)` | Gets details of a single PR |
| `list_branches(repo, filter_prefix)` | Lists branches, optionally filtered |
| `list_commits(repo, branch, top)` | Lists recent commits |
| `create_pr(...)` | Creates a pull request |
| `create_branch(repo, new_branch, source_branch)` | Creates a branch from another branch's HEAD |
| `update_pr(...)` | Updates PR fields (title, description, status, draft) |
| `list_pr_threads(repo, pr_id)` | Lists all comment threads on a PR |
| `create_pr_thread(...)` | Creates a new PR comment thread (optionally inline) |
| `reply_to_thread(repo, pr_id, thread_id, content)` | Replies to an existing thread |
| `update_pr_thread_status(...)` | Marks a thread status (active / fixed / closed / etc.) |
| `list_directory(repo, path, branch, recursive)` | Lists files/dirs in a repo path |
| `search_code(text, ...)` | Calls `almsearch.dev.azure.com` code search |
| `search_workitem(text, ...)` | Calls work item full-text search |
| `search_wiki(text, ...)` | Calls wiki full-text search |
| `list_wikis()` | Lists all wikis in the project |
| `get_wiki_pages(wiki, path, recursive)` | Lists wiki pages |
| `get_wiki_page(wiki, path, include_content)` | Reads a single wiki page |
| `create_wiki_page(wiki, path, content)` | Creates a new wiki page (PUT without If-Match) |
| `update_wiki_page(wiki, path, content)` | Updates a wiki page (PUT with `If-Match: *`) |
| `delete_wiki_page(wiki, path)` | Deletes a wiki page |

**Proxy resolution (in priority order)**

```
os.environ["HTTP_PROXY"]   or   os.environ["http_proxy"]
os.environ["HTTPS_PROXY"]  or   os.environ["https_proxy"]
file_config["HTTP_PROXY"]
file_config["HTTPS_PROXY"]
```

---

### `setup.py` — Credential manager

Manages the `~/.ado-devops.env` config file.

**Subcommands**

| Command | Description |
|---------|-------------|
| `status` | Outputs JSON showing current values, sources (env / file / missing), proxy status, and a `ready` boolean |
| `save [--org] [--project] [--pat] [--proxy] [--clear-proxy]` | Writes specified values to config file, sets Unix permissions to `600` |
| `clear` | Removes the config file entirely |

**`status` output fields**

```json
{
  "platform": "Darwin",
  "python": "3.12.0",
  "config_file": "/home/user/.ado-devops.env",
  "config_file_exists": true,
  "defaults": { "ADO_ORG": "tsmcit", "ADO_PROJECT": "AI Operation Center" },
  "values": {
    "ADO_ORG":     { "value": "myorg",    "source": "file" },
    "ADO_PROJECT": { "value": "MyProject","source": "file" },
    "ADO_PAT":     { "value": "***",      "source": "file", "is_set": true }
  },
  "proxy": {
    "HTTP_PROXY":  { "value": "",  "source": "missing" },
    "HTTPS_PROXY": { "value": "",  "source": "missing" },
    "effective":   null,
    "source":      "missing"
  },
  "ready": true
}
```

---

### `work_items.py` — Work item operations

Covers the full lifecycle of ADO work items.

**Subcommands summary**

| Subcommand | Required args | Key options |
|------------|--------------|-------------|
| `get` | `<id>` | — |
| `list` | — | `--state`, `--type`, `--assignee`, `--title`, `--sprint`, `--top` |
| `create` | `--type`, `--title` | `--assign`, `--priority`, `--description`, `--field`, `--parent` |
| `mine` | — | `--include-closed`, `--top` |
| `sprint-items` | — | `--sprint`, `--team`, `--top` |
| `update` | `<id>` | `--state`, `--title`, `--assign`, `--priority`, `--field` |
| `comment` | `<id>`, `<text>` | — |
| `comments` | `<id>` | — |
| `children` | `<id>` | — |
| `link` | `<id>`, `--parent` | — |

**Work item hierarchy link types (internal)**

| Relation type | Meaning |
|---------------|---------|
| `System.LinkTypes.Hierarchy-Reverse` | Child → Parent (set parent of this item) |
| `System.LinkTypes.Hierarchy-Forward` | Parent → Child (this item has a child) |

**`get` output fields**

```json
{
  "id": 123,
  "type": "Bug",
  "title": "Login page 500 error",
  "state": "Active",
  "assignee": "Jane Doe",
  "priority": 1,
  "area": "MyProject\\Backend",
  "iteration": "MyProject\\Sprint 5",
  "parent_id": 100,
  "child_ids": [201, 202],
  "created_by": "John Smith",
  "created_date": "2025-03-01",
  "changed_date": "2025-03-14",
  "description": "Steps to reproduce...",
  "tags": "hotfix;urgent",
  "url": "https://dev.azure.com/org/project/_workitems/edit/123"
}
```

---

### `repos.py` — Repository and PR operations

**Subcommands summary**

| Subcommand | Required args | Key options |
|------------|--------------|-------------|
| `list` | — | — |
| `ls` | `<repo>` | `--path`, `--branch`, `--recursive` |
| `branches` | `<repo>` | `--filter` |
| `create-branch` | `<repo>`, `--name`, `--from` | — |
| `commits` | `<repo>` | `--branch`, `--top` |
| `prs` | `<repo>` | `--status`, `--top` |
| `pr` | `<repo>`, `<pr_id>` | — |
| `create-pr` | `<repo>`, `--source`, `--target`, `--title` | `--description`, `--draft`, `--work-items` |
| `update-pr` | `<repo>`, `<pr_id>` | `--title`, `--description`, `--status`, `--target`, `--draft`, `--undraft` |
| `threads` | `<repo>`, `<pr_id>` | — |
| `comment-pr` | `<repo>`, `<pr_id>`, `<content>` | `--file`, `--line` |
| `reply` | `<repo>`, `<pr_id>`, `<thread_id>`, `<content>` | — |
| `resolve-thread` | `<repo>`, `<pr_id>`, `<thread_id>` | — |

**PR status values**

| Value | Meaning |
|-------|---------|
| `active` | Open and active (default filter) |
| `completed` | Merged |
| `abandoned` | Closed without merging |
| `all` | All statuses |

**`create-branch` internals (2-step process)**

```
Step 1: GET refs?filter=heads/<source_branch>
        => retrieve source branch objectId (commit SHA)

Step 2: POST refs
        body: [{
          "name": "refs/heads/<new_branch>",
          "oldObjectId": "0000000000000000000000000000000000000000",
          "newObjectId": "<source_commit_id>"
        }]
```

---

### `wiki.py` — Wiki CRUD operations

**Subcommands summary**

| Subcommand | Required args | Key options |
|------------|--------------|-------------|
| `list` | — | — |
| `pages` | `<wiki>` | `--path`, `--recursive` |
| `get` | `<wiki>`, `<page-path>` | — |
| `create` | `<wiki>`, `<page-path>` | `--content`, `--content-file` |
| `update` | `<wiki>`, `<page-path>` | `--content`, `--content-file` |
| `delete` | `<wiki>`, `<page-path>` | — |

**Wiki identifier**

Use the wiki `name` field (e.g. `MyProject.wiki`) returned by `list`, or the GUID. The script URL-encodes both.

**create vs update difference**

| Operation | HTTP method | If-Match header | Behaviour |
|-----------|-------------|-----------------|-----------|
| `create` | PUT | absent | Creates a new page; HTTP 409 if page already exists |
| `update` | PUT | `*` | Force-overwrites any existing page without needing ETag |

---

### `search.py` — Full-text search

> Uses hostname `almsearch.dev.azure.com` (different from the main API). The same PAT is used for authentication.

**Subcommands**

| Subcommand | Required args | Key options |
|------------|--------------|-------------|
| `code` | `<text>` | `--repo`, `--branch`, `--path`, `--top`, `--skip` |
| `workitem` | `<text>` | `--type`, `--state`, `--assignee`, `--area`, `--top`, `--skip` |
| `wiki` | `<text>` | `--wiki`, `--top`, `--skip` |

**Pagination**

All search subcommands support `--top N` (page size) and `--skip N` (offset). For example, to get the second page of 25:

```bash
python3 "$SCRIPT_DIR/search.py" code "TODO" --top 25 --skip 25
```

**search workitem vs work_items.py list**

| Feature | `search.py workitem` | `work_items.py list --title` |
|---------|----------------------|-----------------------------|
| Engine | Azure Search full-text | WIQL query |
| Scope | Title + description + comments | Title only |
| Latency | Slightly higher (indexing lag) | Lower |
| Use case | Broad keyword search | Precise title filter |

---

### `core.py` — Organization / project / team operations

**Subcommands**

| Subcommand | Required args | Key options |
|------------|--------------|-------------|
| `whoami` | — | — |
| `projects` | — | — |
| `project` | optional `<project_name>` | — |
| `teams` | — | `--project` |
| `members` | `<team_name>` | `--project` |
| `sprints` | — | `--team`, `--project`, `--current` |

**`sprints` team resolution**

If `--team` is not specified, the script calls `GET /_apis/projects/<project>` to retrieve the `defaultTeam.name`, then uses that to query iterations.

**`project` output includes**

- `process_template`: Scrum / Agile / CMMI / custom
- `source_control`: Git / TFVC
- `default_team`: default team name

---

## Setup and Configuration

### First-time setup flow

```
  Claude receives user request
          |
          v
  python3 setup.py status
          |
          |--- "ready": true -----> check proxy ----> execute operation
          |
          |--- "ready": false --->  collect missing values:
                                    1. ADO_ORG    (default: tsmcit)
                                    2. ADO_PROJECT (default: AI Operation Center)
                                    3. ADO_PAT    (no default)
                                    4. HTTP_PROXY (optional)
                                    |
                                    v
                                python3 setup.py save \
                                  --org "..." \
                                  --project "..." \
                                  --pat "..." \
                                  [--proxy "http://proxy.corp:8080"]
                                    |
                                    v
                                credentials saved to ~/.ado-devops.env
                                execute user's original operation
```

### PAT required permissions

| Permission | Access level |
|-----------|-------------|
| Work Items | Read & Write |
| Code | Read |
| Wiki | Read & Write |

### Config file location

| Platform | Path |
|----------|------|
| Unix / macOS | `~/.ado-devops.env` |
| Windows | `%USERPROFILE%\.ado-devops.env` |

**File format**

```
# Azure DevOps credentials — auto-generated by ado-devops skill
ADO_ORG=myorg
ADO_PROJECT=MyProject
ADO_PAT=abc123...
HTTP_PROXY=http://proxy.corp:8080
HTTPS_PROXY=http://proxy.corp:8080
```

Unix file permissions are automatically set to `600` (owner read/write only). On Windows this silently no-ops; the OS ACL controls access.

### Script path resolution

The skill's scripts live in the `scripts/` subdirectory alongside `SKILL.md`. When invoking scripts, resolve the absolute path at runtime:

**Unix / macOS**
```bash
SCRIPT_DIR="<absolute path to SKILL.md directory>/scripts"
python3 "$SCRIPT_DIR/work_items.py" get 123
```

**Windows PowerShell**
```powershell
$SCRIPT_DIR = "<absolute path to SKILL.md directory>\scripts"
python "$SCRIPT_DIR\work_items.py" get 123
```

**Detect the right Python command first**

```bash
python -c "import platform, sys; print(platform.system(), sys.version)"
# or
python3 -c "import platform, sys; print(platform.system(), sys.version)"
```

| OS output | Python command | Path separator |
|-----------|---------------|----------------|
| `Windows` | `python` (or `py -3`) | `\` |
| `Linux` / `Darwin` | `python3` | `/` |

---

## Work Items

### Fetch a single work item

```bash
python3 "$SCRIPT_DIR/work_items.py" get 123
```

Returns full detail including description (HTML stripped to plain text), hierarchy relations (`parent_id`, `child_ids`), and a browser URL.

### Query work items

```bash
# All active bugs in the current sprint
python3 "$SCRIPT_DIR/work_items.py" list \
  --sprint current --state "Active" --type "Bug"

# Items assigned to me, not closed
python3 "$SCRIPT_DIR/work_items.py" list --assignee me

# Title contains "payment", any state
python3 "$SCRIPT_DIR/work_items.py" list --title "payment" --top 20
```

Filter flags may be freely combined. All filters map to WIQL `WHERE` clauses.

### My work items

```bash
# Open items assigned to the PAT owner
python3 "$SCRIPT_DIR/work_items.py" mine

# Include closed items
python3 "$SCRIPT_DIR/work_items.py" mine --include-closed
```

### Sprint work items

```bash
# Current sprint (uses @CurrentIteration)
python3 "$SCRIPT_DIR/work_items.py" sprint-items

# Current sprint scoped to a specific team
python3 "$SCRIPT_DIR/work_items.py" sprint-items --team "Backend Team"

# Specific sprint by iteration path
python3 "$SCRIPT_DIR/work_items.py" sprint-items --sprint "MyProject\Sprint 5"
```

### Create a work item

```bash
# Simple bug
python3 "$SCRIPT_DIR/work_items.py" create \
  --type "Bug" --title "Login page 500 error" \
  --assign "dev@company.com" --priority 1 \
  --description "Steps to reproduce..."

# Task under a parent feature (#100)
python3 "$SCRIPT_DIR/work_items.py" create \
  --type "Task" --title "Implement login API" \
  --parent 100
```

Supported `--type` values depend on the project's Process template. Common values: `Bug`, `Task`, `User Story`, `Feature`, `Epic`.

### Update a work item

```bash
# Change state
python3 "$SCRIPT_DIR/work_items.py" update 123 --state "In Progress"

# Reassign and reprioritize
python3 "$SCRIPT_DIR/work_items.py" update 123 \
  --assign "lead@company.com" --priority 1

# Set a custom field
python3 "$SCRIPT_DIR/work_items.py" update 123 \
  --field "System.Tags" "hotfix;urgent"
```

### Comments

```bash
# Add a discussion comment
python3 "$SCRIPT_DIR/work_items.py" comment 123 "Root cause identified: null pointer in auth module"

# Read all discussion comments
python3 "$SCRIPT_DIR/work_items.py" comments 123
```

### Hierarchy / parent-child

```bash
# List all direct children of work item #100
python3 "$SCRIPT_DIR/work_items.py" children 100

# Link existing work item #456 as a child of #100
python3 "$SCRIPT_DIR/work_items.py" link 456 --parent 100
```

### State value reference

| Process template | Common states |
|-----------------|--------------|
| Scrum | New, Active, Resolved, Closed |
| Agile | Active, Resolved, Closed, New |
| CMMI | Proposed, Active, Resolved, Closed |
| Custom | Check Project Settings > Process |

If `--state` triggers HTTP 400, fetch the current state with `get <id>` first to confirm the exact spelling accepted by that project.

---

## Repository Operations

### List repositories

```bash
python3 "$SCRIPT_DIR/repos.py" list
```

### Browse repository contents

```bash
# Root directory (one level)
python3 "$SCRIPT_DIR/repos.py" ls my-repo

# Specific path on a branch
python3 "$SCRIPT_DIR/repos.py" ls my-repo --path "/src" --branch main

# Recursive (all files)
python3 "$SCRIPT_DIR/repos.py" ls my-repo --recursive
```

### Branches

```bash
# All branches
python3 "$SCRIPT_DIR/repos.py" branches my-repo

# Filter by prefix
python3 "$SCRIPT_DIR/repos.py" branches my-repo --filter "feature/"

# Create a new branch
python3 "$SCRIPT_DIR/repos.py" create-branch my-repo \
  --name "feature/new-login" --from main
```

### Commits

```bash
# Last 20 commits (default)
python3 "$SCRIPT_DIR/repos.py" commits my-repo

# Last 50 on a specific branch
python3 "$SCRIPT_DIR/repos.py" commits my-repo --branch develop --top 50
```

### Pull requests

```bash
# List active PRs
python3 "$SCRIPT_DIR/repos.py" prs my-repo

# List all PRs
python3 "$SCRIPT_DIR/repos.py" prs my-repo --status all --top 100

# Get single PR details
python3 "$SCRIPT_DIR/repos.py" pr my-repo 45

# Create a PR
python3 "$SCRIPT_DIR/repos.py" create-pr my-repo \
  --source "feature/new-login" --target main \
  --title "feat: add SSO login" \
  --description "Implements Azure AD SSO" \
  --work-items 123 124

# Create as draft
python3 "$SCRIPT_DIR/repos.py" create-pr my-repo \
  --source "feature/wip" --target main \
  --title "WIP: new feature" --draft

# Update PR title and description
python3 "$SCRIPT_DIR/repos.py" update-pr my-repo 45 \
  --title "fix: corrected login flow" \
  --description "Resolves issue in #123"

# Publish a draft PR
python3 "$SCRIPT_DIR/repos.py" update-pr my-repo 45 --undraft

# Abandon a PR
python3 "$SCRIPT_DIR/repos.py" update-pr my-repo 45 --status abandoned
```

### PR review threads

```bash
# List all threads
python3 "$SCRIPT_DIR/repos.py" threads my-repo 45

# Add a general comment
python3 "$SCRIPT_DIR/repos.py" comment-pr my-repo 45 "LGTM, ready to merge"

# Add an inline comment on a specific file and line
python3 "$SCRIPT_DIR/repos.py" comment-pr my-repo 45 \
  "This should handle None" --file "/src/api.py" --line 42

# Reply to thread ID 3
python3 "$SCRIPT_DIR/repos.py" reply my-repo 45 3 "Fixed in latest commit"

# Mark thread ID 3 as resolved
python3 "$SCRIPT_DIR/repos.py" resolve-thread my-repo 45 3
```

---

## Wiki Operations

### List wikis

```bash
python3 "$SCRIPT_DIR/wiki.py" list
```

Returns each wiki's `name` (use this as `<wiki>` identifier), `type` (`projectWiki` or `codeWiki`), and URL.

### Browse pages

```bash
# Root level (one level)
python3 "$SCRIPT_DIR/wiki.py" pages MyProject.wiki

# Subtree starting at /Architecture
python3 "$SCRIPT_DIR/wiki.py" pages MyProject.wiki --path "/Architecture"

# Full recursive tree
python3 "$SCRIPT_DIR/wiki.py" pages MyProject.wiki --recursive
```

### Read a page

```bash
python3 "$SCRIPT_DIR/wiki.py" get MyProject.wiki "/Architecture/Overview"
```

Output includes `path`, `id`, `url`, and `content` (Markdown source).

### Create a page

```bash
# Inline content
python3 "$SCRIPT_DIR/wiki.py" create MyProject.wiki "/Architecture/NewPage" \
  --content "# New Page\n\nContent here..."

# From a local Markdown file
python3 "$SCRIPT_DIR/wiki.py" create MyProject.wiki "/Architecture/NewPage" \
  --content-file ./page_content.md
```

Returns HTTP 409 if the page already exists — use `update` instead.

### Update a page

```bash
# Full overwrite with inline content
python3 "$SCRIPT_DIR/wiki.py" update MyProject.wiki "/Architecture/Overview" \
  --content "# Updated Title\n\nNew content..."

# Full overwrite from file
python3 "$SCRIPT_DIR/wiki.py" update MyProject.wiki "/Architecture/Overview" \
  --content-file ./updated_content.md
```

The update uses `If-Match: *` so no ETag lookup is needed. The entire page content is replaced.

### Delete a page

```bash
python3 "$SCRIPT_DIR/wiki.py" delete MyProject.wiki "/Architecture/OldPage"
```

> Deletion is irreversible. Always confirm with the user before executing.

---

## Full-Text Search

> The Search API uses a different base URL: `https://almsearch.dev.azure.com/{org}/{project}/_apis/search/`. Authentication uses the same PAT.

### Code search

```bash
# Search all repos
python3 "$SCRIPT_DIR/search.py" code "ConnectionString"

# Scoped to a repo and branch
python3 "$SCRIPT_DIR/search.py" code "ConnectionString" \
  --repo my-repo --branch main

# Scoped to a path prefix
python3 "$SCRIPT_DIR/search.py" code "TODO" --path "/src/api"

# Pagination: second page of 25
python3 "$SCRIPT_DIR/search.py" code "TODO" --top 25 --skip 25
```

### Work item search (full-text)

```bash
# Basic search
python3 "$SCRIPT_DIR/search.py" workitem "login failure"

# With filters
python3 "$SCRIPT_DIR/search.py" workitem "payment" \
  --type "Bug" --state "Active"

python3 "$SCRIPT_DIR/search.py" workitem "timeout" \
  --assignee "dev@company.com"
```

### Wiki search

```bash
# Search all wikis
python3 "$SCRIPT_DIR/search.py" wiki "deployment process"

# Scoped to a specific wiki
python3 "$SCRIPT_DIR/search.py" wiki "API spec" --wiki "my-project.wiki"
```

---

## Core / Org Operations

### Verify connection

```bash
python3 "$SCRIPT_DIR/core.py" whoami
```

Returns `display_name`, `account`, `mail`, `id`, `org`, and `project`. If this returns HTTP 404, use `projects` to verify connectivity instead.

### Projects

```bash
# All projects in the organization
python3 "$SCRIPT_DIR/core.py" projects

# Details for the configured project
python3 "$SCRIPT_DIR/core.py" project

# Details for a different project
python3 "$SCRIPT_DIR/core.py" project "OtherProject"
```

### Teams and members

```bash
# List all teams
python3 "$SCRIPT_DIR/core.py" teams

# Teams in a different project
python3 "$SCRIPT_DIR/core.py" teams --project "OtherProject"

# Members of a specific team
python3 "$SCRIPT_DIR/core.py" members "Backend Team"
```

### Sprints / iterations

```bash
# All sprints for the default team
python3 "$SCRIPT_DIR/core.py" sprints

# Only the current sprint
python3 "$SCRIPT_DIR/core.py" sprints --current

# Sprints for a specific team
python3 "$SCRIPT_DIR/core.py" sprints --team "Backend Team" --current
```

The `time_frame` field in each sprint result is `past`, `current`, or `future`.

---

## Error Reference

| Error / symptom | Cause | Resolution |
|----------------|-------|-----------|
| `"error": "Missing credentials: ADO_PAT"` | Config not set up | Run `setup.py save --pat ...` |
| HTTP 401 | PAT expired or invalid | Generate a new PAT in ADO and run `setup.py save --pat <new>` |
| HTTP 403 | PAT missing required scopes | Regenerate PAT with Work Items (R/W), Code (R), Wiki (R/W) |
| HTTP 404 | Work item ID, repo, or project does not exist | Verify `ADO_PROJECT` and the ID/name |
| HTTP 400 on `update --state` | State value spelling does not match process template | Run `get <id>` to see current state; check project Process settings |
| HTTP 409 on wiki `create` | Page already exists | Use `update` instead of `create` |
| Connection timeout / `ProxyError` | Corporate proxy not configured | Run `setup.py save --proxy http://proxy.corp:8080` |
| SSL / `certificate verify failed` | Corporate self-signed cert | The client bypasses SSL by default; if error persists, verify proxy settings |
| `python3: command not found` | Windows has no `python3` alias | Use `python` or `py -3` |
| `whoami` returns HTTP 404 | Some ADO organizations disable `connectionData` endpoint | Use `core.py projects` to validate connectivity |
| Search returns no results | Index lag (~minutes) or wrong hostname allowed in firewall | Confirm `almsearch.dev.azure.com` is accessible through the corporate proxy |

---

## Developer Guide

### Adding a new script

1. Create `scripts/my_feature.py`.
2. Import the shared client at the top:
   ```python
   import os, sys
   sys.path.insert(0, os.path.dirname(__file__))
   from ado_client import get_client
   ```
3. Add an `argparse` subparser structure with a `main()` entry point.
4. Call `get_client()` inside `main()` after parsing args — this validates credentials and fails fast.
5. Wrap command dispatch in `try/except RuntimeError` and print `{"error": str(e)}` on failure.
6. All output must be valid JSON printed to stdout.

### Adding a new method to `ADOClient`

`ADOClient.request()` is the single HTTP entry point. All new methods should:
- Build the URL using `self.base_url`, `self.project_encoded`, and `urllib.parse.quote()` for any variable segments.
- Call `self.request(url, method, body_dict)`.
- Raise `RuntimeError` on unexpected states (the caller's `except RuntimeError` will catch it).

Example skeleton:

```python
def get_something(self, resource_id):
    resource_enc = urllib.parse.quote(str(resource_id), safe="")
    url = (
        f"{self.base_url}/{self.project_encoded}/_apis/someresource/{resource_enc}"
        f"?api-version=7.1"
    )
    return self.request(url)
```

### Testing credentials locally

```bash
# Check configuration status
python3 scripts/setup.py status

# Verify PAT and connectivity
python3 scripts/core.py whoami

# Quick smoke test: list projects
python3 scripts/core.py projects
```

### Updating the credential file without Claude

```bash
# Save all credentials at once
python3 scripts/setup.py save \
  --org "myorg" \
  --project "MyProject" \
  --pat "abcdef123..." \
  --proxy "http://proxy.corp:8080"

# Update only the PAT
python3 scripts/setup.py save --pat "newtoken..."

# Remove proxy setting
python3 scripts/setup.py save --clear-proxy

# Wipe all saved credentials
python3 scripts/setup.py clear
```

### Understanding WIQL queries

`work_items.py` builds WIQL queries dynamically. The basic form is:

```sql
SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
FROM WorkItems
WHERE [System.TeamProject] = 'MyProject'
  AND [System.WorkItemType] = 'Bug'
  AND [System.State] = 'Active'
  AND [System.AssignedTo] = @Me
ORDER BY [System.ChangedDate] DESC
```

The `@Me` and `@CurrentIteration` macros are resolved server-side based on the authenticated user and the team's current sprint respectively.

### Environment variable override for CI/CD

In CI pipelines, skip the config file entirely by exporting environment variables before running any script:

```bash
export ADO_PAT="$ADO_SERVICE_PAT"
export ADO_ORG="myorg"
export ADO_PROJECT="MyProject"
export HTTPS_PROXY="http://proxy.corp:8080"

python3 scripts/work_items.py list --state "Active" --type "Bug"
```

Environment variables take precedence over the config file, so the file is ignored when all three required vars are set.

### Windows-specific notes

On Windows, use `python` (not `python3`), and use backslashes for paths in shell commands:

```powershell
$SCRIPT_DIR = "C:\Users\me\.cline\skills\ado-devops\scripts"
python "$SCRIPT_DIR\work_items.py" get 123
python "$SCRIPT_DIR\setup.py" status
```

The `~/.ado-devops.env` path expands to `%USERPROFILE%\.ado-devops.env`. The `setup.py save` command handles this via `os.path.expanduser("~/.ado-devops.env")`.

---

## Quick-Reference Cheat Sheet

### Setup

```bash
python3 scripts/setup.py status
python3 scripts/setup.py save --org ORG --project PROJECT --pat PAT [--proxy URL]
python3 scripts/setup.py clear
```

### Work items

```bash
python3 scripts/work_items.py get 123
python3 scripts/work_items.py list [--state S] [--type T] [--assignee me] [--sprint current] [--title KW]
python3 scripts/work_items.py mine [--include-closed]
python3 scripts/work_items.py sprint-items [--team TEAM]
python3 scripts/work_items.py create --type Bug --title "..." [--parent ID] [--priority 1-4]
python3 scripts/work_items.py update 123 [--state S] [--assign EMAIL] [--priority N]
python3 scripts/work_items.py comment 123 "text"
python3 scripts/work_items.py comments 123
python3 scripts/work_items.py children 100
python3 scripts/work_items.py link 456 --parent 100
```

### Repos and PRs

```bash
python3 scripts/repos.py list
python3 scripts/repos.py ls REPO [--path /src] [--branch main] [--recursive]
python3 scripts/repos.py branches REPO [--filter feature/]
python3 scripts/repos.py create-branch REPO --name BRANCH --from main
python3 scripts/repos.py commits REPO [--branch main] [--top 50]
python3 scripts/repos.py prs REPO [--status active|all|completed|abandoned]
python3 scripts/repos.py pr REPO PR_ID
python3 scripts/repos.py create-pr REPO --source SRC --target TGT --title "..." [--draft] [--work-items 123 124]
python3 scripts/repos.py update-pr REPO PR_ID [--title] [--status abandoned] [--draft|--undraft]
python3 scripts/repos.py threads REPO PR_ID
python3 scripts/repos.py comment-pr REPO PR_ID "text" [--file /path.py --line 42]
python3 scripts/repos.py reply REPO PR_ID THREAD_ID "text"
python3 scripts/repos.py resolve-thread REPO PR_ID THREAD_ID
```

### Wiki

```bash
python3 scripts/wiki.py list
python3 scripts/wiki.py pages WIKI [--path /DIR] [--recursive]
python3 scripts/wiki.py get WIKI /PAGE/PATH
python3 scripts/wiki.py create WIKI /PAGE/PATH --content "..." | --content-file FILE
python3 scripts/wiki.py update WIKI /PAGE/PATH --content "..." | --content-file FILE
python3 scripts/wiki.py delete WIKI /PAGE/PATH
```

### Search

```bash
python3 scripts/search.py code "keyword" [--repo REPO] [--branch main] [--path /src]
python3 scripts/search.py workitem "keyword" [--type Bug] [--state Active]
python3 scripts/search.py wiki "keyword" [--wiki MyProject.wiki]
```

### Core

```bash
python3 scripts/core.py whoami
python3 scripts/core.py projects
python3 scripts/core.py project [PROJECT_NAME]
python3 scripts/core.py teams [--project PROJECT]
python3 scripts/core.py members "Team Name"
python3 scripts/core.py sprints [--team TEAM] [--current]
```
