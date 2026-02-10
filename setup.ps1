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
if (-not $python) { Abort "Python not found. Please install Python 3.9+ and re-run this script." }

Write-Host "Using Python: $($python.Source)" -ForegroundColor Green

# Fix Pip if corrupted (Common on Windows with multiple installs)
Write-Host "[*] Checking and repairing pip if necessary..." -ForegroundColor Blue
python -m ensurepip --upgrade
python -m pip install --upgrade pip colorama

# Create venv
if (-not (Test-Path -Path .venv)) {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Blue
    python -m venv .venv
}

Write-Host "[*] Activating environment and installing dependencies..." -ForegroundColor Blue
# Use full path to avoid issues
$activatePath = Join-Path (Get-Location) ".venv\Scripts\Activate.ps1"
& $activatePath

if (Test-Path requirements.txt) {
    python -m pip install -r requirements.txt
    Write-Host "✅ Python requirements installed." -ForegroundColor Green
}
else {
    Write-Host "[!] No requirements.txt found. Skipping pip install." -ForegroundColor Yellow
}

Write-Host "`n🚀 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Install core recon tools (httpx, nuclei, ffuf, etc.):" -ForegroundColor White
Write-Host "   powershell -File install_tools_final.ps1" -ForegroundColor Gray

Write-Host "2. Run your first scan:" -ForegroundColor White
Write-Host "   python reconmaster.py -d target.com --i-understand-this-requires-authorization" -ForegroundColor Gray

Write-Host "`n[+] Setup complete. ReconMaster Pro is ready!`n" -ForegroundColor Green
