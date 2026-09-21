[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$scriptsDir = Join-Path $projectRoot "scripts"
$logDirectory = Join-Path $projectRoot "logs"
$lanIP = "10.34.12.152"
$port = 8012
$baseUrl = "http://${lanIP}:${port}"

if (-not (Test-Path $logDirectory)) {
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
}

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " Starting IEMS Local/LAN Services (Waitress)   " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# 1. Verify PostgreSQL and Redis services
Write-Host "Step 1: Checking PostgreSQL and Redis services..."
& (Join-Path $scriptsDir "check-services.ps1")
if ($LASTEXITCODE -ne 0) {
    throw "Service dependency check failed."
}

# 2. Ensure scheduled tasks are registered
$service = New-Object -ComObject("Schedule.Service")
$service.Connect()
$rootFolder = $service.GetFolder("\")

$taskNames = @("IEMS Web", "IEMS Celery Worker", "IEMS Celery Beat", "IEMS Telegram Poll")
$needRegister = $false
foreach ($name in $taskNames) {
    try {
        $null = $rootFolder.GetTask($name)
    } catch {
        $needRegister = $true
        break
    }
}

if ($needRegister) {
    Write-Host "Step 2: Registering IEMS Windows Scheduled Tasks..."
    & (Join-Path $scriptsDir "register-tasks.ps1")
}

# 3. Start the three Windows scheduled tasks
Write-Host "Step 3: Starting IEMS Windows Scheduled Tasks..."
foreach ($name in $taskNames) {
    $task = $rootFolder.GetTask($name)
    if ($task.State -eq 4) {
        Write-Host "  - Task '$name' is already running."
    } else {
        $task.Run($null)
        Write-Host "  - Task '$name' started."
    }
}

# 4. Wait for readiness
Write-Host "Step 4: Waiting for IEMS Web service readiness at $baseUrl/health/ ..."
$healthUrl = "$baseUrl/health/"
$readyUrl = "$baseUrl/health/ready/"
$maxAttempts = 30
$attempt = 0
$isHealthy = $false

while ($attempt -lt $maxAttempts) {
    $attempt++
    Start-Sleep -Milliseconds 500
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $isHealthy = $true
            break
        }
    } catch {
        # continue waiting
    }
}

if (-not $isHealthy) {
    throw "IEMS Web did not become healthy within 15 seconds. Check $logDirectory\web.log for details."
}

# 5. Verify health & readiness
Write-Host "Step 5: Verifying health and readiness endpoints..."
$healthResp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3
$readyResp = Invoke-WebRequest -Uri $readyUrl -UseBasicParsing -TimeoutSec 3

Write-Host "  Health status: $($healthResp.StatusCode) - $($healthResp.Content.Trim())" -ForegroundColor Green
Write-Host "  Readiness status: $($readyResp.StatusCode) - $($readyResp.Content.Trim())" -ForegroundColor Green

Write-Host "`n==============================================" -ForegroundColor Green
Write-Host " IEMS LAN RUNTIME IS READY AND ACTIVE" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host " Target LAN URL:  $baseUrl/" -ForegroundColor Yellow
Write-Host " Public Dashboard: $baseUrl/dashboard/" -ForegroundColor Yellow
Write-Host " Calendar:        $baseUrl/dashboard/calendar/?view=month" -ForegroundColor Yellow
Write-Host " Workspace:       $baseUrl/workspace/" -ForegroundColor Yellow
Write-Host " Accounts Login:  $baseUrl/accounts/login/" -ForegroundColor Yellow
Write-Host " Health endpoint: $healthUrl" -ForegroundColor Yellow
Write-Host " Logs Directory:  $logDirectory" -ForegroundColor Gray
Write-Host "==============================================`n" -ForegroundColor Green
