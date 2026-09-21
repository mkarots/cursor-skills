# UI/UX builder — how to use it

Personal Cursor skill. Path: `~/.cursor/skills/ui-ux-builder/`

It restyles or redesigns a **real product surface** (app screen, dashboard, settings, docs, PR walkthrough) so it does not look like generic AI UI. Someone is trying to finish a task, not get converted.

It **starts by learning the project** from repo docs, GitHub, or code, then **proposes themes** that fit that product. It should not jump to a random look.

For a marketing landing page, hero, or campaign site, use **landing-page-builder** instead.

The skill does **not** auto-run. You have to attach it or type the slash command.

---

## Invoke

In Agent chat, do one of:

1. Type `/ui-ux-builder` and pick the skill, then describe the surface.
2. Attach the **ui-ux-builder** skill to the message (the same way you attached landing-page-builder).
3. Paste this shape:

```
/ui-ux-builder <surface> [optional aesthetic or references]
```

`<surface>` is required: a file, a route, a screen name, or “the page I have open”. If you omit it, the agent should ask once and stop.

### Good prompts

```
/ui-ux-builder plans/PR34_MERGE_PROGRESS_CI_WALKTHROUGH.html
```

Don’t name a look unless you have one. The first reply should be “here’s what this repo is” plus theme options, not a finished page.

```
/ui-ux-builder the hub index — restyle only, keep catalog data
```

```
/ui-ux-builder settings/profile.html
more editorial, paper and ink, not cartoony
```

```
/ui-ux-builder css/quest-shell.css + index.html
give me direction options first
```

### Weak prompts

- “make the UI awesome” with no screen
- attaching this skill to a landing-page brief (use landing-page-builder)
- asking it to add a new framework or invent product features

---

## What you can specify (optional)

| You say | What happens |
| --- | --- |
| Nothing about look (default) | Agent reads the project, shows a short product readback, then lists **5** theme directions and **waits**. You pick or react (“not cartoony”, “more like the hub”). |
| An aesthetic, metaphor, or references | After the product readback, it uses yours. No competing theme list. |
| “just pick” / “you choose” | Still a short list, then it commits to one and says why it fits the product. |
| “give me options” | Same as default — themes after it understands the project. |
| “restyle only” | Same structure and data; new type, color, composition. |
| “restructure” | Layout and IA can move; business logic and routes stay unless you say otherwise. |

You can also name constraints: keep copy accurate, don’t touch auth, mobile matters, desktop-only, etc.

---

## What the agent will do

In order. It should not skip Orient or the browser check.

1. **Orient** — read README / docs, GitHub (`gh repo view` if needed), and the actual UI code until it can say what the product is. You get a short readback to correct.
2. **Brief** — this surface, the job, the one primary action, states, constraints.
3. **Discover** — **5** theme directions that fit *this* product (unless you already named a look). Waits for you. Seed is only for extra variety inside that brief, never a substitute for understanding the repo.
4. **POC** — implement in the repo’s existing stack. No new framework.
4. **Critic loop** — screenshots at a real width and a narrow width; a **fresh** subagent sees only those images; up to 2 passes. If a pass scores ≤6 with no new structural idea, it should stop and ask you.
5. **Enrich** — generated images/motion only if the UI still looks like code-shapes or you asked for them.
6. **Deliver** — cut extra chrome, kill leftover AI tells, rewrite visible copy.
7. **Verify** — click through the actual job in the browser (not one screenshot). Shared state on other screens, empty/error if they exist, resize if layout changed.

Expect it to take a while. The critic pass is the slow, expensive part; that’s intentional.

---

## What you should get back

First message (before any restyle): a product readback you can correct, then **5** theme directions. Reply with a pick or taste notes.

After the UI ships:

- Direction in one sentence (feeling + layout idea)
- What was cut and which generic tells were replaced
- Final copy, called out so you can rewrite it
- How to open or run the UI
- Which states and widths were actually checked

If copy feels off, rewrite those strings in a follow-up — the skill treats first-draft UI text as placeholder.

---

## Steering after v1

Useful replies:

- “Keep the direction, fix the critic’s layout gaps”
- “Too dark / too much chrome / too much metaphor”
- “Don’t change the code snippets, only the frame”
- “Mobile is wrong; desktop is fine”
- “Stop — show me options instead”

Don’t expect a third critic pass unless the score was clearly rising.

---

## vs landing-page-builder

| | **ui-ux-builder** | **landing-page-builder** |
| --- | --- | --- |
| Job | Finish a task | Convert / explain a product |
| Primary control | Save, run, merge, continue, copy | CTA |
| Default to avoid | Sidebar + KPI cards | Hero + 3 feature cards |
| Hero graphic | The actual content (table, form, diff) | A composed brand moment |

Same critic/polish bones. ui-ux-builder must understand the repo first and propose themes; landing-page-builder may seed a look immediately.

---

## Files in this folder (for the agent)

You don’t need these unless you’re editing the skill.

| File | Role |
| --- | --- |
| `SKILL.md` | Agent instructions |
| `orient.md` | How to learn the product from docs / GitHub / code |
| `critic.md` | Verbatim critic prompt |
| `polish.md` | Cut list + AI-tells + copy rules |
| `ux.md` | Hierarchy, states, forms/tables |
| `motion.md` | Optional image/motion |
| `scripts/seed.sh` | Optional variety *after* the product is understood |
