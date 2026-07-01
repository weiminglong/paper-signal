#!/usr/bin/env bash
# Install a macOS launchd job that runs PaperSignal daily via scripts/run-daily.sh.
# Usage: scripts/install_launchd.sh [HOUR]   (default hour: 7)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOUR="${1:-7}"
PLIST="$HOME/Library/LaunchAgents/com.papersignal.daily.plist"
RUNNER="${ROOT_DIR}/scripts/run-daily.sh"

chmod +x "${RUNNER}"
mkdir -p "${ROOT_DIR}/data" "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.papersignal.daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${RUNNER}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${ROOT_DIR}</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${HOUR}</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>${ROOT_DIR}/data/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>${ROOT_DIR}/data/launchd.err.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Installed launchd job at ${HOUR}:00 -> $PLIST"
echo "Reminder: set OBSIDIAN_VAULT_PATH in ${ROOT_DIR}/.env (launchd does not inherit your shell env)."
