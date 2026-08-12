[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$envFile = Join-Path $projectRoot ".env"

function Get-FirstService([string[]]$Names) {
    foreach ($name in $Names) {
        $service = Get-Service -Name $name -ErrorAction SilentlyContinue
        if ($service) { return $service }
    }
    return $null
}

$postgres = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $postgres) { throw "No native PostgreSQL Windows service was found." }
if ($postgres.Status -ne "Running") { throw "PostgreSQL service '$($postgres.Name)' is not running." }
Write-Host "PostgreSQL service: $($postgres.Name) ($($postgres.Status))"

$pgReady = Get-ChildItem "C:\Program Files\PostgreSQL" -Filter pg_isready.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $pgReady) { throw "pg_isready.exe was not found under C:\Program Files\PostgreSQL." }
& $pgReady.FullName -h 127.0.0.1 -p 5432
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL is not accepting connections on 127.0.0.1:5432." }

$redis = Get-FirstService -Names @("Redis", "Memurai")
if (-not $redis) { throw "No supported native Redis or Memurai Windows service was found." }
if ($redis.Status -ne "Running") { throw "Redis-compatible service '$($redis.Name)' is not running." }
Write-Host "Redis service: $($redis.Name) ($($redis.Status))"

$redisCli = Get-Command redis-cli.exe -ErrorAction SilentlyContinue
if (-not $redisCli -and (Test-Path "C:\Program Files\Redis\redis-cli.exe")) {
    $redisCli = Get-Item "C:\Program Files\Redis\redis-cli.exe"
}
if (-not $redisCli) { throw "redis-cli.exe was not found." }
$redisCliPath = if ($redisCli.Source) { $redisCli.Source } else { $redisCli.FullName }
$pong = & $redisCliPath -h 127.0.0.1 -p 6379 ping
if ($pong -ne "PONG") { throw "Redis PING failed: $pong" }
Write-Host "Redis PING: PONG"

if (-not (Test-Path $venvPython)) { throw "C:\IEMS\.venv is missing. Run scripts\setup-local.ps1." }
if (-not (Test-Path $envFile)) { throw "C:\IEMS\.env is missing. Copy .env.example and set DB_PASSWORD." }
$envText = Get-Content -Raw -LiteralPath $envFile
if ($envText -match "replace-with-your-local-postgresql-password") {
    throw "Set the existing local PostgreSQL password in .env before Django connectivity checks."
}

Push-Location $projectRoot
try {
    & $venvPython manage.py shell -c "from django.core.cache import cache; from config.health_checks import check_database, check_redis; db=check_database(); rd=check_redis(); cache.set('iems_native_probe','ok',10); assert cache.get('iems_native_probe') == 'ok'; print(db.as_dict()); print(rd.as_dict()); print('Django cache: ok')"
    if ($LASTEXITCODE -ne 0) { throw "Django dependency connectivity check failed." }
} finally {
    Pop-Location
}
