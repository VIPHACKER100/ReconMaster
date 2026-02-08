# ReconMaster v3.0.0-Pro: Quick Reference Guide

⚡ **Asynchronous Reconnaissance Orchestration**

---

## 🚀 Basic Commands

### Standard Pro Scan
```bash
python reconmaster.py -d target.com
```

### Passive-Only Discovery (Stealth)
```bash
python reconmaster.py -d target.com --passive-only
```

### High-Velocity Assessment
```bash
python reconmaster.py -d target.com -t 30
```

### Custom Wordlist & Output
```bash
python reconmaster.py -d target.com -w custom.txt -o ./investigation
```

---

## 📁 Artifact Locations

Results are stored in `recon_results/target_TIMESTAMP/`:

- `subdomains/all_subdomains.txt`: Full discovery results.
- `subdomains/live_domains.txt`: Responsive high-value targets.
- `vulns/nuclei_results.json`: Native vulnerability scanning data.
- `endpoints/urls.txt`: Katana crawled endpoints.
- `screenshots/`: Visual verification snapshots.
- `reports/RECON_SUMMARY.md`: Executive summary.

---

## 🛠️ Common Operations

### 1. View Live Targets
```bash
cat recon_results/*/subdomains/live_domains.txt
```

### 2. Check for Vulnerabilities
```bash
cat recon_results/*/reports/RECON_SUMMARY.md | grep "Critical"
```

### 3. Extract API Endpoints
```bash
grep "api" recon_results/*/endpoints/urls.txt
```

### 4. Delete Old Scans
```bash
rm -rf recon_results/old_target_*
```

---

## 🔧 Performance Tuning

| Goal | Command Flag | Note |
|------|--------------|------|
| **Speed** | `-t 50` | Increases asyncio semaphore limit. |
| **Stealth** | `--passive-only` | Skips all active probes. |
| **Depth** | `-w big.txt` | Brute-forces with massive dictionary. |

---

## 🚨 Troubleshooting

| Issue | Resolution |
|-------|------------|
| `Tool not found` | Ensure `~/go/bin` is in your PATH. |
| `Scan aborted` | Check network connection or target status. |
| `Slow performance` | Adjust `-t` value (default 10). |
| `Permissions` | Run `chmod +x *.py` if needed. |

---

**Framework Version:** 3.0.0-Pro  
**Last Updated:** February 8, 2026  
**GitHub:** [VIPHACKER100/ReconMaster](https://github.com/VIPHACKER100/ReconMaster)
