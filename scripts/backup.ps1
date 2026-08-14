param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$BackupRoot = (Join-Path (Split-Path -Parent $PSScriptRoot) "backups")
)

$ErrorActionPreference = "Stop"

function Read-IemsEnv([string]$Path) {
    $values = @{}
    if (Test-Path -LiteralPath $Path) {
        foreach ($line in Get-Content -LiteralPath $Path) {
            if ($line -match '^\s*([^#][^=]*)=(.*)$') {
                $values[$matches[1].Trim()] = $matches[2].Trim().Trim('"').Trim("'")
            }
        }
    }
    return $values
}

function Get-IemsValue($Values, [string]$Name, [string]$Default = "") {
    $processValue = [Environment]::GetEnvironmentVariable($Name, "Process")
    if ($processValue) { return $processValue }
    if ($Values.ContainsKey($Name)) { return $Values[$Name] }
    return $Default
}

$resolvedProject = (Resolve-Path -LiteralPath $ProjectRoot).Path
$values = Read-IemsEnv (Join-Path $resolvedProject ".env")
$databaseName = Get-IemsValue $values "DB_NAME" "iems"
$databaseUser = Get-IemsValue $values "DB_USER" "postgres"
$databasePassword = Get-IemsValue $values "DB_PASSWORD"
$databaseHost = Get-IemsValue $values "DB_HOST" "127.0.0.1"
$databasePort = Get-IemsValue $values "DB_PORT" "5432"
$mediaRoot = Get-IemsValue $values "DJANGO_MEDIA_ROOT" (Join-Path $resolvedProject "media")

$pgDump = Get-Command pg_dump.exe -ErrorAction SilentlyContinue
if (-not $pgDump) {
    $candidate = "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe"
    if (-not (Test-Path -LiteralPath $candidate)) { throw "pg_dump.exe was not found." }
    $pgDumpPath = $candidate
} else { $pgDumpPath = $pgDump.Source }

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDirectory = Join-Path $BackupRoot $timestamp
New-Item -ItemType Directory -Path $backupDirectory -Force | Out-Null
$databaseFile = Join-Path $backupDirectory "database.dump"
$mediaDirectory = Join-Path $backupDirectory "media"
New-Item -ItemType Directory -Path $mediaDirectory -Force | Out-Null

$oldPassword = [Environment]::GetEnvironmentVariable("PGPASSWORD", "Process")
try {
    [Environment]::SetEnvironmentVariable("PGPASSWORD", $databasePassword, "Process")
    & $pgDumpPath -Fc -h $databaseHost -p $databasePort -U $databaseUser -d $databaseName -f $databaseFile
    if ($LASTEXITCODE -ne 0) { throw "pg_dump failed with exit code $LASTEXITCODE." }
} finally {
    [Environment]::SetEnvironmentVariable("PGPASSWORD", $oldPassword, "Process")
}

if (Test-Path -LiteralPath $mediaRoot) {
    Copy-Item -Path (Join-Path $mediaRoot "*") -Destination $mediaDirectory -Recurse -Force -ErrorAction SilentlyContinue
}

$manifest = [ordered]@{
    created_at = (Get-Date).ToUniversalTime().ToString("o")
    format = "iems-backup-v1"
    database = [ordered]@{ name = $databaseName; host = $databaseHost; port = $databasePort; dump = "database.dump" }
    media = "media"
    app_version = (Get-IemsValue $values "APP_VERSION" "unknown")
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backupDirectory "manifest.json") -Encoding utf8

$checksums = Get-ChildItem -LiteralPath $backupDirectory -File -Recurse |
    Where-Object Name -ne "checksums.json" |
    ForEach-Object {
        $relativePath = $_.FullName.Substring($backupDirectory.Length).TrimStart("\")
        [ordered]@{
            path = $relativePath.Replace("\", "/")
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
$checksums | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $backupDirectory "checksums.json") -Encoding utf8
Write-Output $backupDirectory
