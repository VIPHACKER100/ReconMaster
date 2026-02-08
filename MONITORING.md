# 🔍 ReconMaster Monitoring System

Automated reconnaissance monitoring with change detection and multi-channel alerting.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install schedule pyyaml requests
```

### 2. Configure Monitoring

Edit `config/monitoring_config.yaml`:

```yaml
targets:
  - yourdomain.com

schedules:
  daily:
    - yourdomain.com

alerting:
  enabled: true
  # Configure email, Slack, or Discord
```

### 3. Run Your First Scan

**Single scan:**
```bash
python monitor/scheduler.py -t yourdomain.com
```

**Start monitoring daemon:**
```bash
python monitor/scheduler.py --daemon
```

---

## 📋 Features

### ✅ Automated Scanning
- **Hourly, Daily, Weekly** schedules
- Configurable scan options (passive/active, threads)
- Automatic result processing

### ✅ Change Detection
- 🆕 **New subdomains** discovered
- 🚨 **Subdomain takeover** vulnerabilities
- 🔌 **Port changes** (new/closed ports)
- 🔐 **SSL certificate** changes
- 📊 **Diff reports** between scans

### ✅ Multi-Channel Alerts
- 📧 **Email** (SMTP)
- 💬 **Slack** (webhooks)
- 🎮 **Discord** (webhooks)
- 📄 **File-based** alerts (always enabled)

---

## 🛠️ Usage

### Command Line Options

```bash
# Run single scan
python monitor/scheduler.py -t example.com

# Start daemon with default config
python monitor/scheduler.py --daemon

# Use custom config
python monitor/scheduler.py --daemon -c custom_config.yaml
```

### Configuration File

**Location:** `config/monitoring_config.yaml`

```yaml
# Add targets to monitor
targets:
  - example.com
  - subdomain.example.com

# Configure schedules
schedules:
  hourly:
    - critical-site.com
  daily:
    - example.com
  weekly:
    - low-priority.com

# Scan options
scan_options:
  passive_only: false  # true for faster, less intrusive scans
  threads: 10

# Enable alerts
alerting:
  enabled: true
  
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    smtp_port: 587
    sender_email: alerts@example.com
    sender_password: your-app-password
    recipient_emails:
      - security@example.com
  
  slack:
    enabled: true
    webhook_url: https://hooks.slack.com/services/YOUR/WEBHOOK
  
  discord:
    enabled: true
    webhook_url: https://discord.com/api/webhooks/YOUR/WEBHOOK

# What to monitor
monitoring:
  detect_new_subdomains: true
  detect_takeovers: true
  detect_port_changes: true
  detect_ssl_changes: true
```

---

## 📊 How It Works

### 1. Scheduled Scans
The scheduler runs ReconMaster scans based on your configuration:
- Hourly: Every hour
- Daily: At 02:00 AM
- Weekly: Every Monday at 03:00 AM

### 2. Change Detection
After each scan, the system:
1. Compares with the previous scan
2. Detects changes in:
   - Subdomains (new/removed)
   - Takeover vulnerabilities
   - Open ports
   - SSL certificates

### 3. Alerting
When changes are detected:
1. Severity is assessed (critical/high/medium/low)
2. Alerts are sent via configured channels
3. Alert file is saved with scan results

---

## 🔔 Alert Examples

### Email Alert
```
Subject: 🔍 ReconMaster Alert - example.com

🔍 ReconMaster Alert - example.com
Timestamp: 2026-02-08 11:45:00
Scan Directory: /path/to/scan

📊 Total Changes Detected: 3

🚨 CRITICAL CHANGES:
  • 🚨 CRITICAL: 1 new subdomain takeover vulnerability detected!
    - [wix-takeover] [http] [high] https://test.example.com

⚠️ HIGH PRIORITY:
  • New port(s) opened on api.example.com
    - Port: 8080

📊 MEDIUM PRIORITY:
  • Found 2 new subdomain(s)
    - dev.example.com
    - staging.example.com
