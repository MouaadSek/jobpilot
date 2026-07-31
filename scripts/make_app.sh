#!/bin/sh
# Generate JobPilot.app — a Dock icon that opens the dashboard.
#
# The bundle hosts nothing and embeds no Python. It is a bookmark: one
# Info.plist and a one-line executable that runs `open http://127.0.0.1:PORT`.
# Serving is the LaunchAgent's job (scripts/install_agent.sh).
#
# Generated rather than checked in, because a .app is a directory of binaries
# and metadata and a repo is not where that belongs.
#
# Usage: scripts/make_app.sh [destination-dir] [port]
#        scripts/make_app.sh /Applications 8787

set -eu

DEST="${1:-$(cd "$(dirname "$0")/.." && pwd)/build}"
PORT="${2:-8787}"
APP="$DEST/JobPilot.app"

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"

cat > "$APP/Contents/Info.plist" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>JobPilot</string>
    <key>CFBundleDisplayName</key>
    <string>JobPilot</string>
    <key>CFBundleIdentifier</key>
    <string>com.jobpilot.launcher</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>JobPilot</string>
    <key>LSMinimumSystemVersion</key>
    <string>12.0</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
PLIST_EOF

cat > "$APP/Contents/MacOS/JobPilot" <<LAUNCHER_EOF
#!/bin/sh
exec open "http://127.0.0.1:$PORT"
LAUNCHER_EOF

chmod +x "$APP/Contents/MacOS/JobPilot"

echo "Bundle généré : $APP"
echo "Glissez-le dans /Applications ou le Dock."
echo "Il n'héberge rien : lancez le serveur avec scripts/install_agent.sh."
