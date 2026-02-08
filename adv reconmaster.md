# ReconMaster: Advanced Reconnaissance Framework

<p align="center">
  <img src="/api/placeholder/800/200" alt="ReconMaster Logo"/>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#workflow">Workflow</a> •
  <a href="#tools-integrated">Tools Integrated</a> •
  <a href="#output-structure">Output Structure</a> •
  <a href="#examples">Examples</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

ReconMaster is a comprehensive reconnaissance automation framework designed for security professionals, bug bounty hunters, and penetration testers. It orchestrates numerous specialized security tools into a single streamlined workflow, significantly reducing the time and effort required for thorough reconnaissance.

## Features

### Comprehensive Reconnaissance Pipeline

- **Subdomain Discovery**
  - Passive enumeration via subfinder, assetfinder, and amass
  - Active brute forcing with optimized ffuf configurations
  - Fully concurrent processing for maximum efficiency

- **Asset Validation & Exploration**
  - Live domain verification with httpx
  - Technology stack detection
  - Automatic screenshot capture with gowitness
  - Subdomain takeover vulnerability checks with subzy

- **Content Discovery**
  - Intelligent web crawling with katana
  - Automatic JavaScript file extraction and analysis
  - Efficient directory brute forcing with intelligent target selection
  - Parameter discovery and testing with arjun

- **Security Analysis**
  - Broken link discovery for potential hijacking
  - Strategic port scanning with nmap
  - Comprehensive vulnerability reporting

- **Performance Optimization**
  - Asynchronous execution of all components
  - Intelligent rate limiting to avoid detection
  - Smart resource allocation based on target size
  - Parallel processing of all tasks

## Installation

### Automatic Installation (Recommended)

1. Save the installation script to your system:
```bash
curl -o install_reconmaster.sh https://raw.githubusercontent.com/viphacker100/ReconMaster/main/install_reconmaster.sh
```

2. Make it executable:
```bash
chmod +x install_reconmaster.sh
```

3. Run with root privileges:
```bash
sudo ./install_reconmaster.sh
```

The script will automatically install all required dependencies and configure your system for optimal performance.

### Manual Installation

For those who prefer manual control:

1. Clone the repository:
```bash
git clone https://github.com/viphacker100/ReconMaster.git
cd ReconMaster
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install required Go tools:
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/OWASP/Amass/v3/...@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/ffuf/ffuf@latest
go install -v github.com/sensepost/gowitness@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/LukaSikic/subzy@latest
```

4. Install additional tools:
```bash
pip install arjun
```

5. Download wordlists:
```bash
mkdir -p ~/tools/wordlists/n0kovo_subdomains/fuzz
wget https://raw.githubusercontent.com/n0kovo/n0kovo_subdomains/main/n0kovo_subdomains.txt -O ~/tools/wordlists/n0kovo_subdomains/n0kovo_subdomains.txt
wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt -O ~/tools/wordlists/n0kovo_subdomains/fuzz/directory-list.txt
```

6. Clone and set up LinkFinder:
```bash
git clone https://github.com/GerbenJavado/LinkFinder.git
cd LinkFinder
pip install -r requirements.txt
python setup.py install
```

## Usage

### Basic Usage

```bash
reconmaster -d target.com
```
          OR
```python3 reconmaster.py -d target.com -o ./recon_results```          

### Advanced Options

```bash
reconmaster -d target.com -o ./custom_output -t 30 -w custom_wordlist.txt
```
                           OR                   
```bash
python3 reconmaster.py -d target.com -o ./custom_output -t 30 -w custom_wordlist.txt
```
### Full Command Reference

```
usage: reconmaster.py [-h] -d DOMAIN [-o OUTPUT] [-t THREADS] [-w WORDLIST] [--passive-only]

ReconMaster: Automated Reconnaissance Framework

optional arguments:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Target domain to scan
  -o OUTPUT, --output OUTPUT
                        Output directory for results (default: ./recon_results)
  -t THREADS, --threads THREADS
                        Number of threads to use (default: 10)
  -w WORDLIST, --wordlist WORDLIST
                        Custom wordlist for subdomain brute forcing
  --passive-only        Only perform passive reconnaissance
```

## Workflow

ReconMaster follows a logical sequence of operations:

1. **Subdomain Enumeration**: Discovers all possible subdomains using both passive and active methods
2. **Live Domain Resolution**: Filters the subdomain list to identify live assets
3. **Asset Profiling**: Captures screenshots and identifies technology stacks
4. **Subdomain Takeover Analysis**: Checks for potential subdomain takeover vulnerabilities
5. **Content Discovery**: Crawls the web applications to discover endpoints and JavaScript files
6. **Directory Enumeration**: Performs intelligent directory brute forcing
7. **Parameter Discovery**: Identifies possible injection points
8. **Security Testing**: Performs additional tests including broken link detection and port scanning
9. **Reporting**: Generates a comprehensive markdown report with all findings

