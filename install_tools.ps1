# ReconMaster Windows Tool Installer
# This script downloads the missing Go-based reconnaissance tools for Windows.

$currentDir = Get-Location
$toolsDir = Join-Path $currentDir "bin"

if (-not (Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir
}

function Download-Tool($name, $url, $zipName) {
    Write-Host "Installing $name..." -ForegroundColor Cyan
    $tempDir = Join-Path $currentDir "temp_dl"
    if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir }
    
    $zipPath = Join-Path $tempDir $zipName
    
    try {
        Write-Host "Downloading $url" -ForegroundColor Gray
        Invoke-WebRequest -Uri $url -OutFile $zipPath -ErrorAction Stop
        
        if ($zipName.EndsWith(".zip")) {
            Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
        }
        elseif ($zipName.EndsWith(".tar.gz")) {
            tar -xzf $zipPath -C $tempDir
        }
        
        $exe = Get-ChildItem -Path $tempDir -Filter "$name.exe" -Recurse | Select-Object -First 1
        if (-not $exe) {
            $exe = Get-ChildItem -Path $tempDir -Filter "*.exe" -Recurse | Select-Object -First 1
        }
        
        if ($exe) {
            Move-Item -Path $exe.FullName -Destination (Join-Path $toolsDir "$name.exe") -Force
            Write-Host "Successfully installed $name" -ForegroundColor Green
        }
        else {
            Write-Warning "Could not find $name.exe in the downloaded archive."
        }
    }
    catch {
        Write-Error "Failed to install $name: $($_.Exception.Message)"
    }
    finally {
        if (Test-Path $tempDir) { Remove-Item -Path $tempDir -Recurse -Force }
    }
}

# --- Tool Definitions ---

Download-Tool "subfinder" "https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_windows_amd64.zip" "subfinder.zip"
Download-Tool "httpx" "https://github.com/projectdiscovery/httpx/releases/download/v1.6.0/httpx_1.6.0_windows_amd64.zip" "httpx.zip"
Download-Tool "ffuf" "https://github.com/ffuf/ffuf/releases/download/v2.1.0/ffuf_2.1.0_windows_amd64.zip" "ffuf.zip"
Download-Tool "katana" "https://github.com/projectdiscovery/katana/releases/download/v1.1.0/katana_1.1.0_windows_amd64.zip" "katana.zip"
Download-Tool "gowitness" "https://github.com/sensepost/gowitness/releases/download/2.5.1/gowitness_2.5.1_windows_amd64.zip" "gowitness.zip"
Download-Tool "subzy" "https://github.com/LukaSikic/subzy/releases/download/v1.1.6/subzy_v1.1.6_windows_amd64.zip" "subzy.zip"
Download-Tool "amass" "https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_windows_amd64.zip" "amass.zip"

Write-Host "`nTools installed in: $toolsDir" -ForegroundColor Cyan
Write-Host "Reconnaissance tools are now ready." -ForegroundColor Green
