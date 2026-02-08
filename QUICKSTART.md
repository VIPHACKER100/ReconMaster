# ReconMaster Quick Reference Guide

## 🚀 Quick Commands

### Basic Scanning
```powershell
# Passive scan (fast, recommended first)
python reconmaster.py -d example.com --passive-only

# Full comprehensive scan
python reconmaster.py -d example.com

# Custom threads and output
python reconmaster.py -d example.com -t 20 -o ./custom_output
```

### Monitoring
```powershell
# Single monitored scan
python monitor/scheduler.py -t example.com

# Start monitoring daemon
python monitor/scheduler.py --daemon

# Custom config
python monitor/scheduler.py --daemon -c custom_config.yaml
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `reconmaster.py` | Main reconnaissance script |
| `monitor/scheduler.py` | Monitoring scheduler |
| `config/monitoring_config.yaml` | Monitoring configuration |
| `monitor/dashboard.html` | Visual dashboard |
| `MONITORING.md` | Full monitoring docs |

## 🎯 Common Workflows

### Workflow 1: Initial Assessment
```powershell
# 1. Quick passive scan
python reconmaster.py -d target.com --passive-only

# 2. Review results
cat recon_results/target.com_*/reports/summary_report.md

# 3. If needed, run full scan
python reconmaster.py -d target.com
```

### Workflow 2: Continuous Monitoring
```powershell
# 1. Configure monitoring
notepad config/monitoring_config.yaml

# 2. Run baseline scan
python monitor/scheduler.py -t target.com

# 3. Start automated monitoring
python monitor/scheduler.py --daemon

# 4. View dashboard
start monitor/dashboard.html
```

### Workflow 3: Bug Bounty
```powershell
# 1. Passive enumeration
python reconmaster.py -d target.com --passive-only

# 2. Check for takeovers
cat recon_results/target.com_*/subdomains/takeovers.txt

# 3. Review detailed analysis
cat recon_results/target.com_*/DETAILED_ANALYSIS.md
```

## 🔧 Configuration

### Monitoring Config Template
```yaml
targets:
  - example.com

schedules:
  daily:
    - example.com

alerting:
  enabled: true
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    sender_email: your-email@gmail.com
    sender_password: your-app-password
    recipient_emails:
      - security@example.com

monitoring:
  detect_new_subdomains: true
  detect_takeovers: true
  detect_port_changes: true
```

## 📊 Output Locations

```
recon_results/
└── target.com_TIMESTAMP/
    ├── subdomains/
    │   ├── all_passive.txt      ← All subdomains
    │   ├── live_domains.txt     ← Live hosts
    │   └── takeovers.txt        ← Vulnerabilities
    ├── reports/
    │   ├── summary_report.md    ← Quick summary
    │   └── DETAILED_ANALYSIS.md ← Full analysis
    └── screenshots/             ← Visual captures
```

## 🚨 Alert Channels

### Email Setup (Gmail)
1. Enable 2FA on Gmail
2. Generate app password: https://myaccount.google.com/apppasswords
3. Update config:
```yaml
email:
  enabled: true
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender_email: your-email@gmail.com
  sender_password: your-16-char-app-password
```

### Slack Setup
1. Create incoming webhook: https://api.slack.com/messaging/webhooks
2. Update config:
```yaml
slack:
  enabled: true
  webhook_url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Discord Setup
1. Create webhook in channel settings
2. Update config:
```yaml
discord:
  enabled: true
  webhook_url: https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
```

## 🛠️ Troubleshooting

### Tools not found
```powershell
# Re-run tool installer
.\install_tools_final.ps1
.\dl_extra.ps1
```

### Python errors
```powershell
# Reinstall dependencies
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Monitoring not starting
```powershell
# Check config syntax
python -c "import yaml; yaml.safe_load(open('config/monitoring_config.yaml'))"

# Test alerts
python monitor/alerting.py
```

## 📈 Performance Tips

### Faster Scans
- Use `--passive-only` for quick results
- Increase threads: `-t 20`
- Use smaller wordlists

### Resource Management
- Limit concurrent scans
- Use scheduled scans during off-hours
- Monitor disk space for results

## 🔐 Security Best Practices

1. **Permissions**
   ```powershell
   # Restrict config access
   icacls config\monitoring_config.yaml /inheritance:r /grant:r "%USERNAME%:F"
   ```

2. **Credentials**
   - Never commit credentials to Git
   - Use environment variables when possible
   - Rotate API keys/passwords regularly

3. **Responsible Scanning**
   - Only scan authorized targets
   - Respect rate limits
   - Follow responsible disclosure

## 📞 Getting Help

- **Documentation:** README.md, MONITORING.md
- **Issues:** GitHub Issues
- **Examples:** See `examples/` directory

## 🎓 Learning Resources

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Bug Bounty Methodology](https://github.com/jhaddix/tbhm)
- [Reconnaissance Techniques](https://pentester.land/cheatsheets/2019/03/25/compilation-of-recon-workflows.html)

---

**Quick Links:**
- [Full README](README.md)
- [Monitoring Guide](MONITORING.md)
- [Dashboard](monitor/dashboard.html)
