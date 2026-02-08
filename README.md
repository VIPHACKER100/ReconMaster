<p align="center">
  <img src="assets/logo.svg" alt="ReconMaster Logo" width="250">
  <br>
  <b>Professional-Grade Asynchronous Reconnaissance Framework</b>
  <br>
  <i>Empowering Bug Bounty Hunters and Security Engineers</i>
</p>

# 🛰️ ReconMaster v3.1.0-Pro

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.9+-brightgreen.svg" alt="Python">
  <img src="https://img.shields.io/badge/Version-3.1.0--Pro-gold.svg" alt="Version">
  <img src="https://img.shields.io/badge/Status-Production--Ready-success.svg" alt="Status">
</p>

```text
╦═╗╔═╗╔═╗╔═╗╔╗╔╔╦╗╔═╗╔═╗╔╦╗╔═╗╦═╗
╠╦╝║╣ ║  ║ ║║║║║║║╠═╣╚═╗ ║ ║╣ ╠╦╝
╩╚═╚═╝╚═╝╚═╝╝╚╝╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═
```

**ReconMaster** is a high-performance orchestration framework designed for deep, automated discovery and vulnerability assessment. Built for speed and reliability, it seamlessly integrates industry-leading tools into a unified, asynchronous workflow.

---

## ⚡ Core Philosophy: Speed & Stealth

ReconMaster isn't just a wrapper; it's a dedicated orchestration engine.
- **AsyncIO Parallelism**: Non-blocking execution of multiple tools simultaneously.
- **Managed Concurrency**: Global semaphores prevent network saturation and system lockups.
- **OpSec Hardened**: Randomized User-Agents, circuit breakers for WAF detection, and absolute path verification.

---

## ✨ Pro Features (v3.0+)

### 🔍 Intelligence & Discovery
- **Multi-Source Subdomain Enumeration**: Integrated `Subfinder`, `Assetfinder`, and `Amass`.
- **Advanced DNS Validation**: High-speed resolution via `dnsx`.
- **Tech-Aware Strategy**: Automatic fingerprinting (`httpx`) drives specialized `Nuclei` profiling.
- **Deep Endpoint Analysis**: Optimized `Katana` crawling + JS Secrets Analysis engine.

### 🛡️ Hardened Operations
- **Circuit Breaker Logic**: Auto-throttles or stops on WAF/Rate-limit spikes (403/429).
- **Sub-Process Sanitization**: Forced process-group termination prevents orphaned zombie processes.
- **Scope Enforcement**: Strict domain and regex filtering across all modules.

### 🔌 Extensibility & Automation
- **Plugin Architecture**: Easily add custom scanners (WordPress, Cloud, GraphQL examples included).
- **Daily Automation Mode**: Light-weight monitoring with state diffing and real-time alerts.
- **CI/CD Integrated**: Native GitHub Actions support for automated daily reconnaissance.
- **Dockerized Runner**: Fully containerized environment for consistent, isolated scans.
- **Professional Proxy Exports**: Automated generation of **Burp Suite** Site Maps and **OWASP ZAP** contexts.

---

## 🚀 Installation & Deployment

### Local Setup
```bash
git clone https://github.com/VIPHACKER100/ReconMaster.git
pip install -r requirements.txt
```

### Docker (Recommended)
```bash
docker build -t reconmaster .
docker run --rm -v $(pwd)/results:/app/recon_results reconmaster -d target.com --i-understand-this-requires-authorization
```

### CI/CD Deployment
Simply copy `.github/workflows/reconmaster.yml` to your repository and configure `RECON_DOMAIN` and `WEBHOOK_URL` in your GitHub Secrets.

---

## 📖 Usage Examples

### Standard Full Assessment
```bash
python reconmaster.py -d target.com --i-understand-this-requires-authorization
```

### Stealth Passive-Only Scan
```bash
python reconmaster.py -d target.com --passive-only --i-understand-this-requires-authorization
```

### Daily Automation (Bug Bounty Mode)
```bash
python reconmaster.py -d target.com --daily --webhook https://discord.com/api/webhooks/...
```

---

## 📁 Output Structure
Results are neatly organized by timestamp:
```text
recon_results/target_timestamp/
├── subdomains/    # Discovered hosts & DNS data
├── vulns/         # Nuclei findings & exposed secrets
├── endpoints/     # Discovered URLs & JS files
├── js/            # JS analysis reports
├── screenshots/   # Visual assessments (Gowitness)
└── reports/       # Executive Markdown & JSON summaries
```

---

## ⚖️ Legal & Ethical Notice
This tool is for **legal, authorized security testing only**. The author assumes no liability for misuse or damage caused by this tool. You **must** have explicit permission before scanning any infrastructure.

---

**Developed with ❤️ by [VIPHACKER100](https://github.com/VIPHACKER100)**
