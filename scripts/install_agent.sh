#!/bin/sh
# Install the JobPilot LaunchAgents on macOS: the dashboard and the ingestion
# daemon.
#
# The dashboard already runs; this only makes it always up and reachable by
# double-click. The daemon already heartbeats; nothing kept it alive, so the
# queue went stale whenever the terminal it was started from closed.
#
# No Python is bundled: py2app plus torch 2.2.2 on Intel macOS is a multi-day
# hole for no benefit, so the agents run the venv interpreter that is already on
# this machine, resolved here at install time.
#
# Two agents, not one job doing two things. launchd supervises each label on its
# own, so the daemon crashing on a bad source leaves the dashboard serving the
# page, and a dashboard restart never interrupts a cycle mid-ingest. They share
# only the database file, which is why db.connect opens it in WAL mode.
#
# Idempotent: running it twice leaves exactly one of each agent. Each plist is
# rewritten and its agent unloaded before being loaded again, so a changed venv
# path, port, or interval is picked up rather than silently ignored.
#
# Usage:  scripts/install_agent.sh [port] [interval_hours]
# Remove: scripts/uninstall_agent.sh

set -eu

PORT="${1:-8787}"
INTERVAL_HOURS="${2:-3}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_DIR="$HOME/Library/LaunchAgents"
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

# install_one LABEL LOGNAME THROTTLE_SECONDS ARG...
#
# THROTTLE_SECONDS is launchd's floor between respawns. KeepAlive restarts a job
# whatever its exit status, so a job that fails at startup — missing credentials,
# an unreadable database — becomes a hot loop without one.
install_one() {
    label="$1"
    logname="$2"
    throttle="$3"
    shift 3

    plist="$PLIST_DIR/$label.plist"
    # Unload first: launchd keeps the old ProgramArguments for a loaded label, so
    # rewriting the plist alone would not change anything until the next login.
    if [ -f "$plist" ]; then
        launchctl unload "$plist" 2>/dev/null || true
    fi

    arguments=""
    for arg in "$PYTHON" "$@"; do
        arguments="$arguments        <string>$arg</string>
"
    done

    cat > "$plist" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$label</string>

    <key>ProgramArguments</key>
    <array>
$arguments    </array>

    <key>WorkingDirectory</key>
    <string>$REPO_ROOT</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>ThrottleInterval</key>
    <integer>$throttle</integer>

    <key>StandardOutPath</key>
    <string>$LOG_DIR/$logname.out.log</string>

    <key>StandardErrorPath</key>
    <string>$LOG_DIR/$logname.err.log</string>
</dict>
</plist>
PLIST_EOF

    launchctl load "$plist"
    echo "Agent installé : $plist"
}

install_one com.jobpilot.dashboard dashboard 10 \
    -m jobpilot dashboard --port "$PORT"

# A cycle is hours long and starts with one on load, so a daemon that dies on
# startup is worth backing off from harder than a web server is.
install_one com.jobpilot.scheduler scheduler 60 \
    -m jobpilot daemon --interval-hours "$INTERVAL_HOURS"

echo "Journaux       : $LOG_DIR/dashboard.{out,err}.log"
echo "                 $LOG_DIR/scheduler.{out,err}.log"
echo "Tableau de bord: http://127.0.0.1:$PORT"
echo "Démon          : un cycle ingest + scoring toutes les $INTERVAL_HOURS h"
echo "Désinstaller   : scripts/uninstall_agent.sh"
