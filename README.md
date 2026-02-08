# ReconMaster v3.0.0-Pro - Automated Asynchronous Reconnaissance Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Version: 3.0.0-Pro](https://img.shields.io/badge/version-3.0.0--Pro-brightgreen.svg)](https://github.com/VIPHACKER100/ReconMaster)

**ReconMaster v3.0.0-Pro** is a comprehensive, high-performance, and automated reconnaissance framework built for modern security professionals. Completely rewritten with an **asynchronous core**, it orchestrates industry-standard tools into a seamless, high-velocity workflow with integrated vulnerability scanning, change detection, and multi-channel alerting.

![ReconMaster Banner](https://via.placeholder.com/800x200/003366/ffffff?text=ReconMaster+v3.0.0-Pro+High-Performance+Recon)

---

## 🚀 Pro Features

### ⚡ Parallel Orchestration (New in v3.0)
- ✅ **AsyncIO Core**: Simultaneous execution of discovery, crawling, and scanning modules.
- ✅ **Concurrency Semaphore**: Intelligent resource management to prevent target overloading.
- ✅ **Optimized Tooling**: Asynchronous wrappers for all core security binaries.

### 🛡️ Intelligent Reconnaissance
- 🔍 **Multi-Source Subdomain Enumeration**: Integrated `Subfinder`, `Assetfinder`, and `Amass`.
- 🎯 **Vulnerability Discovery**: Native `Nuclei` integration for Critical-Low severity scanning.
- 🕷️ **Advanced Crawling**: Deep endpoint extraction and spidering using `Katana`.
- 🧪 **Parameter & JS Discovery**: Automated `Arjun` and `LinkFinder` workflows for attack surface mapping.
- 📸 **Gowitness Integration**: Parallel screenshot capture with automated chunking.

### 🔄 Automated Monitoring
- 🔄 **Scheduled Scans**: Execute scans Hourly, Daily, or Weekly.
- 🔍 **Change Detection**: Proactive alerts for new subdomains, port changes, and potential takeovers.
- 📧 **Enterprise Alerting**: Instant notifications via Email, Slack, and Discord.
- 📊 **Historical Diffing**: Automated report generation tracking infrastructure evolution.

---

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Monitoring System](#monitoring-system)
- [Configuration](#configuration)
- [Output](#output)
- [Tools Included](#tools-included)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## 🛠️ Installation

### Quick Install (Windows Recommended)

```powershell
# Clone the repository
git clone https://github.com/VIPHACKER100/ReconMaster.git
cd ReconMaster

# Run setup script (installs Python dependencies and downloads tools)
.\setup.ps1

# Download additional tools and wordlists
.\dl_extra.ps1
```

### Manual Installation

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Download security tools
.\install_tools_final.ps1
```

---

## 🚀 Quick Start

### Basic Asynchronous Scan

```powershell
# Run a quick, non-intrusive passive scan
python reconmaster.py -d example.com --passive-only

# Run a comprehensive Pro-level scan (Fastest mode)
python reconmaster.py -d example.com

# Custom concurrency (threads)
python reconmaster.py -d example.com -t 30
```

---

## 📖 Usage

```
usage: reconmaster.py [-h] -d DOMAIN [-o OUTPUT] [-t THREADS] [-w WORDLIST] [--passive-only]

ReconMaster v3.0.0-Pro - Advanced Asynchronous Reconnaissance Framework

options:
  -h, --help            Show this help message and exit
  -d, --domain DOMAIN   Target domain to scan
  -o, --output OUTPUT   Output directory (default: ./recon_results)
  -t, --threads THREADS Concurrency limit (default: 10)
  -w, --wordlist WORDLIST Custom wordlist for discovery
  --passive-only        Skip active scans (no brute-forcing/crawling)
```

---

## 📊 Output & Reporting

ReconMaster v3.0-Pro generates a professional artifact structure:

```
recon_results/
└── example.com_20260208_130000/
    ├── subdomains/       # Subfinder, Assetfinder, Amass results
    ├── vulns/            # Nuclei vulnerability scan results
    ├── endpoints/        # Katana crawling & JS endpoints
    ├── screenshots/      # Gowitness captures
    ├── js/               # Discovered JavaScript files
    ├── params/           # Arjun parameter discovery results
    ├── nmap/             # Service scan results
    └── reports/          # Markdown and JSON summaries
```

---

## 🔧 Tools Included

| Tool | Purpose | Version Status |
|------|---------|---------|
| **Subfinder** | Passive enumeration | Included |
| **Nuclei** | Vulnerability scanning | **Enterprise Integration** |
| **Katana** | Advanced Crawling | **Pro Addition** |
| **Amass** | Deep OSINT Discovery | Included |
| **Gowitness** | Screenshot Capture | Optimized |
| **Httpx** | Live Host Detection | Included |
| **FFuF** | Fuzzing | Parallelized |
| **Arjun** | Parameter Discovery | Included |

---

## 📞 Contact & Support

- **Twitter:** [@VIPHACKER100](https://twitter.com/VIPHACKER100)
- **GitHub:** [VIPHACKER100/ReconMaster](https://github.com/VIPHACKER100/ReconMaster)

---

<div align="center">

**⭐ Star this repository if you find it useful!**

Made with ❤️ by **VIPHACKER100** for the security community.

</div>
