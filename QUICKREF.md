# ReconMaster Quick Reference Guide

Quick command reference and common operations.

## Installation

```bash
# Linux/macOS
chmod +x install_reconmaster.sh
sudo ./install_reconmaster.sh

# Windows (use WSL2)
wsl --install
# Then run Linux commands above
```

## Basic Commands

```bash
# Basic scan
python3 reconmaster.py -d target.com

# Passive only (no brute forcing)
python3 reconmaster.py -d target.com --passive-only

# Custom output directory
python3 reconmaster.py -d target.com -o ~/results

# Custom thread count (higher = faster but more aggressive)
python3 reconmaster.py -d target.com -t 20

# Custom wordlist
python3 reconmaster.py -d target.com -w /path/to/wordlist.txt

# All options
python3 reconmaster.py -d target.com -o ~/results -t 15 -w custom.txt --passive-only
```

## Common Scenarios

### Quick Scan (2-5 minutes)
```bash
python3 reconmaster.py -d target.com --passive-only
```

### Comprehensive Scan (10-30 minutes)
```bash
python3 reconmaster.py -d target.com -t 20
```

### Stealth Scan (60+ minutes)
```bash
python3 reconmaster.py -d target.com -t 3
```

### Multiple Domains
```bash
for domain in target1.com target2.com target3.com; do
    python3 reconmaster.py -d "$domain" &
done
wait
```

### Monitor Changes Daily
```bash
#!/bin/bash
python3 reconmaster.py -d monitor.com -o ~/monitoring/$(date +%Y%m%d)
```

## Output Files

```
recon_results/target.com_YYYYMMDD_HHMMSS/
├── subdomains/
│   ├── all_subdomains.txt          ← All discovered subdomains
│   ├── live_domains.txt             ← Responsive domains only
│   └── takeovers.txt                ← Vulnerable subdomains
├── endpoints/
│   ├── urls.txt                     ← All discovered URLs
│   ├── interesting_dirs.txt         ← Hidden directories
│   └── js_endpoints.txt             ← API endpoints from JS
├── screenshots/
│   ├── domain1.png                  ← Visual captures
│   └── ...
├── js/
│   └── js_files.txt                 ← JavaScript file URLs
├── params/
│   └── parameters.txt               ← Discovered parameters
├── reports/
│   ├── summary_report.md            ← Main findings
│   └── broken_links.txt             ← Broken link findings
└── reconmaster.log                  ← Detailed execution log
```

## Quick Analysis

```bash
# View all subdomains
cat recon_results/target.com_*/subdomains/all_subdomains.txt

# Count statistics
echo "Subdomains: $(wc -l < recon_results/target.com_*/subdomains/all_subdomains.txt)"
echo "Live: $(wc -l < recon_results/target.com_*/subdomains/live_domains.txt)"

# Find admin-related subdomains
grep -i admin recon_results/target.com_*/subdomains/all_subdomains.txt

# Find API subdomains
grep -i api recon_results/target.com_*/subdomains/all_subdomains.txt

# View summary report
cat recon_results/target.com_*/reports/summary_report.md

# View logs
tail -50 recon_results/target.com_*/reconmaster.log

# Check for takeovers
cat recon_results/target.com_*/subdomains/takeovers.txt
```

## Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| "Tool not found" | `export PATH=$PATH:$HOME/go/bin` |
| No results | Verify domain: `nslookup target.com` |
| Too slow | Reduce threads: `-t 5` |
| High memory | Use `--passive-only` |
| Permission denied | Run with `sudo` |
| Disk full | Clean: `rm -r recon_results/old*` |
| Network timeout | Wait, try later |
| API rate limited | Reduce threads or wait |

## File Management

```bash
# List all scans
ls -lh recon_results/

# Delete old results
rm -r recon_results/target_20260101*

# Compress results
tar -czf results.tar.gz recon_results/

# Compare two scans
diff <(sort scan1/subdomains/all_subdomains.txt) \
     <(sort scan2/subdomains/all_subdomains.txt)

# Extract specific findings
grep -l "takeover" recon_results/*/subdomains/takeovers.txt

# Count total results across all scans
find recon_results -name "all_subdomains.txt" -exec wc -l {} + | tail -1
```

