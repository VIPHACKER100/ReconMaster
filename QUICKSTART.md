# ReconMaster v3.2.0-Elite Quick Reference Guide

## 🚀 Elite Commands

### ⚡ High-Speed Scanning (v3.2.0-Elite)
The asynchronous engine is now hardened with JIT directory resilience and the VIP SQLi scanner.

```powershell
# 1. Passive scan (Stealthy, Instant)
python reconmaster.py -d target.com --passive-only --i-understand-this-requires-authorization

# 2. Elite Comprehensive Scan (SQLi + Nuclei + Katana + Cloud)
python reconmaster.py -d target.com --i-understand-this-requires-authorization

# 3. Elite Workflow: Webhook + Resume + Exclusions
python reconmaster.py -d target.com --webhook <WEBHOOK_URL> --resume --exclude staging.target.com --i-understand-this-requires-authorization
```

### 🔄 Automated Monitoring
```powershell
# Execute tracked scan (checks for changes)
python monitor/scheduler.py -t target.com

# Start Monitoring Daemon (Runs in background)
python monitor/scheduler.py --daemon
```

### ⚙️ Configuration (Elite Feature)
ReconMaster supports `config.yaml` and environment variables for persistent settings and API keys.

#### Environment Variables for Intelligence:
```powershell
$env:CENSYS_API_ID="your_id"
$env:CENSYS_API_SECRET="your_secret"
$env:SECURITYTRAILS_API_KEY="your_key"
$env:VIRUSTOTAL_API_KEY="your_key"
```

### ☁️ CI/CD Automation
Use the **Advanced Security Scan** workflow in GitHub Actions:
1. Configure `AUTHORIZED_DOMAINS` secret.
2. Manually trigger via **Actions** tab with target input.
3. Review results in the **Job Summary** and **Artifacts**.

---

## 📁 Artifact Structure (New in v3.2)

| Directory | Content |
|------|---------|
| `subdomains/` | Passive and Active discovery results (`all_subdomains.txt`) |
| `vulns/` | **Nuclei** results and **VIP SQLi Scanner** findings |
| `endpoints/` | **Katana** crawled URLs and high-value candidates |
| `js/` | Extracted JavaScript links for analysis |
| `reports/` | **Premium Dashboard 2.0** (`full_report.html`) and statistics |
| `nmap/` | Target-specific port scan results |

---

## 🎯 Elite Workflows

### Workflow 1: Vulnerability Assessment (SQLi Focused)
```powershell
# 1. Run full Elite scan with native SQLi engine
python reconmaster.py -d target.com --i-understand-this-requires-authorization

# 2. View highest severity findings in Dashboard
# Open recon_results/target.com_*/full_report.html
```

### Workflow 2: Multi-Cloud Discovery
```powershell
# 1. Run scan with cloud modules enabled
python reconmaster.py -d target.com --modules cloud --i-understand-this-requires-authorization

# 2. Check for S3/Azure/GCP exposures
cat recon_results/target.com_*/vulns/exposed_secrets.txt
```

---

## 🛠️ Maintenance & Troubleshooting

### v3.2 Tool Verification
If a module fails, ensure the underlying tool is installed:
```powershell
# Re-run Elite Tool Installer
.\install_tools_final.ps1
```

### Concurrency Issues
If you experience network instability, reduce the semaphore count:
```powershell
python reconmaster.py -d target.com -t 10
```

---

### 🕒 Professional Automation Workflow
Enable **Daily Mode** to monitor for new subdomains and vulnerabilities:

```bash
# Set it as a cron job or scheduled task
python reconmaster.py -d target.com --daily --webhook YOUR_WEBHOOK_URL --i-understand-this-requires-authorization
```

### 🔌 Using Plugins
ReconMaster automatically loads plugins from the `plugins/` directory.
- **VIP SQLi Scanner**: Triggered on input fields and parameters.
- **Cloud Security**: Checks for S3 bucket exposures and cloud misconfigs.

---

## 🔐 Best Practices v3.2

1. **Authorization**: Use the mandatory `--i-understand-this-requires-authorization` flag.
2. **Scan Scope**: Always verify the `-d` (domain) matches your authorized target.
3. **Resource Load**: Elite version is intensive; monitor your local CPU/Memory.
4. **Dashboard**: Use the **Premium Dashboard 2.0** for data visualization.

---

**Quick Links:**
- [Main Documentation](README.md)
- [Monitoring System](MONITORING.md)
- [Developer: VIPHACKER100](https://github.com/VIPHACKER100)
