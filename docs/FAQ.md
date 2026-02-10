# Frequently Asked Questions (FAQ)

## General Questions

### Q: What is ReconMaster?
**A:** ReconMaster is an automated reconnaissance framework that orchestrates multiple security tools (subfinder, httpx, ffuf, katana, etc.) into a streamlined workflow for discovering subdomains, assets, and endpoints on target domains. It's designed for security professionals, bug bounty hunters, and penetration testers.

### Q: Is ReconMaster legal to use?
**A:** ReconMaster is legal when used for **authorized security testing only**. You must have explicit written permission from the system owner before testing. Unauthorized access is illegal and subject to severe criminal penalties. See [LEGAL.md](../LEGAL.md) for details.

### Q: What makes ReconMaster different from manual tool usage?
**A:** ReconMaster:
- Orchestrates multiple tools in optimal sequence
- Deduplicates and merges results from different sources
- Provides structured, organized output
- Generates comprehensive reports automatically
- Handles error cases and retries gracefully
- Saves time on reconnaissance workflow

### Q: Do I need to install all tools separately?
**A:** No. The installation script (`install_reconmaster.sh`) handles installing all dependencies for you. For Windows, use WSL2 and run the Linux installation script.

### Q: Can I use ReconMaster on Windows natively?
**A:** Limited functionality. External Go-based tools (subfinder, httpx, etc.) require WSL2. Recommended approach:
- Install WSL2 with Ubuntu
- Run `sudo ./install_reconmaster.sh` in WSL
- Execute ReconMaster from WSL terminal

### Q: What are the system requirements?
**A:** 
- Python 3.9+
- Go 1.16+ (for Go-based tools)
- 4GB RAM (8GB recommended)
- 20GB disk space (for wordlists and results)
- Linux/macOS or Windows with WSL2

## Installation & Setup

### Q: Installation fails with "permission denied"
**A:** You need sudo privileges. Run:
```bash
sudo ./install_reconmaster.sh
```

Or for individual components:
```bash
sudo bash install_reconmaster.sh
```

### Q: "subfinder not found in PATH" error
**A:** Installation incomplete. Try:
1. Manual PATH addition: `export PATH=$PATH:$HOME/go/bin`
2. Verify tool exists: `which subfinder`
3. Re-run installation: `sudo ./install_reconmaster.sh`
4. Check Go installation: `go version`

### Q: pip install fails with dependency conflicts
**A:** Create a clean virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

### Q: How do I use a custom Python version?
**A:** Specify the Python version:
```bash
/usr/bin/python3.10 -m pip install -r requirements.txt
/usr/bin/python3.10 reconmaster.py -d example.com
```

### Q: Installation on macOS fails
**A:** Install Homebrew first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python3 go git
```

Then run the installation script.

## Usage Questions

### Q: What does "passive-only" mode do?
**A:** `--passive-only` disables aggressive scanning:
- No subdomain brute forcing (ffuf)
- No directory enumeration
- No port scanning
- Only OSINT-based discovery
- Suitable for sensitive targets or when stealth needed

```bash
python3 reconmaster.py -d target.com --passive-only
```

### Q: How many threads should I use?
**A:** 
- **Default (10)**: Safe for most targets
- **Fast (20-50)**: For targets with good uptime/capacity
- **Slow (2-5)**: For rate-limited targets or when avoiding detection
- **Rule of thumb**: Don't exceed target's thread limit

```bash
python3 reconmaster.py -d target.com -t 30
```

### Q: Can I provide a custom wordlist?
**A:** Yes, provide path with `-w` flag:
```bash
python3 reconmaster.py -d target.com -w /path/to/custom-subdomains.txt
```

Wordlist format: one entry per line
```
api
admin
dev
test
staging
...
```

### Q: The scan is taking too long. How do I speed it up?
**A:** 
1. Increase thread count: `-t 50`
2. Use passive-only mode: `--passive-only`
3. Skip certain tools (edit code): Comment out slow operations
4. Run on faster hardware: High CPU/network speed helps
5. Use fast profile: `python3 reconmaster.py -d target.com --profile fast`

### Q: The scan timed out. What do I do?
**A:** 
1. Reduce thread count: `-t 5`
2. Run passive-only: `--passive-only`
3. Increase timeout in config (advanced)
4. Check network: `ping 8.8.8.8`
5. Verify target exists: `nslookup target.com`

### Q: Can I run multiple targets at once?
**A:** Run multiple instances in background:
```bash
python3 reconmaster.py -d target1.com &
python3 reconmaster.py -d target2.com &
python3 reconmaster.py -d target3.com &
```

Or create wrapper script to orchestrate scans.

### Q: Where are the results saved?
**A:** Default: `./recon_results/target.com_TIMESTAMP/`

Specify output directory:
```bash
python3 reconmaster.py -d target.com -o ~/my-results
```

See [README.md](../README.md#output-structure) for output directory structure.

## Tool-Specific Questions

### Q: Why doesn't subfinder find anything?
**A:** Possible causes:
1. No subdomains registered for domain
2. Network/DNS issues - test: `nslookup subdomain.target.com`
3. Tool rate-limited - wait and retry
4. Invalid domain format
5. Verify domain exists: `dig target.com`

### Q: httpx shows 0 live domains
**A:** 
1. Check if domains actually respond: `curl -I https://subdomain.target.com`
2. May be non-web services (SMTP, FTP, etc.)
3. May have robots.txt/crawl restrictions
4. Network connectivity issues

