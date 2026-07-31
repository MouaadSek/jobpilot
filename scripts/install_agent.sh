#!/bin/sh
# Install the JobPilot dashboard as a macOS LaunchAgent.
#
# The dashboard already runs; this only makes it always up and reachable by
# double-click. No Python is bundled: py2app plus torch 2.2.2 on Intel macOS is
# a multi-day hole for no benefit, so the agent runs the venv interpreter that
# is already on this machine, resolved here at install time.
#
# Idempotent: running it twice leaves exactly one agent. The plist is rewritten
# and the agent is unloaded before being loaded again, so a changed venv path or
# a changed port is picked up rather than silently ignored.
#
# Usage:  scripts/install_agent.sh [port]
# Remove: scripts/uninstall_agent.sh

set -eu

PORT="${1:-8787}"
LABEL="com.jobpilot.dashboard"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST="$PLIST_DIR/$LABEL.plist"
LOG_DIR="$HOME/Library/Logs/jobpilot"

PYTHON="$REPO_ROOT/.venv/bin/python3"
if [ ! -x "$PYTHON" ]; then
    PYTHON="$REPO_ROOT/.venv/bin/python"
fi
if [ ! -x "$PYTHON" ]; then
    echo "Interpréteur introuvable dans $REPO_ROOT/.venv." >&2
    echo "Créez le venv puis relancez : python3 -m venv .venv && .venv/bin/pip install -e ." >&2
    exit 1
fi

mkdir -p "$PLIST_DIR" "$LOG_DIR"

# Unload first: launchd keeps the old ProgramArguments for a loaded label, so
# rewriting the plist alone would not change anything until the next login.
if [ -f "$PLIST" ]; then
    launchctl unload "$PLIST" 2>/dev/null || true
fi

cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>-m</string>
        <string>jobpilot</string>
        <string>dashboard</string>
        <string>--port</string>
        <string>$PORT</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$REPO_ROOT</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>$LOG_DIR/dashboard.out.log</string>

    <key>StandardErrorPath</key>
    <string>$LOG_DIR/dashboard.err.log</string>
</dict>
</plist>
PLIST_EOF

launchctl load "$PLIST"

echo "Agent installé : $PLIST"
echo "Journaux       : $LOG_DIR/dashboard.{out,err}.log"
echo "Tableau de bord: http://127.0.0.1:$PORT"
echo "Désinstaller   : scripts/uninstall_agent.sh"
