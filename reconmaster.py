#!/usr/bin/env python3
"""
ReconMaster v3.0.0 - Advanced Asynchronous Reconnaissance Framework
Author: VIPHACKER100
License: MIT
"""

__version__ = "3.0.0-Pro"
VERSION = "3.0.0-Pro"
AUTHOR = "VIPHACKER100"
GITHUB = "https://github.com/VIPHACKER100/ReconMaster"

import os
import sys
import argparse
import json
import time
import asyncio
import logging
import concurrent.futures
from datetime import datetime
from typing import List, Set, Dict, Any, Optional

# Try to import aiohttp, fallback gracefully
try:
    import aiohttp
    _HAVE_AIOHTTP = True
except ImportError:
    aiohttp = None
    _HAVE_AIOHTTP = False

from utils import safe_run, merge_and_dedupe_text_files, find_wordlist

# Fix encoding for Windows consoles
if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Version Info
VERSION = "3.0.0-Pro"
AUTHOR = "VIPHACKER100"
GITHUB = "https://github.com/VIPHACKER100/ReconMaster"

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ReconMaster")

def print_banner():
    """Display ReconMaster ASCII banner"""
    banner = f"""{Colors.CYAN}{Colors.BOLD}
╦═╗╔═╗╔═╗╔═╗╔╗╔╔╦╗╔═╗╔═╗╔╦╗╔═╗╦═╗
╠╦╝║╣ ║  ║ ║║║║║║║╠═╣╚═╗ ║ ║╣ ╠╦╝
╩╚═╚═╝╚═╝╚═╝╝╚╝╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═
{Colors.ENDC}{Colors.YELLOW}
    Advanced Asynchronous Reconnaissance Framework v{VERSION}
    {Colors.CYAN}Author: {Colors.GREEN}{AUTHOR}
    {Colors.CYAN}GitHub: {Colors.BLUE}{GITHUB}
{Colors.ENDC}
{Colors.RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}
    """
    print(banner)

