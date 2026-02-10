# ReconMaster Troubleshooting Guide

This guide helps diagnose and resolve common issues with ReconMaster.

## Pre-Diagnosis Checklist

Before investigating specific issues, verify basics:

1. **Python version**: `python3 --version` (require 3.9+)
2. **Internet connectivity**: `ping 8.8.8.8`
3. **Disk space**: `df -h` (minimum 5GB recommended)
4. **Memory**: `free -h` (minimum 2GB recommended)
5. **Domain validity**: `nslookup target.com`
6. **Permission**: Check file permissions: `ls -la reconmaster.py`

---

## Installation Troubleshooting

### Issue: "Permission Denied" during installation

**Symptoms**: 
```
sudo: command not found
chmod: permission denied
```

**Solutions**:
1. Ensure you have sudo access or are root: `sudo -l`
2. Use full path: `sudo /usr/bin/bash install_reconmaster.sh`
3. Run as root: `su` then `./install_reconmaster.sh`
4. On macOS: May need to verify with Gatekeeper: `spctl --add install_reconmaster.sh`

---

### Issue: "Go not found" or Go installation fails

**Symptoms**:
```
go: command not found
E: Unable to locate package golang-go
```

**Solutions**:

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install -y golang-go
# Verify
go version
```

**macOS**:
```bash
brew install go
# Verify
go version
```

**RHEL/CentOS**:
```bash
sudo yum install -y golang
go version
```

**Verify PATH**:
```bash
export PATH=$PATH:$(go env GOPATH)/bin
echo $PATH  # Should include ~/go/bin
```

---

### Issue: Python dependencies fail to install

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement
pip._vendor.packaging.specifiers.SpecifierSet has no attribute 'contains'
```

**Solutions**:

1. **Update pip/setuptools**:
```bash
python3 -m pip install --upgrade pip setuptools wheel
```

2. **Create fresh virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # Or: venv\Scripts\activate on Windows
pip install -r requirements.txt
```

3. **Use specific Python version**:
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Install with no cache**:
```bash
pip install --no-cache-dir -r requirements.txt
```

---

### Issue: External tools fail to install

**Symptoms**:
```
go install: golang.org/x/crypto: cannot find module
github.com/projectdiscovery/subfinder: permission denied
```

**Solutions**:

1. **Set GOPATH and GOBIN**:
```bash
export GOPATH=$HOME/go
export GOBIN=$GOPATH/bin
export PATH=$PATH:$GOBIN
# Add to ~/.bashrc or ~/.zshrc for persistence
```

2. **Create go directories**:
```bash
mkdir -p ~/go/{bin,src,pkg}
```

3. **Update Go modules**:
```bash
go clean -modcache
go mod tidy
```

4. **Manual tool installation**:
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
# Repeat for other tools
```

---

## Runtime Troubleshooting

### Issue: "Tool not found in PATH"

**Symptoms**:
```
[!] subfinder error: No such file or directory
[!] Tool check failed - install tools or update PATH
```

**Debugging**:
```bash
# Check if tool exists
which subfinder
# Check PATH
echo $PATH
# Test tool directly
subfinder -h
```

**Solutions**:

1. **Add to PATH**:
```bash
export PATH=$PATH:$HOME/go/bin
# Permanent: Add to ~/.bashrc, ~/.zshrc, or ~/.profile
```

2. **Verify installation**:
```bash
ls -la $HOME/go/bin/subfinder
# If missing, reinstall:
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
```

3. **Use full path**:
```bash
$HOME/go/bin/subfinder -d example.com
```

---

### Issue: Target domain gives no results

**Symptoms**:
```
[+] Found 0 unique subdomains via passive enumeration
```

**Debugging Steps**:

1. **Verify domain exists**:
```bash
nslookup example.com
# Or
dig example.com
# Or
host example.com
```

2. **Test DNS resolution**:
```bash
nslookup www.example.com
ping example.com
```

