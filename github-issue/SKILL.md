---
name: github-issue
description: >-
  Picks the next eligible GitHub issue (or a given issue URL), implements
  or writes the design doc, self-reviews, opens a PR, then notifies a
  reviewer or merges. The outer loop sets GITHUB_ISSUE_AUTOMERGE=1.
  Use when the user runs /github-issue, passes a github.com issue URL,
  or runs a CLI loop that drains issues one at a time.
disable-model-invocation: true
---

# Treat a GitHub issue

One invocation does **one issue**. The shell loop is the queue. Do not start a second issue in the same run.

An issue is either a **code** problem or a **design document**. Classify it, then finish that path: implement or write, review, open a PR, then notify (default) or merge (opt-in).

## Invocation

CLI (fresh agent, required for a loop):

```bash
cursor agent -p -f "Follow the github-issue skill. Process the next eligible GitHub issue."
```

Chat:

```
/github-issue
/github-issue https://github.com/<owner>/<repo>/issues/<n>
```

- No URL → pick the next eligible issue in the current repo.
- URL → that issue only. Accept `https://github.com/<owner>/<repo>/issues/<n>` and ignore any `#fragment`.
- `GITHUB_ISSUE_AUTOMERGE=1` → merge the PR after a clean self-review. A single invocation defaults to **notify only**. The outer loop sets this to `1`. Do not merge unless that env var is set or the prompt says to merge.
- `GITHUB_ISSUE_REVIEWER` → GitHub username to request as reviewer (no `@`).
- If `gh` fails (auth, private repo, missing CLI), print `GITHUB_ISSUE_STATUS=failed` and stop. Do not invent an issue.

Work in a checkout of the issue's repo. If the workspace is a different repo, print `GITHUB_ISSUE_STATUS=failed` and stop.

## Pick next

Skip this section when a URL was given.

Run `scripts/pick-next.sh` from this skill directory. If the script is missing, do the same with `gh`:

1. List open issues, oldest first (`number` ascending).
2. Skip labels: `blocked`, `wontfix`, `needs-human`, `on-hold`, `in-progress` (plus `GITHUB_ISSUE_SKIP_LABELS` if set).
3. Skip issues already referenced by an **open** PR (`Fixes #N`, `Closes #N`, `Resolves #N`, or GitHub closing reference).
4. Take the first remaining issue.

If none remain, print exactly this last line and exit without other work:

```
GITHUB_ISSUE_STATUS=idle
```

Immediately after selecting an issue, claim it so a second loop cannot take it:

```bash
gh issue edit "$N" --add-label in-progress --add-assignee "@me"
```

If adding the label fails because it does not exist, create it once (`gh label create in-progress --color E4E669 --description "Claimed by github-issue skill"`) and retry. If claiming fails, print `GITHUB_ISSUE_STATUS=failed` and stop.

Fetch the claimed issue with `gh` (do not guess from memory):

```bash
gh issue view "$N" --json title,body,number,url,labels,comments,author,state
```

## Classify

Read the title, body, and labels. Choose one path:

- **Code** — bug, feature, refactor, tests; solved with code.
- **Design document** — architecture write-up or analysis without implementing product code.

If both appear, or neither is clear, add label `needs-human`, remove `in-progress`, print `GITHUB_ISSUE_STATUS=blocked ISSUE=<n>`, and stop. Do not guess.

Copy the matching checklist and complete it in order. Keep the issue wording; do not reframe the request.

## Repo contribution rules

If the repo has `CONTRIBUTING.md`, `AGENTS.md`, or `.cursor/rules/` about PRs, review, version, or changelog, follow those. Typical contract:

- Branch off the default branch. Never commit directly to it.
- One issue → one PR. Link with `Fixes #<n>` (or `Closes #<n>`).
- Bump version and update `CHANGELOG.md` when the repo versions that way. Read the current version from the freshly pulled default branch (do not reuse a version already on `main`).
- Do not force-push unless the user explicitly asked in this invocation.
- Do not commit secrets, credentials, or files listed in `.gitignore`.

## Sync latest main before any code change

Do this **after** classifying the issue and **before** editing files, creating a branch, or bumping a version. Applies to both the code path and the design-document path.

1. Resolve the default branch (`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`). Treat it as `main` if that command fails and `origin/main` exists.
2. If the working tree is dirty, print `GITHUB_ISSUE_STATUS=failed` and stop. Do not stash, discard, or commit unrelated work.
3. Fetch and fast-forward onto that branch:

   ```bash
   git fetch origin
   git checkout "$DEFAULT_BRANCH"
   git pull --ff-only origin "$DEFAULT_BRANCH"
   ```

