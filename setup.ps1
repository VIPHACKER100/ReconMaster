<#
Simple Windows setup helper for ReconMaster.

This script does NOT install Go-based recon tools (subfinder, httpx, ffuf, etc.).
Those are Linux-native or Go tools and are best installed under WSL2/Ubuntu or a Linux VM.

What this script does:
- Checks for Python and pip
- Creates a virtual environment in `.venv`
- Installs Python requirements from `requirements.txt`
- Prints guidance for installing full recon toolchain (use WSL)
#>

Write-Host "ReconMaster Windows helper script" -ForegroundColor Cyan

function Abort($msg) { Write-Host $msg -ForegroundColor Red; exit 1 }

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { Abort "Python not found. Please install Python 3.8+ and re-run this script." }

Write-Host "Using Python: $($python.Source)" -ForegroundColor Green

# Create venv
if (-not (Test-Path -Path .venv)) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
}

Write-Host "Activating virtual environment and installing requirements..."
.\.venv\Scripts\Activate.ps1
if (Test-Path requirements.txt) {
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    Write-Host "Python requirements installed." -ForegroundColor Green
} else {
    Write-Host "No requirements.txt found. Skipping pip install." -ForegroundColor Yellow
}

Write-Host "\nNotes:" -ForegroundColor Cyan
Write-Host "- Many ReconMaster features require external tools (subfinder, ffuf, httpx, gowitness, katana, nmap, etc.)." -ForegroundColor Yellow
Write-Host "- For full functionality on Windows, install WSL2 (Ubuntu) and run the install script there:" -ForegroundColor Yellow
Write-Host "    1) Open PowerShell as Administrator and run: wsl --install -d Ubuntu" -ForegroundColor Gray
Write-Host "    2) Launch Ubuntu, then in WSL run the provided install script: ./install_reconmaster.sh" -ForegroundColor Gray

Write-Host "- If you prefer not to use WSL, install the Go tools and dependencies natively and ensure they are on PATH." -ForegroundColor Gray

Write-Host "Setup complete." -ForegroundColor Green
