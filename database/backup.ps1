# PostgreSQL Database Backup Script (PowerShell for Windows)
param (
    [string]$ContainerName = "paint_postgres",
    [string]$DbUser = "paint_user",
    [string]$DbName = "paint_db",
    [string]$OutputDir = "./backups"
)

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutputFile = "$OutputDir/paint_db_backup_$Timestamp.sql"

Write-Host "Creating backup for database '$DbName' from container '$ContainerName'..." -ForegroundColor Cyan

docker exec -t $ContainerName pg_dump -U $DbUser $DbName > $OutputFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup successfully created at: $OutputFile" -ForegroundColor Green
} else {
    Write-Host "Backup failed! Please check if Docker container '$ContainerName' is running." -ForegroundColor Red
}