Each step is fully optimized with:
- Concurrent processing for maximum speed
- Intelligent rate limiting to avoid detection
- Error handling and timeout management
- Progress tracking and logging

## Tools Integrated

ReconMaster orchestrates the following best-in-class security tools:

| Category | Tools |
|----------|-------|
| **Subdomain Discovery** | subfinder, assetfinder, amass, ffuf |
| **Domain Processing** | httpx, gowitness, subzy |
| **Content Discovery** | katana, LinkFinder, ffuf |
| **Parameter Discovery** | arjun |
| **Security Analysis** | socialhunter, nmap |

## Output Structure

ReconMaster creates a well-organized directory structure for each reconnaissance target:

```
recon_results/
└── target.com_YYYYMMDD_HHMMSS/
    ├── subdomains/
    │   ├── all_passive.txt          # Domains from passive enumeration
    │   ├── all_subdomains.txt       # All discovered subdomains
    │   ├── live_domains.txt         # Verified live domains
    │   └── takeovers.txt            # Potential subdomain takeovers
    ├── screenshots/                 # Visual snapshots of all sites
    ├── endpoints/
    │   ├── urls.txt                 # All discovered URLs
    │   ├── js_endpoints.txt         # Endpoints from JavaScript analysis
    │   └── interesting_dirs.txt     # Notable directories
    ├── js/
    │   └── js_files.txt             # JavaScript files for review
    ├── params/
    │   └── parameters.txt           # Discovered parameters
    └── reports/
        ├── broken_links.txt         # Potential broken links
        ├── *_nmap.txt               # Port scan results
        └── summary_report.md        # Comprehensive findings summary
```

## Examples

### Basic Reconnaissance

```bash
reconmaster -d example.com
```

### Bug Bounty Mode

```bash
reconmaster -d hackerone.com -t 20 --output ./bounties/hackerone
```

### Targeted Scan with Custom Wordlist

```bash
reconmaster -d sensitive-target.com -w large_wordlist.txt --passive-only
```

## Optimizing Performance

- **Increase threads** for faster scanning of large targets: `-t 30`
- Use **custom wordlists** for more thorough subdomain discovery: `-w custom_list.txt` 
- For sensitive targets, use `--passive-only` to avoid active probing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgements

- All the amazing open-source tools that ReconMaster integrates
- The security research community for continuous innovation
- Bug bounty platforms for providing the opportunity to responsibly disclose vulnerabilities

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/viphacker100">viphacker100</a>
</p>
# ReconMaster: Advanced Reconnaissance Framework

<p align="center">
  <img src="/api/placeholder/800/200" alt="ReconMaster Logo"/>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#workflow">Workflow</a> •
  <a href="#tools-integrated">Tools Integrated</a> •
  <a href="#output-structure">Output Structure</a> •
  <a href="#examples">Examples</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

ReconMaster is a comprehensive reconnaissance automation framework designed for security professionals, bug bounty hunters, and penetration testers. It orchestrates numerous specialized security tools into a single streamlined workflow, significantly reducing the time and effort required for thorough reconnaissance.

## Features

### Comprehensive Reconnaissance Pipeline

- **Subdomain Discovery**
  - Passive enumeration via subfinder, assetfinder, and amass
  - Active brute forcing with optimized ffuf configurations
  - Fully concurrent processing for maximum efficiency

- **Asset Validation & Exploration**
  - Live domain verification with httpx
  - Technology stack detection
  - Automatic screenshot capture with gowitness
  - Subdomain takeover vulnerability checks with subzy

- **Content Discovery**
  - Intelligent web crawling with katana
  - Automatic JavaScript file extraction and analysis
  - Efficient directory brute forcing with intelligent target selection
  - Parameter discovery and testing with arjun

- **Security Analysis**
  - Broken link discovery for potential hijacking
  - Strategic port scanning with nmap
  - Comprehensive vulnerability reporting

- **Performance Optimization**
  - Asynchronous execution of all components
  - Intelligent rate limiting to avoid detection
  - Smart resource allocation based on target size
  - Parallel processing of all tasks

## Installation

### Automatic Installation (Recommended)

1. Save the installation script to your system:
```bash
curl -o install_reconmaster.sh https://raw.githubusercontent.com/viphacker100/ReconMaster/main/install_reconmaster.sh
```

2. Make it executable:
```bash
chmod +x install_reconmaster.sh
```

3. Run with root privileges:
```bash
sudo ./install_reconmaster.sh
```

The script will automatically install all required dependencies and configure your system for optimal performance.

### Manual Installation

For those who prefer manual control:

