#!/usr/bin/env bash
# Install a daily cron job that runs PaperSignal via scripts/run-daily.sh.
# Usage: scripts/install_cron.sh [HOUR]   (default hour: 7)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOUR="${1:-7}"
if ! [[ "$HOUR" =~ ^([0-9]|1[0-9]|2[0-3])$ ]]; then
  echo "HOUR must be an integer 0-23 (got: '$HOUR')" >&2
  exit 1
fi
RUNNER="${ROOT_DIR}/scripts/run-daily.sh"

chmod +x "${RUNNER}"
mkdir -p "${ROOT_DIR}/data"

# Quote the paths so a repo path with spaces survives cron's /bin/sh -c word-splitting.
LINE="0 ${HOUR} * * * \"${RUNNER}\" >> \"${ROOT_DIR}/data/cron.log\" 2>&1"
# grep -F (fixed string): a '.' in the path must not be treated as a regex wildcard,
# or re-installing could delete an unrelated checkout's cron line.
(crontab -l 2>/dev/null | grep -vF "${RUNNER}" || true; echo "${LINE}") | crontab -

echo "Installed daily cron job at ${HOUR}:00 -> ${RUNNER}"
echo "Logs: ${ROOT_DIR}/data/cron.log"
echo "Reminder: set OBSIDIAN_VAULT_PATH (and optionally PAPER_SIGNAL_CONFIG) in ${ROOT_DIR}/.env,"
echo "and make sure paper-signal is installed (pip install -e . creates .venv/bin/paper-signal)."
