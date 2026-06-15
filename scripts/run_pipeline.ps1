# run_pipeline.ps1
# SpiritPulse — Full pipeline runner
# Usage: .\scripts\run_pipeline.ps1
# Runs: ingestion → dbt transform → starts FastAPI

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SpiritPulse Pipeline Runner" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Ingestion
Write-Host "[1/3] Running DLT ingestion..." -ForegroundColor Yellow
Set-Location "$Root\ingestion"
python pipeline.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Ingestion failed." -ForegroundColor Red
    exit 1
}
Write-Host "  Ingestion complete." -ForegroundColor Green
Write-Host ""

# Step 2: dbt transform
Write-Host "[2/3] Running dbt transformations..." -ForegroundColor Yellow
Set-Location "$Root\transform\spiritpulse_dbt"
dbt run --profiles-dir .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: dbt run failed." -ForegroundColor Red
    exit 1
}
Write-Host "  dbt models built." -ForegroundColor Green
Write-Host ""

# Step 3: Start FastAPI
Write-Host "[3/3] Starting FastAPI server..." -ForegroundColor Yellow
Set-Location $Root
Write-Host "  API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Dashboard: open dashboard/index.html in your browser" -ForegroundColor Cyan
Write-Host ""
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
