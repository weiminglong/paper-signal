#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.papersignal.daily.plist"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.papersignal.daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>${ROOT_DIR}/.venv/bin/paper-signal</string>
    <string>run</string>
    <string>--config</string>
    <string>${ROOT_DIR}/config/interests.yaml</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${ROOT_DIR}</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>7</integer>
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
echo "Installed launchd job: $PLIST"
