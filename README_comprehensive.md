# ReconMaster: Automated Reconnaissance Framework

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.7+-brightgreen)
![Status](https://img.shields.io/badge/Status-Active-success)

**ReconMaster** is a comprehensive reconnaissance automation framework designed for security professionals, bug bounty hunters, and penetration testers. It orchestrates multiple specialized security tools into a single streamlined workflow for subdomain discovery, asset validation, content discovery, and security analysis.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Output Structure](#output-structure)
- [Tools Integrated](#tools-integrated)
- [Workflow](#workflow)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### 🎯 Core Capabilities

- **Passive Subdomain Enumeration**: Discover subdomains using multiple OSINT sources (subfinder, assetfinder, amass)
- **Active Subdomain Brute Forcing**: Aggressive discovery using ffuf with customizable wordlists
- **Live Domain Verification**: Filter responsive domains with httpx, including status codes and technology detection
- **Screenshot Capture**: Visual verification of discovered domains using gowitness
- **Subdomain Takeover Detection**: Identify vulnerable subdomains with subzy
- **Web Crawling**: Comprehensive endpoint discovery using katana with configurable depth
- **JavaScript Analysis**: Extract and analyze JavaScript files using subjs and LinkFinder
- **Directory Enumeration**: Discover hidden directories and files using ffuf
- **Parameter Discovery**: Identify application parameters using Arjun
- **Broken Link Detection**: Find hijacking opportunities using socialhunter
- **Port Scanning**: Comprehensive port analysis using nmap
- **Automated Reporting**: Generate detailed markdown reports with findings

### 📊 Operational Features

- Cross-platform support (Linux, macOS, Windows via WSL2)
- Passive-only mode for sensitive assessments
- Customizable thread counts for performance tuning
- Built-in wordlists for operation without external resources
- Comprehensive logging and error handling
- Structured JSON and text output formats
- Resume capability for interrupted scans (v2+)
- Rate limiting to avoid detection

## Quick Start

```bash
# Clone the repository
git clone https://github.com/viphacker100/ReconMaster
cd ReconMaster

# Install dependencies
pip install -r requirements.txt

# Run basic reconnaissance
python3 reconmaster.py -d target.com

# Run passive-only scan
python3 reconmaster.py -d target.com --passive-only

# Specify custom output directory and threads
python3 reconmaster.py -d target.com -o ./results -t 20
```

## Installation

### Prerequisites

- **Python**: 3.7 or higher
- **Go**: 1.16 or higher (for Go-based tools)
- **System Tools**: git, wget, curl, build-essential
- **Recommended**: 4GB RAM, 20GB disk space for wordlists
- **Network**: Unrestricted internet access for reconnaissance operations

### Automatic Installation (Linux/macOS)

```bash
chmod +x install_reconmaster.sh
sudo ./install_reconmaster.sh
```

This script will:
- Install system dependencies
- Install all Go-based reconnaissance tools
- Install Python dependencies
- Download wordlists (SecLists, n0kovo)
- Configure PATH variables
- Create system-wide symlink

### Manual Installation (Windows/WSL2)

Run the PowerShell script:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

Or follow these steps in WSL2:
1. Install Ubuntu from Microsoft Store
2. Open Ubuntu terminal
3. Run: `sudo apt update && sudo apt install -y python3 python3-pip git golang-go`
4. Follow Linux installation steps above

### Docker Installation

```bash
docker build -t reconmaster .
docker run -v $(pwd)/results:/app/results reconmaster -d target.com -o /app/results
```

## Usage

### Basic Command Syntax

```bash
python3 reconmaster.py [OPTIONS] -d DOMAIN
```

### Command-Line Arguments

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `--domain` | `-d` | string | Required | Target domain to scan |
| `--output` | `-o` | path | `./recon_results` | Output directory for results |
| `--threads` | `-t` | int | 10 | Number of concurrent threads |
| `--wordlist` | `-w` | path | (bundled) | Custom wordlist for brute forcing |
| `--passive-only` | | flag | False | Only perform passive reconnaissance |

### Usage Examples

```bash
# Standard full reconnaissance scan
python3 reconmaster.py -d example.com

# Passive reconnaissance only (no brute forcing)
python3 reconmaster.py -d example.com --passive-only

# High-performance scan with custom thread count
python3 reconmaster.py -d example.com -t 50

# Use custom wordlist
python3 reconmaster.py -d example.com -w ~/wordlists/custom-subdomains.txt

# Specify custom output directory
python3 reconmaster.py -d example.com -o ~/projects/example-recon

# Combine options
python3 reconmaster.py -d example.com -o ~/results -t 30 -w ~/wordlists/seclists.txt
```

## Output Structure

Reconnaissance results are organized by category:

```
recon_results/example.com_YYYYMMDD_HHMMSS/
├── subdomains/
│   ├── all_subdomains.txt           # All discovered subdomains
│   ├── all_passive.txt              # Passive enumeration results
│   ├── brute_forced.txt             # Active brute force results
│   ├── live_domains.txt             # Responsive domains
│   ├── live_domains_detailed.json   # httpx detailed output
│   └── takeovers.txt                # Potential takeover targets
├── screenshots/
│   ├── domain1.png
│   ├── domain2.png
│   └── ...                          # Visual captures of domains
├── endpoints/
│   ├── urls.txt                     # All discovered URLs
│   ├── js_endpoints.txt             # Endpoints from JavaScript
│   └── interesting_dirs.txt         # Discovered directories
├── js/
│   ├── js_files.txt                 # JavaScript file URLs
│   └── js_analysis.txt              # JS endpoint analysis
├── params/
│   └── parameters.txt               # Discovered parameters
├── reports/
│   ├── summary_report.md            # Main findings report
│   ├── broken_links.txt             # Broken link findings
│   └── *_nmap.txt                   # Port scan results
└── reconmaster.log                  # Detailed execution log
```

## Tools Integrated

| Tool | Purpose | Type | Status |
|------|---------|------|--------|
| **subfinder** | Passive subdomain enumeration | CLI/Go | Required |
| **assetfinder** | OSINT subdomain discovery | CLI/Go | Required |
| **amass** | Comprehensive subdomain discovery | CLI/Go | Optional* |
| **httpx** | HTTP probe and live domain detection | CLI/Go | Required |
| **ffuf** | Fast web fuzzer (subdomains & directories) | CLI/Go | Required |
| **gowitness** | Website screenshot capture | CLI/Go | Optional |
| **katana** | Web crawler and endpoint discovery | CLI/Go | Required |
| **subjs** | JavaScript file discovery | CLI/Go | Required |
| **LinkFinder** | JavaScript endpoint extraction | CLI/Python | Optional |
| **Arjun** | HTTP parameter discovery | CLI/Python | Optional |
| **subzy** | Subdomain takeover detection | CLI/Go | Optional |
| **socialhunter** | Broken link detection | CLI/Python | Optional |
| **nmap** | Network port scanning | CLI/C | Optional |

*Optional tools will be skipped if not installed; core functionality continues

## Workflow

### Phase 1: Subdomain Discovery
1. **Passive Enumeration** - Query public OSINT sources
   - Subfinder: DNS, Archive.org, Wayback Machine, Certspotter
   - Assetfinder: Rapid7, Certspotter
   - Amass: DNS enumeration and API querying (optional, slower)

2. **Active Brute Forcing** - Attempt dictionary attack
   - ffuf with provided or custom wordlist
   - Attempts common subdomain names

3. **Consolidation** - Merge and deduplicate all sources

### Phase 2: Domain Validation
1. **Live Domain Detection** - Filter responsive domains
   - httpx probes each subdomain
   - Records HTTP status codes, titles, technologies
   
2. **Screenshot Capture** - Visual documentation
   - gowitness captures screenshots of web interfaces
   
3. **Takeover Detection** - Identify vulnerable subdomains
   - subzy tests for service vulnerabilities

### Phase 3: Content Discovery  
1. **Web Crawling** - Discover endpoints and links
   - katana crawls to configurable depth (default: 3)
   - Extracts URLs, forms, JavaScript references
   
2. **JavaScript Extraction** - Identify JS files
   - subjs enumerates JavaScript resources
   - Filters and deduplicates
   
3. **JS Analysis** - Extract endpoints from code
   - LinkFinder parses JavaScript for API endpoints
   
4. **Directory Brute Forcing** - Find hidden paths
   - ffuf attempts directory enumeration (limited to 10 domains)
   - Looks for common paths (admin, api, config, etc.)

### Phase 4: Parameter Discovery
1. **Parameter Enumeration** - Identify application parameters
   - Arjun tests endpoints for common parameters
   - Limited to 50 URLs to avoid excessive testing

### Phase 5: Security Analysis
1. **Broken Link Detection** - Find hijacking opportunities
   - socialhunter identifies broken social media links
   
2. **Port Scanning** - Assess network exposure
   - nmap comprehensive port scan (limited to 5 prioritized targets)
   - Service version detection

### Phase 6: Reporting
1. **Statistics Collection** - Aggregate findings
2. **Report Generation** - Create markdown summary
3. **Result Archival** - Organize outputs by category

## Advanced Configuration

### Using Configuration Files

Create `config.yml`:
```yaml
reconnaissance:
  threads: 10
  timeout: 300
  passive_only: false
  
output:
  directory: ./recon_results
  format: markdown,json
  include_screenshots: true
  
logging:
  level: INFO
  verbose: false
  
wordlists:
  subdomains: /path/to/subdomains.txt
  directories: /path/to/directories.txt
  
tools:
  subfinder:
    enabled: true
    args: "-silent"
  httpx:
    enabled: true
    timeout: 10
  ffuf:
    enabled: true
    threads: 40
```

### Using Scan Profiles

Pre-configured profiles for common scenarios:

```bash
# Fast scan - quick coverage
python3 reconmaster.py -d target.com --profile fast

# Thorough scan - complete coverage
python3 reconmaster.py -d target.com --profile thorough

# Bug bounty optimized
python3 reconmaster.py -d target.com --profile bugbounty

# Stealth scan - slow, randomized, minimal footprint
python3 reconmaster.py -d target.com --profile stealth
```

## Troubleshooting

### Common Issues

**Error: "subfinder not found in PATH"**
- Installation incomplete; run: `sudo ./install_reconmaster.sh`
- Verify PATH: `which subfinder`
- Manual fix: `export PATH=$PATH:$HOME/go/bin`

**Error: "Permission denied" for installation**
- Ensure you have sudo access
- Run installation with: `sudo bash install_reconmaster.sh`

**No results from passive enumeration**
- Check network connectivity: `ping 8.8.8.8`
- Verify target domain exists: `nslookup target.com`
- Try again - some OSINT sources rate limit

**Timeouts during scanning**
- Reduce thread count: `-t 5`
- Increase timeout values in config
- Run specific phase only instead of full scan

**Docker issues on Windows**
- Use WSL2 backend: `docker run --platform linux/amd64`
- Ensure 4GB RAM allocated to Docker

### Getting Help

1. Check [FAQ.md](docs/FAQ.md) for common questions
2. Review [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions
3. Search [GitHub Issues](https://github.com/viphacker100/ReconMaster/issues)
4. Create new issue with:
   - Full error message
   - Python version: `python3 --version`
   - OS and environment: `uname -a` or `systeminfo`
   - Command executed
   - Relevant log lines from `reconmaster.log`

## Project Variants

### ReconMaster v1 (Core)
- Baseline reconnaissance framework
- Sequential tool execution
- File-based output

### ReconMaster v2 (Enhanced)
- Concurrent thread pool execution
- Progress bars with tqdm
- Retry logic for failed tools
- --verbose and --quiet modes
- Resume interrupted scans

### ReconMaster v3 (Advanced)
- Vulnerability scoring system
- CVE integration
- Cloud storage export
- Webhook notifications
- Custom plugin system
- ML-based anomaly detection

### ProReconMaster (Enterprise)
- Team collaboration features
- Centralized PostgreSQL database
- Role-based access control
- Compliance reporting (PCI, HIPAA)
- Scheduled scans
- Email reporting

### Recon Black (Stealth)
- Request randomization and obfuscation
- User-agent rotation
- Proxy/Tor support
- Jittered rate limiting
- Header randomization
- Configurable stealth levels (1-5)

### Recon Tool (Minimal)
- Pure Python implementation
- Standard library only (+ requests)
- No external tool dependencies
- Basic functionality subset
- Lightweight resource usage

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of Conduct
- Development setup
- Coding standards
- Pull request process

## Legal & Ethical

⚠️ **Important Disclaimer**: ReconMaster is designed for **authorized security testing only**. 

Ensure you have:
- Written authorization from target system owner
- Permission to perform security assessment
- Understanding of applicable laws (CFAA, GDPR, etc.)

See [LEGAL.md](LEGAL.md) for complete legal disclaimers.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

**Copyright © 2026 viphacker100**

## Support & Documentation

- **README**: [README.md](README.md) - This file
- **Advanced Documentation**: [adv_reconmaster.md](adv_reconmaster.md) - Technical details
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Version history
- **FAQ**: [docs/FAQ.md](docs/FAQ.md) - Common questions
- **Examples**: [docs/EXAMPLES.md](docs/EXAMPLES.md) - Real-world usage

## Acknowledgments

Built with contributions from:
- The open source security community
- Authors of integrated tools (projectdiscovery, tomnomnom, etc.)
- Bug bounty hunters and security researchers

## Contact

- **Repository**: [github.com/viphacker100/ReconMaster](https://github.com/viphacker100/ReconMaster)
- **Issues**: [Report bugs and request features](https://github.com/viphacker100/ReconMaster/issues)
- **Security**: Report security issues to [security@example.com]

---

**Made with ❤️ for the security research community**