class ReconMaster:
    def __init__(self, target: str, output_dir: str, threads: int = 10, wordlist: Optional[str] = None):
        self.target = target
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = os.path.join(output_dir, f"{target}_{self.timestamp}")
        self.threads = threads
        self.subdomains: Set[str] = set()
        self.live_domains: Set[str] = set()
        self.urls: Set[str] = set()
        self.js_files: Set[str] = set()
        self.takeovers: List[str] = []
        self.vulns: List[Dict[str, Any]] = []
        self.tech_stack: Dict[str, List[str]] = {}
        self.broken_links: List[str] = []
        
        # Wordlist configuration
        base_path = os.path.dirname(os.path.abspath(__file__))
        default_wordlist = os.path.join(base_path, "wordlists", "dns_common.txt")
        self.wordlist = wordlist if wordlist and os.path.exists(wordlist) else find_wordlist([
            default_wordlist,
            os.path.join(base_path, "wordlists", "subdomains_new.txt"),
            "wordlists/subdomains.txt"
        ])
        
        self.dir_wordlist = os.path.join(base_path, "wordlists", "directory-list.txt")
        
        # Initialize semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(self.threads)
        
        # Create directory structure
        self._setup_dirs()

    def _setup_dirs(self):
        """Create output directory structure"""
        dirs = [
            self.output_dir,
            os.path.join(self.output_dir, "subdomains"),
            os.path.join(self.output_dir, "screenshots"),
            os.path.join(self.output_dir, "endpoints"),
            os.path.join(self.output_dir, "js"),
            os.path.join(self.output_dir, "params"),
            os.path.join(self.output_dir, "vulns"),
            os.path.join(self.output_dir, "reports"),
            os.path.join(self.output_dir, "nmap")
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        logger.info(f"Initialized project structure at {self.output_dir}")

    async def _run_command(self, cmd: List[str], timeout: int = 300) -> tuple:
        """Execute command asynchronously through a thread-pool using safe_run"""
        loop = asyncio.get_running_loop()
        async with self.semaphore:
            stdout, stderr, rc = await loop.run_in_executor(
                None, safe_run, cmd, timeout
            )
            return stdout, stderr, rc

    async def passive_subdomain_enum(self):
        """Discover subdomains via passive sources concurrently"""
        print(f"{Colors.BLUE}[*] Starting passive subdomain enumeration...{Colors.ENDC}")
        
        subfinder_out = os.path.join(self.output_dir, "subdomains", "subfinder.txt")
        assetfinder_out = os.path.join(self.output_dir, "subdomains", "assetfinder.txt")
        amass_out = os.path.join(self.output_dir, "subdomains", "amass.txt")

        tasks = [
            self._run_command(["subfinder", "-d", self.target, "-o", subfinder_out, "-silent"]),
            self._run_command(["assetfinder", "--subs-only", self.target]),
            self._run_command(["amass", "enum", "-passive", "-d", self.target, "-o", amass_out], timeout=600)
        ]

        results = await asyncio.gather(*tasks)
        
        # Write assetfinder output manually as it doesn't have an -o flag for raw output
        if results[1][0]:
            with open(assetfinder_out, "w") as f:
                f.write(results[1][0])

        # Merge and dedupe
        all_passive = os.path.join(self.output_dir, "subdomains", "all_passive.txt")
        merge_and_dedupe_text_files(os.path.join(self.output_dir, "subdomains"), "*.txt", all_passive)

        with open(all_passive, "r") as f:
            self.subdomains = set(line.strip() for line in f if line.strip())
        
        print(f"{Colors.GREEN}[+] Passive discovery finished. Found {len(self.subdomains)} unique subdomains.{Colors.ENDC}")

    async def active_subdomain_enum(self):
        """Discover subdomains via brute-forcing using chunks of wordlist"""
        if not self.wordlist:
            logger.warning("No wordlist found for brute-forcing. Skipping active enumeration.")
            return

        print(f"{Colors.BLUE}[*] Starting active subdomain brute-forcing...{Colors.ENDC}")
        
        ffuf_out = os.path.join(self.output_dir, "subdomains", "ffuf_raw.json")
        # Run ffuf with optimized settings
        cmd = [
            "ffuf", "-u", f"http://FUZZ.{self.target}", 
            "-w", self.wordlist, "-of", "json", "-o", ffuf_out, 
            "-s", "-t", "50", "-rate", "100"
        ]
        
        await self._run_command(cmd, timeout=900)
        
        # Parse ffuf results
        if os.path.exists(ffuf_out):
            try:
                with open(ffuf_out, "r") as f:
                    data = json.load(f)
                    for result in data.get("results", []):
                        sub = f"{result['input']['FUZZ']}.{self.target}"
                        self.subdomains.add(sub)
            except Exception as e:
                logger.error(f"Error parsing ffuf results: {e}")

        # Save all subdomains
        final_subs = os.path.join(self.output_dir, "subdomains", "all_subdomains.txt")
        with open(final_subs, "w") as f:
            for sub in sorted(self.subdomains):
                f.write(sub + "\n")
                
        print(f"{Colors.GREEN}[+] Active discovery finished. Total subdomains: {len(self.subdomains)}{Colors.ENDC}")

    async def resolve_live_hosts(self):
        """Identify live web servers and detect technologies"""
        if not self.subdomains:
            return

        print(f"{Colors.BLUE}[*] Resolving live hosts and detecting tech stacks...{Colors.ENDC}")
        
        subs_file = os.path.join(self.output_dir, "subdomains", "all_subdomains.txt")
        live_file = os.path.join(self.output_dir, "subdomains", "live_hosts.txt")
        
        cmd = [
            "httpx", "-l", subs_file, "-o", live_file, 
            "-status-code", "-title", "-tech-detect", "-follow-redirects", 
            "-silent", "-threads", str(self.threads)
        ]
        
        stdout, _, _ = await self._run_command(cmd, timeout=600)
        
        if os.path.exists(live_file):
            with open(live_file, "r") as f:
                for line in f:
                    if not line.strip(): continue
                    parts = line.split()
                    url = parts[0]
                    self.live_domains.add(url)
                    
                    # Extract tech stack
                    tech_match = re.findall(r'\[(.*?)\]', line)
                    if tech_match:
                        # parts[0] is URL, parts[1] is status code, etc.
                        self.tech_stack[url] = tech_match

        print(f"{Colors.GREEN}[+] Found {len(self.live_domains)} live web hosts.{Colors.ENDC}")

    async def scan_vulnerabilities(self):
        """Run nuclei for vulnerability detection"""
        if not self.live_domains:
            return

        print(f"{Colors.BLUE}[*] Scanning for vulnerabilities with Nuclei...{Colors.ENDC}")
        
        live_file = os.path.join(self.output_dir, "subdomains", "live_hosts.txt")
        vuln_out = os.path.join(self.output_dir, "vulns", "nuclei_results.json")
        
        cmd = ["nuclei", "-l", live_file, "-json", "-o", vuln_out, "-silent", "-severity", "low,medium,high,critical"]
        await self._run_command(cmd, timeout=1200)
        
        if os.path.exists(vuln_out):
            try:
                with open(vuln_out, "r") as f:
                    for line in f:
                        if line.strip():
                            self.vulns.append(json.loads(line))
            except Exception as e:
                logger.error(f"Error parsing nuclei results: {e}")
        
        # Check specifically for takeovers
        takeover_out = os.path.join(self.output_dir, "vulns", "takeovers.txt")
        cmd_takeover = ["nuclei", "-l", live_file, "-t", "takeovers/", "-o", takeover_out, "-silent"]
        await self._run_command(cmd_takeover, timeout=600)
        
        if os.path.exists(takeover_out):
            with open(takeover_out, "r") as f:
                self.takeovers = [line.strip() for line in f if line.strip()]

        print(f"{Colors.GREEN}[+] Vulnerability scan complete. Detected {len(self.vulns)} issues.{Colors.ENDC}")

    async def take_screenshots(self):
        """Capture screenshots of live hosts chunk by chunk"""
        if not self.live_domains:
             return

        print(f"{Colors.BLUE}[*] Capturing screenshots with Gowitness...{Colors.ENDC}")
        
        live_list = list(self.live_domains)
        chunk_size = 20
        screenshots_dir = os.path.join(self.output_dir, "screenshots")
        
        for i in range(0, len(live_list), chunk_size):
            chunk = live_list[i:i + chunk_size]
            temp_list = os.path.join(self.output_dir, f"temp_screenshot_list_{i}.txt")
            with open(temp_list, "w") as f:
                for url in chunk:
                    f.write(url + "\n")
            
            cmd = ["gowitness", "file", "-f", temp_list, "-P", screenshots_dir, "--no-http", "--timeout", "15"]
            await self._run_command(cmd, timeout=300)
            os.remove(temp_list)

        print(f"{Colors.GREEN}[+] Screenshot capture finished.{Colors.ENDC}")

    async def crawl_and_extract(self):
        """Crawl endpoints and extract sensitive files/JS"""
        if not self.live_domains:
            return

        print(f"{Colors.BLUE}[*] Crawling endpoints with Katana...{Colors.ENDC}")
        
        live_file = os.path.join(self.output_dir, "subdomains", "live_hosts.txt")
        urls_out = os.path.join(self.output_dir, "endpoints", "all_urls.txt")
        
        cmd = ["katana", "-list", live_file, "-jc", "-o", urls_out, "-silent", "-concurrency", str(self.threads)]
        await self._run_command(cmd, timeout=900)
        
        if os.path.exists(urls_out):
            with open(urls_out, "r") as f:
                for line in f:
                    url = line.strip()
                    if not url: continue
                    self.urls.add(url)
                    if ".js" in url.lower():
                        self.js_files.add(url)
        
        print(f"{Colors.GREEN}[+] Crawling finished. Extracted {len(self.urls)} URLs and {len(self.js_files)} JS files.{Colors.ENDC}")

    async def find_parameters(self):
        """Passive parameter discovery"""
        if not self.live_domains:
            return

        print(f"{Colors.BLUE}[*] Discovering parameters with Arjun...{Colors.ENDC}")
        
        # Sample interesting URLs (max 10)
        candidates = [u for u in list(self.urls) if "?" in u or "=" in u or "api" in u.lower()][:10]
        if not candidates:
            candidates = list(self.live_domains)[:5]
            
        param_out = os.path.join(self.output_dir, "params", "discovered_params.txt")
        
        for url in candidates:
            cmd = ["arjun", "-u", url, "--passive", "-oT", param_out + "_tmp", "--silent"]
            await self._run_command(cmd, timeout=60)
            if os.path.exists(param_out + "_tmp"):
                with open(param_out + "_tmp", "r") as f_src, open(param_out, "a") as f_dst:
                    f_dst.write(f"--- Params for {url} ---\n")
                    f_dst.write(f_src.read() + "\n")
                os.remove(param_out + "_tmp")

    async def port_scan(self):
        """Fast port scanning using nmap"""
        if not self.live_domains:
            return

        print(f"{Colors.BLUE}[*] Performing Nmap port scan on discoverd targets...{Colors.ENDC}")
        
        # Extract hostnames from live URLs
        hosts = set()
        for url in self.live_domains:
            host = url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
            hosts.add(host)
            
        top_hosts = list(hosts)[:5] # Limit to top 5 for speed in general recon
        
        for host in top_hosts:
            host_safe = host.replace(".", "_")
            out_file = os.path.join(self.output_dir, "nmap", f"{host_safe}.txt")
            cmd = ["nmap", "--top-ports", "100", "-T4", "-F", host, "-oN", out_file]
            await self._run_command(cmd, timeout=300)

        print(f"{Colors.GREEN}[+] Port scan complete.{Colors.ENDC}")

    def generate_report(self):
        """Create a professional Markdown summary report"""
        print(f"{Colors.BLUE}[*] Generating final assessment report...{Colors.ENDC}")
        report_path = os.path.join(self.output_dir, "reports", "RECON_SUMMARY.md")
        json_path = os.path.join(self.output_dir, "reports", "recon_data.json")
        
        report_data = {
            "target": self.target,
            "timestamp": self.timestamp,
            "subdomains_count": len(self.subdomains),
            "live_hosts": list(self.live_domains),
            "vulnerabilities": self.vulns,
            "takeovers": self.takeovers,
            "tech_stack": self.tech_stack
        }
        
        with open(json_path, "w") as f:
            json.dump(report_data, f, indent=4)
            
        with open(report_path, "w") as f:
            f.write(f"# Reconnaissance Summary: {self.target}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Scope:** {len(self.subdomains)} Subdomains | {len(self.live_domains)} Live Hosts\n\n")
            
            f.write("## 🛡️ Vulnerabilities & Findings\n")
            if not self.vulns and not self.takeovers:
                f.write("No critical vulnerabilities discovered during basic scan.\n\n")
            else:
                if self.takeovers:
                    f.write("### 🚨 Subdomain Takeovers\n")
                    for t in self.takeovers: f.write(f"- {t}\n")
                    f.write("\n")
                
                if self.vulns:
                    f.write("### ⚠️ Nuclei Findings (Low-Critical)\n")
                    for v in self.vulns[:20]:
                        f.write(f"- **[{v.get('info',{}).get('severity','UNKNOWN')}]** {v.get('info',{}).get('name')} -> {v.get('matched-at')}\n")
                    if len(self.vulns) > 20: f.write(f"\n*... and {len(self.vulns)-20} more findings in JSON report.*\n")

            f.write("\n## 🌐 Infrastructure & Tech Stack\n")
            for url, techs in list(self.tech_stack.items())[:10]:
                f.write(f"- **{url}**: {', '.join(techs)}\n")
            
            f.write(f"\n## 📂 Artifacts\n")
            f.write(f"- Full Reports: `{os.path.abspath(self.output_dir)}`\n")
            f.write(f"- Screenshots: `./screenshots/`\n")
            f.write(f"- Endpoints: `./endpoints/all_urls.txt`\n")
            
        print(f"{Colors.GREEN}[+] Report generated successfully at: {report_path}{Colors.ENDC}")

async def run_recon(args):
    """Orchestrate the recon process"""
    recon = ReconMaster(
        target=args.domain,
        output_dir=args.output,
        threads=args.threads,
        wordlist=args.wordlist
    )
    
    start_time = time.time()
    
    # Discovery Phase
    await recon.passive_subdomain_enum()
    if not args.passive_only:
        await recon.active_subdomain_enum()
    
    # Analysis Phase
    await recon.resolve_live_hosts()
    
    if not args.passive_only:
        # Full scan phase (can run some tasks concurrently)
        await asyncio.gather(
            recon.scan_vulnerabilities(),
            recon.take_screenshots(),
            recon.crawl_and_extract()
        )
        # Sequence dependent tasks
        await recon.find_parameters()
        await recon.port_scan()
    else:
        # Minimal analysis for passive-only
        await recon.take_screenshots()
    
    # Reporting
    recon.generate_report()
    
    duration = time.time() - start_time
    print(f"\n{Colors.BOLD}{Colors.GREEN}[PRO] ReconMaster finished in {duration:.2f}s.{Colors.ENDC}")

def main():
    print_banner()
    parser = argparse.ArgumentParser(
        description=f"ReconMaster {VERSION} - Pro-Level Security Recon",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-d", "--domain", required=True, help="Target domain to scan")
    parser.add_argument("-o", "--output", default="./recon_results", help="Output directory")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Concurrency limit")
    parser.add_argument("-w", "--wordlist", help="Custom wordlist path")
    parser.add_argument("--passive-only", action="store_true", help="Skip active/intrusive scans")

    args = parser.parse_args()
    
    try:
        asyncio.run(run_recon(args))
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Scan aborted by user.{Colors.ENDC}")
    except Exception as e:
        logger.exception(f"Critical error: {e}")

if __name__ == "__main__":
    main()
