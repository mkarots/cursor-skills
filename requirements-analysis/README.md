# Requirements analysis — how to use it

Personal Cursor skill. Path: `~/.cursor/skills/requirements-analysis/`

It turns an informal problem (a paragraph, a feedback dump, a product
idea, “the thing we just discussed”) into a **requirements record**:
environment model, goal hierarchy, constraints, external interfaces.

It does **not** write code, mockups, or a functional specification.
Interface *details* come later. This stage names boundaries and
formalizes the customer's real problem.

The skill does **not** auto-run. Attach it or type the slash command.

---

## Invoke

In Agent chat, do one of:

1. Type `/requirements-analysis` and pick the skill, then name the problem.
2. Attach **requirements-analysis** to the message.
3. Paste:

```
/requirements-analysis <problem>
```

`<problem>` is required. A file, a surface, a pasted brief, or a pointer
to the current conversation. If you omit it, the agent should ask once
and stop.

### Good prompts

```
/requirements-analysis the CS universe hub — use the gathered feedback
```

```
/requirements-analysis we need sign-in that keeps XP across devices
```

```
/requirements-analysis plans/notes.md
```

You are often both **customer and analyst**. Still expect the agent to
define terms, surface unstated requirements, **ask when a gap would make
the record wrong**, and show you the *implications* of the record — not
to start building. It should wait for those answers before writing the
file. It should not interview you for a business plan or ask about
screens and payloads.

---

## What you get

A markdown file, usually:

`plans/<slug>-requirements.md`

Six required sections:

1. Simplified model of the system's environment
2. Goals of the system and functions it must perform
3. Performance constraints on the system
4. Constraints on the implementation
5. Resource constraints for the development project
6. External interfaces (boundaries only)

Plus: verbatim customer statement, unstated items awaiting your
judgment, and a consistency / review block.

---

## What happens

1. Keeps your wording as the informal problem statement
2. Reads the existing system if this is a slice of the current repo
3. Builds a vocabulary (environment model) before goals
4. Writes goals in *your* terms, leaves defined by that model
5. Labels unstated needs (computer-property gaps, familiar constraints)
6. Classifies constraints: resource, performance, environment, form, methods
7. Marks each goal: this version / later / not at all
8. Names external interfaces without specifying their details
9. Checks consistency (undefined terms, contradictions)
10. Asks up to three questions when it cannot write a consistent record
    without the answer (who it is for, undefined terms, conflicting
    goals, this-version priority, hard constraints guessed wrong)
11. Presents consequences for you to accept or correct
12. Writes the record and **stops**

If something would change what the product *is*, or the record would be
wrong without an answer, it should ask (at most three questions per turn)
and wait — it must not write the file while those questions are open.
Non-fork gaps stay labeled as assumptions. Dual independent analysis
(two versions of the requirements, then a correspondence check) only if
you ask — it is for systems that must be very stable.

---

## How to review

You are the judge of what is a requirement.

When the agent presents implications, check:

- Do these goals match what you meant, not only what you typed?
- Did it invent a second product in “later”?
- Are unstated items things you actually want?
- Can every leaf goal be observed in the environment model?
- Did it specify button layouts or JSON payloads? That is too early.

Reply with accept, corrections, or “later / not at all” moves. Then you
can run **mvp-spec** (first demo) or implement. Do not skip this file
and start coding from the chat.

---

## Not this skill

| You want | Use |
|---|---|
| Lock a first shippable demo | `mvp-spec` |
| Restyle / redesign a screen | `ui-ux-builder` |
| Marketing landing | `landing-page-builder` |
| API fields, screen layouts, protocols | Functional specification (after this record is accepted) |
| Code | Implement after the record (and any spec) exists |

---

## Files

| File | Role |
|---|---|
| `SKILL.md` | Agent workflow |
| `template.md` | Record structure |
| `examples.md` | Density: goals, terms, interfaces |
| `README.md` | This how-to |
