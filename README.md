
# ReconMaster Installation Script

I've created a comprehensive installation script that will set up ReconMaster and all its dependencies on your system. This script handles everything from installing basic system packages to downloading and configuring all the specialized security tools required.

## Features of the Installation Script

- Installs all system dependencies (Python, Go, build tools)
- Installs all required reconnaissance tools:
  - subfinder, assetfinder, amass for subdomain discovery
  - httpx for live domain verification
  - ffuf for directory brute forcing
  - gowitness for screenshot capture
  - katana for web crawling
  - subjs for JavaScript discovery
  - subzy for subdomain takeover detection
  - socialhunter for broken link checking
  - LinkFinder for endpoint discovery in JavaScript
  - Arjun for parameter discovery
- Downloads security wordlists:
  - SecLists collection
  - n0kovo subdomains wordlist
- Configures the system PATH for proper tool access
- Creates a symlink so you can run ReconMaster from anywhere
- Includes comprehensive documentation

## How to Install

1. Save the script to a file named `install_reconmaster.sh`
2. Make it executable: `chmod +x install_reconmaster.sh`
3. Run it with root privileges: `sudo ./install_reconmaster.sh`

The script will guide you through the installation process with colored status messages.

## After Installation

Once installed, you can immediately start using ReconMaster:

```bash
reconmaster -d target.com -o ./recon_results
```


# ReconMaster: Automated Reconnaissance Tool

I've created a comprehensive reconnaissance framework called **ReconMaster** that integrates all the tools you mentioned into a single, streamlined workflow. This tool automates the entire reconnaissance process from subdomain discovery to reporting.

## Features

- **Subdomain Enumeration**:
  - Passive discovery using subfinder, assetfinder, and amass
  - Active brute forcing with ffuf
  
- **Domain Processing**:
  - Live domain filtering with httpx
  - Screenshot capture with gowitness
  - Subdomain takeover checks with subzy
  
- **Content Discovery**:
  - Endpoint crawling with katana
  - JavaScript file extraction
  - Directory brute forcing with ffuf
  - Parameter discovery with arjun
  
- **Security Checks**:
  - Broken link detection with socialhunter
  - Port scanning with nmap
  
- **Reporting**:
  - Comprehensive markdown report generation

## Usage

```bash
git clone https://github.com/viphacker-100/ReconMaster
cd ReconMaster
python3 reconmaster.py -d target.com -o ./recon_results
```

Optional flags:
- `-t, --threads`: Set number of threads (default: 10)
- `-w, --wordlist`: Custom wordlist for subdomain brute forcing
- `--passive-only`: Only perform non-intrusive reconnaissance

## Implementation

The tool is implemented as a Python class that orchestrates the various tools in a logical sequence. It creates a structured output directory for each target and stores all results in an organized manner.

## Tools Used
- Passive subdomain discovery: subfinder, assetfinder, amass
- Active subdomain discovery: ffuf
- Live domain filtering: httpx
- Screenshot capture: gowitness
- Subdomain takeover checks: subzy
- Endpoint crawling: katana
- JS analysis: LinkFinder
- Directory brute forcing: ffuf
- Parameter discovery: arjun
- Broken link detection: socialhunter
- Port scanning: nmap

## Windows and cross-platform notes

- The ReconMaster Python scripts now include small pure-Python helpers to avoid shell-only commands (merge/sort of text files, safer subprocess calls). This improves compatibility with Windows (PowerShell) and environments without Unix utilities.
- Many external recon tools (subfinder, httpx, ffuf, gowitness, etc.) are Go or native Linux tools and may require WSL or a Linux environment on Windows. For full functionality on Windows, use WSL2 or run ReconMaster inside a Linux VM/container.
- A minimal bundled `wordlists/` folder is included so some basic scans can run without SecLists installed.

If you plan to run on Windows, the recommended approach is to use WSL2 and install the Go-based tools there, or run inside the Ubuntu terminal provided by WSL.
