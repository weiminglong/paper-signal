#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMAND="cd ${ROOT_DIR} && ${ROOT_DIR}/.venv/bin/paper-signal run --config ${ROOT_DIR}/config/interests.yaml >> ${ROOT_DIR}/data/cron.log 2>&1"

(crontab -l 2>/dev/null | grep -v "paper-signal run" || true; echo "0 7 * * * ${COMMAND}") | crontab -
echo "Installed daily cron job for 07:00"
