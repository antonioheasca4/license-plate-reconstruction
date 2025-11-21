#!/usr/bin/env pwsh
# Stop Script pentru License Plate Reconstruction
# Oprește Backend + Docker PostgreSQL (opțional)

param(
    [switch]$KeepDocker,
    [switch]$RemoveData
)

Write-Host "🛑 Stopping License Plate Reconstruction System..." -ForegroundColor Cyan
Write-Host ""

# Oprește procesele Python (backend)
Write-Host "🔴 Stopping backend processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    $pythonProcesses | Where-Object { $_.Path -like "*venv*" } | Stop-Process -Force
    Write-Host "✅ Backend stopped" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No backend processes running" -ForegroundColor Gray
}

# Oprește procesele Node (frontend)
Write-Host ""
Write-Host "⚛️  Stopping frontend processes..." -ForegroundColor Yellow
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    $nodeProcesses | Where-Object { $_.Path -like "*node*" } | Stop-Process -Force
    Write-Host "✅ Frontend stopped" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No frontend processes running" -ForegroundColor Gray
}

# Oprește Docker (dacă nu e specificat -KeepDocker)
if (-not $KeepDocker) {
    Write-Host ""
    Write-Host "🐘 Stopping PostgreSQL container..." -ForegroundColor Yellow
    
    if ($RemoveData) {
        Write-Host "⚠️  WARNING: Removing container AND data!" -ForegroundColor Red
        docker-compose down -v
        Write-Host "✅ PostgreSQL stopped and data removed" -ForegroundColor Green
    } else {
        docker-compose down
        Write-Host "✅ PostgreSQL stopped (data preserved)" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "ℹ️  Keeping PostgreSQL container running (use -KeepDocker:$false to stop)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ Shutdown complete!" -ForegroundColor Cyan

# Opțiuni de utilizare
Write-Host ""
Write-Host "Usage examples:" -ForegroundColor DarkGray
Write-Host "  .\stop.ps1                    # Stop everything, keep data" -ForegroundColor DarkGray
Write-Host "  .\stop.ps1 -KeepDocker        # Stop backend only" -ForegroundColor DarkGray
Write-Host "  .\stop.ps1 -RemoveData        # Stop everything, remove data" -ForegroundColor DarkGray
