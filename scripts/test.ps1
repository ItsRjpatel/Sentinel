$ErrorActionPreference = "Stop"

if (!(Test-Path -Path ".venv")) {
    Write-Host "Virtual environment not found. Please run scripts\setup.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\Activate.ps1
Set-Location -Path "backend"

Write-Host "Running Tests..."
pytest
