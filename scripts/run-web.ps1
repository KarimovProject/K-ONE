[CmdletBinding()]
param([string]$Bind = "127.0.0.1:8000")

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { throw "Run scripts\setup-local.ps1 first." }

& (Join-Path $PSScriptRoot "check-services.ps1")
Push-Location $projectRoot
try {
    & $python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw "Django migrations failed." }
    & $python manage.py runserver $Bind
} finally {
    Pop-Location
}

