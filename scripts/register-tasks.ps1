[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = "D:\Projects\K ONE\K ONE"
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
    [string]$Arguments,
    [string]$TriggerXml = "",
    [string]$LogFile = ""
) {
    if (-not $TriggerXml) {
        $TriggerXml = "<LogonTrigger><UserId>$user</UserId></LogonTrigger>"
    }
    # Task Scheduler's XML schema (v1.3) has no <Environment> element, so
    # DJANGO_SETTINGS_MODULE is forced via a cmd.exe wrapper instead of
    # relying on manage.py/wsgi.py/celery.py's `local`-defaulting
    # os.environ.setdefault(). Without this, these tasks silently ran under
    # config.settings.local in production (DEBUG=True default, no forced
    # HTTPS/HSTS, insecure cookies).
    $wrappedCommand = "$env:ComSpec"
    # IEMS_PLAIN_HTTP_LAN=True: this LAN deployment is plain HTTP via Waitress
    # with no TLS-terminating reverse proxy in front of it, so production's
    # default HTTPS-only settings (SSL redirect + Secure cookies) would
    # 301-redirect every request to a nonexistent https:// endpoint and drop
    # the CSRF/session cookies entirely. Only this task sets the flag — it is
    # a dedicated name read directly from the process environment (not .env),
    # so it can never leak into a real TLS-fronted deployment or into tests.
    $redirect = if ($LogFile) { " >> `"$LogFile`" 2>&1" } else { "" }
    # pythonw.exe has no console, so without this redirect an uncaught
    # exception (e.g. the command crashing) leaves no trace anywhere —
    # the task just silently stops with LastTaskResult=1.
    $wrappedArguments = "/c set `"DJANGO_SETTINGS_MODULE=config.settings.production`"&& set `"IEMS_PLAIN_HTTP_LAN=True`"&& `"$Command`" $Arguments$redirect"
    # Values go into XML text nodes: the raw "&&" above made every task
    # definition malformed XML, so Task Scheduler rejected all of them.
    $esc = { param($value) [System.Security.SecurityElement]::Escape($value) }
    $Description = & $esc $Description
    $wrappedCommand = & $esc $wrappedCommand
    $wrappedArguments = & $esc $wrappedArguments
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
    $TriggerXml
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>$wrappedCommand</Command>
      <Arguments>$wrappedArguments</Arguments>
      <WorkingDirectory>$projectRoot</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@
    $service = New-Object -ComObject("Schedule.Service")
    $service.Connect()
    $folder = $service.GetFolder("\")
    $task = $folder.RegisterTask($TaskName, $xml, 6, $null, $null, 3)
    Write-Host "Registered task '$TaskName' (RestartOnFailure 3x, ExecutionTimeLimit 0s)."
}

Register-IemsScheduledTask `
    -TaskName "IEMS Web" `
    -Description "IEMS Web Server (Waitress WSGI on 0.0.0.0:8012)" `
    -Command $pythonwExe `
    -Arguments "-m waitress --listen=0.0.0.0:8012 config.wsgi:application"

Register-IemsScheduledTask `
    -TaskName "IEMS Celery Worker" `
    -Description "IEMS Celery Worker (solo pool)" `
    -Command $pythonwExe `
    -Arguments "-m celery -A config worker -l info --pool=solo --logfile=D:\Projects\K ONE\K ONE\logs\worker.log"

Register-IemsScheduledTask `
    -TaskName "IEMS Celery Beat" `
    -Description "IEMS Celery Beat Scheduler" `
    -Command $pythonwExe `
    -Arguments "-m celery -A config beat -l info --logfile=D:\Projects\K ONE\K ONE\logs\beat.log"

Register-IemsScheduledTask `
    -TaskName "IEMS Telegram Poll" `
    -Description "IEMS Telegram long-poll listener (/start account linking)" `
    -Command $pythonwExe `
    -Arguments "manage.py telegram_poll" `
    -LogFile (Join-Path $logDir "telegram_poll.log")

$backupScript = Join-Path $projectRoot "scripts\backup.ps1"
Register-IemsScheduledTask `
    -TaskName "IEMS Daily Backup" `
    -Description "IEMS nightly PostgreSQL + media backup (scripts\backup.ps1)" `
    -Command "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -Arguments "-NoProfile -ExecutionPolicy Bypass -File `"$backupScript`"" `
    -TriggerXml "<CalendarTrigger><StartBoundary>2026-01-01T02:00:00</StartBoundary><ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay></CalendarTrigger>"

Write-Host "All 5 IEMS Windows Scheduled Tasks registered successfully."
