# Personal Cursor skills

Agent skills loaded from `~/.cursor/skills/`. Cursor picks these up across every project.

This repo is the versioned copy of that folder. Clone or pull into `~/.cursor/skills` so the agent keeps using the same paths.

Do not put Cursor’s built-in skills here (`~/.cursor/skills-cursor/`). Those are managed by Cursor.

## Skills

| Skill | What it does |
| --- | --- |
| `cursor-digest` | HTML digest of Cursor sessions plus matching GitHub work |
| `github-issue` | Pick an issue, implement or write the design, open a PR |
| `landing-page-builder` | Distinctive landing pages (discover → critic → deliver) |
| `mvp-spec` | Lock an MVP spec: one user, one job, one demo |
| `requirements-analysis` | Formalize a problem into a requirements record |
| `ui-ux-builder` | Distinctive product UI (orient → critic → polish) |
| `walkthrough` | Standalone HTML walkthrough of a GitHub PR |

## Restore on a new machine

```bash
git clone git@github.com:<owner>/cursor-skills.git ~/.cursor/skills
```

If `~/.cursor/skills` already exists, clone elsewhere and rsync, or add this directory as a git remote and pull.
