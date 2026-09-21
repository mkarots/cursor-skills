#!/usr/bin/env bash
# Daily Cursor digest for yesterday. Invoked by launchd at 10:00 local time.
set -euo pipefail

HOME="${HOME:-$(eval echo ~)}"
export HOME
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

SKILL="$HOME/.cursor/skills/cursor-digest"
ARTIFACTS="$HOME/Projects/cursor-digest-artifacts"
COLLECT="$SKILL/scripts/collect.py"
LOG_DIR="$ARTIFACTS/logs"

mkdir -p "$LOG_DIR"
exec >>"$LOG_DIR/daily.log" 2>&1
echo "---- $(date '+%Y-%m-%d %H:%M:%S %Z') ----"

if [[ ! -f "$COLLECT" ]]; then
  echo "collector missing: $COLLECT" >&2
  exit 1
fi

python3 "$COLLECT" --range yesterday --artifacts-dir "$ARTIFACTS"

HTML="$(python3 - <<'PY'
from datetime import datetime, timedelta
from pathlib import Path
now = datetime.now().astimezone()
yesterday = (now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)).strftime("%Y-%m-%d")
print(Path.home() / "Projects/cursor-digest-artifacts" / f"digest-{yesterday}.html")
PY
)"

if [[ -f "$HTML" ]] && command -v open >/dev/null 2>&1; then
  open "$HTML"
fi

echo "wrote $HTML"
