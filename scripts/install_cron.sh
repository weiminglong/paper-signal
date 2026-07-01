#!/usr/bin/env bash
# Install a daily cron job that runs PaperSignal via scripts/run-daily.sh.
# Usage: scripts/install_cron.sh [HOUR]   (default hour: 7)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOUR="${1:-7}"
RUNNER="${ROOT_DIR}/scripts/run-daily.sh"

chmod +x "${RUNNER}"
mkdir -p "${ROOT_DIR}/data"

LINE="0 ${HOUR} * * * ${RUNNER} >> ${ROOT_DIR}/data/cron.log 2>&1"
(crontab -l 2>/dev/null | grep -v "${RUNNER}" || true; echo "${LINE}") | crontab -

echo "Installed daily cron job at ${HOUR}:00 -> ${RUNNER}"
echo "Logs: ${ROOT_DIR}/data/cron.log"
echo "Reminder: set OBSIDIAN_VAULT_PATH (and optionally PAPER_SIGNAL_CONFIG) in ${ROOT_DIR}/.env,"
echo "and make sure paper-signal is installed (pip install -e . creates .venv/bin/paper-signal)."
