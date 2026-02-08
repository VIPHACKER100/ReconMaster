#!/usr/bin/env python3
"""
ReconMaster v3.1.0-Pro - Advanced Asynchronous Reconnaissance Framework
Author: VIPHACKER100
License: MIT
"""

__version__ = "3.1.0"
VERSION = "3.1.0"
PRO_VERSION = "3.1.0-Pro"
AUTHOR = "VIPHACKER100"
GITHUB = "https://github.com/VIPHACKER100/ReconMaster"

import os
import sys
import argparse
import json
import time
import asyncio
import logging
import re
import shutil
import random
import concurrent.futures
import subprocess
from datetime import datetime
from typing import List, Set, Dict, Any, Optional

# Try to import aiohttp, fallback gracefully
try:
    import aiohttp
    _HAVE_AIOHTTP = True
except ImportError:
    aiohttp = None
    _HAVE_AIOHTTP = False

# Global HTTP Configuration (Lazy initialization recommended for connectors)
HTTP_TIMEOUT = aiohttp.ClientTimeout(total=20) if _HAVE_AIOHTTP else None

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
# Integrated with technical versioning

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
    Advanced Asynchronous Reconnaissance Framework v{PRO_VERSION}
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
        
        self.include_list = []
        self.exclude_list = []
        self.resume = False
        self.daily = False
        self.dry_run = False
        self.tool_paths = {}
        
        self.dir_wordlist = os.path.join(base_path, "wordlists", "directory-list.txt")
        self.php_wordlist = os.path.join(base_path, "wordlists", "php_fuzz.txt")
        self.params_wordlist = os.path.join(base_path, "wordlists", "params.txt")
        self.resolvers = os.path.join(base_path, "wordlists", "resolvers.txt")
        
        # Pro features
        self.webhook_url = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        ]
        
        # Add local bin to PATH for the current process
        local_bin = os.path.join(base_path, "bin")
        if os.path.exists(local_bin):
            os.environ["PATH"] = local_bin + os.pathsep + os.environ.get("PATH", "")
            
        # Initialize semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(self.threads)
        self.screenshot_semaphore = asyncio.Semaphore(3) # Limit parallel screenshots
        
        # Persistence & Regression
        self.state_file = os.path.join(output_dir, f"{target}_state.json")
        self.new_findings = {"subdomains": [], "vulns": [], "ports": []}
        
        # Create directory structure
        self._setup_dirs()
        self._load_state()

    def validate_target(self):
        """Strict domain validation"""
        if not re.fullmatch(r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}", self.target):
            raise ValueError(f"Invalid domain format: {self.target}. Please provide a valid FQDN.")

    def verify_tools(self):
        """Verify all required tools are resolved to absolute paths"""
        critical_tools = ["subfinder", "assetfinder", "amass", "ffuf", "httpx", "nuclei", "gowitness", "katana"]
        optional_tools = ["arjun", "nmap", "dnsx"]
        
        missing_critical = []
        for tool in critical_tools:
            path = shutil.which(tool)
            if not path:
                missing_critical.append(tool)
            else:
                self.tool_paths[tool] = os.path.abspath(path)
        
        if missing_critical:
            logger.error(f"Missing CRITICAL tools in PATH: {', '.join(missing_critical)}")
            print(f"{Colors.RED}[!] Error: The following critical tools are missing: {', '.join(missing_critical)}{Colors.ENDC}")
            print(f"{Colors.YELLOW}[*] Please install them or ensure they are in your system PATH/local bin.{Colors.ENDC}")
            sys.exit(1)
            
        for tool in optional_tools:
            path = shutil.which(tool)
            if not path:
                logger.warning(f"Optional tool missing: {tool}")
                print(f"{Colors.YELLOW}[!] Warning: Optional tool '{tool}' not found. Some features will be skipped.{Colors.ENDC}")
            else:
                self.tool_paths[tool] = os.path.abspath(path)

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
        """Execute command asynchronously with robust User-Agent injection policy"""
        ua = random.choice(self.user_agents)
        processed_cmd = list(cmd)
        tool_name = processed_cmd[0].lower()
        
        # Use absolute path if we resolved it earlier
        if tool_name in self.tool_paths:
            processed_cmd[0] = self.tool_paths[tool_name]

        # Consistent UA injection policy
        UA_TOOLS = {"httpx", "ffuf", "katana", "nuclei"}
        if tool_name in UA_TOOLS:
            header_flag = "-H"
            # Prevent duplicate User-Agent injection
            has_ua = any(isinstance(arg, str) and "user-agent" in arg.lower() for arg in processed_cmd)
            if not has_ua:
                processed_cmd.extend([header_flag, f"User-Agent: {ua}"])

        logger.debug(f"Executing command: {' '.join(processed_cmd)}")
        if self.dry_run:
            print(f"{Colors.YELLOW}[DRY-RUN] Would execute: {' '.join(processed_cmd)}{Colors.ENDC}")
            return "", "", 0

        loop = asyncio.get_running_loop()
        async with self.semaphore:
            stdout, stderr, rc = await loop.run_in_executor(
                None, safe_run, processed_cmd, timeout
            )
            return stdout, stderr, rc

    async def _send_notification(self, message: str):
        """Send notification via Discord/Slack Webhook with safety guard"""
        if not self.webhook_url or not _HAVE_AIOHTTP:
            if not _HAVE_AIOHTTP and self.webhook_url:
                logger.warning("aiohttp not available, skipping webhook notification.")
            return
            
        payload = {"content" if "discord.com" in self.webhook_url else "text": f"[ReconMaster] {message}"}
        try:
            headers = {"User-Agent": random.choice(self.user_agents)}
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT, connector=connector, headers=headers) as session:
                async with session.post(self.webhook_url, json=payload) as resp:
                    if resp.status not in [200, 204]:
                        logger.warning(f"Failed to send webhook notification: {resp.status}")
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")

    async def passive_subdomain_enum(self):
        """Discover subdomains via passive sources concurrently"""
        all_passive = os.path.join(self.output_dir, "subdomains", "all_passive.txt")
        if self.resume and os.path.exists(all_passive):
            print(f"{Colors.YELLOW}[*] Resuming: Found existing passive subdomains file. Skipping.{Colors.ENDC}")
            with open(all_passive, "r") as f:
                self.subdomains.update(line.strip() for line in f if line.strip())
            return

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
                # Filter assetfinder output to ensure it matches the target domain
                lines = results[1][0].splitlines()
                filtered = [line.strip() for line in lines if line.strip().endswith(self.target)]
                f.write("\n".join(filtered) + "\n")

        # Merge and dedupe
        all_passive = os.path.join(self.output_dir, "subdomains", "all_passive.txt")
        merge_and_dedupe_text_files(os.path.join(self.output_dir, "subdomains"), "*.txt", all_passive)

        with open(all_passive, "r") as f:
            self.subdomains = set(line.strip() for line in f if line.strip())
        
        print(f"{Colors.GREEN}[+] Passive discovery finished. Found {len(self.subdomains)} unique subdomains.{Colors.ENDC}")

    async def active_subdomain_enum(self):
        """Discover subdomains via brute-forcing using chunks of wordlist"""
        final_subs = os.path.join(self.output_dir, "subdomains", "all_subdomains.txt")
        if self.resume and os.path.exists(final_subs):
            print(f"{Colors.YELLOW}[*] Resuming: Found existing subdomains file. Skipping brute-force.{Colors.ENDC}")
            with open(final_subs, "r") as f:
                self.subdomains.update(line.strip() for line in f if line.strip())
            return

        if not self.wordlist:
            logger.warning("No wordlist found for brute-forcing. Skipping active enumeration.")
            return

        print(f"{Colors.BLUE}[*] Starting active subdomain brute-forcing...{Colors.ENDC}")
        
        ffuf_out = os.path.join(self.output_dir, "subdomains", "ffuf_raw.json")
        
        # Wordlist chunking for efficiency and resolver safety (simple chunking by lines)
        chunk_size = 5000
        with open(self.wordlist, "r") as f:
            lines = f.readlines()
        
        for i in range(0, len(lines), chunk_size):
            chunk = lines[i:i + chunk_size]
            temp_chunk_file = os.path.join(self.output_dir, "subdomains", f"chunk_{i}.txt")
            with open(temp_chunk_file, "w") as tf:
                tf.writelines(chunk)
            
            print(f"{Colors.CYAN}[-Chunk] Fuzzing chunk {i//chunk_size + 1}/{(len(lines)//chunk_size)+1}...{Colors.ENDC}")
            cmd = [
                "ffuf", "-u", f"http://FUZZ.{self.target}", 
                "-w", temp_chunk_file, "-of", "json", "-o", ffuf_out + f"_{i}.json", 
                "-s", "-t", "30", "-rate", "75" # Safer defaults for stability
            ]
            await self._run_command(cmd, timeout=300)
            
            # Parse chunk results
            if os.path.exists(ffuf_out + f"_{i}.json"):
                try:
                    with open(ffuf_out + f"_{i}.json", "r") as f_json:
                        data = json.load(f_json)
                        for result in data.get("results", []):
                            sub = f"{result['input']['FUZZ']}.{self.target}"
                            # Scope Enforcement
                            if self._is_in_scope(sub):
                                self.subdomains.add(sub)
                    os.remove(ffuf_out + f"_{i}.json")
                except Exception as e:
                    logger.error(f"Error parsing ffuf chunk: {e}")
            os.remove(temp_chunk_file)

        # Save all subdomains
        with open(final_subs, "w") as f:
            for sub in sorted(self.subdomains):
                f.write(sub + "\n")
                
        print(f"{Colors.GREEN}[+] Active discovery finished. Total subdomains: {len(self.subdomains)}{Colors.ENDC}")

    def _is_in_scope(self, subdomain: str) -> bool:
        """Check if a subdomain is within the allowed scope"""
        if self.exclude_list:
            for ex in self.exclude_list:
                if ex in subdomain: return False
        if self.include_list:
            for inc in self.include_list:
                if inc in subdomain: return True
            return False
        return subdomain.endswith(self.target)

    async def resolve_live_hosts(self):
        """Identify live web servers and detect technologies using dnsx for pre-validation"""
        if not self.subdomains:
            return

        print(f"{Colors.BLUE}[*] Validating subdomains with dnsx and detecting tech stacks...{Colors.ENDC}")
        
        subs_file = os.path.join(self.output_dir, "subdomains", "all_subdomains.txt")
        live_subs = os.path.join(self.output_dir, "subdomains", "dnsx_live.txt")
        live_file = os.path.join(self.output_dir, "subdomains", "live_hosts.txt")
        
        # Fast DNS validation
        if "dnsx" in self.tool_paths:
            print(f"{Colors.BLUE}[*] Resolving {len(self.subdomains)} subdomains with dnsx...{Colors.ENDC}")
            dns_cmd = [self.tool_paths["dnsx"], "-l", subs_file, "-silent", "-o", live_subs]
            if os.path.exists(self.resolvers):
                dns_cmd.extend(["-r", self.resolvers])
            await self._run_command(dns_cmd, timeout=300)
            target_list = live_subs if os.path.exists(live_subs) and os.path.getsize(live_subs) > 0 else subs_file
        else:
            target_list = subs_file

        cmd = [
            "httpx", "-l", target_list, "-o", live_file, 
            "-json", "-status-code", "-title", "-tech-detect", "-follow-redirects", 
            "-silent", "-threads", str(self.threads)
        ]
        
        await self._run_command(cmd, timeout=600)
        
        if os.path.exists(live_file):
            with open(live_file, "r") as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        entry = json.loads(line)
                        url = entry.get("url")
                        if url:
                            self.live_domains.add(url)
                            self.tech_stack[url] = entry.get("tech", [])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse httpx JSON line: {line.strip()}")

        print(f"{Colors.GREEN}[+] Found {len(self.live_domains)} live web hosts.{Colors.ENDC}")

    async def scan_vulnerabilities(self):
        """Run nuclei for vulnerability detection with tech-profiling"""
        if not self.live_domains:
            return

        print(f"{Colors.BLUE}[*] Scanning for vulnerabilities with Nuclei (Auto-Profiling)...{Colors.ENDC}")
        
        live_file = os.path.join(self.output_dir, "subdomains", "live_hosts.txt")
        vuln_out = os.path.join(self.output_dir, "vulns", "nuclei_results.json")
        
        # Elite Mapping Logic
        NUCLEI_PROFILE = {
            "wordpress": ["wordpress", "wp-plugin"],
            "nginx": ["misconfig", "nginx"],
            "apache": ["misconfig", "apache"],
            "aws": ["cloud", "s3"],
            "azure": ["cloud", "azure"],
            "gcp": ["cloud", "gcp"],
            "jenkins": ["ci", "jenkins"],
            "gitlab": ["ci", "gitlab"],
            "docker": ["ci", "docker"],
            "graphql": ["graphql"],
        }
        
        selected_tags = set(["cve", "exposure", "misconfig", "takeover"])
        techs = set()
        for t_list in self.tech_stack.values():
            for t in t_list:
                t_lower = t.lower()
                techs.add(t_lower)
                for profile_name, tags in NUCLEI_PROFILE.items():
                    if profile_name in t_lower:
                        selected_tags.update(tags)
        
        cmd = [
            "nuclei", "-l", live_file, "-json", "-o", vuln_out, "-silent", 
            "-severity", "low,medium,high,critical", "-tags", ",".join(selected_tags),
            "-rl", "50", "-c", "20"
        ]
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
        cmd_takeover = [
            "nuclei", "-l", live_file, 
            "-tags", "takeover", 
            "-o", takeover_out, 
            "-silent"
        ]
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
        
        async def capture_chunk(chunk, index):
            async with self.screenshot_semaphore:
                temp_list = os.path.join(self.output_dir, f"temp_screenshot_list_{index}.txt")
                with open(temp_list, "w") as f:
                    for url in chunk:
                        f.write(url + "\n")
                
                cmd = ["gowitness", "file", "-f", temp_list, "-P", screenshots_dir, "--no-http", "--timeout", "15"]
                await self._run_command(cmd, timeout=300)
                if os.path.exists(temp_list):
                    os.remove(temp_list)

        tasks = []
        for i in range(0, len(live_list), chunk_size):
            chunk = live_list[i:i + chunk_size]
            tasks.append(capture_chunk(chunk, i))
            
        await asyncio.gather(*tasks)

        print(f"{Colors.GREEN}[+] Screenshot capture finished.{Colors.ENDC}")

    async def crawl_and_extract(self):
        """Crawl endpoints and extract sensitive files/JS with deep analysis"""
        if not self.live_domains:
            return

        print(f"{Colors.BLUE}[*] Deep crawling endpoints with Katana...{Colors.ENDC}")
        
        live_file = os.path.join(self.output_dir, "subdomains", "live_hosts.txt")
        urls_out = os.path.join(self.output_dir, "endpoints", "all_urls.txt")
        
        cmd = [
            "katana", "-list", live_file, "-jc", "-o", urls_out, 
            "-silent", "-concurrency", str(self.threads), "-depth", "3", 
            "-field", "url,path,header,response"
        ]
        await self._run_command(cmd, timeout=1200)
        
        if os.path.exists(urls_out):
            with open(urls_out, "r") as f:
                for line in f:
                    url = line.strip()
                    if not url: continue
                    self.urls.add(url)
                    if ".js" in url.lower().split("?")[0]:
                        self.js_files.add(url)
        
        print(f"{Colors.GREEN}[+] Crawling finished. Extracted {len(self.urls)} URLs and {len(self.js_files)} JS files.{Colors.ENDC}")
        if self.js_files:
            await self.analyze_js_files()

    async def analyze_js_files(self):
        """Deeper parallel analysis of JS files for secrets and endpoints"""
        if not _HAVE_AIOHTTP:
            logger.warning("aiohttp not available, skipping JS analysis.")
            return

        print(f"{Colors.BLUE}[*] Analyzing {len(self.js_files)} JS files for secrets/endpoints (Parallel)...{Colors.ENDC}")
        js_report = os.path.join(self.output_dir, "js", "js_analysis.txt")
        
        max_js = 100 if not self.daily else 30
        if len(self.js_files) > max_js:
            logger.warning(f"JS analysis truncated to first {max_js} files")
        
        regex_list = {
            "google_api": r"AIza[0-9A-Za-z-_]{35}",
            "amazon_aws_key": r"AKIA[0-9A-Z]{16}",
            "github_access_token": r"[a-zA-Z0-9_-]*:[a-zA-Z0-9_\-]+@github\.com",
            "slack_token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
            "mailgun_api_key": r"key-[0-9a-zA-Z]{32}",
            "stripe_api_key": r"sk_live_[0-9a-zA-Z]{24}",
            "endpoint": r"(?:https?://|/)[a-zA-Z0-9.\-_/]+(?:\?[a-zA-Z0-9.\-_=&]+)?"
        }

        # Optimized aiohttp configuration
        headers = {"User-Agent": random.choice(self.user_agents)}
        connector = aiohttp.TCPConnector(ssl=False, limit=self.threads)
        async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT, connector=connector, headers=headers) as session:
            error_count = 0
            async def scan_js(js_url):
                nonlocal error_count
                if error_count > 10: return js_url, [] # Circuit breaker
                try:
                    async with session.get(js_url, timeout=15) as resp:
                        if resp.status in [403, 429]:
                            error_count += 1
                        if resp.status == 200:
                            error_count = 0 # Reset on success
                            content = await resp.text()
                            findings = []
                            for name, pattern in regex_list.items():
                                matches = re.findall(pattern, content)
                                if matches:
                                    matches = list(set(matches))
                                    if name == "endpoint":
                                        # Fixed precedence bug: (len > 5) AND ('.' OR '/')
                                        matches = [m for m in matches if len(m) > 5 and ("." in m or "/" in m)]
                                    
                                    # Scope check for discovered endpoints
                                    if name == "endpoint":
                                        matches = [m for m in matches if self._is_url_in_scope(m)]

                                    if matches:
                                        findings.append((name, matches))
                            return js_url, findings
                except Exception:
                    return js_url, []
                return js_url, []

            # Process in parallel with limit
            js_tasks = [scan_js(url) for url in list(self.js_files)[:max_js]]
            results = await asyncio.gather(*js_tasks)
            
            with open(js_report, "w") as report:
                for url, findings in results:
                    for name, matches in findings:
                        report.write(f"--- {name.upper()} in {url} ---\n")
                        for m in matches[:10]:
                            report.write(f"{m}\n")
                        if findings:
                            logger.info(f"JS Security Finding in {url}: {len(findings)} categories")

    def _is_url_in_scope(self, url: str) -> bool:
        """Check if a full URL or path is within target scope"""
        if url.startswith("/"): return True # Relative paths are always in scope
        domain = url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
        return self._is_in_scope(domain)

    def _load_state(self):
        """Load historical scan state for regression analysis"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    self.previous_state = json.load(f)
            except Exception:
                self.previous_state = {}
        else:
            self.previous_state = {}

    def _save_state(self):
        """Save current scan state for future comparison"""
        state = {
            "subdomains": list(self.subdomains),
            "vulns": [v.get("template-id") for v in self.vulns],
            "timestamp": datetime.now().isoformat()
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def handle_daily_diff(self):
        """Perform regression analysis to identify new attack surface"""
        if not self.previous_state:
            print(f"{Colors.YELLOW}[!] No previous state found. Initializing baseline.{Colors.ENDC}")
            return

        old_subs = set(self.previous_state.get("subdomains", []))
        self.new_findings["subdomains"] = list(self.subdomains - old_subs)
        
        old_vulns = set(self.previous_state.get("vulns", []))
        current_vuln_ids = set(v.get("template-id") for v in self.vulns)
        self.new_findings["vulns"] = list(current_vuln_ids - old_vulns)

        if self.new_findings["subdomains"]:
            print(f"{Colors.RED}[!] REGRESSION ALERT: {len(self.new_findings['subdomains'])} NEW subdomains discovered!{Colors.ENDC}")
            for sub in self.new_findings["subdomains"]:
                print(f"  --> {sub}")

    def _generate_ai_profile(self, vuln: Dict) -> str:
        """AI-based threat profiling and remediation logic"""
        info = vuln.get("info", {})
        name = info.get("name", "Unknown Issue")
        severity = info.get("severity", "unknown").upper()
        
        # Heuristic Intelligence Engine
        if "cve-" in name.lower():
            return f"CRITICAL: Known exploit for {name}. Immediate patching required to prevent RCE."
        if "takeover" in name.lower():
            return "HIGH RISK: Domain points to dead service. An attacker can hijack this to serve malware."
        if "exposure" in name.lower() or "secret" in name.lower():
            return "SENSITIVE LEAK: Internal keys exposed. Rotate credentials immediately and check logs for access."
            
        return f"Policy Violation: {name} detected. Review configuration in line with {severity} severity protocols."

    async def discover_sensitive_files(self):
        """Check for sensitive files (config, backup, etc.) with safety guard"""
        if not _HAVE_AIOHTTP:
            logger.warning("aiohttp not available, skipping sensitive file discovery.")
            return

        print(f"{Colors.BLUE}[*] Discovering sensitive files...{Colors.ENDC}")
        sensitive_paths = [".env", ".git/config", ".vscode/settings.json", "config.php.bak", "web.config", "robots.txt", "sitemap.xml", ".htaccess"]
        results_file = os.path.join(self.output_dir, "vulns", "sensitive_files.txt")
        
        # Explicitly configure sessions and connectors
        connector = aiohttp.TCPConnector(ssl=False, limit=10)
        async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT, connector=connector) as session:
            error_count = 0
            async def check_path(base_url, path):
                nonlocal error_count
                if error_count > 15: return None
                target = f"{base_url.rstrip('/')}/{path}"
                try:
                    async with session.get(target, timeout=5, allow_redirects=False) as resp:
                        if resp.status in [403, 429]:
                            error_count += 1
                        if resp.status == 200:
                            error_count = 0
                            return target
                except Exception:
                    pass
                return None

            tasks = []
            for base_url in list(self.live_domains)[:20]:
                for path in sensitive_paths:
                    tasks.append(check_path(base_url, path))
            
            found = await asyncio.gather(*tasks)
            with open(results_file, "w") as f:
                for target in filter(None, found):
                    print(f"{Colors.YELLOW}[!] Sensitive file exposed: {target}{Colors.ENDC}")
                    f.write(f"[200] {target}\n")
                    self.vulns.append({
                        "info": {"name": "Sensitive File Exposed", "severity": "medium"},
                        "matched-at": target
                    })

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
            if os.path.exists(self.params_wordlist):
                cmd.extend(["-w", self.params_wordlist])
            await self._run_command(cmd, timeout=120)
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
            cmd = ["nmap", "--top-ports", "1000", "-T4", "--open", host, "-oN", out_file]
            await self._run_command(cmd, timeout=300)

        print(f"{Colors.GREEN}[+] Port scan complete.{Colors.ENDC}")

    def _calculate_risk_score(self) -> int:
        """Calculate a weighted risk score (0-100)"""
        score = 0
        if self.takeovers: score += 50 # High impact
        
        # Weighted severity system
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for v in self.vulns:
            sev = v.get('info', {}).get('severity', 'info').lower()
            if sev in severity_counts:
                severity_counts[sev] += 1
        
        score += severity_counts["critical"] * 30
        score += severity_counts["high"] * 15
        score += severity_counts["medium"] * 5
        score += severity_counts["low"] * 1
        
        if severity_counts["medium"] or severity_counts["high"] or severity_counts["critical"]:
            score += 10 # Base penalty for significant findings
            
        return min(score, 100)

    async def load_and_run_plugins(self):
        """Dynamic plugin loader and runner"""
        if self.daily: return # Skip heavy plugins in daily mode
        
        print(f"{Colors.BLUE}[*] Loading and running extensions...{Colors.ENDC}")
        plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
        if not os.path.exists(plugins_dir): return
        
        import importlib.util
        for file in os.listdir(plugins_dir):
            if file.endswith(".py") and file not in ["__init__.py", "base.py"]:
                try:
                    spec = importlib.util.spec_from_file_location(f"plugins.{file[:-3]}", os.path.join(plugins_dir, file))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for obj_name in dir(module):
                        obj = getattr(module, obj_name)
                        if isinstance(obj, type) and obj.__name__ != "ReconPlugin" and "ReconPlugin" in [base.__name__ for base in obj.__bases__]:
                            plugin_instance = obj()
                            logger.info(f"Executing plugin: {plugin_instance.name}")
                            await plugin_instance.run(self)
                except Exception as e:
                    logger.error(f"Failed to load plugin {file}: {e}")

    def handle_daily_diff(self):
        """Compare current state with previous run for daily automation"""
        state_file = os.path.join(os.path.dirname(self.output_dir), f"{self.target}_state.json")
        current_state = {
            "subdomains": list(self.subdomains),
            "vulns": [v.get('info', {}).get('name') for v in self.vulns]
        }
        
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                old_state = json.load(f)
            
            new_subs = set(current_state["subdomains"]) - set(old_state.get("subdomains", []))
            new_vulns = [v for v in self.vulns if v.get('info', {}).get('name') not in old_state.get("vulns", [])]
            
            if new_subs or new_vulns:
                diff_msg = f"🔔 DAILY DIFF for {self.target}:\n"
                if new_subs: diff_msg += f"- Found {len(new_subs)} NEW subdomains!\n"
                if new_vulns: diff_msg += f"- Detected {len(new_vulns)} NEW potential vulnerabilities!\n"
                logger.info(diff_msg)
                asyncio.run(self._send_notification(diff_msg))
        
        with open(state_file, "w") as f:
            json.dump(current_state, f)

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
            "tech_stack": self.tech_stack,
            "risk_score": self._calculate_risk_score()
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
                    f.write("### ⚠️ Key Findings\n")
                    for v in self.vulns[:20]:
                        f.write(f"- **[{v.get('info',{}).get('severity','UNKNOWN')}]** {v.get('info',{}).get('name')} -> {v.get('matched-at')}\n")
                    if len(self.vulns) > 20: f.write(f"\n*... and {len(self.vulns)-20} more findings in JSON report.*\n")

                f.write("\n## 🧠 AI Threat Analysis\n\n")
                if self.vulns:
                    for v in self.vulns[:5]:
                        analysis = self._generate_ai_profile(v)
                        f.write(f"### {v.get('info', {}).get('name')}\n")
                        f.write(f"- **AI Profile**: {analysis}\n")
                        f.write(f"- **Target**: {v.get('matched-at')}\n\n")
                else:
                    f.write("No vulnerabilities to profile.\n\n")

                if self.new_findings.get("subdomains"):
                    f.write("## 🧬 Regression Analysis (New Findings)\n\n")
                    for sub in self.new_findings["subdomains"]:
                        f.write(f"- 🆕 [New Host] {sub}\n")
                    f.write("\n")

            js_findings_path = os.path.join(self.output_dir, "js", "js_analysis.txt")
            if os.path.exists(js_findings_path) and os.path.getsize(js_findings_path) > 0:
                f.write("\n### 📜 JavaScript Secrets & Endpoints\n")
                f.write("Interesting data found in JS files. Check `./js/js_analysis.txt` for full details.\n")

            f.write("\n## 🌐 Infrastructure & Tech Stack\n")
            for url, techs in list(self.tech_stack.items())[:10]:
                f.write(f"- **{url}**: {', '.join(techs)}\n")
            
            f.write(f"\n## � Assessment Summary\n")
            f.write(f"- **Overall Risk Score:** {report_data['risk_score']}/100\n")
            f.write(f"- Full Reports: `{os.path.abspath(self.output_dir)}`\n")
            f.write(f"- Screenshots: `./screenshots/`\n")
            f.write(f"- Endpoints: `./endpoints/all_urls.txt`\n")
            
        self.export_burp_targets()
        self.export_burp_issues()
        self.export_zap_urls()
        
        print(f"{Colors.GREEN}[+] Report generated successfully at: {report_path}{Colors.ENDC}")

    def export_burp_targets(self):
        """Export URLs for Burp Suite Site Map import"""
        out = os.path.join(self.output_dir, "reports", "burp_urls.txt")
        with open(out, "w") as f:
            for url in sorted(self.urls):
                f.write(url + "\n")

    def export_burp_issues(self):
        """Export findings in a format suitable for Burp Issue Importer (with redaction)"""
        out = os.path.join(self.output_dir, "reports", "burp_issues.json")
        def _redact(val):
            val_str = str(val)
            return val_str[:4] + "****" if len(val_str) > 8 else val_str

        issues = []
        for v in self.vulns:
            name = v.get("info", {}).get("name")
            matched = v.get("matched-at")
            issues.append({
                "name": name,
                "severity": v.get("info", {}).get("severity"),
                "confidence": "Firm",
                "host": matched,
                "detail": _redact(json.dumps(v, indent=2)) if "key" in str(name).lower() or "secret" in str(name).lower() else json.dumps(v, indent=2)
            })
        with open(out, "w") as f:
            json.dump(issues, f, indent=2)

    def export_zap_urls(self):
        """Export URLs for OWASP ZAP Import"""
        out = os.path.join(self.output_dir, "reports", "zap_urls.txt")
        context_out = os.path.join(self.output_dir, "reports", "zap_context.context")
        
        with open(out, "w") as f:
            for url in self.urls:
                f.write(url + "\n")
                
        # Simple ZAP Context
        context_xml = f"""<context>
  <name>ReconMaster_{self.target}</name>
  <includeRegex>https?://{re.escape(self.target)}/.*</includeRegex>
