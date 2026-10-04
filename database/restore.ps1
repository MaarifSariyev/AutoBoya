# PostgreSQL Database Restore Script (PowerShell for Windows)
param (
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    [string]$ContainerName = "paint_postgres",
    [string]$DbUser = "paint_user",
    [string]$DbName = "paint_db"
)

if (!(Test-Path $BackupFile)) {
    Write-Host "Error: Backup file '$BackupFile' does not exist." -ForegroundColor Red
    exit 1
}

Write-Host "Restoring database '$DbName' from '$BackupFile'..." -ForegroundColor Cyan

Get-Content $BackupFile | docker exec -i $ContainerName psql -U $DbUser -d $DbName

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database restore completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Database restore failed!" -ForegroundColor Red
}
