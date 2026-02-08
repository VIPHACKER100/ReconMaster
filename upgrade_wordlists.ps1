# Upgrade ReconMaster Wordlists to Pro Level
$wordlistDir = Join-Path (Get-Location) "wordlists"
if (-not (Test-Path $wordlistDir)) { New-Item -ItemType Directory -Path $wordlistDir | Out-Null }

Write-Host "`n[+] Upgrading ReconMaster Wordlists..." -ForegroundColor Cyan

$lists = @(
    @{ 
        name = "subdomains_pro.txt"
        url  = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt"
        dest = "dns_common.txt"
    },
    @{ 
        name = "directories_pro.txt"
        url  = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-medium-directories.txt"
        dest = "directory-list.txt"
    },
    @{ 
        name = "php_fuzz.txt"
        url  = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/Programming-Language-Specific/PHP.fuzz.txt"
        dest = "php_fuzz.txt"
    },
    @{ 
        name = "parameters.txt"
        url  = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt"
        dest = "params.txt"
    },
    @{
        name = "resolvers.txt"
        url  = "https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt"
        dest = "resolvers.txt"
    }
)

foreach ($list in $lists) {
    $targetPath = Join-Path $wordlistDir $list.dest
    Write-Host "[*] Downloading $($list.name) -> $($list.dest)..." -ForegroundColor Blue
    try {
        Invoke-WebRequest -Uri $list.url -OutFile $targetPath -ErrorAction Stop
        $size = (Get-Item $targetPath).Length / 1KB
        Write-Host "[+] Success! Size: $($size.ToString('F2')) KB" -ForegroundColor Green
    }
    catch {
        Write-Host "[-] Failed to download $($list.name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Cleanup old/redundant files
$redundant = @("subdomains.txt", "subdomains_new.txt", "directory-list_new.txt")
foreach ($file in $redundant) {
    $p = Join-Path $wordlistDir $file
    if (Test-Path $p) {
        Remove-Item $p -Force
        Write-Host "[*] Removed redundant file: $file" -ForegroundColor Gray
    }
}

Write-Host "`n[+] Wordlists upgraded to Pro v3.1 specification." -ForegroundColor Green
