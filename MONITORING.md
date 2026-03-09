# 🔍 ReconMaster Monitoring System v4.0.0-Titan

High-performance, automated reconnaissance monitoring with change detection and multi-channel alerting, powered by the **ReconMaster v4.0.0-Titan Asynchronous Core**.

## 🚀 Quick Start

### 1. Verification
Ensure you have the latest ReconMaster dependencies installed:

```bash
pip install schedule pyyaml requests aiohttp
```

### 2. Configure Monitoring
Edit `config/monitoring_config.yaml` to add your scoped domains and notification channels:

```yaml
targets:
  - example.com

schedules:
  daily:
    - example.com

alerting:
  enabled: true
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/..."
```

### 3. Run Your First Scan

**Single assessment:**
```bash
python monitor/scheduler.py -t example.com
```

**Start monitoring daemon:**
```bash
python monitor/scheduler.py --daemon
```

---

## 📋 Features

### ✅ v4.0 Performance
- **Titan Asynchronous Engine**: The monitoring system now leverages the v4.0.0-Titan async core, completing scheduled scans up to 5x faster than previous versions.
- **Nuclei & GraphQL Integration**: Automated vulnerability re-scanning and GraphQL introspection on every scheduled interval.
- **SOAP Analysis**: Continuous monitoring of SOAP endpoints and WSDL changes.

### ✅ Change Detection
- 🆕 **New subdomains** discovered via combined passive/active discovery.
- 🚨 **Takeover detection** using nuclei templates.
- 🔌 **Service monitoring**: Detects new or closed ports instantly.
- 🕷️ **Endpoint monitoring**: Tracks new URLs and JS files discovered by Katana.

### ✅ Multi-Channel Alerts
- 📧 **Enterprise Email** (SMTP with SSL/TLS support)
- 💬 **Slack & Discord Webhooks** (Optimized Markdown formatting)
- 📊 **Visual Dashboard**: Real-time updates in `monitor/dashboard.html`.

---

## 📁 Artifact Structure (Monitoring)

```
ReconMaster/
├── monitor/
│   ├── scheduler.py       # Async-aware scheduler
│   ├── diff_detector.py   # High-speed result comparison
│   └── alerting.py        # Pro-grade alert manager
├── monitor_results/       # Persistent scan history
│   └── example.com/
│       ├── 20260208_130000/
│       │   ├── ALERT.txt  # Generated only if changes found
│       │   └── ... (full recon artifacts)
└── config/
    └── monitoring_config.yaml
```

---

## 🔧 Advanced Configuration

### Scan Profiles
You can customize the intensity of monitored scans in the config:

```yaml
scan_options:
  passive_only: false
  threads: 20
  timeout: 600
```

---

## 🔐 Security Best Practices

1. **Webhook Safety**: Avoid committing `monitoring_config.yaml` with live webhook URLs. Use environment variables (if supported by your environment) or strict file permissions.
2. **Alert Thresholds**: Start with `daily` scans for large targets to avoid "Alert Fatigue."
3. **Log Rotation**: Monitor the `logs/` directory to ensure disk space remains available for persistent monitoring results.

---

**Quick Links:**
- [Main README](../README.md)
- [Quick Start Guide](../QUICKSTART.md)
- [VIPHACKER100 GitHub](https://github.com/VIPHACKER100)

**Last Updated:** March 09, 2026  
**Version:** 4.0.0-Titan
