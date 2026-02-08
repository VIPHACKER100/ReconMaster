$curr = Get-Location
$bd = Join-Path $curr "bin"
if (-not (Test-Path $bd)) { New-Item -ItemType Directory -Path $bd }

function Get-PDTool($n, $u) {
    Write-Host "Installing $n..."
    $zp = Join-Path $curr "temp.zip"
    $td = Join-Path $curr "temp_dir"
    if (Test-Path $td) { Remove-Item -Path $td -Recurse -Force }
    New-Item -ItemType Directory -Path $td | Out-Null
    
    try {
        Invoke-WebRequest -Uri $u -OutFile $zp
        Expand-Archive -Path $zp -DestinationPath $td -Force
        $e = Get-ChildItem -Path $td -Filter "*.exe" -Recurse | Select-Object -First 1
        if ($e) {
            Move-Item -Path $e.FullName -Destination (Join-Path $bd "$n.exe") -Force
            Write-Host "Success: $n" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "Error installing $n" -ForegroundColor Red
    }
    finally {
        if (Test-Path $zp) { Remove-Item -Path $zp -Force }
        if (Test-Path $td) { Remove-Item -Path $td -Recurse -Force }
    }
}

Get-PDTool "nuclei" "https://github.com/projectdiscovery/nuclei/releases/download/v3.3.4/nuclei_3.3.4_windows_amd64.zip"

# Download some wordlists
$wd = Join-Path $curr "wordlists"
if (-not (Test-Path $wd)) { New-Item -ItemType Directory -Path $wd }

Write-Host "Downloading wordlists..."
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt" -OutFile (Join-Path $wd "dns_common.txt")
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt" -OutFile (Join-Path $wd "directory-list.txt")

Write-Host "Done."
