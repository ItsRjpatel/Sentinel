$ErrorActionPreference = "Stop"

if (!(Test-Path -Path ".venv")) {
    Write-Host "Virtual environment not found. Please run scripts\setup.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\Activate.ps1
Set-Location -Path "backend"

Write-Host "Running Ruff..."
ruff check app

Write-Host "Running Mypy..."
mypy app

Write-Host "Linting complete."
