[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$logDirectory = Join-Path $projectRoot "logs"

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

& (Join-Path $PSScriptRoot "check-services.ps1")

$selectedPort = 8000..8010 | Where-Object { Test-LocalPortAvailable $_ } | Select-Object -First 1
if (-not $selectedPort) {
    throw "Ports 8000 through 8010 are occupied. Stop one process and try again."
}
if ($selectedPort -ne 8000) {
    Write-Warning "Port 8000 is occupied. IEMS will use port $selectedPort."
}

New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$powershell = (Get-Command powershell.exe).Source

function Start-IemsProcess([string]$Name, [string]$Script, [string[]]$ExtraArguments) {
    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $Script
    ) + $ExtraArguments
    $process = Start-Process `
        -FilePath $powershell `
        -ArgumentList $arguments `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $logDirectory "$Name.out.log") `
        -RedirectStandardError (Join-Path $logDirectory "$Name.err.log") `
        -PassThru
    Write-Host "$Name started (PID $($process.Id))."
}

Start-IemsProcess `
    -Name "web" `
    -Script (Join-Path $PSScriptRoot "run-web.ps1") `
    -ExtraArguments @("-Bind", "127.0.0.1:$selectedPort")
Start-IemsProcess -Name "celery" -Script (Join-Path $PSScriptRoot "run-celery.ps1") -ExtraArguments @()
Start-IemsProcess -Name "beat" -Script (Join-Path $PSScriptRoot "run-beat.ps1") -ExtraArguments @()

Write-Host "IEMS local processes are starting."
Write-Host "Open: http://127.0.0.1:$selectedPort/"
Write-Host "Logs: $logDirectory"
Write-Host "If the page is not ready yet, wait a few seconds and refresh."
