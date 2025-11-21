#!/usr/bin/env pwsh
# Start Script - License Plate Reconstruction System
# Porneste Frontend + Backend + PostgreSQL

Write-Host "Starting License Plate Reconstruction System..." -ForegroundColor Cyan
Write-Host "   (Frontend + Backend + PostgreSQL)" -ForegroundColor White
Write-Host ""

# Verifica Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}
Write-Host "Docker is running" -ForegroundColor Green

# Porneste PostgreSQL
Write-Host ""
Write-Host "Starting PostgreSQL..." -ForegroundColor Yellow
$containerStatus = docker ps -a --filter "name=lpr_postgres" --format "{{.Status}}" 2>$null
if ($containerStatus -like "*Up*") {
    Write-Host "PostgreSQL already running" -ForegroundColor Green
} else {
    # Start only PostgreSQL service (not all services)
    docker-compose up -d postgres
    Write-Host "PostgreSQL started" -ForegroundColor Green
}

# Asteapta PostgreSQL
Write-Host ""
Write-Host "Waiting for PostgreSQL..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
while ($attempt -lt $maxAttempts) {
    $attempt++
    $pgReady = docker exec lpr_postgres pg_isready -U lpr_user -d lpr_database 2>$null
    if ($pgReady -like "*accepting connections*") {
        Write-Host "PostgreSQL ready!" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 1
}

# Start Frontend in background
Write-Host ""
Write-Host "Starting React Frontend..." -ForegroundColor Cyan

if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies (first time)..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

$frontendJob = Start-Job -ScriptBlock {
    Set-Location $args[0]
    Set-Location frontend
    npm run dev 2>&1
} -ArgumentList $PWD

Write-Host "Frontend started in background" -ForegroundColor Green
Start-Sleep -Seconds 2

# Start Backend in foreground
Write-Host ""
Write-Host "Starting FastAPI Backend..." -ForegroundColor Cyan
Write-Host "-------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs:" -ForegroundColor White
Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop everything..." -ForegroundColor DarkGray
Write-Host ""

Set-Location backend

try {
    & .\venv\Scripts\Activate.ps1
    python main.py
} finally {
    Write-Host ""
    Write-Host "Shutting down..." -ForegroundColor Yellow
    
    Write-Host "Stopping frontend..." -ForegroundColor Yellow
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    
    # Kill all node processes
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "All services stopped" -ForegroundColor Green
    Write-Host ""
    Write-Host "Tip: PostgreSQL is still running in Docker" -ForegroundColor DarkGray
    Write-Host "   Use '.\stop.ps1' to stop Docker too" -ForegroundColor DarkGray
}
