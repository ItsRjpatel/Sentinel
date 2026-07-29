$ErrorActionPreference = "Stop"

Write-Host "Setting up Sentinel Backend..."

if (!(Test-Path -Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
Set-Location -Path "backend"
python -m pip install --upgrade pip
pip install -e ".[dev]"

Write-Host "Setup complete."
