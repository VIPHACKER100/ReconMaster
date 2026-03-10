# ReconMaster Tool Connectivity - Troubleshooting Guide

## Quick Diagnostic

Run the diagnostic script to identify all connectivity issues:
```bash
python3 tool_connectivity_check.py
```

This will generate a JSON report: `reconmaster_connectivity_report.json`

---

## Common Issues & Solutions

### 1. ❌ "Missing CRITICAL tools" Error

**Symptom:**
```
ERROR] Missing CRITICAL tools: subfinder, assetfinder, amass, ...
```

**Root Cause:** Required tools not found in system PATH

**Solutions:**

#### Option A: Install via Shell Script (Recommended)
```bash
# Linux/macOS
./install_reconmaster.sh

# Windows PowerShell
powershell -File install_tools_final.ps1
```

#### Option B: Manual Go Installation
```bash
# Install Go first (if not already installed)
# From https://golang.org/dl/

# Then install each tool:
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/assetfinder@latest
go install github.com/owasp-amass/amass/v3/...@latest
go install github.com/projectdiscovery/ffuf@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
go install github.com/projectdiscovery/gowitness@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest

# Verify installation
subfinder --version
```

#### Option C: Check PATH Environment Variable
```bash
# Verify Go bin directory is in PATH
echo $PATH  # Linux/macOS
echo %PATH%  # Windows

# Add to PATH if missing:
# Linux/macOS: Add to ~/.bashrc or ~/.zshrc
export PATH=$PATH:~/go/bin

# Windows PowerShell: Run as Admin
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Users\YourUsername\go\bin", "User")
```

#### Option D: Docker (Guaranteed Consistency)
```bash
docker pull projectdiscovery/reconmaster
docker run -v $(pwd)/output:/output projectdiscovery/reconmaster -d example.com -o /output
```

---

### 2. ⚠️ "aiohttp not available" Warning

**Symptom:**
```
WARNING aiohttp not available, skipping JS analysis
WARNING aiohttp not available, skipping API endpoint fuzzing
```

**Impact:**
- ❌ JavaScript secret extraction disabled
- ❌ Sensitive file discovery disabled
- ❌ API endpoint fuzzing disabled
- ❌ Broken link detection disabled

**Solution:**
```bash
pip install aiohttp

# Or with Python 3
pip3 install aiohttp

# Verify
python3 -c "import aiohttp; print(aiohttp.__version__)"
```

**All-in-One Dependencies:**
```bash
pip install aiohttp pyyaml requests
```

---

### 3. 🔐 "Circuit Breaker OPENED" Message

**Symptom:**
```
[ERROR] 🚫 CIRCUIT BREAKER OPENED - Rate limiting detected
```

**Causes:**
- Target server rate-limiting requests (HTTP 429)
- Server blocking IP (HTTP 403)
- Server errors (HTTP 503)

**Solutions:**

#### Solution 1: Wait for Cooldown
- Automatic recovery: Wait 60 seconds (default)
- Monitor logs for "Circuit breaker CLOSED" message

#### Solution 2: Reduce Concurrency
```bash
reconmaster -d example.com -t 5  # Reduce from default 10 to 5 threads
```

#### Solution 3: Use Proxy
```bash
# Via environment variable
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=https://proxy:8080

# Then run reconnaissance
reconmaster -d example.com -o ./results --i-understand-this-requires-authorization
```

#### Solution 4: Enable Passive-Only Mode
```bash
# Skip active scanning (no ffuf, reduced nuclei, etc.)
reconmaster -d example.com -o ./results --passive-only --i-understand-this-requires-authorization
```

---

### 4. 🔨 Individual Tool Failures

#### ffuf Chunking Failure
**Symptom:**
```
[ERROR] Failed to process chunk 0
```

**Solutions:**
- Reduce wordlist size: `--wordlist /path/to/smaller/list.txt`
- Increase timeout: Tool uses 600s default, should be sufficient
- Check resolver availability (if dnsx present)

#### nuclei Runtime Error
**Symptom:**
```
[ERROR] Command execution error: nuclei: ... error
```

**Debugging:**
```bash
# Test nuclei directly
nuclei -h  # Check installation
nuclei -l urls.txt -tags cve  # Test basic execution

# Check template update
nuclei -update
```

#### gowitness Screenshot Failures
**Symptom:**
```
[WARNING] Screenshot capture failed for URL
```

