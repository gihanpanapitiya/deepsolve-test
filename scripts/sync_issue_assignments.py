"""Reconcile each team member's issues and work branch in team.json with live GitHub data.

Ownership is split, because only humans are GitHub assignees:

* **Rows with a ``github_id`` (humans).** GitHub assignments are the source of
  truth: ``plan.githubIssues`` is rewritten to the sorted, comma-joined refs of
  the OPEN issues assigned to that login (e.g. "#12, #34").
* **Rows without one (AI Identities, which share the agent account).** The
  coadvisor owns the field; this script only *prunes* refs whose issue is closed
  or gone. It never blanks the field — doing so wiped live Identities on every
  push to the default branch and made the coadvisor reopen the same
  reconciliation PR on the next heartbeat.

``plan.githubBranch`` is derived for every row from the issue-scoped branches
``task_intake`` creates (``sciencehands/issue-<N>-<slug>``), matched against the
issues the row is working. A row whose issues have no matching ref keeps
whatever the coadvisor wrote.

Every value written here is a pure function of live GitHub state, so consecutive
runs converge and cannot drive a merge loop. Run the render step afterwards.

Required env:
  GITHUB_TOKEN       Token with issues:read (the default Actions token works).
  GITHUB_REPOSITORY  "owner/repo", supplied automatically by Actions.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
TEAM_PATH = Path("team.json")

#: Branch naming from ``sciencehands.tools.research_tools.task_intake``.
ISSUE_BRANCH_RE = re.compile(r"^sciencehands/issue-(\d+)-")
ISSUE_REF_RE = re.compile(r"#(\d+)")


def gh_get(url: str, token: str) -> tuple[list, str | None]:
    """GET a REST endpoint, returning (json_body, Link header)."""
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "issue-assignment-sync",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()), resp.headers.get("Link")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"GitHub API HTTP {e.code} for {url}: {e.read().decode()}")


def next_link(link_header: str | None) -> str | None:
    """Extract the rel="next" URL from a Link header, if present."""
    if not link_header:
        return None
    for part in link_header.split(","):
        section = [s.strip() for s in part.split(";")]
        if len(section) >= 2 and section[1] == 'rel="next"':
            return section[0].strip("<>")
    return None


def open_issues_for(owner: str, name: str, login: str, token: str) -> list[int]:
    """Open issue numbers (excluding PRs) assigned to ``login``, ascending."""
    query = urllib.parse.urlencode(
        {"assignee": login, "state": "open", "per_page": 100}
    )
    return _issue_numbers(f"{API}/repos/{owner}/{name}/issues?{query}", token)


def open_issue_numbers(owner: str, name: str, token: str) -> set[int]:
    """Every open issue number in the repo (excluding PRs)."""
    query = urllib.parse.urlencode({"state": "open", "per_page": 100})
    return set(_issue_numbers(f"{API}/repos/{owner}/{name}/issues?{query}", token))


def _issue_numbers(url: str, token: str) -> list[int]:
    numbers: list[int] = []
    while url:
        items, link = gh_get(url, token)
        # The issues endpoint also returns pull requests; skip those.
        numbers.extend(it["number"] for it in items if "pull_request" not in it)
        url = next_link(link)
    return sorted(set(numbers))


def branches_by_issue(owner: str, name: str, token: str) -> dict[int, list[str]]:
    """Map issue number -> issue-scoped branch names currently on the remote."""
    mapping: dict[int, list[str]] = {}
    query = urllib.parse.urlencode({"per_page": 100})
    url = f"{API}/repos/{owner}/{name}/branches?{query}"
    while url:
        items, link = gh_get(url, token)
        for item in items:
            branch = item.get("name") or ""
            match = ISSUE_BRANCH_RE.match(branch)
            if match:
                mapping.setdefault(int(match.group(1)), []).append(branch)
        url = next_link(link)
    return {number: sorted(names) for number, names in mapping.items()}


def issue_refs(raw: str) -> list[int]:
    """Issue numbers mentioned in a ``plan.githubIssues`` value, in order."""
    seen: set[int] = set()
    numbers: list[int] = []
    for ref in ISSUE_REF_RE.findall(raw or ""):
        number = int(ref)
        if number not in seen:
            seen.add(number)
            numbers.append(number)
    return numbers


def format_refs(numbers: list[int]) -> str:
    return ", ".join(f"#{n}" for n in numbers)


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    repo_slug = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo_slug:
        raise SystemExit("GITHUB_TOKEN and GITHUB_REPOSITORY must be set.")
    owner, name = repo_slug.split("/", 1)

    people = json.loads(TEAM_PATH.read_text())

    # Logins can be shared by more than one member, so query each at most once;
    # the repo-wide lookups are fetched lazily and only once.
    by_login: dict[str, list[int]] = {}
    still_open: set[int] | None = None
    branch_map: dict[int, list[str]] | None = None
    changed = False

    for person in people:
        gid = (person.get("github_id") or "").strip()
        plan = person.get("plan") or {}
        current = plan.get("githubIssues", "") or ""

        if gid:
            key = gid.lower()
            if key not in by_login:
                by_login[key] = open_issues_for(owner, name, gid, token)
            numbers = by_login[key]
        elif current:
            if still_open is None:
                still_open = open_issue_numbers(owner, name, token)
            numbers = [n for n in issue_refs(current) if n in still_open]
        else:
            numbers = []

        new_issues = format_refs(numbers)
        if numbers:
            if branch_map is None:
                branch_map = branches_by_issue(owner, name, token)
            matched = [b for n in numbers for b in branch_map.get(n, [])]
        else:
            matched = []
        # An unmatched row keeps the coadvisor's branch: the ref may be local to
        # the cosolver's container and not pushed yet.
        new_branch = ", ".join(dict.fromkeys(matched)) or plan.get("githubBranch", "")

        for field, new_value in (
            ("githubIssues", new_issues),
            ("githubBranch", new_branch),
        ):
            if plan.get(field, "") != new_value:
                print(
                    f"{person.get('id')} ({gid or 'no handle'}): "
                    f"{field} -> {new_value or '(none)'}"
                )
                person.setdefault("plan", plan)[field] = new_value
                changed = True

    if changed:
        TEAM_PATH.write_text(json.dumps(people, indent=2) + "\n")
        print("team.json updated.")
    else:
        print("team.json already reflects current assignments.")


if __name__ == "__main__":
    main()
