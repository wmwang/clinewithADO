#!/usr/bin/env python3
"""
Shared Azure DevOps HTTP client.

Handles PAT authentication, SSL bypass (verify=False), and optional proxy.

Environment variables:
  ADO_PAT      - Personal Access Token (required)
  ADO_ORG      - Azure DevOps organization (required)
  ADO_PROJECT  - Azure DevOps project (required)
  HTTP_PROXY   - HTTP proxy URL (optional, e.g. http://proxy.corp:8080)
  HTTPS_PROXY  - HTTPS proxy URL (optional)
"""

import os
import sys
import json
import ssl
import base64
import urllib.parse
import urllib.request
import urllib.error


def _load_config_file():
    """Load credentials from ~/.ado-devops.env if it exists."""
    config_path = os.path.expanduser("~/.ado-devops.env")
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip()
    return config


def get_client():
    """Build ADOClient from environment variables or ~/.ado-devops.env config file.

    Priority: environment variables > config file.
    Run setup.py to create/update the config file.
    """
    file_config = _load_config_file()

    pat     = os.environ.get("ADO_PAT")     or file_config.get("ADO_PAT", "")
    org     = os.environ.get("ADO_ORG")     or file_config.get("ADO_ORG", "")
    project = os.environ.get("ADO_PROJECT") or file_config.get("ADO_PROJECT", "")

    errors = []
    if not pat:
        errors.append("ADO_PAT")
    if not org:
        errors.append("ADO_ORG")
    if not project:
        errors.append("ADO_PROJECT")
    if errors:
        print(json.dumps({
            "error": f"Missing credentials: {', '.join(errors)}",
            "hint": "Run: python <SKILL_DIR>/scripts/setup.py status",
        }))
        sys.exit(1)
    return ADOClient(pat, org, project)


