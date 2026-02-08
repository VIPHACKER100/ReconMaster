# ReconMaster v3.1-Pro Windows Installer
# Professional setup for Windows-based reconnaissance

$currentDir = Get-Location
$toolsDir = Join-Path $currentDir "bin"
if (-not (Test-Path $toolsDir)) { New-Item -ItemType Directory -Path $toolsDir | Out-Null }

$tools = @(
    @{ name = "subfinder"; url = "https://github.com/projectdiscovery/subfinder/releases/download/v2.6.5/subfinder_2.6.5_windows_amd64.zip" },
    @{ name = "httpx"; url = "https://github.com/projectdiscovery/httpx/releases/download/v1.6.0/httpx_1.1.5_windows_amd64.zip" },
    @{ name = "nuclei"; url = "https://github.com/projectdiscovery/nuclei/releases/download/v3.1.0/nuclei_3.1.0_windows_amd64.zip" },
    @{ name = "dnsx"; url = "https://github.com/projectdiscovery/dnsx/releases/download/v1.1.6/dnsx_1.1.6_windows_amd64.zip" },
    @{ name = "ffuf"; url = "https://github.com/ffuf/ffuf/releases/download/v2.1.0/ffuf_2.1.0_windows_amd64.zip" },
    @{ name = "katana"; url = "https://github.com/projectdiscovery/katana/releases/download/v1.1.0/katana_1.1.0_windows_amd64.zip" },
    @{ name = "gowitness"; url = "https://github.com/sensepost/gowitness/releases/download/2.5.1/gowitness_2.5.1_windows_amd64.zip" },
    @{ name = "amass"; url = "https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_windows_amd64.zip" }
)

Write-Host "`n╦═╗╔═╗╔═╗╔═╗╔╗╔╔╦╗╔═╗╔═╗╔╦╗╔═╗╦═╗" -ForegroundColor Cyan
Write-Host "╠╦╝║╣ ║  ║ ║║║║║║║╠═╣╚═╗ ║ ║╣ ╠╦╝"
Write-Host "╩╚═╚═╝╚═╝╚═╝╝╚╝╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═" -ForegroundColor Cyan
Write-Host " Professional Windows Installer for v3.1.0-Pro`n" -ForegroundColor Yellow

foreach ($tool in $tools) {
    $destFile = Join-Path $toolsDir "$($tool.name).exe"
    if (Test-Path $destFile) {
        Write-Host "[!] $($tool.name) already exists, skipping." -ForegroundColor Gray
        continue
    }

    Write-Host "[*] Downloading and installing $($tool.name)..." -ForegroundColor Blue
    $tempDir = Join-Path $currentDir "temp_$($tool.name)"
    if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir | Out-Null }
    $zipPath = Join-Path $tempDir "package.zip"
    
    try {
        Invoke-WebRequest -Uri $tool.url -OutFile $zipPath -ErrorAction Stop
        Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
        
        # Find the executable (some zips have subdirectories or different names)
        $exe = Get-ChildItem -Path $tempDir -Filter "*.exe" -Recurse | Where-Object { $_.Name -like "*$($tool.name)*" -or $_.Name -eq "amass.exe" } | Select-Object -First 1
        if ($exe) {
            Move-Item -Path $exe.FullName -Destination $destFile -Force
            Write-Host "[+] $($tool.name) installed successfully." -ForegroundColor Green
        }
        else {
            Write-Warning "[-] Could not find executable for $($tool.name) in the downloaded package."
        }
    }
    catch {
        Write-Error "[-] Failed to install $($tool.name): $($_.Exception.Message)"
    }
    finally {
        if (Test-Path $tempDir) { Remove-Item -Path $tempDir -Recurse -Force }
    }
}

Write-Host "`n[+] All Windows tools are ready in .\bin\" -ForegroundColor Green
Write-Host "[*] You can now run: python reconmaster.py -d target.com" -ForegroundColor White
