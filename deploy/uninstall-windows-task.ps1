<#
.SYNOPSIS
Removes the current user's JobPilot Task Scheduler entry.

.DESCRIPTION
Removes only the named scheduled task. Project files, .env credentials, logs,
and the JobPilot database are not changed.
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "High")]
param(
    [ValidateNotNullOrEmpty()]
    [string]$TaskName = "JobPilot Daemon"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$taskPath = "\"
$task = Get-ScheduledTask -TaskName $TaskName -TaskPath $taskPath -ErrorAction SilentlyContinue
if ($null -eq $task) {
    Write-Host "Task '$TaskName' is not installed."
    return
}

if ($PSCmdlet.ShouldProcess($TaskName, "Unregister scheduled task")) {
    Unregister-ScheduledTask -TaskName $TaskName -TaskPath $taskPath -Confirm:$false
    Write-Host "Removed '$TaskName'. Project data and credentials were not changed."
}
