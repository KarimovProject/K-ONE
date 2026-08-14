param([Parameter(Mandatory = $true)][string]$BackupDirectory)

$ErrorActionPreference = "Stop"
$resolvedBackup = (Resolve-Path -LiteralPath $BackupDirectory).Path
$manifestPath = Join-Path $resolvedBackup "manifest.json"
$checksumsPath = Join-Path $resolvedBackup "checksums.json"
if (-not (Test-Path -LiteralPath $manifestPath)) { throw "manifest.json is missing." }
if (-not (Test-Path -LiteralPath $checksumsPath)) { throw "checksums.json is missing." }
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
if ($manifest.format -ne "iems-backup-v1") { throw "Unsupported backup manifest format." }
$checksums = Get-Content -Raw -LiteralPath $checksumsPath | ConvertFrom-Json
foreach ($entry in $checksums) {
    $target = Join-Path $resolvedBackup $entry.path
    if (-not (Test-Path -LiteralPath $target)) { throw "Backup file missing: $($entry.path)" }
    $actual = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $entry.sha256) { throw "Checksum mismatch: $($entry.path)" }
}
$pgRestore = Get-Command pg_restore.exe -ErrorAction SilentlyContinue
$pgRestorePath = if ($pgRestore) { $pgRestore.Source } else { "C:\Program Files\PostgreSQL\15\bin\pg_restore.exe" }
if (-not (Test-Path -LiteralPath $pgRestorePath)) { throw "pg_restore.exe was not found." }
& $pgRestorePath --list (Join-Path $resolvedBackup $manifest.database.dump) | Out-Null
if ($LASTEXITCODE -ne 0) { throw "The PostgreSQL archive is invalid." }
Write-Output "PASS: backup archive and checksums are valid."
