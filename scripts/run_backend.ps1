$ErrorActionPreference = "Stop"

Write-Host "Starting Sentinel Backend..."

if (!(Test-Path -Path ".venv")) {
    Write-Host "Virtual environment not found. Please run scripts\setup.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\Activate.ps1
Set-Location -Path "backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
