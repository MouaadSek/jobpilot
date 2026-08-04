#!/bin/sh
# Remove the JobPilot LaunchAgents: the dashboard and the ingestion daemon.
#
# Ships alongside install_agent.sh on purpose: an agent you cannot remove is a
# trap, especially one running under KeepAlive.
#
# Removes each label independently, so the two agents stay independent here too:
#   scripts/uninstall_agent.sh                     both
#   scripts/uninstall_agent.sh com.jobpilot.scheduler   only the daemon
#
# Idempotent: removing an agent that is not installed succeeds and says so.

set -eu

if [ "$#" -gt 0 ]; then
    LABELS="$*"
else
    LABELS="com.jobpilot.dashboard com.jobpilot.scheduler"
fi

removed=0
for label in $LABELS; do
    plist="$HOME/Library/LaunchAgents/$label.plist"
    if [ ! -f "$plist" ]; then
        continue
    fi
    launchctl unload "$plist" 2>/dev/null || true
    rm -f "$plist"
    echo "Agent supprimé : $plist"
    removed=$((removed + 1))
done

if [ "$removed" -eq 0 ]; then
    echo "Aucun agent installé ($HOME/Library/LaunchAgents ne contient rien de JobPilot)."
    exit 0
fi

echo "Les journaux restent dans $HOME/Library/Logs/jobpilot/."
