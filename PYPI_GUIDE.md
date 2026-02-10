# PyPI Installation Guide for ReconMaster

## Overview

ReconMaster is available on PyPI and can be installed globally using `pip`. This guide covers installation, configuration, and usage.

---

## Prerequisites

- **Python:** 3.7 or higher
- **pip:** Package installer (comes with Python)
- **System Tools:** nmap, curl, wget (optional but recommended)

### Check Python Version

```bash
python --version
# Output: Python 3.9.0 (or higher)

# On some systems
python3 --version

# Check pip
pip --version
# Output: pip 21.0 (or higher)
```

---

## Installation Methods

### Method 1: Standard Installation (Most Common)

```bash
# Install latest version
pip install reconmaster

# Install specific version
pip install reconmaster==3.1.0-Pro

# Install with extras
pip install reconmaster[dev]     # Development tools
pip install reconmaster[test]    # Testing tools
pip install reconmaster[docs]    # Documentation tools
```

### Method 2: Upgrade Existing Installation

```bash
# Upgrade to latest version
pip install --upgrade reconmaster

# Short form
pip install -U reconmaster

# Upgrade to specific version
pip install --upgrade reconmaster==1.0.0
```

### Method 3: Development Installation

```bash
# Clone repository
git clone https://github.com/VIPHACKER100/ReconMaster.git
cd ReconMaster

# Install in editable mode (for development)
pip install -e .

# Install with development extras
pip install -e ".[dev,test]"
```

### Method 4: From Wheel File

```bash
# Download wheel from GitHub releases
# Then install locally
pip install reconmaster-1.0.0-py3-none-any.whl

# Or from file path
pip install ./dist/reconmaster-1.0.0-py3-none-any.whl
```

---

## Verification

### Verify Installation

```bash
# Check if installed
pip show reconmaster

# Output should show:
# Name: reconmaster
# Version: 3.1.0-Pro
# Location: /path/to/site-packages
```

### Check CLI Command

```bash
# ReconMaster should be available as command
reconmaster --help

# If not in PATH, use Python module
python -m reconmaster --help

# On Windows PowerShell
python -m reconmaster --help
```

---

## Dependencies

### Core Dependencies

```
python >= 3.7
requests >= 2.25.1
dnspython >= 2.0
beautifulsoup4 >= 4.9
click >= 8.0
```

### Optional Dependencies

```
# For development
pytest >= 6.0
pytest-cov >= 2.12
flake8 >= 3.9
black >= 21.0
isort >= 5.0
mypy >= 0.910

# For documentation
sphinx >= 4.0
sphinx-rtd-theme >= 1.0

# For security scanning
bandit >= 1.7
safety >= 1.10
```

---

## Usage

### Basic Usage

```bash
# Show help
reconmaster --help

# Scan a domain
reconmaster -d example.com

# Scan with output file
reconmaster -d example.com -o results.json

# Scan with custom wordlist
reconmaster -d example.com -w wordlists/custom.txt

# Run only passive reconnaissance
reconmaster -d example.com --passive-only
```

### Advanced Usage

```bash
# Custom rate limiting
reconmaster -d example.com --rate-limit 5.0

# Custom thread count
reconmaster -d example.com --threads 20

# Combined options
reconmaster -d example.com \
  -o results.json \
  --rate-limit 10.0 \
  --threads 15 \
  --passive-only
```

### Python API Usage

```python
from reconmaster import ReconMaster

# Create scanner instance
scanner = ReconMaster(domain="example.com")

# Run full reconnaissance
results = scanner.run_full_scan()

# Access results
print(f"Found {len(results['subdomains'])} subdomains")
print(f"Found {len(results['ips'])} IPs")

# Run specific tools
subdomains = scanner.run_subdomain_enumeration()
emails = scanner.run_email_enumeration()
```

---

## Configuration

### Using Config File

Create `~/.reconmaster/config.json`:

```json
{
  "rate_limit": 5.0,
  "threads": 10,
  "output_format": "json",
  "passive_only": false,
  "timeout": 30,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
```

Load in Python:

```python
import json
from pathlib import Path
from reconmaster import ReconMaster

config_path = Path.home() / ".reconmaster" / "config.json"
with open(config_path) as f:
    config = json.load(f)

scanner = ReconMaster(domain="example.com", **config)
```

### Environment Variables

```bash
# Set rate limit
export RECONMASTER_RATE_LIMIT=5.0

# Set threads
export RECONMASTER_THREADS=10

# Set output directory
export RECONMASTER_OUTPUT_DIR=~/reconmaster_results

# Python
RECONMASTER_THREADS=10 reconmaster -d example.com
RECON_TARGET=target.com reconmaster
```

### ⚙️ YAML Configuration Support
Create `config.yaml` in your working directory to store persistent settings:
```yaml
scan:
  threads: 20
notifications:
  webhook_url: "your_discord_webhook"
```
ReconMaster will automatically load this on startup. CLI flags will override these settings.

---

## Virtual Environments

### Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Install in virtual environment
pip install reconmaster

# Deactivate
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n reconmaster python=3.9

# Activate
conda activate reconmaster

# Install
pip install reconmaster

# Deactivate
conda deactivate
```

---

## Troubleshooting

### Installation Issues

```bash
# Clear pip cache
pip cache purge

# Reinstall
pip install --force-reinstall reconmaster

# Verbose installation
pip install -v reconmaster

# Show warnings
pip install --verbose reconmaster
```

### Command Not Found

```bash
# Check if installed correctly
pip list | grep reconmaster

# Check pip location
which pip
# or
Get-Command pip  # PowerShell

# Try Python module
python -m reconmaster --help

