[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$celery = Join-Path $projectRoot ".venv\Scripts\celery.exe"
if (-not (Test-Path $celery)) { throw "Run scripts\setup-local.ps1 first." }

& (Join-Path $PSScriptRoot "check-services.ps1")
Push-Location $projectRoot
try {
    & $celery -A config worker -l info --pool=solo
} finally {
    Pop-Location
}

