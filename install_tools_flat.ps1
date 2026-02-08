# ReconMaster Windows Tool Installer - Flat Version
$currentDir = Get-Location
$toolsDir = Join-Path $currentDir "bin"
if (-not (Test-Path $toolsDir)) { New-Item -ItemType Directory -Path $toolsDir }

$tempDir = Join-Path $currentDir "temp_dl"

function Install-GoTool($name, $url) {
    if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir }
    $zipPath = Join-Path $tempDir "temp.zip"
    
    Write-Host "Installing $name..." -ForegroundColor Cyan
    try {
        Invoke-WebRequest -Uri $url -OutFile $zipPath -ErrorAction Stop
        Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
        $exe = Get-ChildItem -Path $tempDir -Filter "*.exe" -Recurse | Select-Object -First 1
        if ($exe) {
            Move-Item -Path $exe.FullName -Destination (Join-Path $toolsDir "$name.exe") -Force
            Write-Host "Done: $name" -ForegroundColor Green
        }
    }
    catch {
        Write-Error "Failed $name: $($_.Exception.Message)"
    }
    if (Test-Path $tempDir) { Remove-Item -Path $tempDir -Recurse -Force }
}

Install-GoTool "httpx" "https://github.com/projectdiscovery/httpx/releases/download/v1.6.0/httpx_1.6.0_windows_amd64.zip"
Install-GoTool "ffuf" "https://github.com/ffuf/ffuf/releases/download/v2.1.0/ffuf_2.1.0_windows_amd64.zip"
Install-GoTool "katana" "https://github.com/projectdiscovery/katana/releases/download/v1.1.0/katana_1.1.0_windows_amd64.zip"
Install-GoTool "gowitness" "https://github.com/sensepost/gowitness/releases/download/2.5.1/gowitness_2.5.1_windows_amd64.zip"
Install-GoTool "subzy" "https://github.com/LukaSikic/subzy/releases/download/v1.1.6/subzy_v1.1.6_windows_amd64.zip"
Install-GoTool "amass" "https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_windows_amd64.zip"

Write-Host "`nAll tools installed in: $toolsDir" -ForegroundColor Green
