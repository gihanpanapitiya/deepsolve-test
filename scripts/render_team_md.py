"""Render team.json into a browsable TEAM.md.

The mermaid diagram gives a top-down org view; the table is a directory with
links into per-person <details> sections further down. Issue refs like "#201"
get linked to the actual issue pages when we know the repo slug.
"""

import json
import re
import sys
from pathlib import Path

#: Every AI member acts through the one shared agent account, so team.json
#: leaves their `github_id` empty (see sync_issue_assignments.py) and the
#: handle is supplied here at render time.
AI_GITHUB_HANDLE = "sciencehands"


def safe_id(value: str) -> str:
    """Mermaid node id: alphanumerics + underscore only."""
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def anchor(value: str) -> str:
    """GitHub-style anchor slug for a heading."""
    slug = value.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def esc(value) -> str:
    if value is None:
        return ""
    return str(value).replace('"', "'").replace("\n", " ").strip()


def esc_cell(value) -> str:
    """Escape a value for use inside a markdown table cell."""
    return esc(value).replace("|", "\\|")


def parse_issues(raw: str):
    """Pull issue refs like '#201' out of a free-form string."""
    if not raw:
        return []
    return re.findall(r"#(\d+)", raw)


def render_issues(raw: str, repo_slug: str | None) -> str:
    """Render issue refs as markdown links when we know the repo, else bare tokens.

    Bare '#NNN' tokens are also auto-linked by GitHub in normal markdown, but
    explicit links work everywhere (including third-party renderers and mirrors)
    and let us control the link text.
    """
    numbers = parse_issues(raw)
    if not numbers:
        return esc(raw)
    if repo_slug:
        return ", ".join(
            f"[#{n}](https://github.com/{repo_slug}/issues/{n})" for n in numbers
        )
    return ", ".join(f"#{n}" for n in numbers)


def github_profile(github_id) -> str:
    """Full URL to a GitHub user profile, or '' when no handle is set."""
    gid = esc(github_id)
    return f"https://github.com/{gid}" if gid else ""


def github_handle(person: dict) -> str:
    """The handle to display: the shared agent account for AI, else the row's own."""
    if person.get("personType") == "AI":
        return AI_GITHUB_HANDLE
    return esc(person.get("github_id"))


def advisor_ids(person: dict) -> list[str]:
    """Return canonical advisor ids, accepting the legacy singular field."""
    values = person.get("advisorIds")
    if values is None:
        legacy = person.get("advisorId", "")
        return [legacy] if legacy else []
    result = [value for value in values if isinstance(value, str) and value]
    legacy = person.get("advisorId", "")
    if legacy and legacy not in result:
        result.append(legacy)
    return result


def render_branch(branch: str, repo_slug: str | None) -> str:
    """Link each comma-separated branch name to its tree view, else code-span it."""
    names = [esc(part) for part in (branch or "").split(",") if part.strip()]
    if not names:
        return ""
    if repo_slug:
        return ", ".join(
            f"[`{name}`](https://github.com/{repo_slug}/tree/{name})" for name in names
        )
    return ", ".join(f"`{name}`" for name in names)


def person_heading(person: dict) -> str:
    return person["id"]


