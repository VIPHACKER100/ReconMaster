#!/bin/bash

# ReconMaster v3.1-Pro Installation Script
# Automated setup for professional reconnaissance infrastructure

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}[*]${NC} $1"; }
print_success() { echo -e "${GREEN}[+]${NC} $1"; }
print_error() { echo -e "${RED}[!]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

command_exists() { command -v "$1" >/dev/null 2>&1; }

# Welcome banner
echo -e "${CYAN}${BOLD}"
echo "╦═╗╔═╗╔═╗╔═╗╔╗╔╔╦╗╔═╗╔═╗╔╦╗╔═╗╦═╗"
echo "╠╦╝║╣ ║  ║ ║║║║║║║╠═╣╚═╗ ║ ║╣ ╠╦╝"
echo "╩╚═╚═╝╚═╝╚═╝╝╚╝╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═"
echo -e "${NC}${YELLOW} Professional Installer for v3.1.0-Pro${NC}\n"

if [ "$EUID" -ne 0 ]; then
    print_error "This installer requires root privileges for system dependencies. Please run with sudo."
    exit 1
fi

REPO_DIR=$(pwd)
print_status "Installing ReconMaster from $REPO_DIR"

# 1. System Dependencies
print_status "Updating system and installing base dependencies..."
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv git wget curl build-essential libpcap-dev chromium-browser unzip nmap jq

# 2. Go Installation
if ! command_exists go; then
    print_status "Go not found. Installing latest stable Go..."
    GO_VER="1.22.0"
    wget -q "https://go.dev/dl/go${GO_VER}.linux-amd64.tar.gz" -O /tmp/go.tar.gz
    rm -rf /usr/local/go && tar -C /usr/local -xzf /tmp/go.tar.gz
    export PATH=$PATH:/usr/local/go/bin
    echo 'export PATH=$PATH:/usr/local/go/bin' > /etc/profile.d/reconmaster_go.sh
    print_success "Go ${GO_VER} installed."
else
    print_success "Using existing Go: $(go version)"
fi

# Ensure Go bin is in path for the current session
export PATH=$PATH:$HOME/go/bin

# 3. Python Environment
if [ -f "requirements.txt" ]; then
    print_status "Installing Python dependencies from requirements.txt..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    print_warning "requirements.txt not found. Installing base libraries manually..."
    pip3 install aiohttp requests tqdm colorama PyYAML schedule
fi

# 4. Recon Tools (Go-based)
print_status "Installing/Updating professional recon tools via Go..."

GO_TOOLS=(
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder"
    "github.com/projectdiscovery/httpx/cmd/httpx"
    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei"
    "github.com/projectdiscovery/dnsx/cmd/dnsx"
    "github.com/projectdiscovery/katana/cmd/katana"
    "github.com/ffuf/ffuf"
    "github.com/sensepost/gowitness"
    "github.com/tomnomnom/assetfinder"
    "github.com/owasp-amass/amass/v4/..."
    "github.com/lc/subjs"
    "github.com/PentestPad/subzy"
)

for tool in "${GO_TOOLS[@]}"; do
    NAME=$(echo $tool | rev | cut -d'/' -f1 | rev)
    print_status "Installing $NAME..."
    go install "$tool@latest" > /dev/null 2>&1
done

# 5. Specialized Tools
print_status "Setting up specialized tools..."

# Arjun (Parameter Discovery)
if ! command_exists arjun; then
    print_status "Installing Arjun..."
    pip3 install arjun
fi

# 6. Housekeeping & PATH
print_status "Finalizing setup..."

# Ensure the local bin exists for the repo
mkdir -p "$REPO_DIR/bin"

# Link Go binaries to local bin for portability
for bin in subfinder httpx nuclei dnsx katana ffuf gowitness assetfinder amass subjs subzy; do
    if [ -f "$HOME/go/bin/$bin" ]; then
        ln -sf "$HOME/go/bin/$bin" "$REPO_DIR/bin/$bin"
    fi
done

# Create global symlink for ReconMaster
chmod +x "$REPO_DIR/reconmaster.py"
ln -sf "$REPO_DIR/reconmaster.py" /usr/local/bin/reconmaster

print_success "All tools installed and linked to $REPO_DIR/bin."

# 7. Wordlists (Optional Download)
if [ ! -f "wordlists/dns_common.txt" ]; then
    print_status "Downloading baseline wordlists..."
    mkdir -p wordlists
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt -O wordlists/dns_common.txt
fi

echo -e "\n${GREEN}======================================================="
echo "      ReconMaster v3.1-Pro Setup Completed!"
echo "======================================================="
echo -e "${NC}"
echo -e "You can now run: ${BOLD}reconmaster -d example.com${NC}"
echo -e "Tools are also available locally in: ${BLUE}$REPO_DIR/bin/${NC}"
echo ""
echo "Note: If Go tools are not found in your current shell, run:"
echo "source /etc/profile.d/reconmaster_go.sh"
echo ""
echo "Happy Hunting!"