### Q: ffuf takes forever
**A:**
1. Reduce wordlist size: Use smaller wordlist
2. Increase timeout: Edit config file
3. Skip directory enumeration: Comment out in code
4. Reduce thread count: `-t 10`

### Q: Gowitness not capturing screenshots
**A:**
1. Verify gowitness installed: `which gowitness`
2. Check X11 display: Not needed for newer gowitness versions
3. Check disk space: `df -h`
4. Verify domains are actually live: Check reports/live_domains.txt

### Q: Arjun finds no parameters
**A:**
1. Try against more URLs: Edit code to increase sample
2. May need authentication for some endpoints
3. Parameter discovery takes time - be patient
4. Check that httpx found live endpoints first

## Performance & Resource Issues

### Q: High CPU/memory usage
**A:**
1. Reduce thread count: `-t 5`
2. Kill unnecessary processes
3. Use smaller wordlists
4. Run on machine with more resources

### Q: Disk space warning
**A:**
1. Output can be large (100MB - 1GB+) for large domains
2. Ensure 20GB+ free space
3. Clean old results: `rm -r recon_results/old_*`
4. Compress results: `tar -czf results.tar.gz recon_results/`

### Q: Scan interrupted - can I resume?
**A:**
- v2+: Yes! ReconMaster saves state automatically
- v1: No resumption - starts over
- Upgrade to v2 for resume capability

## Troubleshooting

### Q: "Domain not found" or DNS errors
**A:**
1. Verify domain exists: `nslookup target.com`
2. Check network: `ping 8.8.8.8`
3. Try different domain format: `target.com` vs `www.target.com`
4. Check firewall/proxy settings

### Q: Tool crashes with no error message
**A:**
1. Check reconmaster.log: `tail -f recon_results/target.com_*/reconmaster.log`
2. Run with verbose: `python3 reconmaster.py -d target.com --verbose`
3. Test tool separately: `subfinder -d target.com`
4. Check tool version: Most tools require recent versions

### Q: JSON parsing errors
**A:**
1. Some tools may output invalid JSON
2. Tool versions incompatible
3. Check individual tool output: `ffuf -h`
4. Report issue with detailed logs

### Q: Strange output or incomplete results
**A:**
1. Check if all tools installed: `which subfinder assetfinder httpx ffuf katana`
2. Test individual tools: `subfinder -d target.com`
3. Check file permissions: `ls -la recon_results/`
4. Verify disk space: `df -h`

## Advanced Questions

### Q: How do I add a new tool to ReconMaster?
**A:** See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines. Basic steps:
1. Add tool execution method to ReconMaster class
2. Parse tool output
3. Integrate results with existing data
4. Add tests
5. Document in README

### Q: Can I modify the scanning order?
**A:** Edit `reconmaster.py` - modify `run()` method to reorder phase execution.

### Q: How do I use different wordlists?
**A:** 
- Provide with `-w` flag for subdomains
- Edit code for directory wordlist path
- Create custom wordlists: one entry per line

### Q: Can I exclude certain subdomains?
**A:** Post-process results:
```bash
grep -v "staging\|test\|dev" recon_results/target.com_*/subdomains/all_subdomains.txt
```

Or edit filtering logic in code.

## Security & Data Protection (v3.1.0-Pro)

### Q: Does ReconMaster expose my API keys in logs?
**A:** No. ReconMaster v3.1.0-Pro includes a **Sensitive Data Filter** that automatically detects and redacts common API keys (Google, AWS, GitHub, etc.) and passwords before they are written to any log files.

### Q: How safe is the automatic tool execution?
**A:** Very safe. Every command is executed through a **sanitization layer** that prevents shell injection, and all file operations are protected by a **path resolution guard** to prevent path traversal vulnerabilities.

### Q: What happens if I get rate-limited by a target?
**A:** The **Circuit Breaker** module will detect consistent 403 or 429 errors and automatically enter a "Cooldown" state, pausing requests for that target to protect your IP reputation and allow the target's WAF to recover.

## Getting More Help

- **Documentation**: See [README.md](../README.md)
- **Troubleshooting Guide**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **GitHub Issues**: https://github.com/viphacker100/ReconMaster/issues
- **Legal Questions**: See [LEGAL.md](../LEGAL.md)

---

**Still stuck?** [Create an issue](https://github.com/viphacker100/ReconMaster/issues/new) with:
- Full error message
- Python version: `python3 --version`
- OS: `uname -a`
- Command executed
- Relevant log entries
