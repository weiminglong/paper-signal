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
# Run from the repo root so any relative PAPER_SIGNAL_CONFIG resolves correctly
# regardless of the scheduler's working directory (cron runs with CWD=$HOME).
cd "${ROOT_DIR}"

# Load project env if present.
if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

# Resolve how to invoke the CLI: explicit override, project venv, PATH, then the
# no-install module form (`python3 -m paper_signal`) that the onboarding skill uses.
if [[ -n "${PAPER_SIGNAL_BIN:-}" && -x "${PAPER_SIGNAL_BIN}" ]]; then
  CMD=("${PAPER_SIGNAL_BIN}")
elif [[ -x "${ROOT_DIR}/.venv/bin/paper-signal" ]]; then
  CMD=("${ROOT_DIR}/.venv/bin/paper-signal")
elif command -v paper-signal >/dev/null 2>&1; then
  CMD=("$(command -v paper-signal)")
elif command -v python3 >/dev/null 2>&1 && python3 -c 'import yaml, jinja2' >/dev/null 2>&1; then
  # Module form works only if the package's deps (pyyaml, jinja2) are importable.
  CMD=(python3 -m paper_signal)
else
  echo "paper-signal not runnable: install it (pip install -e .), or install its deps" >&2
  echo "(python3 -m pip install pyyaml jinja2), or set PAPER_SIGNAL_BIN in .env." >&2
  exit 1
fi

CONFIG="${PAPER_SIGNAL_CONFIG:-${ROOT_DIR}/config/interests.yaml}"
mkdir -p "${ROOT_DIR}/data"

echo "[$(date)] paper-signal run (config=${CONFIG})"
if [[ -n "${OBSIDIAN_VAULT_PATH:-}" ]]; then
  exec "${CMD[@]}" run --config "${CONFIG}" --vault "${OBSIDIAN_VAULT_PATH}"
else
  # Falls back to vault_path inside the config file.
  exec "${CMD[@]}" run --config "${CONFIG}"
fi
