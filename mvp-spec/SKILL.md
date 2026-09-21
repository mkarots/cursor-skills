---
name: mvp-spec
description: >-
  Turns a product idea into a locked MVP spec: one user, one job, one
  demo, non-goals, and a first-build list. Writes a markdown founding
  brief and a canvas. Use when the user runs /mvp-spec, asks to spec an
  MVP, turn an idea into a product spec, write a founding brief, or
  scope the first version of a product.
disable-model-invocation: true
---

# MVP spec

Turn an idea into a spec a builder could ship against. Do not write product
code. Do not design the company. Lock a demo.

## Invocation

```
/mvp-spec <idea>
```

If the idea is missing, ask once and stop. Keep the user's wording. Do not
rebrand unless they asked.

## Workflow

Copy this checklist and complete it in order:

```
- [ ] Read the idea (and current-repo shape if this is a slice of it)
- [ ] Decide: new product vs slice of this repo
- [ ] Ask at most 3 questions — only at a fork that would be a different product
- [ ] Lock: one user, one job, one demo
- [ ] Write the markdown brief from spec-template.md
- [ ] Write the canvas from canvas.md
- [ ] Self-check, then stop
```

### 1. Read the room

If the idea is a slice of the **current repo's product**, read that product's
shape first (README, `docs/adr/`, `.cursor/rules/product-shape.mdc` if present).
Stay in shape. Do not spec a second SKU.

If it is a **new product**, do not inherit the current repo's constraints.

If a founding brief already exists for this idea, revise it. Do not start a
parallel spec.

### 2. Questions

Ask only when the answer would produce a different product (who pays, what the
demo proves, what must never ship). At most three. Otherwise pick a default,
label it as an assumption, and proceed.

Do not interview the user for a business plan.

### 3. Lock

Write these four lines in the reply **before** writing files:

1. **Who** — one person with a job, not a market segment
2. **Job** — the one thing they hire this for
3. **Demo** — the shortest path that proves the job, with pass/fail
4. **Cut** — the most tempting thing that is *not* in v0

If the demo needs a vendor partnership, an OAuth app store, a new model, or a
framework authors must rewrite for, it is the wrong first demo. Cut until two
surfaces and one new process are enough.

### 4. Write

Follow [spec-template.md](spec-template.md) for the markdown file.
Density target: [examples.md](examples.md).

Follow [canvas.md](canvas.md) for the canvas. Read
`~/.cursor/skills-cursor/canvas/SKILL.md` immediately before writing any
`.canvas.tsx`.

**Markdown path.** Prefer `plans/<slug>-mvp.md` in the current repo. Create
`plans/` if needed. If this is not a git repo, write `<slug>-mvp.md` at the
workspace root. Slug is kebab-case from the working name.

**Canvas path.**
`/Users/<user>/.cursor/projects/<workspace>/canvases/<slug>-mvp.canvas.tsx`

Both files are required. The markdown is the durable brief. The canvas is the
working view. Do not skip either.

Do not open a PR. Do not implement. Do not add a company site, pricing page, or
architecture beyond what the demo needs.

### 5. Self-check

Fix the files if any fail:

- A stranger could run the demo from the script alone
- First build includes only what the demo needs
- Every non-goal is something you were tempted to sneak in
- One term per concept; the one-sentence summary could be the homepage
- Canvas is not a column of identical cards; demo is the visual center
- No empty sections, placeholders, or "TBD" as content

## Product rules

These are load-bearing. Do not "improve" past them.

- **One independent unit of value.** A repo, a room, a workspace — not a
  seat. Name the unit. Do not default to per-seat pricing even as a later note.
- **Events, not merged brains.** If the idea involves multiple agents or
  tools, they stay themselves. Do not spec shared memory or a mega-assistant.
- **Local-folder-first when the product touches customer code.** Do not spec
  "we clone their GitHub." The folder is already on a machine they run.
- **Proof vs company.** v0 is allowed to be only the proof if it makes the
  demo undeniable. Do not pad the MVP with the company.
- **Isolation is the product** when the idea is per-project or per-space.
  Cross-project is an explicit exception, named, not the default.

## Chat output

After the files exist:

- The four lock lines
- Markdown path and canvas link (full absolute path, labeled)
- Say they can open the canvas beside the chat
- If this is the first canvas in the workspace, one sentence on what a canvas is
