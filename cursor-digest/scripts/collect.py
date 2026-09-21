#!/usr/bin/env python3
"""Collect Cursor sessions for a date range and write digest JSON/HTML."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sqlite3
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = SKILL_DIR / "template.html"
DEFAULT_ARTIFACTS = Path.home() / "Projects" / "cursor-digest-artifacts"
DEFAULT_DB = (
    Path.home()
    / "Library/Application Support/Cursor/User/globalStorage/state.vscdb"
)
DEFAULT_PROJECTS = Path.home() / ".cursor/projects"

USER_QUERY_RE = re.compile(r"<user_query>\s*(.*?)\s*</user_query>", re.S)
TIMESTAMP_RE = re.compile(r"<timestamp>(.*?)</timestamp>")
URL_RE = re.compile(r"https://[^\s)\]>'\"<>]+")
ISO_DAY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})$")
ISO_RANGE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})$")

LINK_KINDS = (
    ("pull_request", re.compile(r"^https://github\.com/[^/]+/[^/]+/pull/\d+", re.I)),
    ("issue", re.compile(r"^https://github\.com/[^/]+/[^/]+/issues/\d+", re.I)),
    ("linear", re.compile(r"^https://linear\.app/", re.I)),
    ("notion", re.compile(r"^https://(?:www\.)?notion\.so/", re.I)),
    ("google_doc", re.compile(r"^https://docs\.google\.com/", re.I)),
)


class RangeError(ValueError):
    """The date argument could not be parsed."""


def start_of_day(moment: datetime) -> datetime:
    return moment.replace(hour=0, minute=0, second=0, microsecond=0)


def parse_iso_day(value: str, tzinfo) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=tzinfo)


def parse_range(spec: str | None, now: datetime) -> tuple[datetime, datetime, str]:
    """Return (start, end, label). End is exclusive except 'now' for open ranges."""
    local = now.astimezone()
    today = start_of_day(local)
    raw = (spec or "yesterday").strip().lower()
    raw = re.sub(r"\s+", " ", raw)

    if raw in {"yesterday", "yday"}:
        start = today - timedelta(days=1)
        return start, today, start.strftime("%A %d %B %Y")
    if raw == "today":
        return today, local, f"Today · {today.strftime('%A %d %B %Y')}"
    if raw in {"last week", "past week", "last-week"}:
        start = today - timedelta(days=7)
        return start, local, f"Last 7 days · {start:%d %b} – {local:%d %b %Y}"
    if raw in {"this week", "this-week"}:
        start = today - timedelta(days=today.weekday())
        return start, local, f"This week · {start:%d %b} – {local:%d %b %Y}"

    day_match = ISO_DAY_RE.match(raw)
    if day_match:
        start = parse_iso_day(day_match.group(1), local.tzinfo)
        return start, start + timedelta(days=1), start.strftime("%A %d %B %Y")

    range_match = ISO_RANGE_RE.match(raw)
    if range_match:
        start = parse_iso_day(range_match.group(1), local.tzinfo)
        end_day = parse_iso_day(range_match.group(2), local.tzinfo)
        if end_day < start:
            raise RangeError("Range end is before start.")
        end = end_day + timedelta(days=1)
        if start.date() == end_day.date():
            return start, end, start.strftime("%A %d %B %Y")
        return start, end, f"{start:%d %b %Y} – {end_day:%d %b %Y}"

    raise RangeError(f"Unknown date range: {spec!r}")


def ms_to_dt(ms: int | None, tzinfo) -> datetime | None:
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=tzinfo)


def classify_url(url: str) -> str | None:
    cleaned = url.rstrip(".,;:!?)")
    for kind, pattern in LINK_KINDS:
        if pattern.match(cleaned):
            return kind
    if cleaned.startswith("https://github.com/"):
        return "github"
    return None


def extract_links(text: str) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for match in URL_RE.findall(text or ""):
        url = match.rstrip(".,;:!?)")
        kind = classify_url(url)
        if not kind:
            continue
        found[url] = {"url": url, "kind": kind}
    return list(found.values())


def first_user_query(text: str) -> str:
    match = USER_QUERY_RE.search(text or "")
    if not match:
        return ""
    query = re.sub(r"\s+", " ", match.group(1)).strip()
    return query[:400]


def index_transcripts(projects_root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    if not projects_root.exists():
        return index
    for path in projects_root.glob("*/agent-transcripts/*/*.jsonl"):
        if "subagents" in path.parts:
            continue
        if path.parent.name != path.stem:
            continue
        index[path.stem] = path
    return index


def read_transcript_facts(path: Path) -> dict[str, Any]:
    first_query = ""
    blob_parts: list[str] = []
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for i, line in enumerate(handle):
                if i >= 80:
                    break
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                message = row.get("message") or {}
                content = message.get("content") or []
                texts = []
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            texts.append(block.get("text") or "")
                joined = "\n".join(texts)
                if row.get("role") == "user" and not first_query:
                    first_query = first_user_query(joined)
                if i < 12:
                    blob_parts.append(joined)
    except OSError:
        return {"first_query": "", "links": []}
    blob = "\n".join(blob_parts)
    return {"first_query": first_query, "links": extract_links(blob)}


def workspace_path(header: dict[str, Any]) -> str:
    ident = header.get("workspaceIdentifier") or {}
    uri = ident.get("uri") or {}
    path = uri.get("fsPath") or uri.get("path") or ""
    if path:
        return path
    external = uri.get("external") or ""
    if external.startswith("file://"):
        return unquote(urlparse(external).path)
    return ""


def project_name(path: str) -> str:
    if not path:
        return "(unknown project)"
    return Path(path.rstrip("/")).name or path


def load_headers(db_path: Path) -> list[dict[str, Any]]:
    if not db_path.exists():
        raise FileNotFoundError(f"Cursor session database not found: {db_path}")
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=10)
    try:
        conn.execute("PRAGMA query_only=ON")
        rows = conn.execute(
            "SELECT composerId, workspaceId, createdAt, lastUpdatedAt, "
            "isSubagent, value FROM composerHeaders"
        ).fetchall()
    finally:
        conn.close()

    headers = []
    for composer_id, workspace_id, created_at, last_updated_at, is_subagent, value in rows:
        try:
            payload = json.loads(value) if value else {}
        except json.JSONDecodeError:
            payload = {}
        payload.setdefault("composerId", composer_id)
        payload["_workspaceId"] = workspace_id
        payload["_createdAt"] = created_at
        payload["_lastUpdatedAt"] = last_updated_at
        payload["_isSubagent"] = bool(is_subagent) or bool(
            payload.get("isBestOfNSubcomposer")
        )
        headers.append(payload)
    return headers


def session_in_range(header: dict[str, Any], start: datetime, end: datetime) -> bool:
    tzinfo = start.tzinfo
    updated = ms_to_dt(header.get("_lastUpdatedAt") or header.get("lastUpdatedAt"), tzinfo)
    created = ms_to_dt(header.get("_createdAt") or header.get("createdAt"), tzinfo)
    point = updated or created
    if point is None:
        return False
    return start <= point < end


def is_empty_draft(header: dict[str, Any], facts: dict[str, Any]) -> bool:
    if header.get("name"):
        return False
    if facts.get("first_query"):
        return False
    added = int(header.get("totalLinesAdded") or 0)
    removed = int(header.get("totalLinesRemoved") or 0)
    files_changed = int(header.get("filesChangedCount") or 0)
    return added == 0 and removed == 0 and files_changed == 0


def collect_sessions(
    headers: list[dict[str, Any]],
    start: datetime,
    end: datetime,
    transcripts: dict[str, Path],
) -> list[dict[str, Any]]:
    sessions = []
    for header in headers:
        if header.get("_isSubagent"):
            continue
        if not session_in_range(header, start, end):
            continue
        composer_id = header.get("composerId") or ""
        transcript_path = transcripts.get(composer_id)
        facts = read_transcript_facts(transcript_path) if transcript_path else {
            "first_query": "",
            "links": [],
        }
        if is_empty_draft(header, facts):
            continue
        query = facts["first_query"]
        if query.lower().startswith("/cursor-digest"):
            continue
        tzinfo = start.tzinfo
        created = ms_to_dt(header.get("_createdAt") or header.get("createdAt"), tzinfo)
        updated = ms_to_dt(header.get("_lastUpdatedAt") or header.get("lastUpdatedAt"), tzinfo)
        ws = workspace_path(header)
        repos = []
        for repo in header.get("trackedGitRepos") or []:
            branches = [
                b.get("branchName")
                for b in (repo.get("branches") or [])
                if b.get("branchName")
            ]
            repos.append({"path": repo.get("repoPath") or "", "branches": branches})
        sessions.append(
            {
                "id": composer_id,
                "name": header.get("name") or (query[:80] if query else "Untitled session"),
                "subtitle": header.get("subtitle") or "",
                "mode": header.get("unifiedMode") or "agent",
                "project": project_name(ws),
                "workspace": ws,
                "created_at": created.isoformat() if created else None,
                "updated_at": updated.isoformat() if updated else None,
                "lines_added": int(header.get("totalLinesAdded") or 0),
                "lines_removed": int(header.get("totalLinesRemoved") or 0),
                "files_changed": int(header.get("filesChangedCount") or 0),
                "first_query": query,
                "links": facts["links"],
                "repos": repos,
                "transcript": str(transcript_path) if transcript_path else None,
            }
        )
    sessions.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return sessions


def run_gh_search(kind: str, start: datetime, end: datetime) -> tuple[list[dict[str, Any]], str | None]:
    start_day = start.strftime("%Y-%m-%d")
    end_inclusive = (end - timedelta(seconds=1)).strftime("%Y-%m-%d")
    query = f"--updated={start_day}..{end_inclusive}"
    cmd = [
        "gh",
        "search",
        kind,
        "--author=@me",
        query,
        "--limit",
        "40",
        "--json",
        "title,url,state,number,repository,updatedAt",
    ]
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=45,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], str(exc)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "gh failed").strip()
        return [], err.splitlines()[-1] if err else "gh failed"
    try:
        rows = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as exc:
        return [], f"gh returned invalid JSON: {exc}"
    items = []
    for row in rows:
        repo = row.get("repository") or {}
        items.append(
            {
                "title": row.get("title") or "",
                "url": row.get("url") or "",
                "state": row.get("state") or "",
                "number": row.get("number"),
                "repo": repo.get("nameWithOwner") or repo.get("name") or "",
                "updated_at": row.get("updatedAt") or "",
                "source": "gh",
            }
        )
    return items, None


def merge_work(sessions: list[dict[str, Any]], gh_prs: list[dict[str, Any]], gh_issues: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    work: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for pr in gh_prs:
        if pr.get("url"):
            work["pull_request"][pr["url"]] = {**pr, "kind": "pull_request"}
    for issue in gh_issues:
        if issue.get("url"):
            work["issue"][issue["url"]] = {**issue, "kind": "issue"}
    for session in sessions:
        for link in session.get("links") or []:
            kind = link["kind"]
            bucket = "pull_request" if kind == "pull_request" else (
                "issue" if kind == "issue" else kind
            )
            url = link["url"]
            work[bucket].setdefault(
                url,
                {
                    "title": url,
                    "url": url,
                    "kind": bucket,
                    "source": "transcript",
                    "session": session["name"],
                },
            )
    return {kind: list(items.values()) for kind, items in work.items()}


def chip(text: str, cls: str = "") -> str:
    class_attr = f" chip {cls}".strip()
    return f'<span class="{class_attr}">{html.escape(text)}</span>'


def fmt_when(iso: str | None) -> str:
    if not iso:
        return ""
    try:
        moment = datetime.fromisoformat(iso)
    except ValueError:
        return iso
    return moment.strftime("%a %-d %b, %H:%M")


def auto_summary(payload: dict[str, Any]) -> str:
    sessions = payload["sessions"]
    if not sessions:
        return (
            f"<p>No saved Cursor sessions in {html.escape(payload['label'])}.</p>"
        )
    by_project: dict[str, int] = defaultdict(int)
    for session in sessions:
        by_project[session["project"]] += 1
    top = sorted(by_project.items(), key=lambda item: item[1], reverse=True)[:6]
    bullets = "".join(
        f"<li><strong>{html.escape(name)}</strong> — {count} session{'s' if count != 1 else ''}</li>"
        for name, count in top
    )
    work = payload.get("work") or {}
    prs = len(work.get("pull_request") or [])
    issues = len(work.get("issue") or [])
    extras = []
    if prs:
        extras.append(f"{prs} pull request{'s' if prs != 1 else ''}")
    if issues:
        extras.append(f"{issues} issue{'s' if issues != 1 else ''}")
    extra_clause = f" Linked work: {', '.join(extras)}." if extras else ""
    return (
        f"<p>{payload['stats']['sessions']} Cursor session"
        f"{'s' if payload['stats']['sessions'] != 1 else ''} across "
        f"{payload['stats']['projects']} project"
        f"{'s' if payload['stats']['projects'] != 1 else ''} "
        f"({html.escape(payload['label'])}).{extra_clause}</p>"
        f"<ul class=\"overview\">{bullets}</ul>"
    )


def render_session_card(session: dict[str, Any]) -> str:
    links = "".join(
        f'<a href="{html.escape(link["url"])}">{html.escape(link["kind"])}</a>'
        for link in session.get("links") or []
    )
    query = session.get("first_query") or session.get("subtitle") or ""
    when = " · ".join(filter(None, [fmt_when(session.get("created_at")), fmt_when(session.get("updated_at"))]))
    plus = session["lines_added"]
    minus = session["lines_removed"]
    stats = []
    if plus or minus:
        stats.append(f'<span class="plus">+{plus}</span> / <span class="minus">−{minus}</span>')
    if session["files_changed"]:
        stats.append(f'{session["files_changed"]} files')
    return f"""
    <article class="card">
      <h3>{html.escape(session["name"])} {chip(session.get("mode") or "agent", session.get("mode") or "")}</h3>
      <div class="when">{html.escape(when)}{" · " if stats else ""}{" · ".join(stats)}</div>
      {f'<p class="query">{html.escape(query)}</p>' if query else ""}
      {f'<div class="links">{links}</div>' if links else ""}
    </article>
    """


def render_projects(sessions: list[dict[str, Any]]) -> str:
    if not sessions:
        return '<p class="lede">No sessions in this range.</p>'
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for session in sessions:
        grouped[session["project"]].append(session)
    parts = []
    for name in sorted(grouped, key=lambda item: (-len(grouped[item]), item.lower())):
        cards = "".join(render_session_card(s) for s in grouped[name])
        ws = grouped[name][0].get("workspace") or ""
        parts.append(
            f'<h3 id="p-{html.escape(name)}">{html.escape(name)}</h3>'
            f'{f"<p class=\"lede\"><code>{html.escape(ws)}</code></p>" if ws else ""}'
            f"{cards}"
        )
    return "".join(parts)


def render_work_table(title: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    body = []
    for row in rows:
        label = row.get("title") or row.get("url")
        repo = row.get("repo") or row.get("session") or ""
        state = row.get("state") or row.get("source") or ""
        body.append(
            "<tr>"
            f'<td><a href="{html.escape(row.get("url") or "")}">{html.escape(str(label))}</a></td>'
            f"<td>{html.escape(str(repo))}</td>"
            f"<td>{html.escape(str(state))}</td>"
            "</tr>"
        )
    return (
        f"<h3>{html.escape(title)}</h3>"
        '<table class="work"><thead><tr><th>Item</th><th>Repo / source</th><th>State</th></tr></thead>'
        f"<tbody>{''.join(body)}</tbody></table>"
    )


def render_work(work: dict[str, list[dict[str, Any]]]) -> str:
    sections = [
        render_work_table("Pull requests", work.get("pull_request") or []),
        render_work_table("Issues", work.get("issue") or []),
        render_work_table("Linear", work.get("linear") or []),
        render_work_table("Notion", work.get("notion") or []),
        render_work_table("Google Docs", work.get("google_doc") or []),
        render_work_table("Other GitHub", work.get("github") or []),
    ]
    filled = [section for section in sections if section]
    if not filled:
        return '<p class="lede">No pull requests, issues, or linked documents found for this range.</p>'
    return "".join(filled)


def render_gaps(payload: dict[str, Any]) -> str:
    notes = list(payload.get("gaps") or [])
    if not payload["sessions"]:
        notes.append("No saved Cursor sessions overlapped this range.")
    if not notes:
        return '<p class="lede">Collector completed without gaps.</p>'
    items = "".join(f"<li>{html.escape(note)}</li>" for note in notes)
    return f'<div class="note warn"><ul class="overview">{items}</ul></div>'


def artifact_filename(start: datetime, end: datetime) -> str:
    start_day = start.strftime("%Y-%m-%d")
    end_day = (end - timedelta(seconds=1)).strftime("%Y-%m-%d")
    if start_day == end_day:
        return f"digest-{start_day}.html"
    return f"digest-{start_day}_to_{end_day}.html"


def render_html(payload: dict[str, Any], template: str) -> str:
    stats = payload["stats"]
    chips = " ".join(
        [
            chip(f"{stats['sessions']} sessions"),
            chip(f"{stats['projects']} projects"),
            chip(f"+{stats['lines_added']} / −{stats['lines_removed']}"),
        ]
    )
    cards = (
        f'<div class="card"><div class="stat">{stats["sessions"]}<span>Sessions</span></div></div>'
        f'<div class="card"><div class="stat">{stats["projects"]}<span>Projects</span></div></div>'
        f'<div class="card"><div class="stat"><span class="plus">+{stats["lines_added"]}</span> '
        f'<span class="minus">−{stats["lines_removed"]}</span><span>Line stats</span></div></div>'
    )
    replacements = {
        "{{TITLE}}": html.escape(payload["title"]),
        "{{RANGE_LABEL}}": html.escape(payload["label"]),
        "{{STATS_CHIPS}}": chips,
        "{{STAT_CARDS}}": cards,
        "{{SUMMARY}}": payload["summary_html"],
        "{{PROJECT_SECTIONS}}": payload["project_html"],
        "{{WORK_SECTIONS}}": payload["work_html"],
        "{{GAPS}}": payload["gaps_html"],
        "{{GENERATED_AT}}": html.escape(payload["generated_at"]),
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def rebuild_index(artifacts_dir: Path) -> Path:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(
        [p for p in artifacts_dir.glob("digest-*.html")],
        key=lambda path: path.name,
        reverse=True,
    )
    items = "".join(
        f'<li><a href="{html.escape(path.name)}">{html.escape(path.stem)}</a></li>'
        for path in files
    ) or "<li>No digests yet.</li>"
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Cursor digests</title>
<style>
  body {{ font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 40px auto; max-width: 720px; color: #1f2328; }}
  a {{ color: #0969da; }}
</style></head>
<body>
  <h1>Cursor digests</h1>
  <ul>{items}</ul>
</body></html>
"""
    target = artifacts_dir / "index.html"
    target.write_text(page, encoding="utf-8")
    return target