1. Clone the repository:
```bash
git clone https://github.com/viphacker100/ReconMaster.git
cd ReconMaster
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install required Go tools:
```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/OWASP/Amass/v3/...@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/ffuf/ffuf@latest
go install -v github.com/sensepost/gowitness@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/LukaSikic/subzy@latest
```

4. Install additional tools:
```bash
pip install arjun
```

5. Download wordlists:
```bash
mkdir -p ~/tools/wordlists/n0kovo_subdomains/fuzz
wget https://raw.githubusercontent.com/n0kovo/n0kovo_subdomains/main/n0kovo_subdomains.txt -O ~/tools/wordlists/n0kovo_subdomains/n0kovo_subdomains.txt
wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt -O ~/tools/wordlists/n0kovo_subdomains/fuzz/directory-list.txt
```

6. Clone and set up LinkFinder:
```bash
git clone https://github.com/GerbenJavado/LinkFinder.git
cd LinkFinder
pip install -r requirements.txt
python setup.py install
```

## Usage

### Basic Usage

```bash
reconmaster -d target.com
```
          OR
```python3 reconmaster.py -d target.com -o ./recon_results```          

### Advanced Options

```bash
reconmaster -d target.com -o ./custom_output -t 30 -w custom_wordlist.txt
```
                           OR                   
```bash
python3 reconmaster.py -d target.com -o ./custom_output -t 30 -w custom_wordlist.txt
```
### Full Command Reference

```
usage: reconmaster.py [-h] -d DOMAIN [-o OUTPUT] [-t THREADS] [-w WORDLIST] [--passive-only]

ReconMaster: Automated Reconnaissance Framework

optional arguments:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Target domain to scan
  -o OUTPUT, --output OUTPUT
                        Output directory for results (default: ./recon_results)
  -t THREADS, --threads THREADS
                        Number of threads to use (default: 10)
  -w WORDLIST, --wordlist WORDLIST
                        Custom wordlist for subdomain brute forcing
  --passive-only        Only perform passive reconnaissance
```

## Workflow

ReconMaster follows a logical sequence of operations:

1. **Subdomain Enumeration**: Discovers all possible subdomains using both passive and active methods
2. **Live Domain Resolution**: Filters the subdomain list to identify live assets
3. **Asset Profiling**: Captures screenshots and identifies technology stacks
4. **Subdomain Takeover Analysis**: Checks for potential subdomain takeover vulnerabilities
5. **Content Discovery**: Crawls the web applications to discover endpoints and JavaScript files
6. **Directory Enumeration**: Performs intelligent directory brute forcing
7. **Parameter Discovery**: Identifies possible injection points
8. **Security Testing**: Performs additional tests including broken link detection and port scanning
9. **Reporting**: Generates a comprehensive markdown report with all findings

Each step is fully optimized with:
- Concurrent processing for maximum speed
- Intelligent rate limiting to avoid detection
- Error handling and timeout management
- Progress tracking and logging

## Tools Integrated

ReconMaster orchestrates the following best-in-class security tools:

| Category | Tools |
|----------|-------|
| **Subdomain Discovery** | subfinder, assetfinder, amass, ffuf |
| **Domain Processing** | httpx, gowitness, subzy |
| **Content Discovery** | katana, LinkFinder, ffuf |
| **Parameter Discovery** | arjun |
| **Security Analysis** | socialhunter, nmap |

## Output Structure

ReconMaster creates a well-organized directory structure for each reconnaissance target:

```
recon_results/
└── target.com_YYYYMMDD_HHMMSS/
    ├── subdomains/
    │   ├── all_passive.txt          # Domains from passive enumeration
    │   ├── all_subdomains.txt       # All discovered subdomains
    │   ├── live_domains.txt         # Verified live domains
    │   └── takeovers.txt            # Potential subdomain takeovers
    ├── screenshots/                 # Visual snapshots of all sites
    ├── endpoints/
    │   ├── urls.txt                 # All discovered URLs
    │   ├── js_endpoints.txt         # Endpoints from JavaScript analysis
    │   └── interesting_dirs.txt     # Notable directories
    ├── js/
    │   └── js_files.txt             # JavaScript files for review
    ├── params/
    │   └── parameters.txt           # Discovered parameters
    └── reports/
        ├── broken_links.txt         # Potential broken links
        ├── *_nmap.txt               # Port scan results
        └── summary_report.md        # Comprehensive findings summary
```

## Examples

### Basic Reconnaissance

```bash
reconmaster -d example.com
```

### Bug Bounty Mode

```bash
reconmaster -d hackerone.com -t 20 --output ./bounties/hackerone
```

### Targeted Scan with Custom Wordlist

```bash
reconmaster -d sensitive-target.com -w large_wordlist.txt --passive-only
```

## Optimizing Performance

- **Increase threads** for faster scanning of large targets: `-t 30`
- Use **custom wordlists** for more thorough subdomain discovery: `-w custom_list.txt` 
- For sensitive targets, use `--passive-only` to avoid active probing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgements

- All the amazing open-source tools that ReconMaster integrates
- The security research community for continuous innovation
- Bug bounty platforms for providing the opportunity to responsibly disclose vulnerabilities

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/viphacker100">viphacker100</a>
</p>