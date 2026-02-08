# ReconMaster v3.0.0-Pro Quick Reference Guide

## 🚀 Pro Commands

### ⚡ High-Speed Scanning (v3.0.0-Pro)
The new asynchronous engine allows for significantly higher thread counts and faster execution.

```powershell
# 1. Passive scan (Stealthy, Instant)
python reconmaster.py -d target.com --passive-only --i-understand-this-requires-authorization

# 2. Comprehensive Pro Scan (Nuclei + Katana + JS Analysis)
python reconmaster.py -d target.com --i-understand-this-requires-authorization

# 3. Pro Workflow: Webhook + Resume + Exclusions
python reconmaster.py -d target.com --webhook <WEBHOOK_URL> --resume --exclude staging.target.com --i-understand-this-requires-authorization
```

### 🔄 Automated Monitoring
```powershell
# Execute tracked scan (checks for changes)
python monitor/scheduler.py -t target.com

# Start Monitoring Daemon (Runs in background)
python monitor/scheduler.py --daemon
```

---

## 📁 Artifact Structure (New in v3.0)

| Directory | Content |
|------|---------|
| `subdomains/` | Passive and Active discovery results (`all_subdomains.txt`) |
| `vulns/` | **Nuclei** vulnerability findings and scan results |
| `endpoints/` | **Katana** crawled URLs and high-value candidates |
| `js/` | Extracted JavaScript links for analysis |
| `reports/` | Executive `RECON_SUMMARY.md` and `recon_data.json` |
| `nmap/` | Target-specific port scan results |

---

## 🎯 Pro Workflows

### Workflow 1: Rapid Asset Discovery
```powershell
# 1. Discovery phase
python reconmaster.py -d client.com --passive-only --i-understand-this-requires-authorization

# 2. Inspect live hosts instantly
cat recon_results/client.com_*/subdomains/live_hosts.txt
```

### Workflow 2: Full Vulnerability Assessment
```powershell
# 1. Run full Pro scan
python reconmaster.py -d target.com --i-understand-this-requires-authorization

# 2. View highest severity findings
grep -E "critical|high" recon_results/target.com_*/vulns/nuclei_results.json
```

---

## 🛠️ Maintenance & Troubleshooting

### v3.0 Tool Verification
If a module fails, ensure the underlying tool is installed:
```powershell
# Re-run Pro Tool Installer
.\install_tools_final.ps1
```

### Concurrency Issues
If you experience network instability, reduce the semaphore count:
```powershell
python reconmaster.py -d target.com -t 10
```

---

## 🔐 Best Practices v3.0

1. **Authorization**: Use the mandatory `--i-understand-this-requires-authorization` flag to confirm you have permission.
2. **Scan Scope**: Always verify the `-d` (domain) matches your authorized target; use `--exclude` to avoid sensitive infra.
3. **Resource Load**: The Pro version is intensive; monitor your local CPU/Memory during large `-t 50+` scans.
3. **Report Integrity**: Use the generated `recon_data.json` for automated parsing into your own dashboards.

---

**Quick Links:**
- [Main Documentation](README.md)
- [Monitoring System](MONITORING.md)
- [Developer: VIPHACKER100](https://github.com/VIPHACKER100)
