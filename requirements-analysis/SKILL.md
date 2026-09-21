---
name: requirements-analysis
description: >-
  Formalizes a customer's informal problem into a requirements record:
  environment model, goal hierarchy, constraints, and external interfaces.
  Asks the customer when a gap would make the record wrong. Does not write
  a functional spec or product code. Use when the user runs
  /requirements-analysis, asks to analyze requirements, formalize a problem
  statement, capture needs and constraints, or turn feedback into requirements.
disable-model-invocation: true
---

# Requirements analysis

Determine and document the customer's needs and constraints. Define the
purpose of the proposed system and the constraints on its development.
Do not implement. Do not write a functional specification.

Details of specific interfaces are worked out later, in functional
specification. Name the external interfaces here; do not specify their
fields, messages, or protocols.

The customer is the ultimate judge of what is a requirement. In this
setting the user often plays **client and analyst at the same time**.
Still do the analyst job: formalize undefined concepts, discover unstated
requirements, **ask when a gap would make the record wrong**, and present
implications for review. Do not treat the first message as a complete,
consistent spec.

Related skills: [mvp-spec](../mvp-spec/SKILL.md) locks a first demo after
the problem is formalized. Do not run it unless they asked. UI work is
[ui-ux-builder](../ui-ux-builder/SKILL.md) — out of scope here.

## Invocation

```
/requirements-analysis <problem>
```

`<problem>` is required: a product, a surface, a feedback dump, a
paragraph, or “the thing we just discussed.” If it is missing, ask once
and stop.

Copy this checklist and complete it in order. If a **blocking** gap
appears, stop, ask, wait for the answer, then resume from the same step.
Do not write the record while blocking questions are open.

```
- [ ] Capture the informal problem statement
- [ ] Build the environment model (vocabulary first)
- [ ] Write the goal hierarchy in the customer's terms
- [ ] Discover unstated requirements and label them
- [ ] Record constraints (resource, performance, environment, form, methods)
- [ ] Negotiate: this version / later / not at all
- [ ] Name external interfaces (boundaries only)
- [ ] Consistency check
- [ ] Ask blocking questions — wait; do not write the record while open
- [ ] User review of implications
- [ ] Write the requirements record from template.md
- [ ] Stop. Do not implement.
```

## Ask when necessary

Ask only when you cannot write a consistent record without the answer.
Do not interview for a business plan. Do not ask about screens, schemas,
payloads, or protocols.

**Blocking — stop and ask. Do not guess.**

- The informal problem is missing or you cannot tell which problem to
  formalize
- A primary actor, or who this system is for, cannot be identified
- A term used in a goal or invariant cannot be defined from the
  statement, the conversation, or the existing system
- Two goals or invariants conflict
- Choosing this version / later / not at all would guess the customer's
  priority
- An unstated item would become a hard constraint if guessed wrong
  (who may use it, where the source of truth lives, replace vs extend
  an existing artifact)
- A fork would change who it is for, what “done” means, or what must
  never ship

**Not blocking — label `unstated → proposed` or an assumption and
continue.**

- Computer-motivated details that do not change the product (empty
  states, caching, latency targets you can mark proposed)
- Form or methods defaults that already match the repo
- Wording, density, or which synonym to keep after you pick one term
- Anything already answered in the repo or this conversation

**How to ask**

- If AskQuestion is available, use it. Otherwise ask in chat.
- At most **three** questions per turn. Prefer fewer.
- Each question states the gap, why it blocks the record, and a
  default if you have a reasonable one.
- Offer 2–4 concrete options when the answer is a choice; always allow
  the customer to answer in their own words.
- After answers, resume the checklist. Ask again only if a **new**
  blocking gap appears.
- If the customer declines or says “you decide,” pick a default, label
  it as an assumption, and continue.

## 1. Informal problem statement

Keep the customer's wording. Do not rebrand, “improve,” or invent a
product name.

If this is a slice of the **current repo**, read the existing system
before formalizing (README, catalog, prior specs, code that already
constrains the environment). The vocabulary of the *existing* system and
its environment is the starting language.

The initial statement is usually:

- **Informal** — it depends on application-area concepts assumed to be
  understood
- **Incomplete** — some needs come from computer-system properties the
  customer does not know; others are constraints so familiar they are
  invisible
- **Unformalized** — it is not self-contained relative to a fixed
  notation

A computer program is a formal statement. The problem must be formalized
before it can be solved by a computer. Formalizing means identifying
undefined concepts and giving them precise definitions. The analyst's
job is a formal problem statement that corresponds to the customer's
**real** problem, not only the first wording.

## 2. Environment model

Standardize vocabulary by building a **simplified model of the system's
environment**. Lowest-level goals will be defined in terms of this model.
If a goal cannot be stated with these terms, the model is incomplete.

Record, in the customer's language:

- **Actors** — who or what acts (person, role, existing program, device)
- **Concepts** — term → definition. One term per concept. No synonyms
  used interchangeably
- **Existing artifacts** — systems, files, catalogs, accounts, devices
  already in the environment
