# ReconMaster v3.0.0-Pro: Automated Asynchronous Reconnaissance Framework

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-brightgreen)
![Status](https://img.shields.io/badge/Status-Active-success)
![Version](https://img.shields.io/badge/Version-3.0.0--Pro-brightgreen)

**ReconMaster v3.0.0-Pro** is the latest evolution of the ReconMaster framework, completely re-engineered with a high-performance **Asynchronous Engine**. Designed for modern security professionals, bug bounty hunters, and penetration testers, it orchestrates industry-standard tools into a high-velocity, non-blocking workflow.

---

## 🚀 Pro Features (v3.0+)

### ⚡ Performance & Core
- **AsyncIO Orchestration**: Non-blocking execution of multiple tools simultaneously.
- **Adaptive Concurrency**: Managed by a semaphore for stable high-thread operations.
- **Cross-Platform Asynchronicity**: Full support for Windows, Linux, and macOS without legacy timeout dependencies.
- **Integrated Vulnerability Scanning**: Native `Nuclei` support for rapid target assessment.

### 🛡️ Core Capabilities
- **Multi-Source Discovery**: Combines `Subfinder`, `Assetfinder`, and `Amass`.
- **Advanced Crawling**: Deep extraction using `Katana` for URLs and JavaScript.
- **Intelligent Tech Detection**: Leverages `httpx` for technology mapping and fingerprinting.
- **Visual Assessment**: Parallel `Gowitness` screenshots with automated chunking.
- **Endpoint Analysis**: JavaScript link extraction and parameter discovery with `Arjun`.
- **Port Scanning**: Multi-target `Nmap` service discovery.

---

## 🛠️ Installation

### Quick Install (Windows Recommended)
```powershell
git clone https://github.com/VIPHACKER100/ReconMaster.git
cd ReconMaster
.\setup.ps1
.\dl_extra.ps1
```

### Automatic Install (WSL/Linux)
```bash
chmod +x install_reconmaster.sh
./install_reconmaster.sh
```

---

## 📖 Usage

```bash
# Basic Pro Scan
python reconmaster.py -d example.com

# Stealth Passive Scan
python reconmaster.py -d example.com --passive-only

# High-Intensity Assessment
python reconmaster.py -d example.com -t 30
```

---

## 📁 Optimized Output Structure

ReconMaster v3.0 organizes results into dedicated artifact directories:

| Directory | Content |
|-----------|---------|
| `subdomains/` | Discovery results, live hosts, and takeover logs. |
| `vulns/` | **Nuclei** vulnerability findings (JSON/Txt). |
| `endpoints/` | **Katana** crawl data and interessant candidates. |
| `screenshots/` | Visual captures for verification. |
| `nmap/` | Target service scan results. |
| `reports/` | Markdown summaries and JSON telemetry data. |

---

## 🔧 Tools Orchestrated

| Tool | Purpose | Type | Status |
|------|---------|------|--------|
| **Subfinder** | Passive enumeration | Go | Required |
| **Nuclei** | Vulnerability scanning | Go | **Pro Integrated** |
| **Katana** | Advanced Spidering | Go | **Pro Integrated** |
| **Httpx** | Live Domain Probe | Go | Required |
| **Gowitness** | Screenshots | Go | Included |
| **Arjun** | Parameters | Python | Included |

---

## 🔄 Automated Monitoring

ReconMaster features a persistent monitoring system (`monitor/scheduler.py`) that periodically scans targets, detects changes in infrastructure, and alerts via:
- 📧 Email (SMTP)
- 💬 Slack & Discord Webhooks
- 📊 Real-time Visual Dashboard

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 🔐 Legal Disclaimer

ReconMaster is for **authorized security testing only**. The authors assume no liability for misuse. See [LEGAL.md](LEGAL.md) for full terms.

---

**Copyright © 2026 VIPHACKER100**
**License:** MIT
**GitHub:** [VIPHACKER100/ReconMaster](https://github.com/VIPHACKER100/ReconMaster)