def build_payload(
    spec: str | None,
    now: datetime,
    db_path: Path,
    projects_root: Path,
    include_github: bool,
) -> dict[str, Any]:
    start, end, label = parse_range(spec, now)
    headers = load_headers(db_path)
    transcripts = index_transcripts(projects_root)
    sessions = collect_sessions(headers, start, end, transcripts)
    gaps: list[str] = []
    gh_prs: list[dict[str, Any]] = []
    gh_issues: list[dict[str, Any]] = []
    if include_github:
        gh_prs, pr_err = run_gh_search("prs", start, end)
        gh_issues, issue_err = run_gh_search("issues", start, end)
        if pr_err:
            gaps.append(f"GitHub PR search unavailable: {pr_err}")
        if issue_err:
            gaps.append(f"GitHub issue search unavailable: {issue_err}")
    else:
        gaps.append("GitHub search skipped.")
    work = merge_work(sessions, gh_prs, gh_issues)
    projects = sorted({session["project"] for session in sessions})
    stats = {
        "sessions": len(sessions),
        "projects": len(projects),
        "lines_added": sum(s["lines_added"] for s in sessions),
        "lines_removed": sum(s["lines_removed"] for s in sessions),
        "files_changed": sum(s["files_changed"] for s in sessions),
    }
    start_day = start.strftime("%Y-%m-%d")
    end_day = (end - timedelta(seconds=1)).strftime("%Y-%m-%d")
    title = (
        f"Cursor digest · {start.strftime('%d %b %Y')}"
        if start_day == end_day
        else f"Cursor digest · {start.strftime('%d %b')}–{end.strftime('%d %b %Y')}"
    )
    payload = {
        "title": title,
        "label": label,
        "range": {"start": start.isoformat(), "end": end.isoformat(), "spec": spec or "yesterday"},
        "generated_at": now.astimezone().strftime("%Y-%m-%d %H:%M %Z"),
        "sessions": sessions,
        "work": work,
        "stats": stats,
        "gaps": gaps,
        "filename": artifact_filename(start, end),
    }
    payload["summary_html"] = auto_summary(payload)
    payload["project_html"] = render_projects(sessions)
    payload["work_html"] = render_work(work)
    payload["gaps_html"] = render_gaps(payload)
    return payload


