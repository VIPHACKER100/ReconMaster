$currentDir = Get-Location
$toolsDir = Join-Path $currentDir "bin"
if (-not (Test-Path $toolsDir)) { New-Item -ItemType Directory -Path $toolsDir }

$tools = @(
    @{ name = "httpx"; url = "https://github.com/projectdiscovery/httpx/releases/download/v1.6.0/httpx_1.6.0_windows_amd64.zip" },
    @{ name = "ffuf"; url = "https://github.com/ffuf/ffuf/releases/download/v2.1.0/ffuf_2.1.0_windows_amd64.zip" },
    @{ name = "katana"; url = "https://github.com/projectdiscovery/katana/releases/download/v1.1.0/katana_1.1.0_windows_amd64.zip" },
    @{ name = "gowitness"; url = "https://github.com/sensepost/gowitness/releases/download/2.5.1/gowitness_2.5.1_windows_amd64.zip" },
    @{ name = "subzy"; url = "https://github.com/LukaSikic/subzy/releases/download/v1.1.6/subzy_v1.1.6_windows_amd64.zip" },
    @{ name = "amass"; url = "https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_windows_amd64.zip" }
)

foreach ($tool in $tools) {
    Write-Host "Installing $($tool.name)..." -ForegroundColor Cyan
    $tempDir = Join-Path $currentDir "temp_dl"
    if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir }
    $zipPath = Join-Path $tempDir "temp.zip"
    
    Invoke-WebRequest -Uri $tool.url -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
    $exe = Get-ChildItem -Path $tempDir -Filter "*.exe" -Recurse | Select-Object -First 1
    if ($exe) {
        Move-Item -Path $exe.FullName -Destination (Join-Path $toolsDir "$($tool.name).exe") -Force
    }
    Remove-Item -Path $tempDir -Recurse -Force
}

Write-Host "All tools installed" -ForegroundColor Green
