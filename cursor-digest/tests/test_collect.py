#!/usr/bin/env python3
"""Unit tests for cursor-digest collect.py."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import collect  # noqa: E402


TZ = ZoneInfo("Europe/London")
NOW = datetime(2026, 9, 16, 22, 5, tzinfo=TZ)


def make_db(rows: list[tuple]) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".vscdb", delete=False)
    path = Path(tmp.name)
    tmp.close()
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE composerHeaders ("
        "composerId TEXT, workspaceId TEXT, createdAt INTEGER, "
        "lastUpdatedAt INTEGER, isSubagent INTEGER, value TEXT)"
    )
    conn.executemany(
        "INSERT INTO composerHeaders VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    return path


def header_value(**overrides) -> str:
    payload = {
        "type": "head",
        "composerId": overrides.get("composerId", "aaa"),
        "name": "Landing page for ekzek",
        "unifiedMode": "agent",
        "totalLinesAdded": 120,
        "totalLinesRemoved": 4,
        "filesChangedCount": 3,
        "subtitle": "Edited index.html",
        "workspaceIdentifier": {
            "uri": {"fsPath": "/Users/example/Projects/ekzek"}
        },
        "trackedGitRepos": [
            {
                "repoPath": "/Users/example/Projects/ekzek",
                "branches": [{"branchName": "main"}],
            }
        ],
    }
    payload.update(overrides)
    return json.dumps(payload)


def write_transcript(root: Path, composer_id: str, query: str, extra: str = "") -> Path:
    project = root / "Users-example-Projects-ekzek" / "agent-transcripts" / composer_id
    project.mkdir(parents=True)
    path = project / f"{composer_id}.jsonl"
    text = (
        f"<timestamp>Tuesday, Sep 15, 2026, 11:24 PM (UTC+1)</timestamp>"
        f"<user_query>\n{query}\n</user_query>{extra}"
    )
    row = {
        "role": "user",
        "message": {"content": [{"type": "text", "text": text}]},
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    return path


class ParseRangeTests(unittest.TestCase):
    def test_yesterday(self):
        start, end, label = collect.parse_range("yesterday", NOW)
        self.assertEqual(start.isoformat(), "2026-09-15T00:00:00+01:00")
        self.assertEqual(end.isoformat(), "2026-09-16T00:00:00+01:00")
        self.assertIn("15 September 2026", label)

    def test_default_is_yesterday(self):
        start_a, end_a, _ = collect.parse_range(None, NOW)
        start_b, end_b, _ = collect.parse_range("yesterday", NOW)
        self.assertEqual(start_a, start_b)
        self.assertEqual(end_a, end_b)

    def test_today(self):
        start, end, _ = collect.parse_range("today", NOW)
        self.assertEqual(start.isoformat(), "2026-09-16T00:00:00+01:00")
        self.assertEqual(end, NOW)

    def test_last_week(self):
        start, end, _ = collect.parse_range("last week", NOW)
        self.assertEqual(start.isoformat(), "2026-09-09T00:00:00+01:00")
        self.assertEqual(end, NOW)

    def test_this_week_starts_monday(self):
        start, end, _ = collect.parse_range("this week", NOW)
        self.assertEqual(start.weekday(), 0)
        self.assertEqual(start.isoformat(), "2026-09-14T00:00:00+01:00")
        self.assertEqual(end, NOW)

    def test_iso_day(self):
        start, end, label = collect.parse_range("2026-09-15", NOW)
        self.assertEqual(start.isoformat(), "2026-09-15T00:00:00+01:00")
        self.assertEqual(end.isoformat(), "2026-09-16T00:00:00+01:00")
        self.assertIn("15 September", label)

    def test_iso_range_inclusive(self):
        start, end, label = collect.parse_range("2026-09-08..2026-09-14", NOW)
        self.assertEqual(start.isoformat(), "2026-09-08T00:00:00+01:00")
        self.assertEqual(end.isoformat(), "2026-09-15T00:00:00+01:00")
        self.assertIn("08 Sep", label)

    def test_reversed_range_errors(self):
        with self.assertRaises(collect.RangeError):
            collect.parse_range("2026-09-14..2026-09-08", NOW)

    def test_unknown_range_errors(self):
        with self.assertRaises(collect.RangeError):
            collect.parse_range("next tuesday-ish", NOW)


class LinkAndQueryTests(unittest.TestCase):
    def test_extracts_github_linear_notion_docs(self):
        text = """
        see https://github.com/acme/app/pull/12 and
        https://github.com/acme/app/issues/9,
        https://linear.app/acme/issue/APP-1 plus
        https://notion.so/doc-abc and
        https://docs.google.com/document/d/xyz/edit
        skip https://example.com/secret
        """
        links = {item["kind"]: item["url"] for item in collect.extract_links(text)}
        self.assertEqual(links["pull_request"], "https://github.com/acme/app/pull/12")
        self.assertEqual(links["issue"], "https://github.com/acme/app/issues/9")
        self.assertIn("linear", links)
        self.assertIn("notion", links)
        self.assertIn("google_doc", links)
        self.assertNotIn("https://example.com/secret", {i["url"] for i in collect.extract_links(text)})

    def test_strips_trailing_punctuation(self):
        links = collect.extract_links("PR at https://github.com/acme/app/pull/3.")
        self.assertEqual(links[0]["url"], "https://github.com/acme/app/pull/3")

    def test_first_user_query_ignores_noise(self):
        blob = "<timestamp>x</timestamp>\n<user_query>\n  Fix the login redirect  \n</user_query>"
        self.assertEqual(collect.first_user_query(blob), "Fix the login redirect")

    def test_missing_query_is_empty(self):
        self.assertEqual(collect.first_user_query("hello"), "")


class SessionCollectTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        yesterday_ms = int(datetime(2026, 9, 15, 15, 0, tzinfo=TZ).timestamp() * 1000)
        today_ms = int(datetime(2026, 9, 16, 10, 0, tzinfo=TZ).timestamp() * 1000)
        old_ms = int(datetime(2026, 9, 1, 10, 0, tzinfo=TZ).timestamp() * 1000)
        self.rows = [
            ("sess-yes", "ws", yesterday_ms, yesterday_ms, 0, header_value(composerId="sess-yes")),
            ("sess-sub", "ws", yesterday_ms, yesterday_ms, 1, header_value(composerId="sess-sub", name="subagent")),
            ("sess-old", "ws", old_ms, old_ms, 0, header_value(composerId="sess-old", name="too old")),
            ("sess-today", "ws", today_ms, today_ms, 0, header_value(composerId="sess-today", name="today work")),
            (
                "sess-empty",
                "ws",
                yesterday_ms,
                yesterday_ms,
                0,
                header_value(
                    composerId="sess-empty",
                    name="",
                    totalLinesAdded=0,
                    totalLinesRemoved=0,
                    filesChangedCount=0,
                    subtitle="",
                ),
            ),
            (
                "sess-digest",
                "ws",
                yesterday_ms,
                yesterday_ms,
                0,
                header_value(composerId="sess-digest", name="Cursor digest"),
            ),
        ]
        self.db = make_db(self.rows)
        write_transcript(self.root, "sess-yes", "Build the fleet landing page\nhttps://github.com/acme/ekzek/pull/4")
        write_transcript(self.root, "sess-digest", "/cursor-digest yesterday")

    def tearDown(self):
        Path(self.db).unlink(missing_ok=True)
        self.tmpdir.cleanup()

    def test_yesterday_keeps_parent_skips_subagent_empty_and_digest(self):
        start, end, _ = collect.parse_range("yesterday", NOW)
        headers = collect.load_headers(self.db)
        transcripts = collect.index_transcripts(self.root)
        sessions = collect.collect_sessions(headers, start, end, transcripts)
        ids = {s["id"] for s in sessions}
        self.assertEqual(ids, {"sess-yes"})
        session = sessions[0]
        self.assertEqual(session["project"], "ekzek")
        self.assertIn("fleet landing", session["first_query"])
        self.assertEqual(session["links"][0]["kind"], "pull_request")
        self.assertEqual(session["repos"][0]["branches"], ["main"])

    def test_today_excludes_yesterday(self):
        start, end, _ = collect.parse_range("today", NOW)
        headers = collect.load_headers(self.db)
        sessions = collect.collect_sessions(headers, start, end, {})
        self.assertEqual([s["id"] for s in sessions], ["sess-today"])

    def test_missing_updated_at_does_not_crash(self):
        self.assertFalse(
            collect.session_in_range(
                {"_lastUpdatedAt": None, "_createdAt": None},
                *collect.parse_range("yesterday", NOW)[:2],
            )
        )


class HtmlTests(unittest.TestCase):
    def test_escapes_session_names(self):
        html_out = collect.render_session_card(
            {
                "name": "<script>x</script>",
                "mode": "agent",
                "created_at": "2026-09-15T15:00:00+01:00",
                "updated_at": "2026-09-15T16:00:00+01:00",
                "lines_added": 2,
                "lines_removed": 1,
                "files_changed": 1,
                "first_query": "a & b",
                "links": [],
            }
        )
        self.assertNotIn("<script>", html_out)
        self.assertIn("&lt;script&gt;", html_out)
        self.assertIn("a &amp; b", html_out)

    def test_artifact_filename_single_and_range(self):
        start, end, _ = collect.parse_range("yesterday", NOW)
        self.assertEqual(collect.artifact_filename(start, end), "digest-2026-09-15.html")
        start, end, _ = collect.parse_range("2026-09-08..2026-09-14", NOW)
        self.assertEqual(
            collect.artifact_filename(start, end),
            "digest-2026-09-08_to_2026-09-14.html",
        )

    def test_empty_summary(self):
        text = collect.auto_summary(
            {"sessions": [], "label": "Tuesday 15 September 2026", "stats": {"sessions": 0, "projects": 0}}
        )
        self.assertIn("No saved Cursor sessions", text)

    def test_rebuild_index_lists_digests(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "digest-2026-09-15.html").write_text("x", encoding="utf-8")
            index = collect.rebuild_index(folder)
            body = index.read_text(encoding="utf-8")
            self.assertIn("digest-2026-09-15.html", body)

    def test_merge_work_dedupes_urls(self):
        sessions = [
            {
                "name": "s",
                "links": [
                    {"url": "https://github.com/acme/app/pull/1", "kind": "pull_request"}
                ],
            }
        ]
        gh = [
            {
                "url": "https://github.com/acme/app/pull/1",
                "title": "Fix login",
                "repo": "acme/app",
            }
        ]
        work = collect.merge_work(sessions, gh, [])
        self.assertEqual(len(work["pull_request"]), 1)
        self.assertEqual(work["pull_request"][0]["title"], "Fix login")


class EndToEndFixtureTests(unittest.TestCase):
    def test_build_payload_writes_html_placeholders(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        yesterday_ms = int(datetime(2026, 9, 15, 15, 0, tzinfo=TZ).timestamp() * 1000)
        db = make_db(
            [
                (
                    "sess-yes",
                    "ws",
                    yesterday_ms,
                    yesterday_ms,
                    0,
                    header_value(composerId="sess-yes"),
                )
            ]
        )
        write_transcript(root, "sess-yes", "Ship the sandbox")
        try:
            payload = collect.build_payload(
                spec="yesterday",
                now=NOW,
                db_path=db,
                projects_root=root,
                include_github=False,
            )
            self.assertEqual(payload["stats"]["sessions"], 1)
            self.assertIn("ekzek", payload["summary_html"])
            template = (SKILL_DIR / "template.html").read_text(encoding="utf-8")
            html_out = collect.render_html(payload, template)
            self.assertNotIn("{{TITLE}}", html_out)
            self.assertIn("Landing page for ekzek", html_out)
            self.assertIn("GitHub search skipped", html_out)
        finally:
            Path(db).unlink(missing_ok=True)
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
