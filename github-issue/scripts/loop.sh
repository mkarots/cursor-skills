#!/usr/bin/env bash
# Drain GitHub issues: one fresh Cursor agent per issue, merge each PR.
set -euo pipefail

export GITHUB_ISSUE_AUTOMERGE="${GITHUB_ISSUE_AUTOMERGE:-1}"

PROMPT="${GITHUB_ISSUE_PROMPT:-Follow the github-issue skill. 
Process the next eligible GitHub issue. GITHUB_ISSUE_AUTOMERGE=1: 
after a clean self-review, merge the PR with gh pr merge --squash --delete-branch.}"

while true; do
  out="$(cursor agent -p -f "$PROMPT")"
  printf '%s\n' "$out"
  status="$(printf '%s\n' "$out" | grep -E '^GITHUB_ISSUE_STATUS=' | tail -1 || true)"
  case "$status" in
    GITHUB_ISSUE_STATUS=idle)
      exit 0
      ;;
    GITHUB_ISSUE_STATUS=done*)
      continue
      ;;
    *)
      echo "loop: stopping on '$status'" >&2
      exit 1
      ;;
  esac
done
