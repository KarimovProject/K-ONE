# Dot-sourced by backup.ps1 / verify-backup.ps1 / restore.ps1.
# Resolves a PostgreSQL client tool from PATH, otherwise from the newest
# installed major version under C:\Program Files\PostgreSQL\<n>\bin, so the
# scripts keep working across PostgreSQL upgrades (they used to hard-code 15).
function Find-PgTool([string]$Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    $root = "C:\Program Files\PostgreSQL"
    if (Test-Path -LiteralPath $root) {
        $versions = Get-ChildItem -LiteralPath $root -Directory |
            Where-Object { $_.Name -match '^\d+(\.\d+)?$' } |
            Sort-Object { [double]$_.Name } -Descending
        foreach ($version in $versions) {
            $candidate = Join-Path $version.FullName "bin\$Name"
            if (Test-Path -LiteralPath $candidate) { return $candidate }
        }
    }
    throw "$Name was not found on PATH or under $root."
}
