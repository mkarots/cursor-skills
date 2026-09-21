# Density examples

Write like the short example. Do not write like the padded one.

## Environment concept

**Good**

| Term | Definition |
|---|---|
| Quest | A playable quiz page already in the catalog. One catalog id, one href. |
| Guest | A learner with no signed-in account. Progress may exist only on this device. |

**Bad**

| Term | Definition |
|---|---|
| Quest | A quest is a learning experience / module / course-like unit that the user can engage with in order to learn computer science concepts in an interactive way. |

## Goal leaf

**Good**

- **G2.1** A learner who selects a domain can still see the rest of Computer Science, dimmer, at the edge of the same space.

**Bad**

- **G2.1** Implement a continuous camera in Three.js with dolly-in and bloom.

(How is functional specification / design. The leaf is an observable fact in the environment.)

## External interface

**Good**

| Interface | Counterpart | Purpose | Direction |
|---|---|---|---|
| Play quest | Quest page | Learner leaves the map and opens that quest's href | out |

**Bad**

| Interface | Counterpart | Purpose | Direction |
|---|---|---|---|
| Play quest | `GET /quests/:id` JSON `{id,xp,…}` | REST + schema | both |

## Unstated requirement

**Good**

| Item | Class | Proposed requirement | Customer |
|---|---|---|---|
| Guest mark | computer-motivated | Opening a quest leaves a visible mark without sign-in | pending |

**Bad**

Silently adding “must use localStorage” to implementation constraints without labeling it unstated.

## Blocking question

**Good**

Who is this for? I cannot tell whether a **Guest** (no account) or a
signed-in **Learner** is the primary actor — that forks who “done”
applies to.

- Guest only this version
- Signed-in learner only this version
- Both, guest progress stays on this device

**Bad**

A dozen questions about color, JSON fields, and pricing before any
environment model exists.

**Also bad**

Guessing “signed-in learner” as the only actor and writing the record
without asking, when the statement never said who it is for.