4. Create a new branch from that updated tip. Do not branch from a stale local feature branch, and do not start edits until `git rev-parse HEAD` matches `origin/$DEFAULT_BRANCH`.

If `git pull --ff-only` fails, print `GITHUB_ISSUE_STATUS=failed` and stop.

## Code path

1. Identify the main problem and describe it sufficiently.
2. Identify possible approaches, compare and contrast them.
3. Choose the best approach and document the choice.
4. Break the chosen approach into distinct software changes.
5. **Sync latest main** (section above). Then implement all requirements. Add or update tests when the repo has a test runner and the change is logic, not copy-only HTML.
6. Review the implemented code. Fix correctness, safety, and requirement gaps. Document the rest in the reply and the PR.
7. Open a pull request against the default branch. Use `gh pr create`. Do not push or open a PR if the user asked you not to.

Do steps 1–4 in the reply before writing code. Do not skip the comparison or the choice. Do not write code until latest main is pulled.

## Design document path

- Identify the problem at discussion.
- Write a document that overviews the problem and its subproblems.
- Record requirements and constraints that affect the problem.
- Write a precise analysis that leaves no questions about why it is a problem.
- For each subproblem, lay out possible solutions and compare them.
- Explain how the parts together solve the problem.

**Sync latest main** (section above) before creating files. Write the document in the repo. Prefer the project's existing design-doc location and template. Otherwise use `docs/` and this outline:

```markdown
# <Title>

One-sentence summary.

## Problem

## Subproblems

## Requirements and constraints

## Analysis

## Solutions per subproblem

## How the parts solve the problem
```

Open a pull request that adds the document and links the issue. Do not implement product code on this path unless the issue also requires it and the user confirmed the code path.

## Review then notify (or merge)

After the PR exists:

1. `gh pr checks` / `gh pr view --json statusCheckRollup,url,number` when CI exists. If checks fail and you can fix them in this same PR, fix and push. If you cannot, label the issue `needs-human`, print `GITHUB_ISSUE_STATUS=failed`, and stop.
2. Request a reviewer when `GITHUB_ISSUE_REVIEWER` is set:

   ```bash
   gh pr edit "$PR" --add-reviewer "$GITHUB_ISSUE_REVIEWER"
   ```

3. Comment on the PR with what changed, how to verify, and leftover non-blocking notes.
4. **Single invocation default:** do not merge. Notification is the PR + reviewer request + comment.
5. **If `GITHUB_ISSUE_AUTOMERGE=1` or the prompt says to merge** (the outer loop does both): merge with `gh pr merge --squash --delete-branch` after a clean self-review and green checks. Never merge if the self-review found a correctness issue, or if the repo forbids agent merges.

If implementation cannot finish, add `needs-human`, remove `in-progress` if you added it, comment on the issue with the blocker, and print `GITHUB_ISSUE_STATUS=failed`.

On success, you may leave `in-progress` (the PR will close the issue) or remove it; do not leave the issue unlabeled-and-open with no PR.

## Status line (required)

The **last line** of the run must be exactly one of:

```
GITHUB_ISSUE_STATUS=done ISSUE=<n> PR=<url>
GITHUB_ISSUE_STATUS=idle
GITHUB_ISSUE_STATUS=blocked ISSUE=<n>
GITHUB_ISSUE_STATUS=failed ISSUE=<n>
GITHUB_ISSUE_STATUS=failed
```

No extra text after that line. The outer loop greps it.

## Outer loop

The loop **merges** each PR (`GITHUB_ISSUE_AUTOMERGE=1`). Set `GITHUB_ISSUE_AUTOMERGE=0` to drain without merging. The next iteration pulls latest main, so a merge is visible to the following issue.

From the repo checkout:

```bash
~/.cursor/skills/github-issue/scripts/loop.sh
```

Or:

```bash
export GITHUB_ISSUE_AUTOMERGE=1
while true; do
  out=$(cursor agent -p -f "Follow the github-issue skill. Process the next eligible GitHub issue. GITHUB_ISSUE_AUTOMERGE=1: merge the PR after a clean self-review.")
  printf '%s\n' "$out"
  status=$(printf '%s\n' "$out" | grep -E '^GITHUB_ISSUE_STATUS=' | tail -1)
  case "$status" in
    GITHUB_ISSUE_STATUS=idle) exit 0 ;;
    GITHUB_ISSUE_STATUS=done*) ;;
    *) exit 1 ;;
  esac
done
```

Each iteration is a new agent. Do not `--resume` the previous chat.