**Solutions:**
```bash
# Verify gowitness separately
gowitness --help

# Test single screenshot
gowitness file -f /tmp/test_urls.txt

# Known fix: Disable HTTP fallback (already in code)
# But you can manually test with:
gowitness -u https://example.com --no-http --timeout 20
```

#### katana Crawling Issues
**Symptom:**
```
[ERROR] Katana crawl failed
```

**Solutions:**
```bash
# Test katana directly
katana -u https://example.com -jc

# Check JavaScript crawling
katana -u https://example.com -jc -depth 3

# Reduce depth if hanging
katana -u https://example.com -jc -depth 1
```

---

### 5. 🔑 API Credentials Issues

#### Missing API Keys
**Symptom:**
```
SECURITYTRAILS_API_KEY not set
CENSYS credentials missing
```

**Solution:**
```bash
# Set before running reconnaissance
export CENSYS_API_ID="your_api_id"
export CENSYS_API_SECRET="your_api_secret"
export SECURITYTRAILS_API_KEY="your_key"
export VIRUSTOTAL_API_KEY="your_key"

# Then run
reconmaster -d example.com -o ./results --i-understand-this-requires-authorization
```

**Note:** The code currently has hardcoded fallback keys (SECURITY RISK!)
- These should not be relied upon
- Always use your own API keys

---

### 6. 🌐 Network Connectivity Issues

#### No External Connectivity
**Symptom:**
```
[ERROR] Connection timeout: httpx failed to reach target
```

**Diagnostic:**
```bash
# Test basic connectivity
ping google.com
curl https://www.google.com

# Test specific tool
httpx -u https://www.google.com -silent

# Check DNS resolution
nslookup example.com
dig example.com
```

**Solutions:**
- Check internet connection: `ping 8.8.8.8`
- Check firewall rules
- Check proxy requirements
- Verify target domain is accessible

#### DNS Resolution Failures
**Symptom:**
```
[WARNING] Failed to resolve subdomain
```

**Solution:**
```bash
# Verify dnsx availability
dnsx -h

# Test DNS resolution
dnsx -d example.com -silent

# Use custom resolver
dnsx -d example.com -r resolvers.txt
```

---

### 7. 📝 Wordlist Availability Issues

**Symptom:**
```
[WARNING] No wordlist found for brute-forcing
```

**Solutions:**

#### Check Wordlist Paths:
```bash
ls -la wordlists/
# Expected files:
# - dns_common.txt
# - directory-list.txt
# - api_endpoints.txt
# - params.txt
# - quickhits.txt
```

#### Use Custom Wordlist:
```bash
reconmaster -d example.com -w /path/to/custom/wordlist.txt --i-understand-this-requires-authorization
```

#### Download Wordlists:
```bash
# SecLists (comprehensive)
git clone https://github.com/danielmiessler/SecLists.git

# Copy relevant lists
cp SecLists/Discovery/DNS/dns-big.txt wordlists/dns_common.txt
cp SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt wordlists/directory-list.txt
```

---

### 8. 🔒 SSL/TLS Certificate Issues

**Symptom:**
```
[ERROR] SSL: CERTIFICATE_VERIFY_FAILED
```

**Note:** ReconMaster disables SSL verification by default (`ssl=False`)
- This is intentional for scanning purposes
- Security trade-off for reconnaissance flexibility

**If you need SSL verification:**
```bash
# Edit aiohttp session configuration in analyze_js_files()
# Change: TCPConnector(ssl=False) 
# To: TCPConnector(ssl=True) or TCPConnector(ssl=certifi.where())
```

---

### 9. 📊 Report Generation Failures

**Symptom:**
```
[ERROR] Failed to generate HTML report
```

**Solutions:**
```bash
# Check output directory permissions
ls -la recon_results/

# Make sure directory is writable
chmod -R 755 recon_results/

# Verify required Python modules
python3 -c "import json; import datetime"
```

---

### 10. 🏃 Performance Issues

#### Reconnaissance Running Slow
**Solutions:**

1. **Reduce Threads:**
```bash
reconmaster -d example.com -t 5 --i-understand-this-requires-authorization
```

2. **Use Passive-Only Mode:**
```bash
reconmaster -d example.com --passive-only --i-understand-this-requires-authorization
```

3. **Limit Scope:**
```bash
reconmaster -d example.com --include "api.example.com" --i-understand-this-requires-authorization
```

4. **Skip Heavy Modules:**
- Screenshots: Remove `gowitness` from PATH temporarily
- Directory fuzzing: Use smaller wordlist
- JavaScript analysis: Reduce max JS files in code (Line 1717)

