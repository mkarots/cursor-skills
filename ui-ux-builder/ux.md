# UX pass (product surfaces)

Read this before the POC when the UI is a tool, form, table, nav, or multi-state screen. Skip it for a purely narrative static page with no controls.

## Hierarchy

- One primary action per view. Secondary actions are quieter, not equally loud.
- The content they came for (data, editor, diff, canvas) gets the most area. Chrome is thin.
- Density should match the job: a merge inspector can be tight; onboarding can breathe. Don’t split the difference into medium-padding everywhere.

## States

If the surface already has these, they must look designed, not leftover:

| State | Bar |
| --- | --- |
| Populated | Primary visual is readable; action is findable |
| Empty | Says what’s missing and the next step. No cute illustration unless it teaches. |
| Loading | Placeholder matches the real layout |
| Error | What failed, what to do, how to retry |
| Permission / logged out | Honest about the gate; no fake filled-in app |

Do not invent states the product doesn’t have.

## Interaction

- Native controls unless a custom one is clearly better.
- Visible focus. Keyboard order matches visual order.
- Don’t trap scroll in nested panes without a reason.
- Destructive actions need a confirm or an undo the product already uses — don’t invent a new pattern.

## Navigation

- One way to move, used consistently.
- Don’t add a marketing-style sticky pill nav to an app that already has a shell.
- If you change how state is written, check every other screen that reads it.

## Tables, code, forms

- Align numbers. Don’t card-wrap every row.
- Code is for reading: line numbers, overflow, contrast. Don’t theme it into unreadability.
- Forms: label, control, error. Not label, helper, tooltip, placeholder, and footnote saying the same thing.
