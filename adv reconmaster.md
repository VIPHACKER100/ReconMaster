# ReconMaster v3.0.0-Pro: Advanced Asynchronous Reconnaissance Framework

<p align="center">
  <img src="https://via.placeholder.com/800x200/003366/ffffff?text=ReconMaster+v3.0.0-Pro+High-Performance+Recon" alt="ReconMaster Logo"/>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#workflow">Workflow</a> •
  <a href="#tools-integrated">Tools Orchestrated</a> •
  <a href="#output-structure">Output Structure</a> •
  <a href="#examples">Examples</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

**ReconMaster v3.0.0-Pro** is the latest evolution of the ReconMaster framework, re-engineered from the ground up with a high-performance **Asynchronous Engine**. Built for professional security researchers and bug bounty hunters, it provides high-velocity non-blocking orchestration of industry-standard tools.

---

## ⚡ Features

### Asynchronous Core (v3.0+ New)
- **Non-Blocking Orchestration**: Execute multiple discovery and scanning tasks concurrently via `asyncio`.
- **Adaptive Concurrency**: Managed via a high-level semaphore to prevent network congestion while maximizing throughput.
- **Improved Cross-Platform Reliability**: Fixed Windows timeout dependencies, ensuring 100% stability on all operating systems.

### Comprehensive Pipeline
- **Advanced Subdomain Discovery**: Multi-source passive enumeration (`Subfinder`, `Assetfinder`, `Amass`) plus optimized active brute-forcing.
- **Enterprise Vulnerability Scanning**: Integrated `Nuclei` support with custom templates for rapid risk assessment.
- **High-Velocity Crawling**: Deep extraction of URLs, forms, and JavaScript candidates using `Katana`.
- **Infrastructure Profiling**: Technology mapping via `httpx` and parallel visual assessment via `Gowitness`.
- **Attack Surface Mapping**: Automated parameter discovery (`Arjun`) and JavaScript analysis.

---

## 🛠️ Installation

### Automatic Installation (Recommended)
```bash
# Clone and Install
git clone https://github.com/VIPHACKER100/ReconMaster.git
cd ReconMaster
chmod +x install_reconmaster.sh
./install_reconmaster.sh
```

### Windows/PowerShell Setup
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
.\dl_extra.ps1
```

---

## 📖 Usage

### Command Syntax
```bash
python reconmaster.py -d <domain> [options]
```

### Options
| Shortcut | Argument | Description |
|----------|----------|-------------|
| `-d` | `--domain` | **Required.** Target domain to scan. |
| `-o` | `--output` | Output directory (default: `./recon_results`). |
| `-t` | `--threads` | Concurrency limit (default: 10). |
| `-w` | `--wordlist` | Custom wordlist path for brute-forcing. |
| `--passive-only` | | Skip intrusive active scanning/crawling. |

---

## 🔧 Tools Orchestrated

ReconMaster v3.0-Pro integrates best-in-class security tools into a unified async workflow:

- **Subdomain Discovery**: `Subfinder`, `Assetfinder`, `Amass`, `FFuF`
- **Asset Verification**: `Httpx`, `Gowitness`, `Nuclei (Takeovers)`
- **Content Discovery**: `Katana`, `Arjun (Parameters)`
- **Vulnerability Scanning**: `Nuclei (Templates)`
- **Network Analysis**: `Nmap`

---

## 📂 Output Structure

Results are organized into a logical artifact hierarchy for efficient analysis:

```
recon_results/
└── target.com_TIMESTAMP/
    ├── subdomains/       # Subdomain discovery and live host logs
    ├── vulns/            # Nuclei vulnerability scan results
    ├── endpoints/        # Katana crawling and URL extraction
    ├── js/               # Discovered JavaScript artifacts
    ├── screenshots/      #gowitness visual captures
    ├── nmap/             # Service scan reports
    └── reports/          # RECON_SUMMARY.md and recon_data.json
```

---

## 🎓 Examples

### 1. High-Performance Full Scan
```bash
python reconmaster.py -d target.com -t 30
```

### 2. Stealth Passive Discovery
```bash
python reconmaster.py -d target.com --passive-only
```

### 3. Focused Bug Bounty Assessment
```bash
python reconmaster.py -d program.com -w wordlists/subdomains_new.txt
```

---

## 🤝 Contributing

Contributions are welcome! Please submit a Pull Request or open an issue on our [GitHub Repository](https://github.com/VIPHACKER100/ReconMaster).

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/VIPHACKER100">VIPHACKER100</a>
</p>