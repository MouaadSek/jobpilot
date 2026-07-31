@echo off
REM Launch the JobPilot dashboard and open it in the default browser (Windows).
REM
REM Deliberately not automated into a scheduled task: the Startup-folder
REM shortcut is one documented drag (see README, "Windows startup"), and a
REM script that installs itself into someone's login is harder to remove than
REM to add.
REM
REM A dashboard already listening on the port is not an error: the CLI prints
REM that it is already running and exits 0, so double-clicking this twice is
REM harmless.

setlocal
set "REPO_ROOT=%~dp0.."
set "PORT=%~1"
if "%PORT%"=="" set "PORT=8787"

set "PYTHON=%REPO_ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo Interpreteur introuvable : %PYTHON%
    echo Creez le venv puis relancez : python -m venv .venv ^&^& .venv\Scripts\pip install -e .
    exit /b 1
)

start "" "http://127.0.0.1:%PORT%"
"%PYTHON%" -m jobpilot dashboard --port %PORT%
endlocal
