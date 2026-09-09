[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "==============================================" -ForegroundColor Yellow
Write-Host " Stopping IEMS Local/LAN Services             " -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Yellow

$taskNames = @("IEMS Web", "IEMS Celery Worker", "IEMS Celery Beat")

try {
    $service = New-Object -ComObject("Schedule.Service")
    $service.Connect()
    $rootFolder = $service.GetFolder("\")

    foreach ($name in $taskNames) {
        try {
            $task = $rootFolder.GetTask($name)
            if ($task.State -eq 4) { # Running
                Write-Host "Stopping task '$name'..."
                $task.Stop(0)
                Write-Host "  Stopped task '$name'."
            } else {
                Write-Host "Task '$name' is not running (State: $($task.State))."
            }
        } catch {
            Write-Warning "Could not access task '$name': $_"
        }
    }
} catch {
    Write-Warning "Could not connect to Task Scheduler: $_"
}

# Wait for graceful shutdown
Start-Sleep -Seconds 2

# Safely verify if any IEMS processes remain and stop ONLY those specific to C:\IEMS
$iemsProcesses = Get-CimInstance Win32_Process | Where-Object {
    ($_.CommandLine -like "*D:\Projects\K ONE*" -or $_.CommandLine -like "*$projectRoot*") -and (
        $_.CommandLine -match "waitress" -or
        $_.CommandLine -match "manage\.py runserver" -or
        $_.CommandLine -match "celery -A config"
    )
}

if ($iemsProcesses) {
    foreach ($proc in $iemsProcesses) {
        try {
            Write-Host "Terminating lingering IEMS process $($proc.Name) (PID $($proc.ProcessId))..."
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Warning "Could not stop PID $($proc.ProcessId): $_"
        }
    }
}

# Check listener
$listener = netstat -ano -p tcp | findstr ":8012"
if ($listener) {
    Write-Warning "Port 8012 still has an active listener:`n$listener"
} else {
    Write-Host "Port 8012 is successfully freed." -ForegroundColor Green
}

Write-Host "IEMS services have been stopped." -ForegroundColor Green
