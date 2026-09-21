#!/usr/bin/env bash
# Print a long random alphanumeric seed for design inspiration.
# Inspiration only — never render this string in the page.
set -euo pipefail
python3 -c "import secrets,string; a=string.ascii_letters+string.digits; print(''.join(secrets.choice(a) for _ in range(64)))"
