$currentDir = Get-Location
$toolsDir = Join-Path $currentDir "bin"
$tempDir = Join-Path $currentDir "temp_dl"
if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir }
$zipPath = Join-Path $tempDir "temp.zip"

$url = "https://github.com/projectdiscovery/httpx/releases/download/v1.6.0/httpx_1.6.0_windows_amd64.zip"
Write-Host "Downloading..."
Invoke-WebRequest -Uri $url -OutFile $zipPath
Write-Host "Expanding..."
Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
Write-Host "Cleaning up..."
Remove-Item -Path $tempDir -Recurse -Force
Write-Host "Done"
