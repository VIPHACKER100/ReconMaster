#!/bin/bash

################################################################################
# ReconMaster Tool Installation Script
# Version: 3.1.0
# Author: VIPHACKER100
# Description: Automated installation of all required reconnaissance tools
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
cat << "EOF"
╦═╗╔═╗╔═╗╔═╗╔╗╔╔╦╗╔═╗╔═╗╔╦╗╔═╗╦═╗
╠╦╝║╣ ║  ║ ║║║║║║║╠═╣╚═╗ ║ ║╣ ╠╦╝
╩╚═╚═╝╚═╝╚═╝╝╚╝╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═
    Tool Installation Script v3.1.0
EOF
echo -e "${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}Warning: Running as root. This is not recommended.${NC}"
   read -p "Continue anyway? (y/n) " -n 1 -r
   echo
   if [[ ! $REPLY =~ ^[Yy]$ ]]; then
       exit 1
   fi
fi

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo -e "${GREEN}✓ Detected OS: Linux${NC}"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "${GREEN}✓ Detected OS: macOS${NC}"
else
    echo -e "${RED}✗ Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

# Check for required dependencies
echo -e "\n${BLUE}[*] Checking dependencies...${NC}"

check_dependency() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓ $1 is installed${NC}"
        return 0
    else
        echo -e "${YELLOW}✗ $1 is not installed${NC}"
        return 1
    fi
}

# Install Go if not present
if ! check_dependency go; then
    echo -e "${BLUE}[*] Installing Go...${NC}"
    if [[ "$OS" == "linux" ]]; then
        wget -q https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
        sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
        rm go1.21.5.linux-amd64.tar.gz
        export PATH=$PATH:/usr/local/go/bin
        echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    elif [[ "$OS" == "macos" ]]; then
        brew install go
    fi
    echo -e "${GREEN}✓ Go installed${NC}"
fi

# Set up Go environment
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
mkdir -p $GOPATH/bin

# Install Python dependencies
if check_dependency python3; then
    echo -e "${BLUE}[*] Installing Python dependencies...${NC}"
    pip3 install -r requirements.txt
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
fi

# Install reconnaissance tools
echo -e "\n${BLUE}[*] Installing reconnaissance tools...${NC}"

install_go_tool() {
    local tool_name=$1
    local tool_path=$2
    
    echo -e "${BLUE}[*] Installing $tool_name...${NC}"
    if go install -v $tool_path@latest; then
        echo -e "${GREEN}✓ $tool_name installed${NC}"
    else
        echo -e "${RED}✗ Failed to install $tool_name${NC}"
        return 1
    fi
}

# ProjectDiscovery Tools
install_go_tool "Subfinder" "github.com/projectdiscovery/subfinder/v2/cmd/subfinder"
install_go_tool "HTTPx" "github.com/projectdiscovery/httpx/cmd/httpx"
install_go_tool "Nuclei" "github.com/projectdiscovery/nuclei/v3/cmd/nuclei"
install_go_tool "Katana" "github.com/projectdiscovery/katana/cmd/katana"
install_go_tool "DNSX" "github.com/projectdiscovery/dnsx/cmd/dnsx"
install_go_tool "Naabu" "github.com/projectdiscovery/naabu/v2/cmd/naabu"

# TomNomNom Tools
install_go_tool "Assetfinder" "github.com/tomnomnom/assetfinder"
install_go_tool "Waybackurls" "github.com/tomnomnom/waybackurls"
install_go_tool "Gf" "github.com/tomnomnom/gf"

# Other Tools
install_go_tool "Amass" "github.com/owasp-amass/amass/v4/...@master"
install_go_tool "GoWitness" "github.com/sensepost/gowitness"
install_go_tool "Hakrawler" "github.com/hakluke/hakrawler"

# Update Nuclei templates
echo -e "\n${BLUE}[*] Updating Nuclei templates...${NC}"
if nuclei -update-templates &> /dev/null; then
    echo -e "${GREEN}✓ Nuclei templates updated${NC}"
else
    echo -e "${YELLOW}⚠ Failed to update Nuclei templates${NC}"
fi

# Install system tools (optional)
echo -e "\n${BLUE}[*] Installing system tools...${NC}"

if [[ "$OS" == "linux" ]]; then
    if command -v apt-get &> /dev/null; then
        echo -e "${BLUE}[*] Installing via apt-get...${NC}"
        sudo apt-get update -qq
        sudo apt-get install -y -qq nmap jq git curl wget
    elif command -v yum &> /dev/null; then
        echo -e "${BLUE}[*] Installing via yum...${NC}"
        sudo yum install -y nmap jq git curl wget
    fi
elif [[ "$OS" == "macos" ]]; then
    if command -v brew &> /dev/null; then
        echo -e "${BLUE}[*] Installing via Homebrew...${NC}"
        brew install nmap jq git curl wget
    else
        echo -e "${YELLOW}⚠ Homebrew not found. Please install manually.${NC}"
    fi
fi

# Verify installations
echo -e "\n${BLUE}[*] Verifying installations...${NC}"

TOOLS=(
    "subfinder"
    "assetfinder"
    "amass"
    "httpx"
    "nuclei"
    "katana"
    "dnsx"
    "gowitness"
    "nmap"
    "jq"
)

FAILED_TOOLS=()

for tool in "${TOOLS[@]}"; do
    if command -v $tool &> /dev/null; then
        VERSION=$(command $tool -version 2>&1 | head -n1 || echo "unknown")
        echo -e "${GREEN}✓ $tool - $VERSION${NC}"
    else
        echo -e "${RED}✗ $tool - NOT FOUND${NC}"
        FAILED_TOOLS+=($tool)
    fi
done

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}        Installation Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

if [ ${#FAILED_TOOLS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All tools installed successfully!${NC}"
    echo -e "\n${GREEN}ReconMaster is ready to use!${NC}"
    echo -e "\nRun: ${YELLOW}python3 reconmaster.py -d example.com --i-understand-this-requires-authorization${NC}"
else
    echo -e "${YELLOW}⚠ Some tools failed to install:${NC}"
    for tool in "${FAILED_TOOLS[@]}"; do
        echo -e "  ${RED}✗ $tool${NC}"
    done
    echo -e "\n${YELLOW}Please install missing tools manually.${NC}"
fi

# Add tools to PATH permanently
echo -e "\n${BLUE}[*] Adding tools to PATH...${NC}"
if ! grep -q "export PATH=\$PATH:\$GOPATH/bin" ~/.bashrc; then
    echo 'export GOPATH=$HOME/go' >> ~/.bashrc
    echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
    echo -e "${GREEN}✓ Added to ~/.bashrc${NC}"
fi

if [[ "$OS" == "macos" ]] && [ -f ~/.zshrc ]; then
    if ! grep -q "export PATH=\$PATH:\$GOPATH/bin" ~/.zshrc; then
        echo 'export GOPATH=$HOME/go' >> ~/.zshrc
        echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.zshrc
        echo -e "${GREEN}✓ Added to ~/.zshrc${NC}"
    fi
fi

echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}Note: You may need to restart your terminal or run 'source ~/.bashrc'${NC}"
