$currentDir = Get-Location
$toolsDir = Join-Path $currentDir "bin"
if (-not (Test-Path $toolsDir)) { New-Item -ItemType Directory -Path $toolsDir }

$name = "subfinder"
$url = "https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_windows_amd64.zip"
$zipName = "subfinder.zip"

Write-Host "Installing $name..."
$tempDir = Join-Path $currentDir "temp_dl"
if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir }
$zipPath = Join-Path $tempDir $zipName

Invoke-WebRequest -Uri $url -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
$exe = Get-ChildItem -Path $tempDir -Filter "$name.exe" -Recurse | Select-Object -First 1
Move-Item -Path $exe.FullName -Destination (Join-Path $toolsDir "$name.exe") -Force
Remove-Item -Path $tempDir -Recurse -Force

Write-Host "Done"