# Add to PATH (if needed)
export PATH=$PATH:~/.local/bin  # Linux/macOS
# or use full path
~/.local/bin/reconmaster --help
```

### Import Errors

```bash
# Verify installation
python -c "import reconmaster; print(reconmaster.__version__)"

# Check dependencies
pip check

# Reinstall dependencies
pip install --upgrade --force-reinstall reconmaster
```

### Permission Errors

```bash
# Install for current user only
pip install --user reconmaster

# Use sudo (not recommended)
sudo pip install reconmaster

# Better: use virtual environment
python -m venv myenv
source myenv/bin/activate
pip install reconmaster
```

---

## Updating

### Check for Updates

```bash
# Check available versions
pip index versions reconmaster

# Or visit PyPI
# https://pypi.org/project/reconmaster/
```

### Update Installation

```bash
# Update to latest
pip install --upgrade reconmaster

# Update to specific version
pip install reconmaster==1.0.1

# Update with extras
pip install --upgrade "reconmaster[dev]"
```

---

## Uninstallation

```bash
# Remove package
pip uninstall reconmaster

# Remove with dependencies (if no longer needed)
pip uninstall reconmaster dnspython beautifulsoup4

# Remove completely
pip uninstall -y reconmaster
```

---

## Advanced Features

### Installing from GitHub

```bash
# Install latest development version
pip install git+https://github.com/VIPHACKER100/ReconMaster.git

# Install specific branch
pip install git+https://github.com/VIPHACKER100/ReconMaster.git@develop

# Install specific commit
pip install git+https://github.com/VIPHACKER100/ReconMaster.git@abc123
```

### Building from Source

```bash
# Clone repository
git clone https://github.com/VIPHACKER100/ReconMaster.git
cd ReconMaster

# Install build tools
pip install build wheel

# Build distribution
python -m build

# Install built wheel
pip install dist/reconmaster-1.0.0-py3-none-any.whl
```

### Creating Custom Wheel

```bash
# Create wheel for distribution
python setup.py bdist_wheel

# Install custom wheel
pip install dist/reconmaster-1.0.0-py3-none-any.whl
```

---

## System Integration

### Linux/macOS

```bash
# Create alias in ~/.bashrc or ~/.zshrc
alias recon='reconmaster'

# Source the file
source ~/.bashrc

# Now use
recon -d example.com
```

### Windows PowerShell

```powershell
# Create function in $PROFILE
function recon {
    python -m reconmaster @args
}

# Edit profile
notepad $PROFILE

# Add function
function recon {
    python -m reconmaster @args
}
```

---

## Performance Optimization

### Large-Scale Scanning

```bash
# Use high thread count
reconmaster -d example.com --threads 100

# Adjust rate limiting
reconmaster -d example.com --rate-limit 50.0

# Combine options
reconmaster -d example.com --threads 100 --rate-limit 50.0
```

### Memory Usage

```python
# Use generator for large results
from reconmaster import ReconMaster

scanner = ReconMaster(domain="example.com")
for result in scanner.run_subdomain_enumeration():
    print(result)
    # Process one result at a time
```

---

## Maintenance

### Check Dependencies

```bash
# Check all packages
pip list

# Check for updates
pip list --outdated

# Show dependency tree
pip install pipdeptree
pipdeptree -p reconmaster
```

### Clean Up

```bash
# Remove unused packages
pip autoremove

# Clear pip cache
pip cache purge

# Remove Python cache
find . -type d -name __pycache__ -delete
find . -type f -name "*.pyc" -delete
```

---

## Security

### Verify Package

```bash
# Check package integrity
pip install --require-hashes reconmaster

# View package source
pip show -f reconmaster
```

### Secure Installation

```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install reconmaster

# Never use sudo with pip
# Always keep dependencies updated
pip install --upgrade pip setuptools wheel
```

---

## Examples

### Example 1: Quick Setup

```bash
pip install reconmaster
reconmaster -d example.com
```

### Example 2: Development Setup

```bash
git clone https://github.com/VIPHACKER100/ReconMaster.git
cd ReconMaster
pip install -e ".[dev,test]"
pytest tests/
```

### Example 3: Production Setup

```bash
# Create virtual environment
python -m venv /opt/reconmaster
source /opt/reconmaster/bin/activate

# Install package
pip install reconmaster

# Run as service or scheduled task
/opt/reconmaster/bin/reconmaster -d example.com -o results.json
```

### Example 4: CI/CD Integration

```bash
# GitLab CI
image: python:3.9

install:
  - pip install reconmaster

script:
  - reconmaster -d example.com --output results.json
```

### Example 5: Batch Processing

```bash
#!/bin/bash
# Install globally
pip install reconmaster

# Process domains
while read domain; do
  echo "Scanning $domain..."
  reconmaster -d "$domain" -o "results/$domain.json"
done < domains.txt
```

---

## Support

- **Documentation:** See [PHASE_19_GUIDE.md](PHASE_19_GUIDE.md)
- **PyPI:** [reconmaster](https://pypi.org/project/reconmaster/)
- **GitHub:** [ReconMaster](https://github.com/VIPHACKER100/ReconMaster)
- **Issues:** [GitHub Issues](https://github.com/VIPHACKER100/ReconMaster/issues)

---

## Summary

ReconMaster on PyPI provides:
- ✅ Easy installation with `pip install reconmaster`
- ✅ Global CLI access with `reconmaster` command
- ✅ Python API for programmatic use
- ✅ Virtual environment support
- ✅ Development and testing extras
- ✅ Seamless updates

Start using: `pip install reconmaster`

---

**Last Updated:** February 10, 2026  
**Version:** 3.1.0-Pro