</context>"""
        with open(context_out, "w") as f:
            f.write(context_xml)

async def run_recon(recon, args):
    """Orchestrate the recon process"""
    
    start_time = time.time()
    
    # Discovery Phase
    await recon._send_notification(f"🚀 Starting recon on {recon.target}")
    await recon.passive_subdomain_enum()
    if not args.passive_only:
        await recon.active_subdomain_enum()
    
    await recon._send_notification(f"🔍 Discovery finished. Found {len(recon.subdomains)} subdomains.")
    
    # Analysis Phase
    await recon.resolve_live_hosts()
    
    if not args.passive_only and not recon.daily:
        # Full scan phase (can run some tasks concurrently)
        await asyncio.gather(
            recon.scan_vulnerabilities(),
            recon.take_screenshots(),
            recon.crawl_and_extract(),
            recon.discover_sensitive_files()
        )
        # Sequence dependent tasks
        await recon.find_parameters()
        await recon.port_scan()
        await recon.load_and_run_plugins()
    elif recon.daily:
        # Specialized light-weight automation mode
        await recon.scan_vulnerabilities()
        recon.handle_daily_diff()
    else:
        # Minimal analysis for passive-only
        await recon.take_screenshots()
    
    # Post-processing and state management
    recon._save_state()
    recon.generate_report()
    await recon._send_notification(f"✅ Recon complete for {recon.target}. Risk Score: {recon._calculate_risk_score()}/100")
    
    duration = time.time() - start_time
    print(f"\n{Colors.BOLD}{Colors.GREEN}[PRO] ReconMaster finished in {duration:.2f}s.{Colors.ENDC}")

def main():
    print_banner()
    parser = argparse.ArgumentParser(
        description=f"ReconMaster {VERSION} - Pro-Level Security Recon",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-d", "--domain", required=True, help="Target domain to scan")
    parser.add_argument("-v", "--version", action="version", version=f"ReconMaster {VERSION}")
    parser.add_argument("-o", "--output", default="./recon_results", help="Output directory")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Concurrency limit")
    parser.add_argument("-w", "--wordlist", help="Custom wordlist path")
    parser.add_argument("--passive-only", action="store_true", help="Skip active/intrusive scans")
    parser.add_argument("--dry-run", action="store_true", help="Preview commands without executing them")
    parser.add_argument("--webhook", help="Discord/Slack webhook URL for notifications")
    parser.add_argument("--include", help="Comma-separated list of domains/patterns to include")
    parser.add_argument("--exclude", help="Comma-separated list of domains/patterns to exclude")
    parser.add_argument("--resume", action="store_true", help="Resume from existing artifacts")
    parser.add_argument("--daily", action="store_true", help="Enable daily automation mode (light recon + diff)")
    parser.add_argument("--i-understand-this-requires-authorization", action="store_true", 
                        dest="authorized", help="Confirm you have permission to scan the target")

    args = parser.parse_args()
    
    if not args.authorized:
        print(f"{Colors.RED}[!] Error: You must confirm authorization to scan the target.{Colors.ENDC}")
        print(f"{Colors.YELLOW}[*] Use the flag: --i-understand-this-requires-authorization{Colors.ENDC}")
        sys.exit(1)
    
    try:
        recon = ReconMaster(
            target=args.domain,
            output_dir=args.output,
            threads=args.threads,
            wordlist=args.wordlist
        )
        recon.validate_target()
        recon.verify_tools()
        
        # Apply CLI args to recon instance
        if args.include: recon.include_list = [x.strip() for x in args.include.split(",")]
        if args.exclude: recon.exclude_list = [x.strip() for x in args.exclude.split(",")]
        recon.resume = args.resume
        recon.daily = args.daily
        recon.dry_run = getattr(args, 'dry_run', False)
        recon.webhook_url = args.webhook
        
        # Power-Up: Load state and handle regressions after flags are set
        recon._load_state() 
        if recon.daily:
            recon.handle_daily_diff()
        
        asyncio.run(run_recon(recon, args))
        
        # Post-processing state save
        recon._save_state()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Scan aborted by user.{Colors.ENDC}")
    except Exception as e:
        logger.exception(f"Critical error: {e}")

if __name__ == "__main__":
    main()
