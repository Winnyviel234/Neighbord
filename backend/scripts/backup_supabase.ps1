param(
  [string]$OutputPath = ".\backups\neighbord-backup.sql"
)

$ErrorActionPreference = "Stop"

if (-not $env:DATABASE_URL) {
  Write-Host "DATABASE_URL no esta definido en el entorno."
  Write-Host "Ejemplo:"
  Write-Host '$env:DATABASE_URL="postgresql://postgres.ref:password@host:5432/postgres"'
  exit 1
}

$backupDir = Split-Path -Parent $OutputPath
if ($backupDir -and -not (Test-Path $backupDir)) {
  New-Item -ItemType Directory -Path $backupDir | Out-Null
}

pg_dump $env:DATABASE_URL --clean --if-exists --schema=public --file=$OutputPath
Write-Host "Backup creado en $OutputPath"