```

### Slack/Discord Alert
Similar format, optimized for each platform's markdown support.

---

## 📁 Directory Structure

```
ReconMaster/
├── monitor/
│   ├── __init__.py
│   ├── scheduler.py       # Main scheduler
│   ├── diff_detector.py   # Change detection
│   └── alerting.py        # Alert manager
├── monitor_results/       # Scan results (auto-created)
│   └── example.com/
│       ├── 20260208_114500/
│       │   ├── subdomains/
│       │   ├── reports/
│       │   ├── ALERT.txt
│       │   └── scan_metadata.json
│       └── 20260208_020000/
└── config/
    └── monitoring_config.yaml
```

---

## 🔧 Advanced Usage

### Running as Windows Service

Use **NSSM** (Non-Sucking Service Manager):

```powershell
# Download NSSM from nssm.cc

# Install service
nssm install ReconMaster "C:\Python\python.exe" "C:\ReconMaster\monitor\scheduler.py --daemon"

# Start service
nssm start ReconMaster
```

### Running as Linux Service

Create systemd service file `/etc/systemd/system/reconmaster.service`:

```ini
[Unit]
Description=ReconMaster Monitoring Service
After=network.target

[Service]
Type=simple
User=reconmaster
WorkingDirectory=/opt/ReconMaster
ExecStart=/usr/bin/python3 /opt/ReconMaster/monitor/scheduler.py --daemon
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable reconmaster
sudo systemctl start reconmaster
```

---

## 🔐 Security Best Practices

### Email Configuration
- Use **app-specific passwords** (not your main password)
- For Gmail: Enable 2FA and create app password
- Store credentials securely (environment variables, secrets manager)

### Webhook Security
- Keep webhook URLs private
- Rotate webhooks periodically
- Use webhook signing when available

### File Permissions
```bash
# Restrict config file access
chmod 600 config/monitoring_config.yaml

# Restrict monitor results
chmod 700 monitor_results/
```

---

## 📈 Monitoring Best Practices

### Scan Frequency
- **Critical assets:** Hourly or daily
- **Standard assets:** Daily or weekly
- **Low priority:** Weekly

### Alert Fatigue
- Start with critical alerts only
- Gradually add medium/low priority
- Fine-tune detection thresholds

### Baseline Scans
- First scan establishes baseline
- No alerts on first scan
- Changes detected from second scan onwards

---

## 🐛 Troubleshooting

### No alerts received
1. Check `alerting.enabled: true` in config
2. Verify channel-specific configuration
3. Test with: `python monitor/alerting.py`

### Scans not running
1. Check scheduler is running: `ps aux | grep scheduler`
2. Verify config file path
3. Check system time is correct

### Permission errors
```bash
# Fix permissions
chmod +x monitor/scheduler.py
chmod 600 config/monitoring_config.yaml
```

---

## 📚 API Reference

### ReconScheduler

```python
from monitor import ReconScheduler

# Initialize
scheduler = ReconScheduler("config/monitoring_config.yaml")

# Run single scan
scheduler.run_once("example.com")

# Start daemon
scheduler.start_monitoring()
```

### DiffDetector

```python
from monitor import DiffDetector

detector = DiffDetector()
changes = detector.detect_changes(
    previous_scan="/path/to/old",
    current_scan="/path/to/new",
    monitoring_config={"detect_new_subdomains": True}
)
```

### AlertManager

```python
from monitor import AlertManager

alert_mgr = AlertManager(config)
alert_mgr.send_alerts(
    target="example.com",
    changes=changes,
    scan_dir="/path/to/scan"
)
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional alert channels (Teams, PagerDuty, etc.)
- Web dashboard for monitoring
- Machine learning for anomaly detection
- Integration with SIEM systems

---

## 📄 License

Same as ReconMaster main project.

---

## 🙏 Acknowledgments

Built on top of ReconMaster reconnaissance framework.

**Powered by:**
- schedule - Job scheduling
- PyYAML - Configuration management
- requests - HTTP notifications
