---
name: landing-page-builder
description: >-
  Builds distinctive landing pages instead of generic AI-slop layouts.
  Follows Discover (seed or taste-led brief), Define (screenshot-only
  critic loop, optional image/motion), and Deliver (cut, kill AI tells,
  rewrite copy). Use when the user runs /landing-page or asks to build,
  redesign, or polish a landing page, marketing site, or hero page.
disable-model-invocation: true
---

# Landing page builder

Build a landing page that could only have come from this brief. Do not ship the default AI page: purple/indigo gradient, Inter, text-left / abstract-orb-right, pill nav, feature-card grid, glow.

Copy this checklist and complete it in order:

```
- [ ] Brief (product, audience, CTA, constraints)
- [ ] Discover (seed and/or taste direction)
- [ ] POC in the repo’s existing stack
- [ ] Critic loop (1–2 passes; stop rules below)
- [ ] Enrich (images/motion only if needed and tools exist)
- [ ] Deliver (cut, tells, copy)
- [ ] Verify in the browser
```

## Invocation

```
/landing-page <product> [optional aesthetic or references]
```

If the product is missing, ask once and stop.

## Discover

**If the user already named an aesthetic, metaphor, or references:** use that. Do not seed. Do not invent a competing theme.

**If they want options:** list 12–20 *short, high-level* directions. No mockups yet. Wait for their reaction, sharpen from their taste (likes, dislikes, “not cartoony”, “more texture”), then write a one-paragraph build brief. Do not paste an unedited AI idea list back into the build.

**Otherwise (default):** inject variety from outside the model.

1. Run [scripts/seed.sh](scripts/seed.sh). Do not invent the string.
2. Derive palette, type, layout, motion, and metaphor from the string (subpatterns, number fragments, letter runs). The string is inspiration only — never show it in the UI, source comments, or alt text.
3. Commit to one bold direction. Prefer ideas that feel slightly too ambitious.

Direction must answer: feeling to evoke, layout idea (not “hero + 3 cards”), type pairing, palette (not purple-by-default), what the primary visual *is*.

## Define

Implement a working POC in whatever the repo already uses (don’t add a new framework). Make opinionated structural choices in v1. Do **not** ban gradients/cards/labels in the first prompt to yourself — that creates weirder defaults. Strip tells in Deliver.

### Critic loop

Self-review of your own code does not count.

1. Render the page and capture screenshots (desktop + a mobile width).
2. Launch a **fresh** subagent with **only** the screenshots (and optional moodboard images). No code, no prior rationale, no scores-to-date. Use the prompt in [critic.md](critic.md) verbatim.
3. Apply the critic’s specific gaps. Same critic prompt every pass.
4. **Stop at 2 passes** unless scores are clearly rising. Never put “stop at 9/10” in the critic prompt. If a pass is ≤6 with no new structural insight, stop and ask the user.

Prefer a stronger model for the critic if one is available; keep implementing yourself.

### Images and motion (optional)

Skip unless the page is still “code shapes pretending to be a brand,” or the user asked for it.

- Use image generation only if a tool is already available. Never paste or invent API keys. If keys exist, read `.env.agents` (gitignored) — do not write keys into source.
- Prefer one strong generated image, shader, or 3D moment over a collage of stock-looking assets.
- Video/looping graphics and scroll-scrubbed keyframe transitions: see [motion.md](motion.md). Only if the user wants motion and an aggregator/key already exists.

Verify any generated asset in the browser, frame by frame if animated.

## Deliver

AI adds. Premium pages subtract. After the critic, do a subtractive pass using [polish.md](polish.md):

1. Remove anything that doesn’t help the CTA or the feeling.
2. Scan the AI-tells list. Replace defaults that aren’t earning their place — don’t blanket-ban.
3. Rewrite **all** visible copy as if a human editor will ship it: shorter, specific, no filler. Treat first-draft marketing prose as lorem ipsum.
4. Prefer native/simple controls over custom chrome that looks worse.

## Verify

Use the browser. Click, type, submit, resize. Check empty/error states and the mobile layout. Fix what you find before claiming done.

## Output to the user

- Direction in one sentence (feeling + layout idea)
- What you cut and which tells you replaced
- Final copy, called out so they can rewrite it
- How to open/run the page