- **Relationships** — what is part of what, what depends on what
- **Invariants** — facts that must remain true whether or not the new
  system exists

This is a model of the **world the system will sit in**, not a design of
the system. Do not smuggle screens, schemas, or APIs into it.

Check the model for internal consistency and completeness (every term
used in a goal is defined; no two concepts share a name; no cycle of
contradictory invariants). Inconsistent requirements cannot be met by
any system. If a term that a goal needs cannot be defined from what
you have, that is blocking — ask; do not invent a meaning.

## 3. Goal hierarchy

The purpose of the system is a list of the customer's individual goals,
in **user terms**, using the environment vocabulary.

Organize them as a hierarchy:

- Informal high-level goals at the top
- More specific lower-level goals beneath
- **Leaves** explicitly defined by the environment model (observable
  in that world)

Each leaf says what must become true in the environment, not how the
program is built.

Also record **functions the system must perform** as goal leaves, still
in user terms (e.g. “the learner can enter a domain and see its topics”),
not as endpoint lists.

## 4. Unstated requirements

Search the informal statement and the repo for two classes of gaps, then
**check them with the customer** (do not silently promote them). Ask now
if the item is blocking; otherwise label it and continue:

1. **Computer-motivated** — needs that exist because of properties of
   computer systems the customer did not mention (persistence, auth,
   guests vs signed-in, latency, offline, caching, empty states).
2. **Familiar constraints** — rules so ordinary the customer cannot
   easily imagine violating them (one catalog of truth, no second
   product, existing URLs, existing progress store).

Label each as `unstated → proposed` until the customer accepts, defers,
or rejects it.

Produce a **simple** formalization. Capture enough of the essential
aspects that a system solving the formalized problem is useful in the
real application. Do not grow a second product in the footnotes.

## 5. Constraints

Constraints limit the developers' choices. They come from negotiation
with the customer and from the development situation. Classify every
constraint. If a class has none, write `none stated` and any assumption.

| Type | Covers |
|---|---|
| **Resource** | schedule, budget, people / agent-time |
| **Performance** | execution time, memory, downtime |
| **Environment** | hardware, OS, external systems already required |
| **Form** | language, coding standards, documentation standards |
| **Methods** | tools, testing procedures, performance benchmarks |

Split the write-up into the three required constraint sections:

3. **Performance constraints on the system** (runtime)
4. **Constraints on the implementation** (environment + form + methods)
5. **Resource constraints for the development project**

## 6. Negotiation (this version)

The record is the result of a negotiation. For every goal and every
non-trivial constraint, assign exactly one:

- **This version** — must be met by the system to be developed now
- **Later** — acknowledged, not in this version
- **Not at all** — out of scope; do not pretend it is deferred

Do not leave tempting extras unlabeled. If two goals conflict, or this
version vs later cannot be assigned without guessing priority, stop and
ask; do not pick in secret.

## 7. External interfaces

List each **external interface of the system** as a boundary:

- Name
- Counterpart in the environment (actor or existing artifact)
- Purpose (what crosses the boundary)
- Direction (in / out / both)

Stop there. No payload shapes, no wire formats, no UI layouts. Those
belong to functional specification after the customer accepts this
record.

## 8. User review and confidence

Present the **consequences** of the requirements, not a recap of the
prompt. The customer judges whether the implications match their
intentions.

In the reply, before or with the file:

- What the system will make true in the environment
- What this version will **not** do
- Assumptions you promoted from silence
- Any inconsistency you could not resolve

If a fork would change the product (who it is for, what “done” means,
what must never ship), **wait** — that is blocking. Ask per “Ask when
necessary.” Do not write the record until those answers land. Non-fork
gaps stay labeled as assumptions.

**Two independent versions** of the analysis (separate goal/environment
passes, then a correspondence check) only when the user asks for a
system that must be very stable, or says “dual analysis.” It is
expensive; it is not the default.

## 9. Write the record

Follow [template.md](template.md). Prefer
`plans/<slug>-requirements.md` in the current repo (`plans/` if needed).
If this is not a git repo, write `<slug>-requirements.md` at the
workspace root. Slug is kebab-case from the working name. If a record
already exists for this problem, revise it; do not start a parallel
file.

Goals and constraints may stay as outlines plus a diagram (mermaid is
fine). The environment model must define terms precisely.

The record is complete only when it includes all six results:

1. A simplified model of the system's environment
2. A description of the goals of the system and the functions it must perform
3. Performance constraints on the system
4. Constraints on the implementation of the system
5. Resource constraints for the development project
6. A specification of the external interfaces of the system

Functional specifications become part of the requirements **only after**
they have been completed and accepted. Do not attach them here.

Density: [examples.md](examples.md). How to invoke: [README.md](README.md).

## Chat output

If blocking questions are open, ask them and **stop**. Do not write the
file yet.

After the file exists:

- One sentence: the formalized problem (customer's terms)
- Path to the record
- The implication review (what follows if they accept this)
- What you need confirmed, if anything (non-blocking items only)
- Stop. No code, no mockups, no functional spec.
