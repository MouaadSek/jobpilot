#!/bin/sh
# One command after a merge: pick up main and leave the machine running it.
#
#   scripts/update.sh [port] [interval_hours]
#
# What it does, in order:
#   1. refuses to run on a dirty tree
#   2. backs the database up, online, before anything can touch it
#   3. git pull --ff-only
#   4. pip install -e .   only if pyproject.toml changed in that pull
#   5. jobpilot init-db   only if migrations/ changed in that pull
#   6. reinstalls and restarts both LaunchAgents
#   7. waits for the dashboard to answer, and fails if it does not
#
# Steps 4 and 5 are conditional because they are the slow ones — a resolve of
# torch, and a schema pass — and skipping them on a pull that changed neither is
# the difference between this being one command and being a chore.
#
# The agents are stopped for the duration and restored by a trap, so an update
# that fails half way still leaves them running rather than leaving the machine
# with no dashboard and no ingestion.

set -eu

PORT="${1:-8787}"
INTERVAL_HOURS="${2:-3}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$REPO_ROOT/backups"
PLIST_DIR="$HOME/Library/LaunchAgents"
LABELS="com.jobpilot.dashboard com.jobpilot.scheduler"

cd "$REPO_ROOT"

die() {
    echo "" >&2
    echo "ÉCHEC : $1" >&2
    exit 1
}

# ----- 1. a dirty tree is a refusal, not a warning -----
#
# git pull --ff-only would refuse a conflicting merge on its own, but it happily
# carries uncommitted work across a fast-forward, and the reinstall below would
# then run agents against a tree nobody has read. Loud and early.

git rev-parse --git-dir >/dev/null 2>&1 || die "$REPO_ROOT n'est pas un dépôt git."

DIRTY="$(git status --porcelain)"
if [ -n "$DIRTY" ]; then
    echo "Arbre de travail non propre :" >&2
    echo "$DIRTY" >&2
    die "commitez, remisez (git stash) ou nettoyez avant de mettre à jour."
fi

PYTHON="$REPO_ROOT/.venv/bin/python3"
if [ ! -x "$PYTHON" ]; then
    PYTHON="$REPO_ROOT/.venv/bin/python"
fi
[ -x "$PYTHON" ] || die "interpréteur introuvable dans $REPO_ROOT/.venv."

# ----- 2. back the database up first -----
#
# sqlite3's backup API and not cp: the database runs in WAL mode and the daemon
# may be mid-cycle, so a file copy can capture a main database whose latest
# committed rows are still only in the -wal file. The API takes a consistent
# snapshot of a live database, which is exactly the situation here.

DB_PATH="$("$PYTHON" -c 'from jobpilot.config import get_settings; print(get_settings().db_path)')"
if [ -f "$DB_PATH" ]; then
    mkdir -p "$BACKUP_DIR"
    BACKUP="$BACKUP_DIR/jobpilot-$(date -u +%Y%m%dT%H%M%SZ).db"
    "$PYTHON" - "$DB_PATH" "$BACKUP" <<'PY'
import sqlite3
import sys

source, destination = sys.argv[1], sys.argv[2]
with sqlite3.connect(source) as src, sqlite3.connect(destination) as dst:
    src.backup(dst)
PY
    echo "Sauvegarde     : $BACKUP"
else
    echo "Sauvegarde     : aucune ($DB_PATH n'existe pas encore)"
fi

# ----- restore the agents whatever happens from here -----

restore_agents() {
    sh "$REPO_ROOT/scripts/install_agent.sh" "$PORT" "$INTERVAL_HOURS" >/dev/null 2>&1 || true
    echo "Agents rechargés après interruption." >&2
}

for label in $LABELS; do
    plist="$PLIST_DIR/$label.plist"
    if [ -f "$plist" ]; then
        launchctl unload "$plist" 2>/dev/null || true
    fi
done
trap restore_agents EXIT INT TERM

# ----- 3. fast-forward only -----

BEFORE="$(git rev-parse HEAD)"
git pull --ff-only || die "git pull --ff-only a refusé : divergence avec le distant."
AFTER="$(git rev-parse HEAD)"

if [ "$BEFORE" = "$AFTER" ]; then
    echo "Dépôt         : déjà à jour ($AFTER)"
else
    echo "Dépôt         : $BEFORE -> $AFTER"
fi

changed_since_pull() {
    ! git diff --quiet "$BEFORE" "$AFTER" -- "$1"
}

# ----- 4. dependencies, only when they moved -----

if changed_since_pull pyproject.toml; then
    echo "Dépendances   : pyproject.toml a changé, réinstallation…"
    "$PYTHON" -m pip install -e . || die "pip install -e . a échoué."
else
    echo "Dépendances   : inchangées, rien à réinstaller."
fi

# ----- 5. schema, only when it moved -----
#
# init-db is idempotent — it skips an applied schema and every recorded
# migration — so this is a cost decision, not a safety one.

if changed_since_pull migrations; then
    echo "Base          : migrations/ a changé, application…"
    "$PYTHON" -m jobpilot init-db || die "jobpilot init-db a échoué."
else
    echo "Base          : aucune nouvelle migration."
fi

# ----- 6. reinstall and restart both agents -----

sh "$REPO_ROOT/scripts/install_agent.sh" "$PORT" "$INTERVAL_HOURS" || die "réinstallation des agents impossible."
trap - EXIT INT TERM

# ----- 7. the dashboard has to actually answer -----
#
# Not "the port is bound": launchd reports a job as started the moment it has
# execed, and a dashboard that dies on an import error binds nothing. This asks
# for the page.

echo "Vérification  : attente d'une réponse sur http://127.0.0.1:$PORT/ …"
if "$PYTHON" - "$PORT" <<'PY'
import sys
import time
import urllib.error
import urllib.request

port = sys.argv[1]
url = f"http://127.0.0.1:{port}/"
deadline = time.monotonic() + 45
while time.monotonic() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            if response.status == 200:
                sys.exit(0)
    except (urllib.error.URLError, OSError):
        pass
    time.sleep(1)
sys.exit(1)
PY
then
    echo ""
    echo "À jour. Tableau de bord : http://127.0.0.1:$PORT"
    echo "Journaux : $HOME/Library/Logs/jobpilot/{dashboard,scheduler}.{out,err}.log"
else
    die "le tableau de bord ne répond pas sur le port $PORT après 45 s.
Regardez $HOME/Library/Logs/jobpilot/dashboard.err.log ; le code est à jour
et la sauvegarde est intacte."
fi