class ADOClient:
    def __init__(self, pat, org, project):
        self.org = org
        self.project = project
        self.project_encoded = urllib.parse.quote(project, safe="")
        self.base_url = f"https://dev.azure.com/{org}"
        self._token = base64.b64encode(f":{pat}".encode()).decode()
        self._opener = self._build_opener()

    def _build_opener(self):
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        handlers = [urllib.request.HTTPSHandler(context=ssl_ctx)]
        proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
        if proxy:
            handlers.insert(0, urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
        return urllib.request.build_opener(*handlers)

    def request(self, url, method="GET", data=None, content_type="application/json"):
        headers = {
            "Authorization": f"Basic {self._token}",
            "Content-Type": content_type,
            "Accept": "application/json",
        }
        req_data = json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        try:
            with self._opener.open(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"HTTP {e.code} {method} {url}: {body}")

    # ── Work Items ──────────────────────────────────────────────────────────

    def wiql(self, query_str):
        url = f"{self.base_url}/{self.project_encoded}/_apis/wit/wiql?api-version=7.1"
        return self.request(url, "POST", {"query": query_str})

    def get_work_item(self, item_id, expand="all"):
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/wit/workitems/{item_id}"
            f"?$expand={expand}&api-version=7.1"
        )
        return self.request(url)

    def get_work_items_batch(self, ids):
        ids_str = ",".join(str(i) for i in ids[:200])  # API max 200
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/wit/workitems"
            f"?ids={ids_str}&$expand=fields&api-version=7.1"
        )
        return self.request(url)

    def update_work_item(self, item_id, operations):
        """operations: list of JSON Patch ops [{op, path, value}, ...]"""
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/wit/workitems/{item_id}"
            f"?api-version=7.1"
        )
        return self.request(url, "PATCH", operations, content_type="application/json-patch+json")

    def add_comment(self, item_id, text):
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/wit/workitems/{item_id}"
            f"/comments?api-version=7.1-preview.3"
        )
        return self.request(url, "POST", {"text": text})

    def get_comments(self, item_id):
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/wit/workitems/{item_id}"
            f"/comments?api-version=7.1-preview.3"
        )
        return self.request(url)

    def create_work_item(self, work_item_type, operations):
        """operations: list of JSON Patch ops [{op, path, value}, ...]"""
        type_enc = urllib.parse.quote(work_item_type, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/wit/workitems/${type_enc}"
            f"?api-version=7.1"
        )
        return self.request(url, "POST", operations, content_type="application/json-patch+json")

    def add_relation(self, item_id, rel_type, target_id):
        """Add a hierarchical relation link to a work item.

        rel_type:
          'System.LinkTypes.Hierarchy-Reverse' — set parent (child → parent)
          'System.LinkTypes.Hierarchy-Forward' — add child (parent → child)
        """
        target_url = (
            f"{self.base_url}/{self.project_encoded}/_apis/wit/workitems/{target_id}"
        )
        ops = [{
            "op": "add",
            "path": "/relations/-",
            "value": {"rel": rel_type, "url": target_url},
        }]
        return self.update_work_item(item_id, ops)

    def get_work_items_for_iteration(self, iteration_id, team=""):
        """Get work item relations for a specific iteration. team defaults to project name."""
        team_enc = urllib.parse.quote(team or self.project, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/{team_enc}"
            f"/_apis/work/teamsettings/iterations/{iteration_id}/workitems?api-version=7.1"
        )
        return self.request(url)

    # ── Repositories ─────────────────────────────────────────────────────────

    def list_repos(self):
        url = f"{self.base_url}/{self.project_encoded}/_apis/git/repositories?api-version=7.1"
        return self.request(url)

    def get_repo(self, repo):
        repo_enc = urllib.parse.quote(repo, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"?api-version=7.1"
        )
        return self.request(url)

    def list_prs(self, repo, status="active", top=50):
        repo_enc = urllib.parse.quote(repo, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/pullrequests?searchCriteria.status={status}&$top={top}&api-version=7.1"
        )
        return self.request(url)

    def get_pr(self, repo, pr_id):
        repo_enc = urllib.parse.quote(repo, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/pullrequests/{pr_id}?api-version=7.1"
        )
        return self.request(url)

    def list_branches(self, repo, filter_prefix=""):
        repo_enc = urllib.parse.quote(repo, safe="")
        filter_param = urllib.parse.quote(filter_prefix, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/refs?filter=heads/{filter_param}&api-version=7.1"
        )
        return self.request(url)

    def list_commits(self, repo, branch="", top=20):
        repo_enc = urllib.parse.quote(repo, safe="")
        params = f"$top={top}"
        if branch:
            params += f"&searchCriteria.itemVersion.version={urllib.parse.quote(branch, safe='')}"
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/commits?{params}&api-version=7.1"
        )
        return self.request(url)

    def create_pr(self, repo, source_branch, target_branch, title,
                  description="", work_item_ids=None, is_draft=False):
        repo_enc = urllib.parse.quote(repo, safe="")
        src = source_branch if source_branch.startswith("refs/") else f"refs/heads/{source_branch}"
        tgt = target_branch if target_branch.startswith("refs/") else f"refs/heads/{target_branch}"
        body = {
            "title": title,
            "description": description,
            "sourceRefName": src,
            "targetRefName": tgt,
            "isDraft": is_draft,
        }
        if work_item_ids:
            body["workItemRefs"] = [{"id": str(wid)} for wid in work_item_ids]
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/pullrequests?api-version=7.1"
        )
        return self.request(url, "POST", body)

    def get_branch_ref(self, repo, branch_name):
        """Resolve a branch name to its latest commit ID."""
        repo_enc = urllib.parse.quote(repo, safe="")
        branch_enc = urllib.parse.quote(branch_name, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/refs?filter=heads/{branch_enc}&api-version=7.1"
        )
        result = self.request(url)
        items = result.get("value", [])
        if not items:
            raise RuntimeError(f"Branch '{branch_name}' not found in repo '{repo}'")
        return items[0]

    def create_branch(self, repo, new_branch, source_branch):
        """Create new_branch from the HEAD of source_branch."""
        source_ref = self.get_branch_ref(repo, source_branch)
        source_commit_id = source_ref["objectId"]
        repo_enc = urllib.parse.quote(repo, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/refs?api-version=7.1"
        )
        body = [{
            "name": f"refs/heads/{new_branch}",
            "oldObjectId": "0000000000000000000000000000000000000000",
            "newObjectId": source_commit_id,
        }]
        return self.request(url, "POST", body)

    def update_pr(self, repo, pr_id, title=None, description=None,
                  status=None, target_branch=None, is_draft=None):
        """Update PR fields. Only provided fields are changed."""
        repo_enc = urllib.parse.quote(repo, safe="")
        body = {}
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        if status is not None:
            body["status"] = status  # active | abandoned | completed
        if target_branch is not None:
            body["targetRefName"] = (
                target_branch if target_branch.startswith("refs/") else f"refs/heads/{target_branch}"
            )
        if is_draft is not None:
            body["isDraft"] = is_draft
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/pullrequests/{pr_id}?api-version=7.1"
        )
        return self.request(url, "PATCH", body)

    def list_pr_threads(self, repo, pr_id):
        repo_enc = urllib.parse.quote(repo, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/pullrequests/{pr_id}/threads?api-version=7.1"
        )
        return self.request(url)

    def create_pr_thread(self, repo, pr_id, content, file_path=None,
                         line=None, status="active"):
        repo_enc = urllib.parse.quote(repo, safe="")
        body = {
            "comments": [{"parentCommentId": 0, "content": content, "commentType": 1}],
            "status": status,
        }
        if file_path:
            body["threadContext"] = {
                "filePath": file_path,
                "rightFileStart": {"line": line or 1, "offset": 1},
                "rightFileEnd": {"line": line or 1, "offset": 1},
            }
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/pullrequests/{pr_id}/threads?api-version=7.1"
        )
        return self.request(url, "POST", body)

    def reply_to_thread(self, repo, pr_id, thread_id, content):
        repo_enc = urllib.parse.quote(repo, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/pullrequests/{pr_id}/threads/{thread_id}/comments?api-version=7.1"
        )
        return self.request(url, "POST", {"parentCommentId": 1, "content": content, "commentType": 1})

    def update_pr_thread_status(self, repo, pr_id, thread_id, status):
        """status: active | fixed | wontFix | closed | byDesign | pending"""
        repo_enc = urllib.parse.quote(repo, safe="")
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/pullrequests/{pr_id}/threads/{thread_id}?api-version=7.1"
        )
        return self.request(url, "PATCH", {"status": status})

    def list_directory(self, repo, path="/", branch="", recursive=False):
        repo_enc = urllib.parse.quote(repo, safe="")
        scope = "oneLevel" if not recursive else "full"
        params = f"recursionLevel={scope}&api-version=7.1"
        if path and path != "/":
            params += f"&path={urllib.parse.quote(path, safe='/')}"
        if branch:
            params += f"&versionDescriptor.version={urllib.parse.quote(branch, safe='')}&versionDescriptor.versionType=branch"
        url = (
            f"{self.base_url}/{self.project_encoded}/_apis/git/repositories/{repo_enc}"
            f"/items?{params}"
        )
        return self.request(url)

    # ── Search ────────────────────────────────────────────────────────────────
    # Search uses a different hostname: almsearch.dev.azure.com

    def _search_url(self, endpoint):
        return (
            f"https://almsearch.dev.azure.com/{self.org}/{self.project_encoded}"
            f"/_apis/search/{endpoint}?api-version=7.1"
        )

    def search_code(self, text, repo=None, branch=None, path=None, top=25, skip=0):
        filters = {}
        if repo:
            filters["Repository"] = [repo]
        if branch:
            filters["Branch"] = [branch]
        if path:
            filters["Path"] = [path]
        body = {"searchText": text, "$skip": skip, "$top": top,
                "includeFacets": False, "filters": filters}
        return self.request(self._search_url("codesearchresults"), "POST", body)

    def search_workitem(self, text, work_item_type=None, state=None,
                        assignee=None, area_path=None, top=25, skip=0):
        filters = {}
        if work_item_type:
            filters["System.WorkItemType"] = [work_item_type]
        if state:
            filters["System.State"] = [state]
        if assignee:
            filters["System.AssignedTo"] = [assignee]
        if area_path:
            filters["System.AreaPath"] = [area_path]
        body = {"searchText": text, "$skip": skip, "$top": top,
                "includeFacets": False, "filters": filters}
        return self.request(self._search_url("workitemsearchresults"), "POST", body)

    def search_wiki(self, text, wiki=None, top=25, skip=0):
        filters = {}
        if wiki:
            filters["Wiki"] = [wiki]
        body = {"searchText": text, "$skip": skip, "$top": top,
                "includeFacets": False, "filters": filters}
        return self.request(self._search_url("wikisearchresults"), "POST", body)
