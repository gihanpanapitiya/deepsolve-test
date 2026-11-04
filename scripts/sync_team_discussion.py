"""Create or update a pinned 'Team' discussion that mirrors TEAM.md.

State (the discussion's node id and number) is persisted to
.github/team-discussion.json so subsequent runs update instead of creating
a duplicate.

Required env:
  GITHUB_TOKEN     A token with Discussions write. A **GitHub App installation
                   token** works (verified 2026-08-28: with `discussions: write`
                   granted it can read discussionCategories and run
                   createDiscussion / updateDiscussion / addDiscussionComment) —
                   preferred, so the discussion is authored by the bot rather
                   than a person. A USER PAT also works (classic: `repo` +
                   `write:discussion`; fine-grained: Discussions RW). The default
                   Actions GITHUB_TOKEN can only CREATE discussions, not update
                   them, so it is a last resort. The workflow supplies the
                   renderer App token, falling back to DISCUSSION_TOKEN, then
                   GITHUB_TOKEN.
  GITHUB_REPOSITORY  "owner/repo", supplied automatically by Actions.

Optional env:
  TEAM_DISCUSSION_CATEGORY  Category name (default: "General"). The category
                            must already exist in the repo's discussion
                            settings.
  TEAM_DISCUSSION_TITLE     Title to use when creating (default:
                            "Team Roster and Discussion").
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

GRAPHQL_URL = "https://api.github.com/graphql"
STATE_PATH = Path(".github/team-discussion.json")
DEFAULT_CATEGORY = "General"
DEFAULT_TITLE = "Team Roster and Discussion"

PREAMBLE = (
    "> This post is auto-generated from `team_plan.md` and `team.json` in the "
    "repo root and is updated by the `team_discussion` workflow. "
    "**Do not edit the body** — your changes will be overwritten on the next run.\n>\n"
    "> Use the comments below to ask questions, request changes, or talk "
    "to the sciencehands agent, which polls this thread on a schedule.\n\n"
    "---\n\n"
)


def gql(query: str, variables: dict, token: str) -> dict:
    """Run a GraphQL query/mutation and return the data block, raising on errors."""
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "team-discussion-sync",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"GraphQL HTTP {e.code}: {e.read().decode()}")
    if body.get("errors"):
        raise SystemExit(f"GraphQL errors: {json.dumps(body['errors'], indent=2)}")
    return body["data"]


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def fetch_repo_and_category(
    owner: str, name: str, category: str, token: str
) -> tuple[str, str]:
    """Return (repository_id, category_id). Raises if discussions are off or category missing."""
    data = gql(
        """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            id
            hasDiscussionsEnabled
            discussionCategories(first: 25) {
              nodes { id name }
            }
          }
        }
        """,
        {"owner": owner, "name": name},
        token,
    )
    repo = data["repository"]
    if not repo["hasDiscussionsEnabled"]:
        raise SystemExit(
            "Discussions are not enabled on this repository. Enable them in "
            "Settings → General → Features → Discussions, then re-run the workflow."
        )
    for c in repo["discussionCategories"]["nodes"]:
        if c["name"].lower() == category.lower():
            return repo["id"], c["id"]
    available = ", ".join(c["name"] for c in repo["discussionCategories"]["nodes"])
    raise SystemExit(
        f"Discussion category {category!r} not found. Available: {available}. "
        "Either create the category or set TEAM_DISCUSSION_CATEGORY."
    )


def find_discussion_by_title(
    owner: str, name: str, category_id: str, title: str, token: str
) -> dict | None:
    """Find an existing discussion in the category whose title matches (case-insensitive).

    Used as a fallback when the persisted state file is missing or stale, so we
    adopt an existing roster discussion instead of creating a duplicate. Returns
    the first match (oldest first), or None.
    """
    target = title.strip().lower()
    cursor = None
    while True:
        data = gql(
            """
            query($owner: String!, $name: String!, $cat: ID!, $cursor: String) {
              repository(owner: $owner, name: $name) {
                discussions(first: 50, categoryId: $cat, after: $cursor,
                            orderBy: {field: CREATED_AT, direction: ASC}) {
                  nodes { id number url title }
                  pageInfo { hasNextPage endCursor }
                }
              }
            }
            """,
            {"owner": owner, "name": name, "cat": category_id, "cursor": cursor},
            token,
        )
        conn = data["repository"]["discussions"]
        for node in conn["nodes"]:
            if node["title"].strip().lower() == target:
                return node
        if not conn["pageInfo"]["hasNextPage"]:
            return None
        cursor = conn["pageInfo"]["endCursor"]


def create_discussion(
    repo_id: str, category_id: str, title: str, body: str, token: str
) -> dict:
    data = gql(
        """
        mutation($repo: ID!, $cat: ID!, $title: String!, $body: String!) {
          createDiscussion(input: {
            repositoryId: $repo, categoryId: $cat, title: $title, body: $body
          }) {
            discussion { id number url }
          }
        }
        """,
        {"repo": repo_id, "cat": category_id, "title": title, "body": body},
        token,
    )
    return data["createDiscussion"]["discussion"]


def update_discussion(discussion_id: str, body: str, token: str) -> dict:
    data = gql(
        """
        mutation($id: ID!, $body: String!) {
          updateDiscussion(input: { discussionId: $id, body: $body }) {
            discussion { id number url }
          }
        }
        """,
        {"id": discussion_id, "body": body},
        token,
    )
    return data["updateDiscussion"]["discussion"]


def pin_discussion(discussion_id: str, token: str) -> None:
    """Pinning isn't exposed via the public GraphQL API yet. Skip with a note."""
    print(
        "Note: pinning must be done manually in the UI. "
        "GitHub does not expose a pinDiscussion mutation."
    )


