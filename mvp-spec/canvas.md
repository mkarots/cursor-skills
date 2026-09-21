# MVP spec canvas

Read `~/.cursor/skills-cursor/canvas/SKILL.md` and the `cursor/canvas` SDK
declarations before writing. One `.canvas.tsx` file. Import only from
`cursor/canvas`. Embed all content inline. Default-export the page component.

Filename: `<slug>-mvp.canvas.tsx` in the workspace `canvases/` directory.

When you mention the canvas, link the full absolute path.

## Purpose

A stranger should see the lock in one screen: who, job, demo, cut, first
build. The markdown holds the argument. The canvas holds the decision.

## Layout

Use `Stack` as the page. Mix open sections with cards. Do not wrap every
block in `Card`. No charts unless the spec has real numbers. No empty
sections. No placeholders.

```
Stack
  H1 working name
  Text one-sentence summary (the thesis, not a tagline)
  Row of 3 Stats: User · Job · Demo time-to-wow
  Divider
  Grid 2 columns
    Card "In v0" — Pills or a short list from First build
    Card "Out of v0" — the cuts; use a quieter tone
  H2 Locked demo          ← visual center, more space
  Card
    CardHeader title + pass/fail Pill
    CardBody: stage, then numbered script
    Callout: what you are proving
  H2 First build
  TodoList — every item status "pending"
  H2 Rejected
  Table: option | why rejected (from Alternatives)
  CollapsibleSection "Open questions"
    only if there are real questions; otherwise omit
```

## Hierarchy

The locked demo is the thing that stands out. Stats are compact. Cuts sit
beside v0 so the product is defined by what it refuses. First build is a
checklist, not a paragraph.

## Tokens and slop

Colors from `useHostTheme()` only. No gradients, emojis, box-shadows, rainbow
pills, or a wall of identical cards. Most surfaces neutral; accent on the
demo card or the pass/fail pill.

`Pill` for in/out items if there are few (≤8). `Table` if there are many.
`Callout` for pass/fail or a load-bearing invariant — at most two callouts.

## Data

Copy from the markdown you just wrote. Do not invent a second thesis for the
canvas. If a section would be empty, omit it.

Do not put the full terminology table or the session transcript on the
canvas. Those stay in the markdown.
