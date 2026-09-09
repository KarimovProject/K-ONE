[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = "D:\Projects\K ONE"
$venvDir = Join-Path $projectRoot ".venv\Scripts"
$pythonwExe = Join-Path $venvDir "pythonw.exe"
$logDir = Join-Path $projectRoot "logs"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

function Register-IemsScheduledTask(
    [string]$TaskName,
    [string]$Description,
    [string]$Command,
    [string]$Arguments
) {
    $xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.3" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>$Description</Description>
    <URI>\$TaskName</URI>
  </RegistrationInfo>
  <Principals>
    <Principal id="Author">
      <UserId>$sid</UserId>
      <LogonType>InteractiveToken</LogonType>
    </Principal>
  </Principals>
  <Settings>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
    <IdleSettings>
      <Duration>PT10M</Duration>
      <WaitTimeout>PT1H</WaitTimeout>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
  </Settings>
  <Triggers>
    <LogonTrigger>
      <UserId>$user</UserId>
    </LogonTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>$Command</Command>
      <Arguments>$Arguments</Arguments>
      <WorkingDirectory>$projectRoot</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@
    $service = New-Object -ComObject("Schedule.Service")
    $service.Connect()
    $folder = $service.GetFolder("\")
    $task = $folder.RegisterTask($TaskName, $xml, 6, $null, $null, 3)
    Write-Host "Registered task '$TaskName' (Logon trigger, RestartOnFailure 3x, ExecutionTimeLimit 0s)."
}

Register-IemsScheduledTask `
    -TaskName "IEMS Web" `
    -Description "IEMS Web Server (Waitress WSGI on 10.34.12.2:8012)" `
    -Command $pythonwExe `
    -Arguments "-m waitress --listen=10.34.12.2:8012 config.wsgi:application"

Register-IemsScheduledTask `
    -TaskName "IEMS Celery Worker" `
    -Description "IEMS Celery Worker (solo pool)" `
    -Command $pythonwExe `
    -Arguments "-m celery -A config worker -l info --pool=solo --logfile=D:\Projects\K ONE\logs\worker.log"

Register-IemsScheduledTask `
    -TaskName "IEMS Celery Beat" `
    -Description "IEMS Celery Beat Scheduler" `
    -Command $pythonwExe `
    -Arguments "-m celery -A config beat -l info --logfile=D:\Projects\K ONE\logs\beat.log"

Write-Host "All 3 IEMS Windows Scheduled Tasks registered successfully."
