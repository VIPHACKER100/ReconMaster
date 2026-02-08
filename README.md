# ReconMaster - Automated Reconnaissance Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

**ReconMaster** is a comprehensive, automated reconnaissance framework for security professionals and penetration testers. It combines multiple industry-standard tools into a unified workflow with automated monitoring and alerting capabilities.

![ReconMaster Banner](https://via.placeholder.com/800x200/667eea/ffffff?text=ReconMaster+Reconnaissance+Framework)

---

## 🚀 Features

### Core Reconnaissance
- ✅ **Passive Subdomain Enumeration** (Subfinder, Assetfinder, Amass)
- ✅ **Active Subdomain Brute-forcing** (FFuF)
- ✅ **Live Host Discovery** (Httpx)
- ✅ **Port Scanning** (Nmap - Top 1000 ports)
- ✅ **Subdomain Takeover Detection** (Nuclei)
- ✅ **Web Crawling** (Katana)
- ✅ **Directory Brute-forcing** (FFuF)
- ✅ **Screenshot Capture** (Gowitness)
- ✅ **Parameter Discovery** (Arjun)

### Automated Monitoring 🆕
- 🔄 **Scheduled Scans** (Hourly, Daily, Weekly)
- 🔍 **Change Detection** (New subdomains, port changes, takeovers)
- 📧 **Multi-Channel Alerts** (Email, Slack, Discord)
- 📊 **Historical Tracking** & Diff Reports
- 🎯 **Continuous Security Monitoring**

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

### Prerequisites
- **Python 3.8+**
- **Windows 10/11** (with PowerShell)
- **Nmap** (installed separately)

### Quick Install

```powershell
# Clone the repository
git clone https://github.com/yourusername/ReconMaster.git
cd ReconMaster

# Run setup script (installs Python dependencies and downloads tools)
.\setup.ps1

# Download additional tools and wordlists
.\dl_extra.ps1
```

### Manual Installation

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Install monitoring dependencies
pip install schedule pyyaml

# Download reconnaissance tools
.\install_tools_final.ps1
```

---

## 🚀 Quick Start

### Basic Reconnaissance Scan

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run passive-only scan (faster, less intrusive)
python reconmaster.py -d example.com --passive-only

# Run comprehensive scan
python reconmaster.py -d example.com

# Custom output directory and threads
python reconmaster.py -d example.com -o ./my_scans -t 20
```

### Start Monitoring

```powershell
# Run single monitored scan
python monitor/scheduler.py -t example.com

# Start continuous monitoring daemon
python monitor/scheduler.py --daemon
```

---

## 📖 Usage

### Command Line Options

```
usage: reconmaster.py [-h] -d DOMAIN [-o OUTPUT] [-t THREADS] [-w WORDLIST] [--passive-only]

ReconMaster: Automated Reconnaissance Framework

options:
  -h, --help            Show this help message and exit
  -d, --domain DOMAIN   Target domain to scan
  -o, --output OUTPUT   Output directory for results (default: ./recon_results)
  -t, --threads THREADS Number of threads to use (default: 10)
  -w, --wordlist WORDLIST
                        Custom wordlist for subdomain brute forcing
  --passive-only        Only perform passive reconnaissance
```

### Scan Modes

**Passive Only** (Recommended for initial scans)
```powershell
python reconmaster.py -d example.com --passive-only
```
- Subfinder, Assetfinder, Amass
- Live host verification
- Screenshot capture
- **No active brute-forcing**

**Comprehensive** (Full reconnaissance)
```powershell
python reconmaster.py -d example.com
```
- All passive techniques
- Active subdomain brute-forcing
- Port scanning (top 1000 ports)
- Directory brute-forcing
- Endpoint crawling
- Parameter discovery

---

## 🔄 Monitoring System

ReconMaster includes a powerful monitoring system for continuous security assessment.

### Features
- ✅ Automated scheduled scans
- ✅ Change detection (subdomains, ports, takeovers)
- ✅ Multi-channel alerting
- ✅ Historical tracking
- ✅ Visual dashboard

### Quick Setup

1. **Configure targets** in `config/monitoring_config.yaml`:

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
    sender_email: alerts@example.com
    sender_password: your-app-password
    recipient_emails:
      - security@example.com
```

2. **Start monitoring**:

```powershell
python monitor/scheduler.py --daemon
```

3. **View dashboard**:

Open `monitor/dashboard.html` in your browser

📚 **Full Documentation:** [MONITORING.md](MONITORING.md)

---

## ⚙️ Configuration

### Wordlists

Custom wordlists are located in `wordlists/`:
- `subdomains.txt` - Subdomain enumeration
- `directory-list.txt` - Directory brute-forcing
- `dns_common.txt` - DNS enumeration

### Tool Configuration

All tools are automatically configured to use the local `bin/` directory. No PATH modification required!

---

## 📊 Output

### Directory Structure

```
recon_results/
└── example.com_20260208_114500/
    ├── subdomains/
    │   ├── all_passive.txt       # All discovered subdomains
    │   ├── live_domains.txt      # Live/responding domains
    │   ├── takeovers.txt         # Takeover vulnerabilities
    │   ├── subfinder.txt
    │   ├── assetfinder.txt
    │   └── amass.txt
    ├── screenshots/              # Gowitness screenshots
    ├── endpoints/
    │   ├── urls.txt              # Discovered URLs
    │   └── *_dirs.json           # Directory brute-force results
    ├── js/
    │   └── js_files.txt          # JavaScript files
    ├── params/
    │   └── parameters.txt        # Discovered parameters
    └── reports/
        ├── summary_report.md     # Executive summary
        ├── DETAILED_ANALYSIS.md  # Comprehensive analysis
        └── *_nmap.txt            # Nmap scan results
```

### Reports

**Summary Report** (`summary_report.md`)
- Quick overview of findings
- Subdomain count
- Takeover vulnerabilities
- Next steps

**Detailed Analysis** (`DETAILED_ANALYSIS.md`)
- Comprehensive security assessment
- Risk scoring
- Remediation recommendations
- Technical details

---

## 🔧 Tools Included

ReconMaster automatically downloads and configures these tools:

| Tool | Purpose | Version |
|------|---------|---------|
| **Subfinder** | Passive subdomain enumeration | Latest |
| **Assetfinder** | Certificate transparency logs | Latest |
| **Amass** | Comprehensive OSINT | Latest |
| **Httpx** | Live host verification | Latest |
| **FFuF** | Fuzzing & brute-forcing | Latest |
| **Katana** | Web crawling | Latest |
| **Gowitness** | Screenshot capture | Latest |
| **Nuclei** | Vulnerability scanning | Latest |
| **Arjun** | Parameter discovery | Latest |
| **Nmap** | Port scanning | 7.98 |

All tools are stored in `bin/` and automatically used by ReconMaster.

---

## 💡 Examples

### Example 1: Quick Passive Scan

```powershell
python reconmaster.py -d viphacker100.com --passive-only
```

**Output:**
```
[+] Found 5 unique subdomains via passive enumeration
[+] Found 5 live domains
[+] Report generated: ./recon_results/viphacker100.com_20260208_114500/reports/summary_report.md
```

### Example 2: Comprehensive Scan with Custom Wordlist

```powershell
python reconmaster.py -d example.com -w ./custom_wordlist.txt -t 20
```

### Example 3: Automated Daily Monitoring

```yaml
# config/monitoring_config.yaml
schedules:
  daily:
    - example.com
    - subdomain.example.com
```

```powershell
python monitor/scheduler.py --daemon
```

---

## 🎯 Real-World Use Cases

### 1. Bug Bounty Hunting
- Discover forgotten subdomains
- Identify takeover opportunities
- Find exposed services

### 2. Security Auditing
- Asset discovery
- Attack surface mapping
- Continuous monitoring

### 3. Penetration Testing
- Initial reconnaissance
- Target enumeration
- Vulnerability identification

---

## 🔐 Security Considerations

### Responsible Use
- ✅ Only scan domains you own or have permission to test
- ✅ Respect rate limits and robots.txt
- ✅ Follow responsible disclosure practices

### Privacy
- 🔒 Store credentials securely (use environment variables)
- 🔒 Restrict access to scan results
- 🔒 Encrypt sensitive data

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Additional reconnaissance tools integration
- [ ] Web-based dashboard with real-time updates
- [ ] Machine learning for anomaly detection
- [ ] Integration with SIEM systems
- [ ] Docker containerization
- [ ] Linux/macOS support

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

**Built with:**
- [ProjectDiscovery](https://projectdiscovery.io/) tools (Subfinder, Httpx, Katana, Nuclei)
- [FFuF](https://github.com/ffuf/ffuf) by Joona Hoikkala
- [Amass](https://github.com/owasp-amass/amass) by OWASP
- [Gowitness](https://github.com/sensepost/gowitness) by SensePost
- [Arjun](https://github.com/s0md3v/Arjun) by s0md3v

**Special Thanks:**
- The open-source security community
- All tool developers and maintainers

---

## 📞 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/ReconMaster/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/ReconMaster/discussions)
- **Twitter:** [@yourusername](https://twitter.com/yourusername)

---

## 📈 Roadmap

- [x] Core reconnaissance functionality
- [x] Automated monitoring system
- [x] Multi-channel alerting
- [ ] Web-based dashboard
- [ ] Docker support
- [ ] CI/CD integration
- [ ] API endpoints
- [ ] Machine learning integration

---

<div align="center">

**⭐ Star this repository if you find it useful!**

Made with ❤️ by security professionals, for security professionals

</div>