## Performance Tuning

```bash
# Monitor resources during scan
watch -n 1 'free -h && df -h'

# Check CPU usage
top -b -n 1 | head -20

# Limit resources
ulimit -n 1024  # Max open files

# Run in background
python3 reconmaster.py -d target.com &
jobs  # View running jobs
```

## Automation

```bash
# Daily cron job
0 2 * * * /path/to/reconmaster.py -d target.com -o ~/daily

# Run on file change
while true; do
    python3 reconmaster.py -d target.com
    sleep 3600  # Wait 1 hour
done

# Alert on new subdomains
PREV=$(sort recon_results/scan1/subdomains/all_subdomains.txt)
CURR=$(sort recon_results/scan2/subdomains/all_subdomains.txt)
NEW=$(comm -23 <(echo "$CURR") <(echo "$PREV"))
if [ ! -z "$NEW" ]; then
    echo "NEW SUBDOMAINS: $NEW" | mail -s alert user@example.com
fi
```

## Command Aliases (Add to ~/.bashrc)

```bash
# Quick reconnaissance
alias recon='python3 ~/ReconMaster/reconmaster.py'

# Results analysis
alias recon-ls='ls -lhS recon_results/*/ | head -20'
alias recon-subs='wc -l recon_results/*/subdomains/all_subdomains.txt'
alias recon-live='cat recon_results/*/subdomains/live_domains.txt | head -10'

# Reporting
alias recon-report='cat recon_results/*/reports/summary_report.md'
alias recon-log='tail -50 recon_results/*/reconmaster.log'
```

## Environment Variables

```bash
# Set default domain
export RECON_DOMAIN="mycompany.com"

# Set default threads
export RECON_THREADS=20

# Set results directory
export RECON_OUTPUT="$HOME/recon"

# Use in commands
python3 reconmaster.py -d $RECON_DOMAIN -t $RECON_THREADS -o $RECON_OUTPUT
```

## Useful External Commands

```bash
# Verify domain exists
nslookup example.com
dig example.com
host example.com

# Check if service is up
curl -I https://subdomain.target.com
wget --spider https://subdomain.target.com

# Check port availability
nc -zv hostname port
telnet hostname port

# DNS enumeration
dnsrecon -d example.com
dnsenum example.com

# Whois lookup
whois example.com

# Certificate transparency
curl https://crt.sh/?q=target.com
```

## Documentation Links

| Resource | Location |
|----------|----------|
| Main Documentation | README_comprehensive.md |
| FAQs | docs/FAQ.md |
| Troubleshooting | docs/TROUBLESHOOTING.md |
| Examples | docs/EXAMPLES.md |
| Legal Disclaimer | LEGAL.md |
| Contributing | CONTRIBUTING.md |
| Changelog | CHANGELOG.md |

## Key Statistics

- **Tools Integrated**: 13
- **Subdomains Discovered**: 50-5,000+ (depends on target)
- **Execution Time**: 5-120 minutes (depends on settings)
- **Output Size**: 10MB-1GB (depends on target size)
- **Memory Usage**: 100MB-2GB (depends on settings)
- **Disk Space Needed**: 20GB+ recommended

## Safety Checklist

- ✅ Do you have written authorization?
- ✅ Is this the correct target domain?
- ✅ Have you verified scope with client?
- ✅ Are you on appropriate network?
- ✅ Have you checked data sensitivity?
- ✅ Is your output directory secure?
- ✅ Will you follow responsible disclosure?

## Common Issues Quick Diagnose

```bash
# Test all dependencies
which subfinder assetfinder httpx ffuf katana subjs subzy
which nmap arjun

# Test basic functionality
subfinder -d example.com -silent
httpx -h
ffuf -h

# Check Python version
python3 --version

# Check Go setup
go version
echo $GOPATH
echo $GOBIN
```

---

**For detailed help**: Check the [FAQ](docs/FAQ.md) or [TROUBLESHOOTING](docs/TROUBLESHOOTING.md) guides.

**Last Updated**: February 1, 2026
