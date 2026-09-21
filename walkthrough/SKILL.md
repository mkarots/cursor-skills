---
name: walkthrough
description: >-
  Builds a standalone HTML walkthrough of a GitHub pull request so the
  structure, component connections, and key diffs are easy to see. Use when
  the user runs /walkthrough, asks for a PR walkthrough, or passes a
  github.com pull request URL.
disable-model-invocation: true
---

# PR walkthrough

Create a visual representation of the changes made in the PR for the user's better understanding. The representation should be in HTML, GitHub colors appreciated otherwise reuse some known and expected dark or light editor choices for code segments and similarly for text — no surprises there. Focus on the structure of the PR and the changes introduced. Also show the connections between the different components so the user understands dependencies. The walkthrough should render code segments correctly where possible, otherwise point to the equivalent lines in the pull request or code by providing a link. The skill takes as argument a GitHub URL pointing to a pull request.

## Invocation

```
/walkthrough https://github.com/<owner>/<repo>/pull/<n>
```

The URL is required. If the user omitted it, ask for it and stop. Do not invent a PR.

## Workflow

Copy this checklist and complete it in order:

```
- [ ] Parse the PR URL
- [ ] Fetch metadata, file list, and diff
- [ ] Group files and map dependencies
- [ ] Write HTML from template.html
- [ ] Verify links and open the page
```

### 1. Parse

Accept:

- `https://github.com/<owner>/<repo>/pull/<n>`
- `https://github.com/<owner>/<repo>/pull/<n>/...` (ignore the suffix)

Extract `owner`, `repo`, `n`.

### 2. Fetch (required)

Use `gh`. Do not guess file lists from memory.

```bash
gh pr view "<url>" --json title,body,number,url,headRefName,baseRefName,additions,deletions,changedFiles,files,commits,author
gh pr diff "<url>"
gh api "repos/<owner>/<repo>/pulls/<n>" --jq '{sha: .head.sha, html: .html_url}'
```

If `gh` fails (auth, private repo, missing CLI), say so and stop. Do not fabricate diffs.

Permalink base (prefer the head SHA):

```
https://github.com/<owner>/<repo>/blob/<sha>/<path>#L<start>-L<end>
https://github.com/<owner>/<repo>/pull/<n>/files
```

If a snippet cannot be quoted faithfully, do not approximate. Link the blob range and/or the Files tab instead.

### 3. Analyze

Read the changed files (local checkout if it matches `owner/repo`, otherwise `gh` + API). Answer:

1. What problem does this PR solve? (from title, body, and code — not marketing)
2. What is new vs what is only wired into existing code?
3. What calls what? Draw the runtime graph.
4. What did **not** change that a reader might assume changed?

Group files by role (new module, instrumentation, wiring, tests, docs). Ignore generated lockfile noise unless the PR is about dependencies.

### 4. Write the HTML

Copy [template.html](template.html) and fill every `{{PLACEHOLDER}}`. Do not restyle the page. Do not introduce new fonts, palettes, or animation.

Output path:

- Repo has `plans/` → `plans/PR<n>_<SLUG>_WALKTHROUGH.html`
- Else → `PR<n>_<SLUG>_WALKTHROUGH.html` at the repo root

`SLUG` is a short uppercase token from the title (`OPERATOR_UI`, `MCP_SERVER`). Overwrite an existing file for the same PR.

Required sections (already in the template):

1. **Header** — PR number, title, link, +/- stats, base ← head
2. **What changed** — 2–4 sentences, concrete
3. **Structure** — file groups, not a raw `git diff --stat`
4. **Connections** — a box-and-arrow diagram of components and data flow
5. **Key code** — 2–6 short snippets with line numbers and permalinks
6. **What stayed the same** — explicit non-goals
7. **How to verify** — commands from the PR test plan when present

### 5. Code snippets

- Quote the real text from the fetched SHA. Trim with `…` only at obvious gaps.
- Highlight with the template classes: `k` keyword, `s` string, `c` comment, `f` function, `t` type, `mi` number. Skip highlighting rather than guess.
- 8–25 lines per snippet. Prefer the public contract (`begin`, route table, new type) over internals.
- Every snippet caption is a link to the blob range. Add “View in PR” when the Files tab is more useful (large rewrite, binary, generated HTML).
- Never paste secrets, tokens, or `.env` values.

### 6. Connections diagram

Use the template’s `.graph` / `.node` / `.edge` markup (HTML + CSS). No Mermaid, no screenshots, no new JS layout libraries.

Show:

- who creates the new object
- who writes / who reads
- process boundaries (same process vs another process)
- the data file or network hop in between

One diagram is enough. A second is allowed only if Slack-path and other-path truly diverge.

### 7. Finish

- Open the HTML in the browser (`open <path>` on macOS, `xdg-open` on Linux) when a shell is available.
- Reply with the file path, the PR URL, and 3–5 bullets of what the walkthrough shows.
- Do not commit or open a follow-up PR unless the user asks.

## Non-goals

- Not a code review and not a merge recommendation.
- Not a restyle of the product UI.
- Do not include files that are not in the PR.
- Do not narrate every hunk. Structure first, then a few proof snippets.
