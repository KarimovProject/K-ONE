[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$envFile = Join-Path $projectRoot ".env"
$envExample = Join-Path $projectRoot ".env.example"

Push-Location $projectRoot
try {
    & py -3.13 --version
    if ($LASTEXITCODE -ne 0) {
        throw "Python 3.13 is required. Install it with: winget install Python.Python.3.13"
    }

    if (-not (Test-Path $venvPython)) {
        Write-Host "Creating C:\IEMS\.venv with Python 3.13..."
        & py -3.13 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
    }

    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements\dev.txt
    if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed." }

    if (-not (Test-Path $envFile)) {
        Copy-Item -LiteralPath $envExample -Destination $envFile
        Write-Warning "Created .env. Set DB_PASSWORD before starting Django."
    } elseif (Select-String -LiteralPath $envFile -Pattern "^POSTGRES_" -Quiet) {
        Write-Warning ".env uses legacy POSTGRES_* names. Replace them with DB_* from .env.example."
    }

    Write-Host "Native Windows environment is prepared. Run scripts\check-services.ps1 next."
} finally {
    Pop-Location
}

