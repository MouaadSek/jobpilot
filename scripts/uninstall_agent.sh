#!/bin/sh
# Remove the JobPilot dashboard LaunchAgent.
#
# Ships alongside install_agent.sh on purpose: an agent you cannot remove is a
# trap, especially one running under KeepAlive.
#
# Idempotent: removing an agent that is not installed succeeds and says so.

set -eu

LABEL="com.jobpilot.dashboard"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

if [ ! -f "$PLIST" ]; then
    echo "Aucun agent installé ($PLIST absent)."
    exit 0
fi

launchctl unload "$PLIST" 2>/dev/null || true
rm -f "$PLIST"

echo "Agent supprimé : $PLIST"
echo "Les journaux restent dans $HOME/Library/Logs/jobpilot/."
