#!/usr/bin/env bash
# Print the next eligible open issue URL, or exit 2 if the queue is empty.
set -euo pipefail

SKIP_DEFAULT="blocked,wontfix,needs-human,on-hold,in-progress"
IFS=',' read -r -a SKIP_LABELS <<< "${GITHUB_ISSUE_SKIP_LABELS:-$SKIP_DEFAULT}"

should_skip_label() {
  local name="$1"
  local skip
  for skip in "${SKIP_LABELS[@]}"; do
    skip="${skip#"${skip%%[![:space:]]*}"}"
    skip="${skip%"${skip##*[![:space:]]}"}"
    if [[ "${name,,}" == "${skip,,}" ]]; then
      return 0
    fi
  done
  return 1
}

issue_has_skip_label() {
  local labels_json="$1"
  local name
  while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    if should_skip_label "$name"; then
      return 0
    fi
  done < <(printf '%s' "$labels_json" | jq -r '.[].name')
  return 1
}

pr_mentions_issue() {
  local n="$1"
  local blob="$2"
  grep -Eiq "(fixes|closes|resolves)[[:space:]]+#${n}\b" <<<"$blob"
}

issues_json="$(gh issue list --state open --limit 100 --json number,title,url,labels)"
if [[ "$(jq 'length' <<<"$issues_json")" -eq 0 ]]; then
  exit 2
fi

prs_json="$(gh pr list --state open --limit 100 --json number,title,body)"

sorted_numbers="$(jq -r 'sort_by(.number) | .[].number' <<<"$issues_json")"

while IFS= read -r n; do
  [[ -z "$n" ]] && continue
  labels="$(jq -c --argjson n "$n" '.[] | select(.number == $n) | .labels' <<<"$issues_json")"
  if issue_has_skip_label "$labels"; then
    continue
  fi

  claimed=0
  while IFS= read -r pr; do
    [[ -z "$pr" ]] && continue
    if pr_mentions_issue "$n" "$pr"; then
      claimed=1
      break
    fi
  done < <(jq -r '.[] | (.title // "") + "\n" + (.body // "") + "\n"' <<<"$prs_json")

  if [[ "$claimed" -eq 1 ]]; then
    continue
  fi

  jq -r --argjson n "$n" '.[] | select(.number == $n) | .url' <<<"$issues_json"
  exit 0
done <<<"$sorted_numbers"

exit 2
