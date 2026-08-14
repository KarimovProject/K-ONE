param(
    [Parameter(Mandatory = $true)][string]$BackupDirectory,
    [Parameter(Mandatory = $true)][string]$RestoreDatabase,
    [string]$RestoreMediaRoot = (Join-Path (Split-Path -Parent $PSScriptRoot) "restore-media"),
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"
if ($RestoreDatabase -notmatch '^iems_restore_[a-zA-Z0-9_]+$') {
    throw "Restore database must begin with iems_restore_ and contain only letters, numbers or underscores."
}
& (Join-Path $PSScriptRoot "verify-backup.ps1") -BackupDirectory $BackupDirectory
$resolvedBackup = (Resolve-Path -LiteralPath $BackupDirectory).Path
$manifest = Get-Content -Raw -LiteralPath (Join-Path $resolvedBackup "manifest.json") | ConvertFrom-Json

$projectRoot = Split-Path -Parent $PSScriptRoot
$values = @{}
foreach ($line in Get-Content -LiteralPath (Join-Path $projectRoot ".env")) {
    if ($line -match '^\s*([^#][^=]*)=(.*)$') { $values[$matches[1].Trim()] = $matches[2].Trim() }
}
$databaseUser = if ($env:DB_USER) { $env:DB_USER } elseif ($values.DB_USER) { $values.DB_USER } else { "postgres" }
$databasePassword = if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { $values.DB_PASSWORD }
$databaseHost = if ($env:DB_HOST) { $env:DB_HOST } elseif ($values.DB_HOST) { $values.DB_HOST } else { "127.0.0.1" }
$databasePort = if ($env:DB_PORT) { $env:DB_PORT } elseif ($values.DB_PORT) { $values.DB_PORT } else { "5432" }
$bin = "C:\Program Files\PostgreSQL\15\bin"
$createdb = Join-Path $bin "createdb.exe"
$dropdb = Join-Path $bin "dropdb.exe"
$pgRestore = Join-Path $bin "pg_restore.exe"

$oldPassword = [Environment]::GetEnvironmentVariable("PGPASSWORD", "Process")
try {
    [Environment]::SetEnvironmentVariable("PGPASSWORD", $databasePassword, "Process")
    if ($Recreate) { & $dropdb -h $databaseHost -p $databasePort -U $databaseUser --if-exists $RestoreDatabase }
    & $createdb -h $databaseHost -p $databasePort -U $databaseUser $RestoreDatabase
    if ($LASTEXITCODE -ne 0) { throw "Could not create isolated restore database." }
    & $pgRestore -h $databaseHost -p $databasePort -U $databaseUser -d $RestoreDatabase --no-owner --no-privileges (Join-Path $resolvedBackup $manifest.database.dump)
    if ($LASTEXITCODE -ne 0) { throw "pg_restore failed." }
} finally {
    [Environment]::SetEnvironmentVariable("PGPASSWORD", $oldPassword, "Process")
}

$resolvedMediaParent = Split-Path -Parent ([IO.Path]::GetFullPath($RestoreMediaRoot))
if (-not (Test-Path -LiteralPath $resolvedMediaParent)) { New-Item -ItemType Directory -Path $resolvedMediaParent -Force | Out-Null }
New-Item -ItemType Directory -Path $RestoreMediaRoot -Force | Out-Null
$backupMedia = Join-Path $resolvedBackup $manifest.media
if (Test-Path -LiteralPath $backupMedia) {
    Copy-Item -Path (Join-Path $backupMedia "*") -Destination $RestoreMediaRoot -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Output "PASS: restored database=$RestoreDatabase media=$RestoreMediaRoot"
