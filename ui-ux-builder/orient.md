# Orient (before any theme)

Do this first. Do not seed, propose themes, or write CSS until you can say what the product is in plain language.

## Goal

A short product readback the user can correct:

- What it is (one sentence)
- Who it’s for
- What this surface is for (the job)
- Existing visual language (type, color, density, metaphors already in the repo) — even if you will later depart from it
- What you will not invent (features, data, frameworks)

If the readback would be guesswork, keep looking. If sources conflict, say so.

## Where to look (stop when the readback is solid)

Use what’s there. Don’t invent a GitHub tour if a README already answers it.

1. **Docs in the repo** — `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/`, `CHANGELOG.md`, package description, existing design notes.
2. **GitHub** (if this is a git repo with a remote) — `gh repo view`, repo description/topics, the README on origin if local docs are thin. Only fetch issues/PRs if they explain the product or this surface.
3. **Code** — the app entry (e.g. `index.html`), shared theme/CSS tokens, catalog/copy, the target surface and its parents. Prefer existing tokens and components over a new palette that fights the rest of the app.

Also open the current surface and one neighboring screen so the job is visible, not just described.

## Don’t

- Skip this because the user named a file
- Treat a walkthrough, settings page, or empty state as the whole product
- Propose “SaaS dashboard” / “purple glow” themes that ignore what you just read
- Copy the existing look slavishly unless they asked to extend the current theme — you still have to *know* it
