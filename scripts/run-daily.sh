#!/usr/bin/env bash
# Canonical unattended daily runner for PaperSignal (deterministic path A).
#
# cron and launchd both call this. Schedulers do NOT inherit your shell environment,
# so this script loads a project .env, resolves the paper-signal executable, ensures
# the log directory exists, and passes the vault explicitly.
#
# Configure by creating <repo>/.env (see .env.example):
#   OBSIDIAN_VAULT_PATH="/path/to/your/Obsidian Vault"
#   PAPER_SIGNAL_CONFIG="/path/to/config/interests.yaml"   # optional
#   PAPER_SIGNAL_BIN="/path/to/paper-signal"               # optional override
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load project env if present.
if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

# Resolve the paper-signal executable: explicit override, project venv, then PATH.
if [[ -n "${PAPER_SIGNAL_BIN:-}" && -x "${PAPER_SIGNAL_BIN}" ]]; then
  BIN="${PAPER_SIGNAL_BIN}"
elif [[ -x "${ROOT_DIR}/.venv/bin/paper-signal" ]]; then
  BIN="${ROOT_DIR}/.venv/bin/paper-signal"
elif command -v paper-signal >/dev/null 2>&1; then
  BIN="$(command -v paper-signal)"
else
  echo "paper-signal not found. Install it (pip install -e .) or set PAPER_SIGNAL_BIN in .env." >&2
  exit 1
fi

CONFIG="${PAPER_SIGNAL_CONFIG:-${ROOT_DIR}/config/interests.yaml}"
mkdir -p "${ROOT_DIR}/data"

echo "[$(date)] paper-signal run (config=${CONFIG})"
if [[ -n "${OBSIDIAN_VAULT_PATH:-}" ]]; then
  exec "${BIN}" run --config "${CONFIG}" --vault "${OBSIDIAN_VAULT_PATH}"
else
  # Falls back to vault_path inside the config file.
  exec "${BIN}" run --config "${CONFIG}"
fi