3. **Test tool directly**:
```bash
subfinder -d example.com -silent
assetfinder --subs-only example.com
```

4. **Check internet connectivity**:
```bash
curl -I https://example.com
wget --spider https://example.com
```

**Solutions**:

- Domain may not have public subdomains
- Try different top-level domain
- Some OSINT sources may rate-limit
- Test with known domain first: `example.com`
- Check firewall/proxy blocking

---

### Issue: httpx shows 0 live domains

**Symptoms**:
```
[!] No live domains found
live_domains.txt is empty
```

**Debugging**:

1. **Check subdomains file exists**:
```bash
ls -la recon_results/*/subdomains/all_subdomains.txt
wc -l recon_results/*/subdomains/all_subdomains.txt
```

2. **Test manually**:
```bash
echo "www.example.com" | httpx -status-code
```

3. **Check if domains respond**:
```bash
curl -I https://www.example.com
# Without HTTPS
curl -I http://www.example.com
```

**Solutions**:

- Domains may not run web services
- May need HTTP instead of HTTPS
- Firewall may block your requests
- Try again later (intermittent issues)
- Check for WAF blocking

---

### Issue: "Connection timeout" errors

**Symptoms**:
```
[!] httpx error: Timeout after 10s
Connection refused
```

**Debugging**:

```bash
# Test connectivity
ping 8.8.8.8
curl -I https://example.com
telnet 8.8.8.8 443
```

**Solutions**:

1. **Increase timeouts** (edit in code or config):
```python
timeout = 30  # Increase from default 10
```

2. **Check network**:
```bash
# Check DNS
nslookup 8.8.8.8
# Check routing
traceroute 8.8.8.8
```

3. **Firewall issues**:
   - Disable temporarily: `sudo ufw disable` (Ubuntu)
   - Check rules: `sudo firewall-cmd --list-all`
   - Check proxy settings

4. **ISP/Network blocking**:
   - Try from different network
   - Use VPN
   - Try later (rate limiting)

---

### Issue: Memory usage too high

**Symptoms**:
```
Killed (OOM killer)
malloc: cannot allocate memory
```

**Debugging**:
```bash
# Monitor memory
watch -n 1 'free -h'
# Check process memory
ps aux | grep reconmaster
# Check available memory
free -h
```

**Solutions**:

1. **Reduce thread count**:
```bash
python3 reconmaster.py -d target.com -t 5
```

2. **Reduce wordlist size**:
   - Use smaller wordlist
   - Edit code to process in chunks

3. **Increase swap** (temporary):
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

4. **Run on higher-memory system**:
   - Use cloud VM with 8GB+ RAM
   - Allocate more resources to Docker

---

### Issue: Disk space errors

**Symptoms**:
```
[!] Error: No space left on device
Disk quota exceeded
```

**Debugging**:
```bash
df -h  # Disk usage
du -sh recon_results/  # Result size
```

**Solutions**:

1. **Clean old results**:
```bash
rm -r recon_results/old_targets
rm -r recon_results/failed_scans
```

2. **Compress results**:
```bash
tar -czf results-backup.tar.gz recon_results/
rm -r recon_results/
```

3. **Move to external drive**:
```bash
mv recon_results /mnt/external/
ln -s /mnt/external/recon_results ./
```

4. **Clean system**:
```bash
sudo apt clean
sudo apt autoclean
# Find large files
find / -size +1G -type f 2>/dev/null
```

---

## Logging & Debugging

### Viewing Logs

**Location**: `recon_results/target.com_TIMESTAMP/reconmaster.log`

```bash
# View logs
tail -f recon_results/*/reconmaster.log

# Search logs for errors
grep ERROR recon_results/*/reconmaster.log

# View last 50 lines
tail -50 recon_results/*/reconmaster.log
```

### Running with verbose output

```bash
python3 reconmaster.py -d target.com --verbose
```

