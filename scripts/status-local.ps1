[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
$projectRoot = Split-Path -Parent $PSScriptRoot
$lanIP = "10.34.12.2"
$port = 8012
$baseUrl = "http://${lanIP}:${port}"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " IEMS Local/LAN Service Status Report         " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# 1. PostgreSQL Status
Write-Host "`n[1] PostgreSQL Service:" -ForegroundColor White
$pgService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($pgService) {
    $pgColor = if ($pgService.Status -eq "Running") { "Green" } else { "Red" }
    Write-Host "  Service: $($pgService.Name) | Status: $($pgService.Status) | StartType: $($pgService.StartType)" -ForegroundColor $pgColor
} else {
    Write-Host "  PostgreSQL service NOT FOUND" -ForegroundColor Red
}

$pgReady = Get-ChildItem "C:\Program Files\PostgreSQL" -Filter pg_isready.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if ($pgReady) {
    $pgReadyOut = & $pgReady.FullName -h 127.0.0.1 -p 5432 2>&1
    Write-Host "  Port 5432 Connectivity: $($pgReadyOut)" -ForegroundColor $(if ($LASTEXITCODE -eq 0) { "Green" } else { "Red" })
}

# 2. Redis Status
Write-Host "`n[2] Redis Service:" -ForegroundColor White
$redisService = Get-Service -Name "Redis", "Memurai" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($redisService) {
    $rdColor = if ($redisService.Status -eq "Running") { "Green" } else { "Red" }
    Write-Host "  Service: $($redisService.Name) | Status: $($redisService.Status) | StartType: $($redisService.StartType)" -ForegroundColor $rdColor
} else {
    Write-Host "  Redis service NOT FOUND" -ForegroundColor Red
}

$redisCli = Get-Command redis-cli.exe -ErrorAction SilentlyContinue
if (-not $redisCli -and (Test-Path "C:\Program Files\Redis\redis-cli.exe")) {
    $redisCli = Get-Item "C:\Program Files\Redis\redis-cli.exe"
}
if ($redisCli) {
    $cliPath = if ($redisCli.Source) { $redisCli.Source } else { $redisCli.FullName }
    $pong = & $cliPath -h 127.0.0.1 -p 6379 ping 2>&1
    Write-Host "  Redis PING (127.0.0.1:6379): $pong" -ForegroundColor $(if ($pong -eq "PONG") { "Green" } else { "Red" })
}

# 3. Scheduled Tasks Status
Write-Host "`n[3] Windows Scheduled Tasks:" -ForegroundColor White
$taskStateMap = @{
    0 = "Unknown";
    1 = "Disabled";
    2 = "Queued";
    3 = "Ready";
    4 = "Running"
}

try {
    $service = New-Object -ComObject("Schedule.Service")
    $service.Connect()
    $rootFolder = $service.GetFolder("\")

    $tasks = @("IEMS Web", "IEMS Celery Worker", "IEMS Celery Beat")
    foreach ($taskName in $tasks) {
        try {
            $task = $rootFolder.GetTask($taskName)
            $stateName = if ($taskStateMap.ContainsKey($task.State)) { $taskStateMap[$task.State] } else { "State ($($task.State))" }
            $color = if ($task.State -eq 4) { "Green" } else { "Yellow" }
            $enabled = if ($task.Enabled) { "Enabled" } else { "Disabled" }
            $lastRunTime = $task.LastRunTime
            $lastResult = $task.LastTaskResult
            Write-Host "  Task: $($task.Name)" -ForegroundColor $color
            Write-Host "    State: $stateName | Status: $enabled | Last Run: $lastRunTime | Last Result: $lastResult"
        } catch {
            Write-Host "  Task: $taskName - NOT REGISTERED ($($_))" -ForegroundColor Red
        }
    }
} catch {
    Write-Warning "Could not query Task Scheduler: $_"
}

# 4. Port 8012 Listener
Write-Host "`n[4] Port 8012 Listener:" -ForegroundColor White
$listener = netstat -ano -p tcp | findstr ":8012"
if ($listener) {
    Write-Host "  $listener" -ForegroundColor Green
} else {
    Write-Host "  No active listener on port 8012" -ForegroundColor Red
}

# 5. HTTP Health Checks
Write-Host "`n[5] Application Health Check:" -ForegroundColor White
$healthUrl = "$baseUrl/health/"
$readyUrl = "$baseUrl/health/ready/"
try {
    $healthResp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  $healthUrl -> HTTP $($healthResp.StatusCode): $($healthResp.Content.Trim())" -ForegroundColor Green
} catch {
    Write-Host "  $healthUrl -> FAILED ($($_.Exception.Message))" -ForegroundColor Red
}

try {
    $readyResp = Invoke-WebRequest -Uri $readyUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  $readyUrl -> HTTP $($readyResp.StatusCode): $($readyResp.Content.Trim())" -ForegroundColor Green
} catch {
    Write-Host "  $readyUrl -> FAILED ($($_.Exception.Message))" -ForegroundColor Red
}

# 6. Exact URLs
Write-Host "`n[6] Target LAN URLs:" -ForegroundColor White
Write-Host "  Base URL:         $baseUrl/" -ForegroundColor Cyan
Write-Host "  Dashboard:        $baseUrl/dashboard/" -ForegroundColor Cyan
Write-Host "  Calendar (Month): $baseUrl/dashboard/calendar/?view=month" -ForegroundColor Cyan
Write-Host "  Calendar (Week):  $baseUrl/dashboard/calendar/?view=week" -ForegroundColor Cyan
Write-Host "  Workspace:        $baseUrl/workspace/" -ForegroundColor Cyan
Write-Host "  Login:            $baseUrl/accounts/login/" -ForegroundColor Cyan
Write-Host "==============================================`n" -ForegroundColor Cyan
