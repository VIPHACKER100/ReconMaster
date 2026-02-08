#!/bin/bash

################################################################################
# ReconMaster Wordlist Upgrade Script
# Version: 3.1.0
# Author: VIPHACKER100
# Description: Download and upgrade wordlists to Pro level
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
WORDLIST_DIR="$PROJECT_DIR/wordlists"

# Create wordlists directory if it doesn't exist
mkdir -p "$WORDLIST_DIR"

echo -e "\n${CYAN}[+] Upgrading ReconMaster Wordlists...${NC}\n"

# Define wordlists to download
# Format: "name|url|destination_filename"
declare -a WORDLISTS=(
    "subdomains_pro.txt|https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt|dns_common.txt"
    "directories_pro.txt|https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-medium-directories.txt|directory-list.txt"
    "php_fuzz.txt|https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/Programming-Language-Specific/PHP.fuzz.txt|php_fuzz.txt"
    "parameters.txt|https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt|params.txt"
    "resolvers.txt|https://raw.githubusercontent.com/trickest/resolvers/main/resolvers.txt|resolvers.txt"
)

# Download wordlists
for wordlist in "${WORDLISTS[@]}"; do
    IFS='|' read -r name url dest <<< "$wordlist"
    target_path="$WORDLIST_DIR/$dest"
    
    echo -e "${BLUE}[*] Downloading $name -> $dest...${NC}"
    
    if curl -fsSL "$url" -o "$target_path"; then
        # Get file size in KB
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            size=$(stat -f%z "$target_path")
        else
            # Linux
            size=$(stat -c%s "$target_path")
        fi
        size_kb=$(echo "scale=2; $size / 1024" | bc)
        
        echo -e "${GREEN}[+] Success! Size: ${size_kb} KB${NC}"
    else
        echo -e "${RED}[-] Failed to download $name${NC}"
    fi
done

# Cleanup old/redundant files
echo -e "\n${BLUE}[*] Cleaning up redundant files...${NC}"

declare -a REDUNDANT_FILES=(
    "subdomains.txt"
    "subdomains_new.txt"
    "directory-list_new.txt"
)

for file in "${REDUNDANT_FILES[@]}"; do
    file_path="$WORDLIST_DIR/$file"
    if [ -f "$file_path" ]; then
        rm -f "$file_path"
        echo -e "${GRAY}[*] Removed redundant file: $file${NC}"
    fi
done

# Summary
echo -e "\n${GREEN}[+] Wordlists upgraded to Pro v3.1 specification.${NC}"
echo -e "${CYAN}[*] Wordlists location: $WORDLIST_DIR${NC}\n"

# List downloaded wordlists
echo -e "${CYAN}Downloaded wordlists:${NC}"
for wordlist in "${WORDLISTS[@]}"; do
    IFS='|' read -r name url dest <<< "$wordlist"
    target_path="$WORDLIST_DIR/$dest"
    
    if [ -f "$target_path" ]; then
        # Get file size
        if [[ "$OSTYPE" == "darwin"* ]]; then
            size=$(stat -f%z "$target_path")
        else
            size=$(stat -c%s "$target_path")
        fi
        size_kb=$(echo "scale=2; $size / 1024" | bc)
        
        # Count lines
        lines=$(wc -l < "$target_path")
        
        echo -e "  ${GREEN}✓${NC} $dest - ${size_kb} KB ($lines lines)"
    else
        echo -e "  ${RED}✗${NC} $dest - Not found"
    fi
done

echo -e "\n${GREEN}Done!${NC}\n"