### Capturing debug information

```bash
# Redirect output to file
python3 reconmaster.py -d target.com > debug.log 2>&1

# See what commands are being run
bash -x ./install_reconmaster.sh
```

---

## Platform-Specific Issues

### macOS Issues

**Xcode command line tools missing**:
```bash
xcode-select --install
```

**M1/M2 chip compatibility**:
- Some Go tools may need: `go install` with `GOARCH=amd64`
- Or use native M1 builds

### Windows/WSL2 Issues

**WSL not installed**:
```powershell
wsl --install
```

**WSL can't access Windows files properly**:
```bash
# From WSL
cd /mnt/c/Users/VIPHACKER100/ReconMaster
```

**Port scanning with nmap fails in WSL**:
- nmap has limited functionality in WSL
- Use Windows nmap: `C:\Program Files (x86)\Nmap\nmap.exe`
- Or use WSL2 with proper network

### Linux (Ubuntu/Debian) Issues

**apt-get rate limit**:
```bash
# Change mirrors
sudo sed -i 's/archive.ubuntu.com/mirror.example.com/g' /etc/apt/sources.list
sudo apt update
```

**Snap installation conflicts**:
- Some packages conflict with snap versions
- Prefer apt over snap

---

## Network/Proxy Issues

### Behind corporate proxy

1. **Configure pip**:
```bash
pip install -r requirements.txt -i https://pypi.org/simple/ --proxy [user:passwd@]proxy.server:port
```

2. **Configure git** (for tool installation):
```bash
git config --global http.proxy [user:passwd@]proxy.server:port
```

3. **Test connectivity**:
```bash
curl -x [proxy:port] https://example.com
```

### Rate limiting / IP blocking

**Symptoms**:
```
Connection reset by peer
403 Forbidden
429 Too Many Requests
```

**Solutions**:

1. **Reduce request rate**:
```bash
python3 reconmaster.py -d target.com -t 3
```

2. **Use passive-only mode**:
```bash
python3 reconmaster.py -d target.com --passive-only
```

3. **Wait before retrying**:
```bash
sleep 3600  # Wait 1 hour
python3 reconmaster.py -d target.com
```

4. **Use VPN** (if allowed):
```bash
sudo apt install openvpn
openvpn --config config.ovpn
```

### Issue: "CIRCUIT BREAKER OPEN" in logs
**Symptoms**:
- Scan stops or skips many targets
- Log shows `🚫 CIRCUIT BREAKER OPENED`
- Many `skipping JS request` warnings

**Solutions**:
1. **Wait for cooldown**: The circuit breaker typically resets after 60 seconds of inactivity.
2. **Reduce concurrency**: If it happens frequently, decrease threads with `-t 5`.
3. **Change IP**: Your current IP might be permanently flagged; try a rotating proxy or VPN.
4. **Tune thresholds**: If you believe it's too sensitive, adjust `CIRCUIT_BREAKER_THRESHOLD` in `reconmaster.py`.

---

## Getting Help

### Before asking for help, gather information:

```bash
# System info
uname -a
python3 --version
go version

# Tool versions
subfinder --version 2>/dev/null || echo "Not installed"
httpx --version 2>/dev/null || echo "Not installed"

# Error output
tail -50 recon_results/*/reconmaster.log

# Resource info
free -h
df -h
```

### Report issues with:

1. **Full error message** (not truncated)
2. **Steps to reproduce**
3. **System information** (OS, versions)
4. **Relevant logs**
5. **Environment** (Docker, VM, bare metal, WSL)

### Resources:

- **GitHub Issues**: https://github.com/viphacker100/ReconMaster/issues
- **FAQ**: See [FAQ.md](FAQ.md)
- **Documentation**: See [README.md](../README.md)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Last Updated**: 2026-02-10

**Still stuck?** Create a detailed issue on GitHub with the information from "Getting Help" section above.