#### Memory Issues
**Symptom:**
```
MemoryError or system becomes unresponsive
```

**Solutions:**
```bash
# Reduce concurrency
reconmaster -d example.com -t 3 --i-understand-this-requires-authorization

# Limit JavaScript analysis
# Edit: MAX_JS_FILES = 30 (instead of 100)

# Skip screenshots
# Set tool not in PATH: mv $(which gowitness) /tmp/
```

---

## Diagnostic Commands Reference

### Test Individual Tools

```bash
# Subdomain Discovery
subfinder -d example.com -silent
assetfinder --subs-only example.com
amass enum -passive -d example.com

# DNS Resolution
dnsx -d example.com -silent
nslookup example.com
dig example.com

# HTTP Probing
httpx -u https://example.com -silent

# Vulnerability Scanning
nuclei -u https://example.com -tags cve

# Web Crawling
katana -u https://example.com

# Fuzzing
ffuf -u http://FUZZ.example.com -w wordlist.txt

# Screenshots
gowitness file -f urls.txt

# Parameters
arjun -u https://example.com --passive

# Port Scanning
nmap example.com --top-ports 1000
```

### Verify Environment

```bash
# Check PATH
echo $PATH  # Linux/macOS
echo %PATH%  # Windows

# Find installed tools
which subfinder httpx nuclei
command -v ffuf  # Alternative

# Check Python environment
python3 --version
pip3 list | grep -i aiohttp
python3 -c "import aiohttp; print(aiohttp.__version__)"

# Check DNS resolution
nslookup google.com
host google.com

# Check network
ping 8.8.8.8
curl -I https://www.google.com
```

---

## Emergency Fallback Procedures

If critical tools are completely unavailable:

### Option 1: Use Online Tools
```bash
# Subdomain enumeration via Shodan, etc.
# Then use reconnaissance module on discovered subdomains
```

### Option 2: Minimal Scanning (Python-only)
- Edit ReconMaster to skip unavailable tools
- Focus on httpx and nuclei (if available)
- Export and analyze results manually

### Option 3: Docker Container
```bash
# Guaranteed all tools installed correctly
docker pull projectdiscovery/reconmaster
docker run --rm -v $(pwd):/output projectdiscovery/reconmaster scan
```

### Option 4: Manual Reconnaissance
```bash
# Use online services (Shodan, Censys, SecurityTrails)
# Combine results and test manually
# Generate custom reports from findings
```

---

## Tool Verification Script Output Explanation

When you run `python3 tool_connectivity_check.py`:

**Key Metrics:**
- ✅ **INSTALLED**: Tool found and executable
- ⚠️ **WARNING**: Tool found but may have issues
- ❌ **MISSING**: Tool not found in PATH
- ✓ **READY**: All critical requirements met

**Critical vs Optional:**
- **Critical:** Reconnaissance fails without these
- **Optional:** Specific features disabled, but core functions work

**Report File:** `reconmaster_connectivity_report.json`
- Detailed version info
- File paths
- Environment status
- Recommendations

---

## When to Report Issues

### Create GitHub Issue If:
1. Tool is installed correctly but ReconMaster can't find it
2. Tool works standalone but fails within ReconMaster
3. API keys configured but not being used
4. Specific error messages not covered here

### Information to Include:
```bash
# Collect diagnostic data
python3 tool_connectivity_check.py > diagnostic_report.txt

# Tool versions
subfinder --version
httpx --version
nuclei --version

# Python info
python3 --version
pip3 list

# Error logs
cat recon_results/logs/errors.log
```

---

## Quick Reference Checklist

- [ ] All 8 critical tools installed (`tool_connectivity_check.py`)
- [ ] Python 3.8+ with asyncio
- [ ] aiohttp installed (`pip3 install aiohttp`)
- [ ] Environment variables set (if using custom API keys)
- [ ] Wordlists present in `wordlists/` directory
- [ ] Go bin directory in PATH
- [ ] Target domain is valid FQDN
- [ ] Output directory is writable
- [ ] Network connectivity confirmed (ping 8.8.8.8)
- [ ] Authorization flag used (`--i-understand-this-requires-authorization`)

---

## Support Resources

- **Official Docs:** https://github.com/VIPHACKER100/ReconMaster
- **ProjectDiscovery:** https://projectdiscovery.io/
- **Tool Repositories:**
  - https://github.com/projectdiscovery/subfinder
  - https://github.com/projectdiscovery/httpx
  - https://github.com/projectdiscovery/nuclei
  - https://github.com/projectdiscovery/katana

