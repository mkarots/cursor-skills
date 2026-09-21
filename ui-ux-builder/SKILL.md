---
name: ui-ux-builder
description: >-
  Builds distinctive product UI after first reading the repo (docs, GitHub,
  or code) and optionally proposing themes. Same critic/polish loop as
  landing-page-builder, for app screens, dashboards, docs, walkthroughs,
  and settings — not marketing landings. Use when the user runs /ui-ux or
  /ui-ux-builder, or asks to redesign, restyle, or polish an interface.
disable-model-invocation: true
---

# UI/UX builder

Build an interface that could only have come from this brief. Do not ship the default AI UI: purple/indigo, Inter, sidebar + KPI cards, pill soup, glow, three identical feature tiles.

This is [landing-page-builder](../landing-page-builder/SKILL.md) transferred to product surfaces. Same critic/polish loop. Different job: someone is trying to **finish a task**, not be converted. **Orient on the real product before any theme.**

Marketing landing page / hero / campaign site → use landing-page-builder. If they attached this skill anyway, still run this loop; do not turn a tool UI into a landing page.

Copy this checklist and complete it in order:

```
- [ ] Orient (docs, GitHub, and/or code — product readback)
- [ ] Brief (surface, job, primary action, states, constraints)
- [ ] Discover (propose themes unless they already named one)
- [ ] POC in the repo’s existing stack
- [ ] Critic loop (1–2 passes; stop rules below)
- [ ] Enrich (images/motion only if needed and tools exist)
- [ ] Deliver (cut, tells, copy)
- [ ] Verify in the browser (the job, not just the look)
```

## Invocation

```
/ui-ux-builder <surface> [optional aesthetic or references]
```

If the surface is missing (which screen, file, or flow), ask once and stop.

## Orient

Required. Follow [orient.md](orient.md). Do not design, seed, or list themes until you have a product readback grounded in **documentation, GitHub, or code** (whichever exists).

Show the user a short readback (what it is, who it’s for, what this surface does, what visual language already exists). If they correct it, believe them.

## Brief

Write this down before designing. Do not skip it.

- **Surface** — the screen(s) or file(s). Restyle vs restructure vs new surface: pick one unless they asked for more.
- **Job** — who and what they came to finish.
- **Primary action** — the one control that completes the job (submit, merge, save, continue, copy, run).
- **States** — empty, loading, error, success, permission/logged-out, dense data. Design the populated state first; do not leave the others as afterthoughts if they already exist.
- **Constraints** — existing stack (do not add a framework), what data must stay accurate, a11y, what is out of scope.

The primary visual should be the thing they came to use (table, form, code, canvas, map, diff) — composed with intent, not parked next to a decorative graphic.

## Discover

Themes come **after** Orient. They must fit this product (audience, job, existing tokens, tone). A random “night dispatch board” on a kids’ quiz hub is a miss even if it looks distinctive.

**If the user already named an aesthetic, metaphor, or references:** use that on top of the product readback. Do not seed. Do not invent a competing theme. Skip the proposal list.

**Otherwise (default): propose themes and wait.** List **5** *short, high-level* directions that could only belong to this product. No mockups yet. Include 1 that extends the current visual language and 4 that are a bold but plausible departure. Wait for their reaction (likes, dislikes, “not cartoony”, “more like the hub”). Then write a one-paragraph build brief. Do not paste an unedited AI idea list back into the build.

**If they say “just pick” / “you choose”:** still propose a short list in the same message, then commit to one and say why it fits the product.

**Seed (optional, never instead of Orient):** if the shortlist needs variety from outside the model, run [scripts/seed.sh](scripts/seed.sh). Do not invent the string. Derive palette/type/layout *within* the product brief (subpatterns, number fragments, letter runs). The string is inspiration only — never show it in the UI, source comments, or alt text. Discard a seed-derived idea that contradicts the product.

Direction must answer: feeling to evoke, layout idea, type pairing, palette (not purple-by-default), what the primary visual *is*.

Layout idea is not “hero + 3 cards” and not “sidebar + KPI row + card grid”. Name the actual composition (e.g. “sticky runbook spine + maple code slips on onyx”, “single ledger with a joining rail”, “dense inspector, no page chrome”).

## Define

Implement a working POC in whatever the repo already uses. Make opinionated structural choices in v1. Do **not** ban gradients/cards/labels in the first prompt to yourself — that creates weirder defaults. Strip tells in Deliver.

Keep business logic, routes, and data contracts intact unless the brief says otherwise. Restyling is not a rewrite of the product.

Read [ux.md](ux.md) before the POC if the surface has forms, tables, navigation, or more than one state.

### Critic loop

Self-review of your own code does not count.

1. Render the UI and capture screenshots: a real working width (desktop or the actual app width) **and** a narrow/mobile width if the UI is responsive. Include one non-happy state if it already exists (empty or error).
2. Launch a **fresh** subagent with **only** the screenshots (and optional moodboard images). No code, no prior rationale, no scores-to-date. Use the prompt in [critic.md](critic.md) verbatim.
3. Apply the critic’s specific gaps. Same critic prompt every pass.
4. **Stop at 2 passes** unless scores are clearly rising. Never put “stop at 9/10” in the critic prompt. If a pass is ≤6 with no new structural insight, stop and ask the user.

Prefer a stronger model for the critic if one is available; keep implementing yourself.

### Images and motion (optional)

Skip unless the UI is still “code shapes pretending to be a brand,” or the user asked for it. Product chrome rarely needs generated art; a walkthrough or empty state might.

- Use image generation only if a tool is already available. Never paste or invent API keys. If keys exist, read `.env.agents` (gitignored) — do not write keys into source.
- Prefer one strong generated image, shader, or 3D moment over a collage of stock-looking assets.
- Video/looping graphics and scroll-scrubbed keyframe transitions: see [motion.md](motion.md). Only if the user wants motion and an aggregator/key already exists.

Verify any generated asset in the browser, frame by frame if animated.

## Deliver

AI adds. Premium UI subtracts. After the critic, do a subtractive pass using [polish.md](polish.md):

1. Remove anything that doesn’t help the primary action or the feeling.
2. Scan the AI-tells list. Replace defaults that aren’t earning their place — don’t blanket-ban.
3. Rewrite **all** visible copy as if a human editor will ship it: shorter, specific, no filler. Labels name the control’s job. Errors say what happened and what to do. Treat first-draft marketing prose as lorem ipsum — including on utility screens that grew a fake headline.
4. Prefer native/simple controls over custom chrome that looks worse.

## Verify

Use the browser. Exercise the job the way a real user would: click, type, submit, navigate. A single render screenshot is not verification.

- Check every screen that shares the state, data, or components you touched.
- Hit empty / error / permission if those states exist.
- Resize if layout changed. Keyboard and focus if you added controls.
- Fix what you find before claiming done.

If no browser tools are available, say so and verify with the closest substitute (tests, curl, a render script).

## Output to the user

**After Orient, before building:** product readback + **5 themes** (unless they already named a look). Wait.

**After the UI ships:**

- Direction in one sentence (feeling + layout idea)
- What you cut and which tells you replaced
- Final copy, called out so they can rewrite it
- How to open/run the UI
- Which states and widths you actually checked
