# ReconMaster Examples

Real-world usage examples and best practices for ReconMaster.

## Table of Contents

1. [Basic Scans](#basic-scans)
2. [Advanced Techniques](#advanced-techniques)
3. [Bug Bounty Workflows](#bug-bounty-workflows)
4. [Automation & Scripting](#automation--scripting)
5. [Performance Tuning](#performance-tuning)
6. [Output Analysis](#output-analysis)

---

## Basic Scans

### Example 1: Simple Domain Scan

**Scenario**: Quick reconnaissance of a domain with default settings

```bash
python3 reconmaster.py -d example.com
```

**What happens**:
- Passive subdomain enumeration (subfinder, assetfinder, amass)
- Active brute forcing with default wordlist
- Live domain verification with httpx
- Screenshot capture with gowitness
- Subdomain takeover checks
- Web crawling and endpoint discovery
- Directory brute forcing on top 10 domains
- Parameter discovery on selected endpoints
- Port scanning on priority subdomains
- Comprehensive report generation

**Output**: Results in `recon_results/example.com_YYYYMMDD_HHMMSS/`

---

### Example 2: Passive-Only Reconnaissance

**Scenario**: Authorized test on sensitive system - minimize footprint

```bash
python3 reconmaster.py -d banking.example.com --passive-only
```

**What happens**:
- Passive OSINT only (no brute forcing)
- No aggressive probing
- Only queries public sources
- Minimal logging

**When to use**: 
- Sensitive/critical systems
- Restricted networks
- Educational/demonstration purposes

---

### Example 3: Custom Output Directory

**Scenario**: Organize results in project structure

```bash
python3 reconmaster.py -d client.com -o ~/projects/client-security-audit
```

**Directory structure created**:
```
~/projects/client-security-audit/
└── client.com_20260201_143022/
    ├── subdomains/
    ├── endpoints/
    ├── screenshots/
    ├── js/
    ├── params/
    ├── reports/
    └── reconmaster.log
```

---

### Example 4: High-Performance Scan

**Scenario**: Large organization with many subdomains - speed matters

```bash
python3 reconmaster.py -d fortune500.com -t 50
```

**Considerations**:
- 50 threads is aggressive
- Requires good hardware (4+ CPU cores)
- May trigger WAF/IDS if target has aggressive rate limiting
- Monitor system resources: `watch -n 1 'free -h && df -h'`

---

## Advanced Techniques

### Example 5: Custom Wordlist for Brute Forcing

**Scenario**: Organization-specific subdomains with custom dictionary

```bash
# Create custom wordlist with your findings
cat > custom-subdomains.txt << EOF
internal
legacy
backup
staging-v2
prod-api
dev-internal
test-payment
qa-portal
EOF

# Run with custom wordlist
python3 reconmaster.py -d target.com -w custom-subdomains.txt
```

**Tips**:
- Add infrastructure-specific names (data, cache, queue)
- Include version numbers (v1, v2, v3)
- Add functional areas (payment, auth, admin)
- Remove duplicates for efficiency

---

### Example 6: Sequential Scans on Multiple Domains

**Scenario**: Security assessment of corporate acquisition - multiple domains

```bash
#!/bin/bash
# scan_multiple.sh

DOMAINS=(
    "company-a.com"
    "company-b.com"
    "company-c.org"
)

for domain in "${DOMAINS[@]}"; do
    echo "[*] Starting scan for $domain"
    python3 reconmaster.py -d "$domain" -o ~/assessments/acquisition
    echo "[+] Completed scan for $domain"
done

echo "[+] All scans complete"
```

**Run it**:
```bash
bash scan_multiple.sh
```

---

### Example 7: Parallel Domain Scanning

**Scenario**: Multiple domains run concurrently (requires careful management)

```bash
#!/bin/bash
# parallel_scan.sh

DOMAINS=(
    "target1.com"
    "target2.com"
    "target3.com"
    "target4.com"
)

for domain in "${DOMAINS[@]}"; do
    echo "[*] Starting background scan for $domain"
    python3 reconmaster.py -d "$domain" > /tmp/scan-$domain.log 2>&1 &
done

# Wait for all backgrounds jobs
wait

echo "[+] All parallel scans complete"
# Combine results
cat /tmp/scan-*.log
```

**Warning**: Only do this if:
- Running on high-resource system
- Target can handle parallel load
- You have authorization for aggressive testing

---

### Example 8: Follow-up Scan with Different Wordlist

**Scenario**: Initial scan incomplete - try again with larger wordlist

```bash
# First scan with default wordlist
python3 reconmaster.py -d example.com

# Download larger wordlist
wget https://raw.githubusercontent.com/n0kovo/n0kovo_subdomains/master/n0kovo_subdomains.txt

# Second pass with larger wordlist
python3 reconmaster.py -d example.com -w n0kovo_subdomains.txt -o ~/recon/extended
```

---

## Bug Bounty Workflows

### Example 9: Complete Bug Bounty Reconnaissance

**Scenario**: Comprehensive reconnaissance for bug bounty program

```bash
#!/bin/bash
# bugbounty-recon.sh

TARGET="bugbounty-company.com"
OUTPUT_DIR="~/bbh/$(date +%Y%m%d)"

echo "[*] ReconMaster Bug Bounty Scan - $TARGET"
echo "[*] Output: $OUTPUT_DIR"

# Phase 1: Full reconnaissance
echo "[+] Phase 1: Comprehensive reconnaissance"
python3 reconmaster.py -d "$TARGET" -o "$OUTPUT_DIR" -t 20

# Phase 2: Generate summary report
echo "[+] Phase 2: Analyzing results"
cd "$OUTPUT_DIR/$TARGET"*/

echo "=== SUMMARY ==="
echo "Total subdomains:"
wc -l subdomains/all_subdomains.txt

echo -e "\nLive domains:"
wc -l subdomains/live_domains.txt

echo -e "\nPotential takeovers:"
wc -l subdomains/takeovers.txt 2>/dev/null || echo "None"

echo -e "\nDiscovered URLs:"
wc -l endpoints/urls.txt 2>/dev/null || echo "None"

echo -e "\nJavaScript files:"
wc -l js/js_files.txt 2>/dev/null || echo "None"

echo -e "\nDiscovered parameters:"
wc -l params/parameters.txt 2>/dev/null || echo "None"

echo -e "\n=== TOP 20 SUBDOMAINS ==="
head -20 subdomains/all_subdomains.txt

echo -e "\n[+] Full report: $PWD/reports/summary_report.md"
```

**Run it**:
```bash
bash bugbounty-recon.sh
```

**Next steps**:
1. Review live domains in `live_domains.txt`
2. Check for vulnerable endpoints in `endpoints/interesting_dirs.txt`
3. Analyze JavaScript files in `js/js_files.txt` for secrets
4. Test discovered parameters for vulnerabilities
5. Check for subdomain takeovers in `takeovers.txt`

---

### Example 10: Scope Mapping

**Scenario**: Clarify scope before deep dive

```bash
# Quick passive-only scan to map scope
python3 reconmaster.py -d target.com --passive-only -o ~/scope-mapping

# Review discovered assets
echo "Discovered subdomains:"
sort -u recon_results/target.com_*subdomains/all_passive.txt

# Ask yourself:
# - Are all these in scope?
# - Which are production? Which are development?
# - Any third-party services?
# - Any cloud assets (AWS, GCP, Azure)?
```

---

## Automation & Scripting

### Example 11: Automated Daily Reconnaissance

**Scenario**: Monitor domain changes over time

```bash
#!/bin/bash
# daily-monitor.sh - Run daily via cron

TARGET="monitor.example.com"
MONITORING_DIR="$HOME/.recon-monitor"
RESULTS_DIR="$MONITORING_DIR/results"
ALERTS="$MONITORING_DIR/alerts"

mkdir -p "$RESULTS_DIR" "$ALERTS"

# Run scan
TODAY=$(date +%Y%m%d)
python3 reconmaster.py -d "$TARGET" -o "$RESULTS_DIR/$TODAY"

# Compare with previous day
YESTERDAY=$(date -d yesterday +%Y%m%d)
if [ -f "$RESULTS_DIR/$YESTERDAY/$TARGET/subdomains/all_subdomains.txt" ]; then
    # Find new subdomains
    PREVIOUS="$RESULTS_DIR/$YESTERDAY/$TARGET/subdomains/all_subdomains.txt"
    CURRENT="$RESULTS_DIR/$TODAY/$TARGET/subdomains/all_subdomains.txt"
    
    NEW_SUBDOMAINS=$(comm -23 <(sort "$CURRENT") <(sort "$PREVIOUS"))
    
    if [ ! -z "$NEW_SUBDOMAINS" ]; then
        echo "=== NEW SUBDOMAINS FOUND ===" > "$ALERTS/$TODAY-new-subdomains.txt"
        echo "$NEW_SUBDOMAINS" >> "$ALERTS/$TODAY-new-subdomains.txt"
        echo "[!] New subdomains discovered!"
        cat "$ALERTS/$TODAY-new-subdomains.txt"
    fi
fi

# Clean old results (keep last 30 days)
find "$RESULTS_DIR" -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null
```

**Add to crontab**:
```bash
# Run daily at 2 AM
crontab -e
# Add line:
0 2 * * * /path/to/daily-monitor.sh
```

---

### Example 12: CI/CD Integration

**Scenario**: Automated scanning in development pipeline

```yaml
# .github/workflows/recon.yml
name: Automated Reconnaissance

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  recon:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install ReconMaster
        run: |
          bash install_reconmaster.sh
          
      - name: Run reconnaissance
        run: |
          python3 reconmaster.py -d ${{ secrets.TARGET_DOMAIN }} -o ./results
          
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: reconnaissance-results
          path: results/
          
      - name: Create issue if vulnerabilities found
        if: hashFiles('results/**/takeovers.txt') != ''
        run: |
          echo "Potential takeovers found!" > /tmp/issue.md
          cat results/*/subdomains/takeovers.txt >> /tmp/issue.md
          gh issue create -F /tmp/issue.md
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Performance Tuning

### Example 13: Slow Network - Optimized Scan

**Scenario**: Testing from slow/unstable connection

```bash
# Reduce aggressive settings
python3 reconmaster.py \
    -d slow-target.com \
    -t 5 \              # Very low thread count
    --passive-only      # No active brute forcing

# Or edit config for higher timeouts
# Set: timeout = 30 (instead of 10)
```

---

### Example 14: Large Organization - Staged Scan

**Scenario**: Domain with hundreds of subdomains - break into stages

```bash
#!/bin/bash
# staged-scan.sh

TARGET="large-org.com"

# Stage 1: Passive enumeration
echo "[+] Stage 1: Passive subdomain discovery"
python3 reconmaster.py -d "$TARGET" --passive-only -o ~/scans/stage1

# Review results
echo "[?] Review subdomains before active scanning:"
head -20 ~/scans/stage1/$TARGET*/subdomains/all_passive.txt

# Stage 2: Active brute forcing (selective)
echo "[+] Stage 2: Active brute forcing (limited)"
python3 reconmaster.py -d "$TARGET" -w ~/wordlists/smaller-list.txt -t 10 -o ~/scans/stage2

# Stage 3: Deep analysis
echo "[+] Stage 3: Deep endpoint analysis"
python3 reconmaster.py -d "$TARGET" -t 5 -o ~/scans/stage3
```

---

## Output Analysis

### Example 15: Post-Scan Analysis

**Scenario**: Extract actionable intelligence from results

```bash
#!/bin/bash
# analyze-results.sh

DOMAIN="$1"
SCAN_DIR=$(ls -dt ~/recon_results/$DOMAIN* | head -1)

echo "=== Reconnaissance Analysis ==="
echo "Domain: $DOMAIN"
echo "Scan: $SCAN_DIR"
echo ""

# Count statistics
echo "=== Statistics ==="
echo "Total subdomains: $(wc -l < $SCAN_DIR/subdomains/all_subdomains.txt)"
echo "Live domains: $(wc -l < $SCAN_DIR/subdomains/live_domains.txt 2>/dev/null || echo '0')"
echo "Interesting directories: $(wc -l < $SCAN_DIR/endpoints/interesting_dirs.txt 2>/dev/null || echo '0')"
echo "JavaScript files: $(wc -l < $SCAN_DIR/js/js_files.txt 2>/dev/null || echo '0')"
echo ""

# Identify priorities
echo "=== Priority Findings ==="

# Check for admin/sensitive subdomains
echo "Admin-related subdomains:"
grep -i "admin\|manage\|control\|dashboard" $SCAN_DIR/subdomains/all_subdomains.txt | head -10

# Check for API subdomains
echo -e "\nAPI-related subdomains:"
grep -i "api\|service\|backend" $SCAN_DIR/subdomains/all_subdomains.txt | head -10

# Check for development/staging
echo -e "\nDevelopment/Staging subdomains:"
grep -i "dev\|test\|staging\|uat\|qa" $SCAN_DIR/subdomains/all_subdomains.txt | head -10

# Potential takeovers
if [ -s "$SCAN_DIR/subdomains/takeovers.txt" ]; then
    echo -e "\n⚠️  POTENTIAL TAKEOVERS:"
    cat "$SCAN_DIR/subdomains/takeovers.txt"
fi

# Interesting directories
echo -e "\nInteresting directories (sample):"
head -10 "$SCAN_DIR/endpoints/interesting_dirs.txt" 2>/dev/null || echo "None found"

echo -e "\n=== Report Location ==="
echo "$SCAN_DIR/reports/summary_report.md"
```

**Run it**:
```bash
bash analyze-results.sh example.com
```

---

### Example 16: Comparing Scans Over Time

**Scenario**: Track changes in reconnaissance data

```bash
#!/bin/bash
# compare-scans.sh

DOMAIN="$1"
SCAN1="$2"
SCAN2="$3"

echo "=== Comparing $DOMAIN scans ==="
echo "Scan 1: $SCAN1"
echo "Scan 2: $SCAN2"
echo ""

# New subdomains
echo "=== NEW SUBDOMAINS ==="
comm -23 \
    <(sort "$SCAN2/subdomains/all_subdomains.txt") \
    <(sort "$SCAN1/subdomains/all_subdomains.txt")

# Removed subdomains
echo -e "\n=== REMOVED SUBDOMAINS ==="
comm -13 \
    <(sort "$SCAN2/subdomains/all_subdomains.txt") \
    <(sort "$SCAN1/subdomains/all_subdomains.txt")

# New live domains
echo -e "\n=== NEWLY LIVE DOMAINS ==="
comm -23 \
    <(sort "$SCAN2/subdomains/live_domains.txt") \
    <(sort "$SCAN1/subdomains/live_domains.txt")
```

---

## Best Practices Summary

1. **Always verify authorization** before scanning
2. **Start with passive-only** for sensitive targets
3. **Use appropriate thread counts** for target capacity
4. **Monitor system resources** during scans
5. **Review results carefully** before reporting
6. **Cross-check findings** with multiple tools
7. **Document assumptions** about scope and targets
8. **Keep historical records** for trend analysis
9. **Test on known domains first** (example.com, testphp.vulnweb.com)
10. **Stay updated** on tool versions and wordlists

---

**Need more examples?** Check the [FAQ](FAQ.md) or [TROUBLESHOOTING](TROUBLESHOOTING.md) guides.
