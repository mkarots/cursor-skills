# Spec template

Write a markdown founding brief. Short sentences. Active voice. One idea per
paragraph. No unstated assumptions.

Fill every section. If a section has nothing true to say, delete it — do not
leave a heading over a shrug.

Status line: `Draft` until the user locks it. Date today. Working name in the
title, even if it will change.

```markdown
# <Working name> — MVP spec

Status: Draft
Date: YYYY-MM-DD

One-sentence summary:
<what it is, for whom, the proof it must produce>

## 1. Overview

**What.** One paragraph. Concrete. Observable.

**Why.** The job that exists without this product. Who does it today, and how
badly.

**When to use this document.** Starting the repo, writing v0, or rehearsing
the demo. If a later idea fights the locked demo, the demo wins until this
brief is revised.

## 2. Non-Goals

Not in v0. Each bullet is a tempting extra, not a category ("no enterprise").
Five to ten. Include the company-shaped version of the idea if it is not the
demo.

## 3. Key Concepts & Terminology

A table. Use these words only. One term per concept.

End with one sentence that must stay true.

## 4. Who and the job

- **User.** One person. Role and situation, not a TAM.
- **Job.** What they hire this to do, in their words if you have them.
- **Surface.** Where they already work (Slack, a URL, an IDE, a phone).
- **Unit of value.** What you would charge for later (workspace, repo, room).
  Not seats.

## 5. High-Level Design

The smallest system that makes the demo true. Main parts, data flow in 1–2
paragraphs, then numbered invariants.

Do not design year-two architecture. Names may change; the shape should not.

## 6. Locked demo

This is the product until a later brief replaces it.

**Title.** One line.

**Stage.** Which windows, devices, or channels. Name them.

**Script.** Numbered steps a stranger can follow. Setup must be short.

**Pass/fail.** The demo fails if… Be specific (too many pastes, no artifact,
human still the glue).

**What you are proving.** One paragraph. The claim, not the stack.

## 7. Edge Cases & Failure Modes

Only failures that kill the demo or lie to the user. For each: what happens,
how v0 handles it, what is guaranteed. Say ugly fallbacks out loud.

## 8. Constraints & Assumptions

Environment, auth, what already exists, what you refuse to require. Label
guesses as assumptions.

## 9. Alternatives Considered

Each row: the option, why it was rejected. Do not defend. Include the
obvious existing tool ("just use Slack / a spreadsheet / GitHub").

## 10. Open Questions

Real uncertainty. Not fake TBD. Not blockers you already decided.

## 11. First build

Build only what the locked demo needs. Numbered. Three to six items. The
last item is the rehearsal of §6, not a landing page.

Do not build adapters, auth, pricing, or a company site until the demo has
passed once.
```

## Writing bar

Steal the density of a locked thesis, not a pitch deck.

- Front-load: what it is, why it matters, when to use the doc
- Examples before theory; the demo before the architecture
- Rejected options get a reason, not a strawman
- Do not pad with TAM, personas, or "north star" slides
- If a sentence could be the homepage, it belongs in the one-sentence summary
- If a sentence is strategy for later, it belongs in Non-Goals or Open Questions
