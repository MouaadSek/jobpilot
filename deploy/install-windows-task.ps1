<#
.SYNOPSIS
Registers the JobPilot daemon for the current Windows user.

.DESCRIPTION
Creates a Task Scheduler task that starts JobPilot at sign-in and lets the
Python daemon run its ingest-and-score cycle at the requested interval.

The task uses the current user's interactive token, so it does not store a
password and runs only while that user is signed in. API keys remain in the
project's gitignored .env file and are never copied into the task definition.

.PARAMETER ProjectRoot
JobPilot checkout containing .venv\Scripts\jobpilot.exe.

.PARAMETER IntervalHours
Hours between daemon cycles. Defaults to 3.

.PARAMETER TaskName
Task Scheduler name. Defaults to "JobPilot Daemon".

.PARAMETER Replace
Replace an existing task with the same name.
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [ValidateRange(0.1, 168.0)]
    [double]$IntervalHours = 3,
    [ValidateNotNullOrEmpty()]
    [string]$TaskName = "JobPilot Daemon",
    [switch]$Replace
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$jobpilotExe = Join-Path $resolvedRoot ".venv\Scripts\jobpilot.exe"
if (-not (Test-Path -LiteralPath $jobpilotExe -PathType Leaf)) {
    throw "Missing $jobpilotExe. Create the Windows virtual environment and run pip install -e `".[dev]`" first."
}

$taskPath = "\"
$existingTask = Get-ScheduledTask -TaskName $TaskName -TaskPath $taskPath -ErrorAction SilentlyContinue
if ($null -ne $existingTask -and -not $Replace) {
    throw "Task '$TaskName' already exists. Re-run with -Replace to update it."
}

$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$interval = $IntervalHours.ToString(
    [System.Globalization.CultureInfo]::InvariantCulture
)
$action = New-ScheduledTaskAction `
    -Execute $jobpilotExe `
    -Argument "daemon --interval-hours $interval" `
    -WorkingDirectory $resolvedRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
$principal = New-ScheduledTaskPrincipal `
    -UserId $currentUser `
    -LogonType Interactive `
    -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

if ($PSCmdlet.ShouldProcess($TaskName, "Register current-user scheduled task")) {
    $registerParams = @{
        TaskName = $TaskName
        Description = "JobPilot ingest and scoring daemon (credentials loaded from project .env)"
        Action = $action
        Trigger = $trigger
        TaskPath = $taskPath
        Principal = $principal
        Settings = $settings
    }
    if ($Replace) {
        $registerParams.Force = $true
    }
    Register-ScheduledTask @registerParams | Out-Null
    Write-Host "Registered '$TaskName' for $currentUser."
    Write-Host "Start now: Start-ScheduledTask -TaskName '$TaskName' -TaskPath '$taskPath'"
    Write-Host "Logs:      $resolvedRoot\logs\jobpilot.log"
}