def discussion_still_exists(discussion_id: str, token: str) -> bool:
    """Confirm the stored id resolves to a live discussion (it could've been deleted)."""
    try:
        data = gql(
            "query($id: ID!) { node(id: $id) { ... on Discussion { id } } }",
            {"id": discussion_id},
            token,
        )
        return data.get("node") is not None
    except SystemExit:
        return False


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    repo_slug = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo_slug:
        raise SystemExit("GITHUB_TOKEN and GITHUB_REPOSITORY must be set.")
    owner, name = repo_slug.split("/", 1)

    category = os.environ.get("TEAM_DISCUSSION_CATEGORY", DEFAULT_CATEGORY)
    title = os.environ.get("TEAM_DISCUSSION_TITLE", DEFAULT_TITLE)

    team_md = Path("TEAM.md")
    if not team_md.exists():
        raise SystemExit("TEAM.md not found. Run the render workflow first.")

    # team_plan.md is free-form markdown shown above the rendered roster. The
    # workflow guarantees the file exists (creating a blank one if needed);
    # when its content is just whitespace we omit the divider so the body
    # doesn't have an awkward empty section.
    #
    # We wrap the plan content under a `# Research Plan` H1 and demote any
    # existing ATX headings in the plan by one level so they nest cleanly as
    # subsections under it. Without this the plan's own `#` headings sit at
    # the same level as the roster's `# Team Roles and Responsibilities`,
    # making the two top-level sections visually indistinguishable.
    plan_path = Path("team_plan.md")
    plan_section = plan_path.read_text().strip() if plan_path.exists() else ""
    if plan_section:
        demoted = re.sub(r"^(#{1,5}) ", r"#\1 ", plan_section, flags=re.MULTILINE)
        body = (
            PREAMBLE
            + "# Research Plan\n\n"
            + demoted
            + "\n\n---\n\n"
            + team_md.read_text()
        )
    else:
        body = PREAMBLE + team_md.read_text()

    state = load_state()
    discussion_id = state.get("id")

    if discussion_id and not discussion_still_exists(discussion_id, token):
        print(f"Stored discussion {discussion_id} no longer exists; recreating.")
        discussion_id = None

    # When state is missing or stale, the repo may still hold a matching
    # discussion (e.g. the state file was lost or never committed). Adopt it
    # instead of creating a duplicate.
    repo_id = category_id = None
    if not discussion_id:
        repo_id, category_id = fetch_repo_and_category(owner, name, category, token)
        existing = find_discussion_by_title(owner, name, category_id, title, token)
        if existing:
            print(
                f"Adopting existing discussion #{existing['number']}: {existing['url']}"
            )
            discussion_id = existing["id"]
            save_state(
                {
                    "id": existing["id"],
                    "number": existing["number"],
                    "url": existing["url"],
                }
            )

    if discussion_id:
        d = update_discussion(discussion_id, body, token)
        print(f"Updated discussion #{d['number']}: {d['url']}")
    else:
        d = create_discussion(repo_id, category_id, title, body, token)
        print(f"Created discussion #{d['number']}: {d['url']}")
        pin_discussion(d["id"], token)
        print("Pinned.")
        save_state({"id": d["id"], "number": d["number"], "url": d["url"]})


if __name__ == "__main__":
    main()
