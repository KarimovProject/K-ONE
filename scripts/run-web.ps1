[CmdletBinding()]
param([string]$Bind = "")

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$waitress = Join-Path $projectRoot ".venv\Scripts\waitress-serve.exe"

if (-not (Test-Path $python) -or -not (Test-Path $waitress)) {
    throw "Virtual environment executables missing. Run scripts\setup-local.ps1 first."
}

if (-not $Bind) {
    $Bind = "0.0.0.0:8012"
}

Write-Host "IEMS URL: http://$Bind/"

& (Join-Path $PSScriptRoot "check-services.ps1")
Push-Location $projectRoot
try {
    & $python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw "Django migrations failed." }
    & $waitress --listen=$Bind config.wsgi:application
} finally {
    Pop-Location
}