def write_outputs(payload: dict[str, Any], artifacts_dir: Path, json_path: Path | None, html_path: Path | None) -> dict[str, str]:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    if json_path is not None:
        slim = {
            key: payload[key]
            for key in (
                "title",
                "label",
                "range",
                "generated_at",
                "sessions",
                "work",
                "stats",
                "gaps",
                "filename",
            )
        }
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(slim, indent=2) + "\n", encoding="utf-8")
        written["json"] = str(json_path)
    if html_path is not None:
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(render_html(payload, template), encoding="utf-8")
        written["html"] = str(html_path)
        rebuild_index(artifacts_dir)
        written["index"] = str(artifacts_dir / "index.html")
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect Cursor sessions into a digest.")
    parser.add_argument("--range", default="yesterday", help="today | yesterday | last week | ISO date or range")
    parser.add_argument("--json", help="Write collector JSON to this path (use - for stdout)")
    parser.add_argument("--html", nargs="?", const="AUTO", help="Write HTML digest (default artifacts path if flag only)")
    parser.add_argument("--artifacts-dir", default=str(DEFAULT_ARTIFACTS))
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--projects-root", default=str(DEFAULT_PROJECTS))
    parser.add_argument("--no-github", action="store_true")
    parser.add_argument("--rebuild-index", action="store_true")
    args = parser.parse_args(argv)

    artifacts_dir = Path(os.path.expanduser(args.artifacts_dir))
    if args.rebuild_index:
        path = rebuild_index(artifacts_dir)
        print(path)
        return 0

    try:
        payload = build_payload(
            spec=args.range,
            now=datetime.now().astimezone(),
            db_path=Path(os.path.expanduser(args.db)),
            projects_root=Path(os.path.expanduser(args.projects_root)),
            include_github=not args.no_github,
        )
    except RangeError as exc:
        print(exc, file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    json_path: Path | None = None
    html_path: Path | None = None
    if args.json == "-":
        slim = {k: payload[k] for k in ("title", "label", "range", "generated_at", "sessions", "work", "stats", "gaps", "filename")}
        json.dump(slim, sys.stdout, indent=2)
        sys.stdout.write("\n")
    elif args.json:
        json_path = Path(os.path.expanduser(args.json))
    if args.html:
        html_path = (
            artifacts_dir / payload["filename"]
            if args.html == "AUTO"
            else Path(os.path.expanduser(args.html))
        )
    if json_path is None and html_path is None and args.json != "-":
        json_path = artifacts_dir / ".last.json"
        html_path = artifacts_dir / payload["filename"]

    written = write_outputs(payload, artifacts_dir, json_path, html_path)
    if written:
        print(json.dumps(written, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
