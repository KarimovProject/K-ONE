[CmdletBinding()]
param([string]$Bind = "")

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Run scripts\setup-local.ps1 first." }

function Test-LocalPortAvailable([int]$Port) {
    $listener = [System.Net.Sockets.TcpListener]::new(
        [System.Net.IPAddress]::Loopback,
        $Port
    )
    try {
        $listener.Start()
        return $true
    } catch {
        return $false
    } finally {
        $listener.Stop()
    }
}

if (-not $Bind) {
    $selectedPort = 8000..8010 | Where-Object { Test-LocalPortAvailable $_ } | Select-Object -First 1
    if (-not $selectedPort) {
        throw "Ports 8000 through 8010 are occupied. Stop one process and try again."
    }
    $Bind = "127.0.0.1:$selectedPort"
    if ($selectedPort -ne 8000) {
        Write-Warning "Port 8000 is occupied. IEMS will use port $selectedPort."
    }
}

Write-Host "IEMS URL: http://$Bind/"

& (Join-Path $PSScriptRoot "check-services.ps1")
Push-Location $projectRoot
try {
    & $python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw "Django migrations failed." }
    & $python manage.py runserver $Bind
} finally {
    Pop-Location
}
