---
name: cursor-digest
description: >-
  Summarizes saved Cursor sessions for a natural-language date range
  (today, yesterday, last week) and the matching GitHub pull requests,
  issues, documents, and tasks, then writes a standalone HTML digest.
  Use when the user runs /cursor-digest or asks for a Cursor session
  digest, daily recap, or yesterday's work summary.
disable-model-invocation: true
---

# Cursor digest

Build an HTML recap of **saved Cursor sessions** in a date range, plus the
equivalent work those sessions produced (PRs, issues, docs, tasks).

## Invocation

```
/cursor-digest
/cursor-digest today
/cursor-digest yesterday
/cursor-digest last week
/cursor-digest this week
/cursor-digest 2026-09-15
/cursor-digest 2026-09-08..2026-09-14
```

If the date argument is omitted, use **yesterday** (the previous local
calendar day). That is the scheduled morning-digest default.

Resolve the range in the machine's local timezone. Do not invent sessions.

## Output

Write a standalone HTML file under:

```
~/Projects/cursor-digest-artifacts/
```

Names:

- Single day → `digest-YYYY-MM-DD.html`
- Range → `digest-YYYY-MM-DD_to_YYYY-MM-DD.html`

Also refresh `index.html` in that directory. Overwrite an existing file for
the same range. Then open the digest (`open <path>` on macOS).

## Workflow

Copy this checklist and complete it in order:

```
- [ ] Parse the date range
- [ ] Collect sessions (required script)
- [ ] Enrich GitHub / docs / tasks
- [ ] Write HTML from template.html
- [ ] Open the artifact and reply
```

### 1. Parse

Accept the argument as a duration, not a search query.

| Input | Range (local tz) |
| --- | --- |
| omitted / `yesterday` | previous calendar day, `[00:00, next 00:00)` |
| `today` | today 00:00 → now |
| `last week` / `past week` | today minus 7 days, 00:00 → now |
| `this week` | Monday 00:00 → now |
| `YYYY-MM-DD` | that calendar day |
| `YYYY-MM-DD..YYYY-MM-DD` | inclusive start day through end day 24:00 |

Unknown input: say so and stop. Do not guess a range.

### 2. Collect (required)

Run the collector. Do not invent a session list from memory.

```bash
python3 ~/.cursor/skills/cursor-digest/scripts/collect.py \
  --range "<ARGUMENT_OR_yesterday>" \
  --json "$HOME/Projects/cursor-digest-artifacts/.last.json"
```

The script reads:

- Session index: `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` (`composerHeaders`)
- Transcripts: `~/.cursor/projects/*/agent-transcripts/<id>/<id>.jsonl`
- GitHub (best-effort): `gh search` for PRs and issues you authored/updated in the window

If the collector fails, report the error and stop. If `gh` is unauthenticated,
continue with transcript-extracted links only and note the gap in the HTML.

Skip subagent / best-of-N child sessions. Skip empty drafts with no title,
no transcript, and no line stats.

### 3. Enrich

From collector JSON + `gh` (when it works):

- **Sessions** — title, project, mode, time, first user request, +/− lines
- **Pull requests** — opened, updated, or merged in the window; link them
- **Issues** — created or updated; link them
- **Documents / tasks** — `linear.app`, `notion.so`, `docs.google.com`,
  and other tracker URLs found in transcripts. Do not invent URLs.
- **Repos / branches** — from `trackedGitRepos` on the session

For 1–3 unclear titles, read the matching transcript's first user message
only. Do not reread every chat.

Never paste secrets, tokens, `.env` values, or keyring output.

### 4. Write the HTML

Copy [template.html](template.html) and fill every `{{PLACEHOLDER}}`.
Do not restyle the page. Do not add fonts, palettes, animation, or emoji.

Required sections (already in the template):

1. **Header** — range label, generated-at, session / project / line chips
2. **Overview** — 1 short paragraph + 3–7 bullets of what actually happened
3. **By project** — sessions grouped by workspace, each with a 1–2 sentence
   recap (not a transcript dump)
4. **Equivalent work** — PRs, issues, documents, tasks, with links
5. **Gaps** — collector/`gh` failures, empty projects, nothing-found

Overview rules:

- Concrete: named projects, named PRs/issues, named deliverables
- Group related sessions ("three chats on X landed PR #N")
- If a session has no equivalent GitHub/doc artifact, say what the chat
  produced instead (plan, prototype, debug, research)
- If there were no sessions, say so and still write the HTML

If the collector already wrote a mechanical HTML next to the JSON, replace
the Overview (and tighten session blurbs) rather than restyling.

Refresh `index.html` by running:

```bash
python3 ~/.cursor/skills/cursor-digest/scripts/collect.py --rebuild-index
```

### 5. Finish

- Open the digest in the browser when a shell is available.
- Reply with the file path and 3–7 bullets of the recap.
- Do not commit the artifact unless the user asks.

## Scheduled run

The morning job is a macOS Launch Agent, 10:00 local time, label
`com.cursor.digest.daily`. It runs
[scripts/run-digest.sh](scripts/run-digest.sh), which collects **yesterday**
and writes the HTML artifact (then opens it). Re-run `/cursor-digest yesterday`
in Cursor when you want a tighter written overview on top of that file.

Do not reinstall or unload that agent unless the user asks.

## Non-goals

- Not a code review and not a timesheet.
- Do not summarize chats outside the requested range.
- Do not include subagent transcripts as top-level sessions.
- Do not dump full conversations into the HTML.