def main(infile: str, outfile: str, repo_slug: str | None = None) -> None:
    people = json.loads(Path(infile).read_text())
    by_id = {p["id"]: p for p in people}

    anchors = {p["id"]: anchor(person_heading(p)) for p in people}

    reports = {p["id"]: [] for p in people}
    for p in people:
        for advisor_id in advisor_ids(p):
            if advisor_id in reports:
                reports[advisor_id].append(p["id"])

    lines = [
        "# Team Roles and Responsibilities",
        "",
        "<!-- Generated from team.json. Do not edit by hand. -->",
        "",
        (
            "Member ids in the table link to their cards below — or click a node "
            "in the org chart above — for a person's details."
        ),
        "",
        "```mermaid",
        "flowchart TD",
    ]

    for p in people:
        node_id = safe_id(p["id"])
        # Show the capability template (identity_class) as the descriptor line for
        # AI Identities that have one; humans and the coadvisor just show id + type.
        klass = p.get("identity_class")
        label = f"{esc(p['id'])}<br/>"
        if klass:
            label += f"{esc(klass)}<br/>"
        label += f"<b>Type:</b> {esc(p.get('personType'))}"
        lines.append(f'  {node_id}["{label}"]')

    lines.append("")

    for p in people:
        for advisor_id in advisor_ids(p):
            if advisor_id not in by_id:
                continue
            lines.append(
                f"  {safe_id(advisor_id)} -->|advises / supervises| {safe_id(p['id'])}"
            )

    lines.append("")
    for p in people:
        lines.append(
            f'  click {safe_id(p["id"])} "#{anchors[p["id"]]}" "Jump to {esc(p["id"])}"'
        )

    lines.extend(
        [
            "```",
            "",
            "## Team directory",
            "",
            "| ID | GitHub | Identity class | Type | Advisors | Branch | Issues |",
            "|---|---|---|---|---|---|---|",
        ]
    )

    for p in people:
        advisor = ", ".join(
            by_id[advisor_id]["id"]
            for advisor_id in advisor_ids(p)
            if advisor_id in by_id
        )
        plan = p.get("plan", {})
        handle = github_handle(p)
        profile = github_profile(handle)
        # Link the id to the member's own card: AI rows all share one profile,
        # so the profile URL would not identify them.
        name_link = f"[{esc_cell(p['id'])}](#{anchors[p['id']]})"
        github_cell = f"[@{esc_cell(handle)}]({profile})" if profile else "—"
        lines.append(
            "| "
            + " | ".join(
                [
                    name_link,
                    github_cell,
                    esc_cell(p.get("identity_class")),
                    esc_cell(p.get("personType")),
                    esc_cell(advisor),
                    esc_cell(render_branch(plan.get("githubBranch"), repo_slug)),
                    esc_cell(render_issues(plan.get("githubIssues"), repo_slug)),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Team members", ""])

    for p in people:
        plan = p.get("plan", {})
        metadata = p.get("metadata", {})
        advisor_text = (
            ", ".join(
                f"[{esc(by_id[advisor_id]['id'])}](#{anchors[advisor_id]})"
                for advisor_id in advisor_ids(p)
                if advisor_id in by_id
            )
            or "—"
        )

        direct_reports = reports.get(p["id"], [])
        if direct_reports:
            reports_text = ", ".join(
                f"[{esc(by_id[rid]['id'])}](#{anchors[rid]})" for rid in direct_reports
            )
        else:
            reports_text = "—"

        issues_text = render_issues(plan.get("githubIssues"), repo_slug) or "—"
        branch_text = render_branch(plan.get("githubBranch"), repo_slug) or "—"
        handle = github_handle(p)
        profile = github_profile(handle)
        github_text = f"[@{esc(handle)}]({profile})" if profile else "—"
        # Card summary: capability template (if any) + type; the class stands in for
        # the removed free-form role title.
        klass = p.get("identity_class")
        summary = (
            f"<b>{esc(klass)}</b> &middot; {esc(p.get('personType'))}"
            if klass
            else f"<b>{esc(p.get('personType'))}</b>"
        )

        lines.extend(
            [
                f"### {person_heading(p)}",
                "",
                "<details>",
                f"<summary>{summary}</summary>",
                "",
                f"- **ID:** `{esc(p['id'])}`",
                f"- **Type:** {esc(p.get('personType')) or '—'}",
                f"- **GitHub:** {github_text}",
                f"- **Advisors:** {advisor_text}",
                f"- **Direct reports:** {reports_text}",
                "",
                "**Plan**",
                "",
                f"- **Branch:** {branch_text}",
                f"- **Issues:** {issues_text}",
                "",
                "**Expertise & limits**",
                "",
                f"- **Consult on:** {esc(metadata.get('consultOn')) or '—'}",
                f"- **Known limitations:** {esc(metadata.get('knownLimitations')) or '—'}",
            ]
        )
        # Identity details for recruited AI Identities: the capability template
        # it is built from and its standing (reputation) on the team.
        if p.get("identity_class"):
            lines.append(f"- **Identity class:** `{esc(p.get('identity_class'))}`")
        reputation = metadata.get("reputation")
        if isinstance(reputation, dict) and reputation:
            rep = ", ".join(f"{esc(k)}: {esc(v)}" for k, v in reputation.items())
            lines.append(f"- **Reputation:** {rep}")
        lines.extend(
            [
                "",
                "</details>",
                "",
            ]
        )

    Path(outfile).write_text(
        "\n".join(line.rstrip(" \t") for line in lines).rstrip("\n") + "\n"
    )


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        raise SystemExit("Usage: render_team_md.py team.json TEAM.md [owner/repo]")
    repo = sys.argv[3] if len(sys.argv) == 4 else None
    main(sys.argv[1], sys.argv[2], repo)
