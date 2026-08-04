@echo off
REM Run the JobPilot ingestion daemon (Windows).
REM
REM The macOS side of this is a launchd agent that install_agent.sh writes for
REM you. There is no Windows equivalent here on purpose: the same reasoning as
REM jobpilot-dashboard.bat. A Startup-folder shortcut to this file is one
REM documented drag (see README, "Windows startup"), and a script that registers
REM a scheduled task under someone's login is harder to remove than to add.
REM
REM Unlike the dashboard there is no port to collide on: a second daemon would
REM be a second writer on the same SQLite file, doing the same idempotent
REM inserts. It wastes API calls rather than duplicating rows, but run one.
REM
REM Usage: jobpilot-daemon.bat [interval_hours]   (default 3)

setlocal
set "REPO_ROOT=%~dp0.."
set "INTERVAL=%~1"
if "%INTERVAL%"=="" set "INTERVAL=3"

set "PYTHON=%REPO_ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo Interpreteur introuvable : %PYTHON%
    echo Creez le venv puis relancez : python -m venv .venv ^&^& .venv\Scripts\pip install -e .
    exit /b 1
)

"%PYTHON%" -m jobpilot daemon --interval-hours %INTERVAL%
endlocal
