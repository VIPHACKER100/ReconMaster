#!/usr/bin/env python3
"""
ReconMaster v3.1.0-Pro - Advanced Asynchronous Reconnaissance Framework
Author: VIPHACKER100 ( Aryan Ahirwar )
License: MIT
"""

__version__ = "3.1.0"
VERSION = "3.1.0"
PRO_VERSION = "3.1.0-Pro"
AUTHOR = "VIPHACKER100 ( Aryan Ahirwar )"
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
from pathlib import Path
from typing import List, Set, Dict, Any, Optional, Tuple, Union

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

class CircuitBreaker:
    """Unified circuit breaker for all HTTP operations to prevent rate limiting and saturation"""
    def __init__(self, threshold: int = 10, timeout: int = 60):
        self.error_count = 0
        self.threshold = threshold
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.open_time = 0.0
        self.timeout = timeout
        self.lock = asyncio.Lock()
    
    async def record_error(self, status_code: int):
        """Record failed request and potentially open the circuit"""
        async with self.lock:
            if status_code in [403, 429, 503]:
                self.error_count += 1
                logger.warning(f"Circuit breaker alert: {self.error_count}/{self.threshold} errors recorded.")
                
                if self.error_count >= self.threshold and self.state == "CLOSED":
                    self.state = "OPEN"
                    self.open_time = time.time()
                    logger.error(f"🚫 CIRCUIT BREAKER OPENED - Rate limiting detected. Cooling down for {self.timeout}s.")
                
    async def record_success(self):
        """Record successful request and recovery"""
        async with self.lock:
            if self.error_count > 0:
                self.error_count = max(0, self.error_count - 1)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                logger.info("✅ Circuit breaker CLOSED - System recovered.")
    
    async def check_can_proceed(self) -> bool:
        """Check if requests can proceed based on current state"""
        async with self.lock:
            if self.state == "CLOSED":
                return True
            
            if self.state == "OPEN":
                elapsed = time.time() - self.open_time
                if elapsed > self.timeout:
                    self.state = "HALF_OPEN"
                    logger.info("🔌 Circuit breaker Entering HALF_OPEN - testing connectivity.")
                    return True
                return False
            
            # HALF_OPEN - allow requests but monitor closely
            return True

class SensitiveFilter(logging.Filter):
    """Filter sensitive data (keys, tokens, passwords) from all log outputs"""
    PATTERNS = [
        (r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_GOOGLE_API_KEY]'),
        (r'AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]'),
        (r'ghp_[A-Za-z0-9]{36}', '[REDACTED_GITHUB_TOKEN]'),
        (r'xox[baprs]-[0-9a-zA-Z]{10,48}', '[REDACTED_SLACK_TOKEN]'),
        (r'sk_live_[0-9a-zA-Z]{24}', '[REDACTED_STRIPE_KEY]'),
        (r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)', 'password=[REDACTED]'),
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})', 'api_key=[REDACTED]'),
        (r'Xq9FjcfL', '[REDACTED_CENSYS_ID]'),
        (r'wf256DDVZSsJHUtpSAs3pX-yQsKWACSM', '[REDACTED_SECURITYTRAILS_KEY]'),
        (r'4305df5d2d95222bca49a37e7298208e85fb7c5afe8d1ae1ff6f6f241733fb98', '[REDACTED_VIRUSTOTAL_KEY]'),
    ]
    
    def filter(self, record):
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            for pattern, replacement in self.PATTERNS:
                msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
            record.msg = msg
        return True

# Fix encoding for Windows consoles
if sys.platform == "win32":
    import io
    try:
        import colorama
        colorama.init()
    except ImportError:
        pass
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
    # --- Configuration Constants ---
    MAX_JS_FILES = 100
    MAX_JS_FILES_DAILY = 30
    MAX_SENSITIVE_PATHS = 100
    CHUNK_SIZE_FFUF = 5000
    SCREENSHOT_CHUNK_SIZE = 20
    MAX_FILE_SIZE_MB = 5
    CIRCUIT_BREAKER_THRESHOLD = 10
    CIRCUIT_BREAKER_COOLDOWN = 60

    def __init__(self, target: str, output_dir: str, threads: int = 10, wordlist: Optional[str] = None):
        self.target = target
        self.validate_target() # Sanitize and validate before path creation
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_dir = os.path.join(output_dir, f"{self.target}_{self.timestamp}")
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
        self.api_wordlist = os.path.join(base_path, "wordlists", "api_endpoints.txt")
        self.common_wordlist = os.path.join(base_path, "wordlists", "common.txt")
        self.quickhits_wordlist = os.path.join(base_path, "wordlists", "quickhits.txt")

        # Pro features
        self.webhook_url = None
        self.censys_id = os.getenv('CENSYS_API_ID') or 'Xq9FjcfL'
        self.censys_secret = os.getenv('CENSYS_API_SECRET') or '5oQsVfKogh3DeuwM63gCMjQr'
        self.sectrails_key = os.getenv('SECURITYTRAILS_API_KEY') or 'wf256DDVZSsJHUtpSAs3pX-yQsKWACSM'
        self.vt_key = os.getenv('VIRUSTOTAL_API_KEY') or '4305df5d2d95222bca49a37e7298208e85fb7c5afe8d1ae1ff6f6f241733fb98'
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        ]

        # Add local bin and tools to PATH for the current process
        local_bin = os.path.join(base_path, "bin")
        local_tools = os.path.join(base_path, "tools")
        paths_to_add = [p for p in [local_bin, local_tools] if os.path.exists(p)]
        if paths_to_add:
            os.environ["PATH"] = os.pathsep.join(paths_to_add) + os.pathsep + os.environ.get("PATH", "")

        # Initialize semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(self.threads)
        self.screenshot_semaphore = asyncio.Semaphore(3)  # Limit parallel screenshots
        self.circuit_breaker = CircuitBreaker(threshold=self.CIRCUIT_BREAKER_THRESHOLD, timeout=self.CIRCUIT_BREAKER_COOLDOWN)

        # Persistence & Regression
        self.state_file = os.path.join(output_dir, f"{self.target}_state.json")
        self.new_findings = {"subdomains": [], "vulns": [], "ports": []}

        # Create directory structure
        self._setup_dirs()
        self._load_state()
        self.load_config()

    def load_config(self, config_file: Optional[str] = None):
        """Load configuration from YAML file and apply to current instance"""
        if not config_file:
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        
        if not os.path.exists(config_file):
            return
            
        try:
            # Lazy import yaml to avoid strict dependency
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config: return

            # Apply scan settings
            scan_cfg = config.get('scan', {})
            self.threads = scan_cfg.get('threads', self.threads)
            
            # Apply notification settings
            notif_cfg = config.get('notifications', {})
            if not self.webhook_url: # CLI takes precedence
                self.webhook_url = notif_cfg.get('webhook_url')
                
            logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}")

        # Configure file logging
        self._setup_logging()

    def _sanitize_header_value(self, value: str) -> str:
        """Sanitize header values to prevent multi-line or shell injection in potential log/shell scenarios"""
        dangerous = [';', '&', '|', '$', '`', '(', ')', '<', '>', '\n', '\r', '"', "'"]
        sanitized = value
        for char in dangerous:
            sanitized = sanitized.replace(char, '')
        return sanitized

    def _safe_path(self, directory_key: str, filename: str) -> str:
        """Safely construct file path and strictly prevent path traversal"""
        if directory_key not in self.dirs:
            raise ValueError(f"Invalid directory key: {directory_key}")
            
        base_dir = Path(self.dirs[directory_key]).resolve()
        # Sanitize filename to prevent basic directory navigation
        clean_filename = os.path.basename(filename)
        target_path = (base_dir / clean_filename).resolve()
        
        # Ensure target is strictly within the intended base directory
        if not str(target_path).startswith(str(base_dir)):
            logger.error(f"🛑 Path Traversal Violation Attempt: {filename} against {directory_key}")
            raise ValueError(f"Security Violation: Path traversal detected for {filename}")
        
        return str(target_path)

    def _setup_logging(self):
        """Configure file handlers for the logger"""
        log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        
        # Apply Sensitive Filter to all handlers
        sensitive_filter = SensitiveFilter()

        # Scan Log (INFO)
        scan_handler = logging.FileHandler(self.files["scan_log"])
        scan_handler.setLevel(logging.INFO)
        scan_handler.setFormatter(log_format)
        scan_handler.addFilter(sensitive_filter)
        logger.addHandler(scan_handler)
        
        # Debug Log (DEBUG)
        debug_handler = logging.FileHandler(self.files["debug_log"])
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(log_format)
        debug_handler.addFilter(sensitive_filter)
        logger.addHandler(debug_handler)
        
        # Errors Log (ERROR)
        error_handler = logging.FileHandler(self.files["errors_log"])
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(log_format)
        error_handler.addFilter(sensitive_filter)
        logger.addHandler(error_handler)

    def validate_target(self):
        """Enhanced domain validation with strict RFC and security checks"""
        # Sanitize input: strip whitespace and trailing dots
        self.target = self.target.strip().rstrip('.')
        
        # Strip protocol if present (e.g., https://example.com -> example.com)
        if "://" in self.target:
            self.target = self.target.split("://")[-1]
            
        # Strip trailing path if present (e.g., example.com/test -> example.com)
        self.target = self.target.split("/")[0]

        # Final strip for any stray whitespace
        self.target = self.target.strip()
        
        # Check for empty or invalid input
        if not self.target or self.target in ['.', '..', '']:
            raise ValueError("Invalid domain format: Target cannot be empty.")
            
        # RFC 1035: Check length constraints
        if len(self.target) > 253:
            raise ValueError(f"Domain too long: {len(self.target)} characters (max 253)")
            
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z0-9.-]+$', self.target):
            raise ValueError(f"Invalid characters in domain: {self.target}")
            
        # Validate FQDN format
        if not re.fullmatch(r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}", self.target):
            raise ValueError(f"Invalid domain format: '{self.target}'. Please provide a valid FQDN (e.g., example.com).")

        # Security: Prevent scanning of private infrastructure
        private_patterns = [
            r'^localhost', r'^127\.', r'^192\.168\.', r'^10\.', 
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.', r'.*\.local$', r'.*\.internal$'
        ]
        for pattern in private_patterns:
            if re.match(pattern, self.target, re.IGNORECASE):
                logger.error(f"🛑 Security Block: Attempted scan of private/localhost target: {self.target}")
                raise ValueError(f"Security Restriction: Cannot scan localhost or private infrastructure: {self.target}")

        logger.info(f"✅ Target validated: {self.target}")

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
            logger.error(f"Missing CRITICAL tools: {', '.join(missing_critical)}")
            print(f"\n{Colors.RED}╔══════════════════════════════════════════════════╗")
            print(f"║  ⚠️  MISSING CRITICAL TOOLS                     ║")
            print(f"╚══════════════════════════════════════════════════╝{Colors.ENDC}\n")
            
            print(f"{Colors.YELLOW}The following tools are required but not found in your PATH:{Colors.ENDC}")
            for tool in missing_critical:
                print(f"  ❌ {tool}")
            
            print(f"\n{Colors.CYAN}Installation Instructions:{Colors.ENDC}")
            print(f"  Run the installer: './install_reconmaster.sh' (Linux/macOS)")
            print(f"  Or: 'powershell -File install_tools_final.ps1' (Windows)")
            print(f"  Alternatively, install via go: 'go install github.com/projectdiscovery/{{tool}}@latest'\n")
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
        self.dirs = {
            "base": self.output_dir,
            "subdomains": os.path.join(self.output_dir, "subdomains"),
            "http": os.path.join(self.output_dir, "http"),
            "vulns": os.path.join(self.output_dir, "vulns"),
            "endpoints": os.path.join(self.output_dir, "endpoints"),
            "js": os.path.join(self.output_dir, "js"),
            "js_analysis": os.path.join(self.output_dir, "js", "analysis"),
            "screenshots": os.path.join(self.output_dir, "screenshots"),
            "exports": os.path.join(self.output_dir, "exports"),
            "logs": os.path.join(self.output_dir, "logs"),
            "nmap": os.path.join(self.output_dir, "nmap") # Legacy support
        }

        for d in self.dirs.values():
            os.makedirs(d, exist_ok=True)

        # Map logical file keys to paths
        self.files = {
            "summary": os.path.join(self.dirs["base"], "summary.json"),
            "executive_report": os.path.join(self.dirs["base"], "executive_report.md"),
            "full_report": os.path.join(self.dirs["base"], "full_report.html"),

            "all_subdomains": os.path.join(self.dirs["subdomains"], "all_subdomains.txt"),
            "live_subdomains": os.path.join(self.dirs["subdomains"], "live_subdomains.txt"),
            "subfinder": os.path.join(self.dirs["subdomains"], "subfinder.txt"),
            "assetfinder": os.path.join(self.dirs["subdomains"], "assetfinder.txt"),
            "amass": os.path.join(self.dirs["subdomains"], "amass.txt"),
            "dns_records": os.path.join(self.dirs["subdomains"], "dns_records.json"),

            "alive": os.path.join(self.dirs["http"], "alive.txt"),
            "httpx_full": os.path.join(self.dirs["http"], "httpx_full.json"),
            "technologies": os.path.join(self.dirs["http"], "technologies.json"),
            "certificates": os.path.join(self.dirs["http"], "certificates.json"),

            "nuclei_results": os.path.join(self.dirs["vulns"], "nuclei_results.json"),
            "vuln_critical": os.path.join(self.dirs["vulns"], "critical.txt"),
            "vuln_high": os.path.join(self.dirs["vulns"], "high.txt"),
            "vuln_medium": os.path.join(self.dirs["vulns"], "medium.txt"),
            "vuln_low": os.path.join(self.dirs["vulns"], "low.txt"),
            "exposed_secrets": os.path.join(self.dirs["vulns"], "exposed_secrets.txt"),

            "all_urls": os.path.join(self.dirs["endpoints"], "all_urls.txt"),
            "parameters": os.path.join(self.dirs["endpoints"], "parameters.txt"),
            "api_endpoints": os.path.join(self.dirs["endpoints"], "api_endpoints.txt"),
            "admin_panels": os.path.join(self.dirs["endpoints"], "admin_panels.txt"),
            "crawl_tree": os.path.join(self.dirs["endpoints"], "crawl_tree.json"),

            "javascript_files": os.path.join(self.dirs["js"], "javascript_files.txt"),
            "js_secrets": os.path.join(self.dirs["js"], "secrets.txt"),
            "js_endpoints": os.path.join(self.dirs["js"], "endpoints.txt"),

            "burp_sitemap": os.path.join(self.dirs["exports"], "burp_sitemap.xml"),
            "zap_context": os.path.join(self.dirs["exports"], "zap_context.xml"),
            "nuclei_sarif": os.path.join(self.dirs["exports"], "nuclei_sarif.json"),

            "scan_log": os.path.join(self.dirs["logs"], "scan.log"),
            "errors_log": os.path.join(self.dirs["logs"], "errors.log"),
            "debug_log": os.path.join(self.dirs["logs"], "debug.log")
        }
        logger.info(f"Initialized project structure at {self.output_dir}")

    async def _run_command(self, cmd: List[str], timeout: int = 300) -> Tuple[str, str, int]:
        """Execute command asynchronously with robust security and timeout policy"""
        raw_ua = random.choice(self.user_agents)
        ua = self._sanitize_header_value(raw_ua)
        processed_cmd = list(cmd)
        tool_name = processed_cmd[0].lower()

        # Use absolute path if we resolved it earlier
        if tool_name in self.tool_paths:
            processed_cmd[0] = self.tool_paths[tool_name]

        # Consistent UA injection policy
        UA_TOOLS = {"httpx", "ffuf", "katana", "nuclei", "subfinder", "amass"}
        if tool_name in UA_TOOLS:
            header_flag = "-H"
            # Prevent duplicate User-Agent injection
            has_ua = any(isinstance(arg, str) and "user-agent" in arg.lower() for arg in processed_cmd)
            if not has_ua:
                processed_cmd.extend([header_flag, f"User-Agent: {ua}"])

        # Inject API keys for discovery tools
        env = os.environ.copy()
        if self.censys_id and self.censys_secret:
            # Inject for subfinder (via env is one way, but flags are clearer for debugging)
            # Actually, subfinder uses a config file, but many tools respect these env vars:
            env["CENSYS_API_ID"] = self.censys_id
            env["CENSYS_API_SECRET"] = self.censys_secret
            
            # For Amass, it often looks for specific env names or config
            env["AMASS_CENSYS_API_ID"] = self.censys_id 
            env["AMASS_CENSYS_API_SECRET"] = self.censys_secret
            
        if self.sectrails_key:
            env["SECURITYTRAILS_API_KEY"] = self.sectrails_key
            env["AMASS_SECURITYTRAILS_API_KEY"] = self.sectrails_key
            
        if self.vt_key:
            env["VIRUSTOTAL_API_KEY"] = self.vt_key
            env["AMASS_VIRUSTOTAL_API_KEY"] = self.vt_key
            
        logger.debug(f"Executing command: {' '.join(processed_cmd)}")

        if self.dry_run:
            print(f"{Colors.YELLOW}[DRY-RUN] Would execute: {' '.join(processed_cmd)}{Colors.ENDC}")
            return "", "", 0

        try:
            # Add top-level async timeout for safety
            async with asyncio.timeout(timeout + 5):
                loop = asyncio.get_running_loop()
                async with self.semaphore:
                    stdout, stderr, rc = await loop.run_in_executor(
                        None, safe_run, processed_cmd, timeout, env
                    )
            return stdout, stderr, rc
        except asyncio.TimeoutError:
            logger.error(f"Command timed out after {timeout}s: {tool_name}")
            return "", "Execution Timeout", -1
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return "", str(e), -1

    async def _send_notification(self, message: str, severity: str = "info"):
        """Send notification via Discord/Slack Webhook with severity handling"""
        if not self.webhook_url or not _HAVE_AIOHTTP:
            if not _HAVE_AIOHTTP and self.webhook_url:
                logger.warning("aiohttp not available, skipping webhook notification.")
            return

        # Severity Colors for Discord (decimal)
        colors = {
            "critical": 15158332,  # Red
            "warning": 16776960,   # Yellow
            "info": 3447003,       # Blue
            "success": 3066993     # Green
        }
        color = colors.get(severity, colors["info"])

        if "discord.com" in self.webhook_url:
            payload = {
                "embeds": [{
                    "title": "🛰️ ReconMaster Alert",
                    "description": message,
                    "color": color,
                    "fields": [
                        {"name": "Target", "value": self.target, "inline": True},
                        {"name": "Severity", "value": severity.upper(), "inline": True}
                    ],
                    "footer": {"text": f"ReconMaster {PRO_VERSION}"},
                    "timestamp": datetime.now().isoformat()
                }]
            }
        else:
            payload = {"text": f"[{severity.upper()}] [ReconMaster] {message}"}

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
        all_passive = os.path.join(self.dirs["subdomains"], "all_passive.txt")
        if self.resume and os.path.exists(all_passive):
            print(f"{Colors.YELLOW}[*] Resuming: Found existing passive subdomains file. Skipping.{Colors.ENDC}")
            with open(all_passive, "r") as f:
                self.subdomains.update(line.strip() for line in f if line.strip())
            return

        print(f"{Colors.BLUE}[*] Starting passive subdomain enumeration...{Colors.ENDC}")

        completed = 0
        total_tasks = 3
        
        async def run_with_tracking(coro, name):
            nonlocal completed
            res = await coro
            completed += 1
            progress = (completed / total_tasks) * 100
            print(f"{Colors.CYAN}[{progress:.0f}%] Completed passive task: {name}{Colors.ENDC}")
            return res

        # Dynamic task list based on available keys
        tasks = []
        tasks.append(run_with_tracking(self._run_command(["subfinder", "-d", self.target, "-o", self.files["subfinder"], "-silent"]), "Subfinder"))
        tasks.append(run_with_tracking(self._run_command(["assetfinder", "--subs-only", self.target]), "Assetfinder"))
        
        amass_cmd = ["amass", "enum", "-passive", "-d", self.target, "-o", self.files["amass"]]
        tasks.append(run_with_tracking(self._run_command(amass_cmd, timeout=600), "Amass"))

        total_tasks = len(tasks)

        results = await asyncio.gather(*tasks)

        # Write assetfinder output manually as it doesn't have an -o flag for raw output
        if results[1][0]:
            with open(self.files["assetfinder"], "w") as f:
                # Filter assetfinder output to ensure it matches the target domain
                lines = results[1][0].splitlines()
                filtered = [line.strip() for line in lines if line.strip().endswith(self.target)]
                f.write("\n".join(filtered) + "\n")

        # Merge and dedupe
        merge_and_dedupe_text_files(self.dirs["subdomains"], "*.txt", all_passive)
        with open(all_passive, "r") as f:
            self.subdomains = set(line.strip() for line in f if line.strip())

        print(f"{Colors.GREEN}[+] Passive discovery finished. Found {len(self.subdomains)} unique subdomains.{Colors.ENDC}")

    async def active_subdomain_enum(self):
        """Discover subdomains via brute-forcing using chunks of wordlist"""
        if self.resume and os.path.exists(self.files["all_subdomains"]):
            print(f"{Colors.YELLOW}[*] Resuming: Found existing subdomains file. Skipping brute-force.{Colors.ENDC}")
            with open(self.files["all_subdomains"], "r") as f:
                self.subdomains.update(line.strip() for line in f if line.strip())
            return

        if not self.wordlist:
            logger.warning("No wordlist found for brute-forcing. Skipping active enumeration.")
            return

        print(f"{Colors.BLUE}[*] Starting active subdomain brute-forcing...{Colors.ENDC}")

        ffuf_out = os.path.join(self.dirs["subdomains"], "ffuf_raw.json")

        # Wordlist chunking for efficiency and resolver safety (simple chunking by lines)
        chunk_size = self.CHUNK_SIZE_FFUF
        with open(self.wordlist, "r") as f:
            lines = f.readlines()

        temp_files_to_clean = []
        
        async def process_chunk(index, chunk_lines):
            temp_chunk_file = os.path.join(self.dirs["subdomains"], f"chunk_{index}.txt")
            ffuf_raw = ffuf_out + f"_{index}.json"
            
            temp_files_to_clean.extend([temp_chunk_file, ffuf_raw])
            try:
                with open(temp_chunk_file, "w") as tf:
                    tf.writelines(chunk_lines)

                print(f"{Colors.CYAN}[-Chunk] Fuzzing chunk {index//chunk_size + 1}/{(len(lines)//chunk_size)+1}...{Colors.ENDC}")

                cmd = [
                    "ffuf",
                    "-u", f"http://FUZZ.{self.target}",
                    "-w", temp_chunk_file,
                    "-of", "json",
                    "-o", ffuf_raw,
                    "-s",
                    "-t", "30",
                    "-rate", "75"
                ]
                await self._run_command(cmd, timeout=300)

                # Parse chunk results
                if os.path.exists(ffuf_raw):
                    try:
                        with open(ffuf_raw, "r") as f_json:
                            data = json.load(f_json)
                            for result in data.get("results", []):
                                sub = f"{result['input']['FUZZ']}.{self.target}"
                                if self._is_in_scope(sub):
                                    self.subdomains.add(sub)
                    except Exception as e:
                        logger.error(f"Error parsing ffuf chunk {index}: {e}")
            except Exception as e:
                logger.error(f"Failed to process chunk {index}: {e}")

        try:
            tasks = []
            for i in range(0, len(lines), chunk_size):
                tasks.append(process_chunk(i, lines[i:i + chunk_size]))
            
            await asyncio.gather(*tasks)
        finally:
            # CRITICAL: Comprehensive Resource Cleanup
            for f_path in temp_files_to_clean:
                try:
                    if os.path.exists(f_path):
                        os.remove(f_path)
                except Exception as e:
                    logger.warning(f"Cleanup failure for {f_path}: {e}")

        # Save all subdomains
        with open(self.files["all_subdomains"], "w", encoding="utf-8") as f:
            for sub in sorted(self.subdomains):
                f.write(sub + "\n")

        print(f"{Colors.GREEN}[+] Active discovery finished. Total subdomains: {len(self.subdomains)}{Colors.ENDC}")

    def _is_in_scope(self, subdomain: str) -> bool:
        """Check if a subdomain is within the allowed scope"""
        if self.exclude_list:
            for ex in self.exclude_list:
                if ex in subdomain:
                    return False

        if self.include_list:
            for inc in self.include_list:
                if inc in subdomain:
                    return True
            return False

        return subdomain.endswith(self.target)

    async def resolve_live_hosts(self):
        """Identify live web servers and detect technologies using dnsx for pre-validation"""
        if not self.subdomains:
            return

        print(f"{Colors.BLUE}[*] Validating subdomains with dnsx and detecting tech stacks...{Colors.ENDC}")

        if not os.path.exists(self.files["all_subdomains"]):
            # In passive-only mode, the file might not exist yet. Create it.
            with open(self.files["all_subdomains"], "w") as f:
                for sub in sorted(self.subdomains):
                    f.write(sub + "\n")

        # Fast DNS validation
        if "dnsx" in self.tool_paths:
            print(f"{Colors.BLUE}[*] Resolving {len(self.subdomains)} subdomains with dnsx...{Colors.ENDC}")
            dns_cmd = [self.tool_paths["dnsx"], "-l", self.files["all_subdomains"], "-silent", "-o", self.files["live_subdomains"], "-json", "-oe", self.files["dns_records"]]
            if os.path.exists(self.resolvers):
                dns_cmd.extend(["-r", self.resolvers])
            await self._run_command(dns_cmd, timeout=300)
            target_list = self.files["live_subdomains"] if os.path.exists(self.files["live_subdomains"]) and os.path.getsize(self.files["live_subdomains"]) > 0 else self.files["all_subdomains"]
        else:
            target_list = self.files["all_subdomains"]

        cmd = [
            "httpx",
            "-l", target_list,
            "-o", self.files["alive"],
            "-json",
            "-oJ", self.files["httpx_full"],
            "-status-code",
            "-title",
            "-tech-detect",
            "-follow-redirects",
            "-tls-probe",
            "-csp-probe",
            "-silent",
            "-threads", str(self.threads)
        ]
        await self._run_command(cmd, timeout=600)

        certificates = []
        if os.path.exists(self.files["httpx_full"]):
            with open(self.files["httpx_full"], "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        url = entry.get("url")
                        if url:
                            self.live_domains.add(url)
                            self.tech_stack[url] = entry.get("tech", [])
                            
                            # Extract TLS info
                            tls = entry.get("tls-grab")
                            if tls:
                                certificates.append({
                                    "url": url,
                                    "certificate": tls
                                })
                    except Exception:
                        continue

        if certificates:
            with open(self.files["certificates"], "w") as f:
                json.dump(certificates, f, indent=4)
        
        if self.tech_stack:
            with open(self.files["technologies"], "w") as f:
                json.dump(self.tech_stack, f, indent=4)

        print(f"{Colors.GREEN}[+] Found {len(self.live_domains)} live web hosts.{Colors.ENDC}")

    async def scan_vulnerabilities(self):
        """Run nuclei for vulnerability detection with tech-profiling"""
        if not self.live_domains:
            return

        print(f"{Colors.BLUE}[*] Scanning for vulnerabilities with Nuclei (Auto-Profiling)...{Colors.ENDC}")

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
            "nuclei",
            "-l", self.files["alive"],
            "-json",
            "-o", self.files["nuclei_results"],
            "-as", "-silent", # Added -as for sarif export later
            "-severity", "low,medium,high,critical",
            "-tags", ",".join(selected_tags),
            "-rl", "50",
            "-c", "20"
        ]
        await self._run_command(cmd, timeout=1200)

        # Export SARIF
        await self._run_command(["nuclei", "-l", self.files["alive"], "-tags", ",".join(selected_tags), "-severity", "low,medium,high,critical", "-sarif", "-o", self.files["nuclei_sarif"], "-silent"])

        if os.path.exists(self.files["nuclei_results"]):
            severities = {"critical": [], "high": [], "medium": [], "low": [], "info": []}
            try:
                with open(self.files["nuclei_results"], "r") as f:
                    for line in f:
                        if line.strip():
                            v = json.loads(line)
                            self.vulns.append(v)
                            sev = v.get("info", {}).get("severity", "info").lower()
                            if sev in severities:
                                severities[sev].append(f"[{v.get('info', {}).get('name')}] {v.get('matched-at')}")
                
                # Write severity files
                for sev, items in severities.items():
                    if items:
                        file_key = f"vuln_{sev}"
                        if file_key in self.files:
                            with open(self.files[file_key], "w") as sf:
                                sf.write("\n".join(items) + "\n")
            except Exception as e:
                logger.error(f"Error parsing nuclei results: {e}")

        # Check specifically for takeovers
        takeover_out = os.path.join(self.dirs["vulns"], "takeovers.txt")
        cmd_takeover = [
            "nuclei",
            "-l", self.files["alive"],
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
        screenshots_dir = self.dirs["screenshots"]

        async def capture_chunk(chunk, index):
            async with self.screenshot_semaphore:
                temp_list = os.path.join(self.dirs["base"], f"temp_screenshot_list_{index}.txt")
                try:
                    with open(temp_list, "w") as f:
                        for url in chunk:
                            f.write(url + "\n")

                    cmd = ["gowitness", "file", "-f", temp_list, "-P", screenshots_dir, "--no-http", "--timeout", "15"]
                    await self._run_command(cmd, timeout=300)
                finally:
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

        cmd = [
            "katana",
            "-list", self.files["alive"],
            "-jc",
            "-o", self.files["all_urls"],
            "-jsonl", "-oJ", self.files["crawl_tree"],
            "-silent",
            "-concurrency", str(self.threads),
            "-depth", "3",
            "-field", "url,path,header,response"
        ]
        await self._run_command(cmd, timeout=1200)

        if os.path.exists(self.files["all_urls"]):
            admin_panels = []
            with open(self.files["all_urls"], "r") as f:
                for line in f:
                    url = line.strip()
                    if not url:
                        continue
                    self.urls.add(url)
                    
                    # Identify JS files
                    if ".js" in url.lower().split("?")[0]:
                        self.js_files.add(url)
                    
                    # Identify admin panels
                    admin_keywords = ["admin", "login", "wp-admin", "dashboard", "control", "panel", "auth"]
                    if any(kw in url.lower() for kw in admin_keywords) and not url.endswith((".js", ".css", ".png", ".jpg")):
                        admin_panels.append(url)

            if admin_panels:
                with open(self.files["admin_panels"], "w") as f:
                    for panel in sorted(set(admin_panels)):
                        f.write(panel + "\n")

        # Save JS files separately
        if self.js_files:
            with open(self.files["javascript_files"], "w") as f:
                for js in sorted(self.js_files):
                    f.write(js + "\n")

        print(f"{Colors.GREEN}[+] Crawling finished. Extracted {len(self.urls)} URLs and {len(self.js_files)} JS files.{Colors.ENDC}")

        if self.js_files:
            await self.analyze_js_files()

    async def analyze_js_files(self):
        """Deeper parallel analysis of JS files for secrets and endpoints"""
        if not _HAVE_AIOHTTP:
            logger.warning("aiohttp not available, skipping JS analysis.")
            return

        print(f"{Colors.BLUE}[*] Analyzing {len(self.js_files)} JS files for secrets/endpoints (Parallel)...{Colors.ENDC}")

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
            
            async def scan_js(js_url):
                if not await self.circuit_breaker.check_can_proceed():
                    logger.warning(f"Circuit breaker OPEN/COOLDOWN - skipping JS request: {js_url}")
                    return js_url, []

                try:
                    async with session.get(js_url, timeout=15) as resp:
                        if resp.status in [403, 429, 503]:
                            await self.circuit_breaker.record_error(resp.status)
                            return js_url, []
                        
                        if resp.status == 200:
                            await self.circuit_breaker.record_success()
                            
                            # MEMORY OPTIMIZATION & PROTECTION
                            content_length = resp.headers.get('Content-Length')
                            if content_length and int(content_length) > self.MAX_FILE_SIZE_MB * 1024 * 1024:
                                logger.warning(f"Skipping large JS file ({content_length} bytes): {js_url}")
                                return js_url, []
                                
                            content = await resp.text()
                            if len(content) > self.MAX_FILE_SIZE_MB * 1024 * 1024:
                                logger.warning(f"Truncating massive JS response: {js_url}")
                                content = content[:self.MAX_FILE_SIZE_MB * 1024 * 1024]

                            findings = []
                            for name, pattern in regex_list.items():
                                matches = re.findall(pattern, content)
                                if matches:
                                    matches = list(set(matches))
                                    if name == "endpoint":
                                        # Better endpoint filtering: avoid single chars/slashes
                                        matches = [m for m in matches 
                                                   if len(m) > 5 
                                                   and ("." in m or (m.count("/") > 1))
                                                   and m not in ["/", "//"]]
                                        # Scope check for discovered endpoints
                                        matches = [m for m in matches if self._is_url_in_scope(m)]
                                    if matches:
                                        findings.append((name, matches))
                            
                            # Save per-file analysis with security
                            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', js_url.split('/')[-1])[:50]
                            analysis_path = self._safe_path("js_analysis", f"{safe_name}_analysis.json")
                            with open(analysis_path, "w") as f:
                                json.dump({"url": js_url, "findings": findings}, f, indent=4)
                                
                            return js_url, findings
                except Exception as e:
                    logger.debug(f"JS scan failed for {js_url}: {e}")
                    return js_url, []
                return js_url, []

            # Process in parallel with limit
            js_tasks = [scan_js(url) for url in list(self.js_files)[:max_js]]
            results = await asyncio.gather(*js_tasks)

            all_secrets = []
            all_endpoints = []
            
            with open(self.files["js_secrets"], "w") as secret_f, open(self.files["js_endpoints"], "w") as end_f:
                for url, findings in results:
                    for name, matches in findings:
                        if name == "endpoint":
                            for m in matches:
                                end_f.write(f"{m} (from {url})\n")
                        else:
                            for m in matches:
                                secret_f.write(f"[{name}] {m} (from {url})\n")
                                all_secrets.append(m)

            if all_secrets:
                with open(self.files["exposed_secrets"], "a") as f:
                    for s in all_secrets:
                        f.write(f"[JS Secret] {s}\n")

    def _is_url_in_scope(self, url: str) -> bool:
        """Check if a full URL or path is within target scope"""
        if url.startswith("/"):
            return True  # Relative paths are always in scope
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

        # Also log key events
        log_file = self.files["scan_log"]
        with open(log_file, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] Completed scan for {self.target}. Found {len(self.subdomains)} subdomains and {len(self.vulns)} vulns.\n")

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
        
        # Load from Pro wordlists if available
        for wl in [self.quickhits_wordlist, self.common_wordlist]:
            if os.path.exists(wl):
                try:
                    with open(wl, "r") as f:
                        for line in f:
                            p = line.strip()
                            if p and p not in sensitive_paths:
                                sensitive_paths.append(p)
                except Exception as e:
                    logger.warning(f"Failed to load wordlist {wl}: {e}")

        # Deduplicate and limit for safety
        sensitive_paths = list(dict.fromkeys(sensitive_paths))[:self.MAX_SENSITIVE_PATHS]
        
        # Explicitly configure sessions and connectors
        connector = aiohttp.TCPConnector(ssl=False, limit=10)
        async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT, connector=connector) as session:

            async def check_path(base_url, path):
                if not await self.circuit_breaker.check_can_proceed():
                    return None
                    
                target = f"{base_url.rstrip('/')}/{path}"
                try:
                    async with session.get(target, timeout=5, allow_redirects=False) as resp:
                        if resp.status in [403, 429, 503]:
                            await self.circuit_breaker.record_error(resp.status)
                        if resp.status == 200:
                            await self.circuit_breaker.record_success()
                            return target
                except Exception:
                    pass
                return None

            tasks = []
            for base_url in list(self.live_domains)[:20]:
                for path in sensitive_paths:
                    tasks.append(check_path(base_url, path))

            found = await asyncio.gather(*tasks)

            with open(self.files["exposed_secrets"], "a") as f:
                for target in filter(None, found):
                    print(f"{Colors.YELLOW}[!] Sensitive file exposed: {target}{Colors.ENDC}")
                    f.write(f"[200] Sensitive File Exposed: {target}\n")
                    self.vulns.append({
                        "info": {"name": "Sensitive File Exposed", "severity": "medium"},
                        "matched-at": target
                    })

    async def fuzz_api_endpoints(self):
        """Discover hidden API endpoints using specialized pro wordlist"""
        if not _HAVE_AIOHTTP:
            logger.warning("aiohttp not available, skipping API endpoint fuzzing.")
            return

        if not self.live_domains or not os.path.exists(self.api_wordlist):
            return

        print(f"{Colors.BLUE}[*] Fuzzing for hidden API endpoints...{Colors.ENDC}")
        
        # Load API endpoints
        api_paths = []
        try:
            with open(self.api_wordlist, "r") as f:
                api_paths = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error reading API wordlist: {e}")
            return

        connector = aiohttp.TCPConnector(ssl=False, limit=self.threads)
        async with aiohttp.ClientSession(timeout=HTTP_TIMEOUT, connector=connector) as session:
            async def check_api(base_url, path):
                if not await self.circuit_breaker.check_can_proceed():
                    return None
                    
                target = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
                try:
                    async with session.get(target, timeout=5) as resp:
                        if resp.status in [403, 429, 503]:
                            await self.circuit_breaker.record_error(resp.status)
                            
                        if resp.status in [200, 201, 401, 403]: # Interested in access or restricted
                            if resp.status == 200:
                                await self.circuit_breaker.record_success()
                            return target, resp.status
                except Exception:
                    pass
                return None

            tasks = []
            for base_url in list(self.live_domains)[:10]: # Limit targets for performance
                for path in api_paths[:50]: # First 50 for quick check
                    tasks.append(check_api(base_url, path))

            found = await asyncio.gather(*tasks)
            
            with open(self.files["api_endpoints"], "w") as f:
                for res in filter(None, found):
                    target, status = res
                    f.write(f"[{status}] {target}\n")
                    if status == 200:
                        print(f"{Colors.CYAN}[+] Discovered API Endpoint: {target}{Colors.ENDC}")

    async def find_parameters(self):
        """Passive parameter discovery"""
        if not self.live_domains:
            return

        print(f"{Colors.BLUE}[*] Discovering parameters with Arjun...{Colors.ENDC}")

        # Sample interesting URLs (max 10)
        candidates = [u for u in list(self.urls) if "?" in u or "=" in u or "api" in u.lower()][:10]
        if not candidates:
            candidates = list(self.live_domains)[:5]

        for url in candidates:
            cmd = ["arjun", "-u", url, "--passive", "-oT", self.files["parameters"] + "_tmp", "--silent"]
            if os.path.exists(self.params_wordlist):
                cmd.extend(["-w", self.params_wordlist])
            await self._run_command(cmd, timeout=120)

            if os.path.exists(self.files["parameters"] + "_tmp"):
                with open(self.files["parameters"] + "_tmp", "r") as f_src, open(self.files["parameters"], "a") as f_dst:
                    f_dst.write(f"--- Params for {url} ---\n")
                    f_dst.write(f_src.read() + "\n")
                os.remove(self.files["parameters"] + "_tmp")

    async def port_scan(self):
        """Fast port scanning using nmap"""
        if not self.live_domains:
            return

        print(f"{Colors.BLUE}[*] Performing Nmap port scan on discovered targets...{Colors.ENDC}")

        # Extract hostnames from live URLs
        hosts = set()
        for url in self.live_domains:
            host = url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
            hosts.add(host)

        top_hosts = list(hosts)[:5]  # Limit to top 5 for speed in general recon

        for host in top_hosts:
            host_safe = host.replace(".", "_")
            out_file = os.path.join(self.dirs["nmap"], f"{host_safe}.txt")
            cmd = ["nmap", "--top-ports", "1000", "-T4", "--open", host, "-oN", out_file]
            await self._run_command(cmd, timeout=300)

        print(f"{Colors.GREEN}[+] Port scan complete.{Colors.ENDC}")

    def _calculate_risk_score(self) -> int:
        """Calculate a weighted risk score (0-100)"""
        score = 0

        if self.takeovers:
            score += 50  # High impact

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
            score += 10  # Base penalty for significant findings

        return min(score, 100)

    async def load_and_run_plugins(self):
        """Dynamic plugin loader and runner"""
        if self.daily:
            return  # Skip heavy plugins in daily mode

        print(f"{Colors.BLUE}[*] Loading and running extensions...{Colors.ENDC}")
        plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
        if not os.path.exists(plugins_dir):
            return

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

    def generate_report(self):
        """Create professional reports (JSON, Markdown, HTML)"""
        print(f"{Colors.BLUE}[*] Generating final assessment reports...{Colors.ENDC}")

        # 📊 summary.json
        start_dt = datetime.strptime(self.timestamp, "%Y-%m-%d_%H-%M-%S")
        end_dt = datetime.now()
        duration = str(end_dt - start_dt)

        summary_data = {
            "scan_info": {
                "target": self.target,
                "start_time": self.timestamp,
                "end_time": end_dt.strftime("%Y-%m-%d_%H-%M-%S"),
                "duration": duration,
                "version": PRO_VERSION
            },
            "statistics": {
                "subdomains_found": len(self.subdomains),
                "live_hosts": len(self.live_domains),
                "vulnerabilities": len(self.vulns),
                "endpoints_discovered": len(self.urls),
                "js_files_analyzed": len(self.js_files)
            },
            "findings": {
                "critical": len([v for v in self.vulns if v.get("info", {}).get("severity") == "critical"]),
                "high": len([v for v in self.vulns if v.get("info", {}).get("severity") == "high"]),
                "medium": len([v for v in self.vulns if v.get("info", {}).get("severity") == "medium"]),
                "low": len([v for v in self.vulns if v.get("info", {}).get("severity") == "low"]),
                "info": len([v for v in self.vulns if v.get("info", {}).get("severity") == "info"])
            }
        }
        with open(self.files["summary"], "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=4)

        # 📝 executive_report.md
        with open(self.files["executive_report"], "w", encoding="utf-8") as f:
            f.write(f"# Reconnaissance Executive Report: {self.target}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Scope:** {len(self.subdomains)} Subdomains | {len(self.live_domains)} Live Hosts\n\n")
            f.write(f"**Overall Risk Score:** {self._calculate_risk_score()}/100\n\n")

            f.write("## 🛡️ Vulnerabilities & Findings\n")
            if not self.vulns and not self.takeovers:
                f.write("No critical vulnerabilities discovered.\n\n")
            else:
                if self.takeovers:
                    f.write("### 🚨 Subdomain Takeovers\n")
                    for t in self.takeovers:
                        f.write(f"- {t}\n")
                    f.write("\n")

                if self.vulns:
                    f.write("### ⚠️ Key Findings\n")
                    for v in self.vulns[:20]:
                        info = v.get('info', {}) or {}
                        severity = str(info.get('severity', 'UNKNOWN')).upper()
                        name = info.get('name', 'Unknown Finding')
                        matched = v.get('matched-at', 'N/A')
                        f.write(f"- **[{severity}]** {name} -> {matched}\n")

            f.write("\n## 🧠 AI Threat Analysis\n\n")
            if self.vulns:
                for v in self.vulns[:5]:
                    analysis = self._generate_ai_profile(v)
                    f.write(f"### {v.get('info', {}).get('name')}\n")
                    f.write(f"- **AI Profile**: {analysis}\n")
                    f.write(f"- **Target**: {v.get('matched-at')}\n\n")

            if self.new_findings.get("subdomains"):
                f.write("## 🧬 Regression Analysis (New Findings)\n\n")
                for sub in self.new_findings["subdomains"]:
                    f.write(f"- 🆕 [New Host] {sub}\n")
                f.write("\n")

            f.write("\n## 🌐 Infrastructure & Tech Stack\n")
            for url, techs in list(self.tech_stack.items())[:10]:
                f.write(f"- **{url}**: {', '.join(techs)}\n")

            f.write(f"\n## 📊 Data Mapping\n")
            f.write(f"- Full Reports: `{os.path.abspath(self.output_dir)}`\n")
            f.write(f"- Subdomains: `./subdomains/all_subdomains.txt`\n")
            f.write(f"- Screenshots: `./screenshots/`\n")
            f.write(f"- Endpoints: `./endpoints/all_urls.txt`\n")

        # 🌐 full_report.html (Basic Interactive)
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReconMaster Report - {self.target}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px; text-align: center; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: center; transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-5px); border-color: #38bdf8; }}
        .card h3 {{ margin: 0; color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; }}
        .card .value {{ font-size: 2rem; font-weight: bold; color: #38bdf8; margin: 10px 0; }}
        .findings {{ background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #94a3b8; }}
        .severity-critical {{ color: #ef4444; font-weight: bold; }}
        .severity-high {{ color: #f97316; font-weight: bold; }}
        .severity-medium {{ color: #eab308; font-weight: bold; }}
        .severity-low {{ color: #22c55e; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ReconMaster Assessment: {self.target}</h1>
        <p>Scan completed at {end_dt.strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    <div class="stats">
        <div class="card"><h3>Subdomains</h3><div class="value">{len(self.subdomains)}</div></div>
        <div class="card"><h3>Live Hosts</h3><div class="value">{len(self.live_domains)}</div></div>
        <div class="card"><h3>Vulnerabilities</h3><div class="value">{len(self.vulns)}</div></div>
        <div class="card"><h3>Risk Score</h3><div class="value">{self._calculate_risk_score()}/100</div></div>
    </div>
    <div class="findings">
        <h2>Key Vulnerabilities</h2>
        <table>
            <thead><tr><th>Severity</th><th>Vulnerability</th><th>Target</th></tr></thead>
            <tbody>
                {''.join([f"<tr><td class='severity-{v.get('info',{}).get('severity','info').lower()}'>{v.get('info',{}).get('severity','unknown').upper()}</td><td>{v.get('info',{}).get('name')}</td><td>{v.get('matched-at')}</td></tr>" for v in self.vulns[:50]])}
            </tbody>
        </table>
    </div>
</body>
</html>
        """
        with open(self.files["full_report"], "w", encoding="utf-8") as f:
            f.write(html_content)

        self.export_burp_targets()
        self.export_burp_issues()
        self.export_zap_urls()

        print(f"{Colors.GREEN}[+] Reports generated successfully: {Colors.ENDC}")
        print(f"    - JSON Summary: {self.files['summary']}")
        print(f"    - Executive Report: {self.files['executive_report']}")
        print(f"    - Interactive HTML: {self.files['full_report']}")

    def export_burp_targets(self):
        """Export URLs for Burp Suite Site Map import"""
        with open(self.files["burp_sitemap"], "w", encoding="utf-8") as f:
            for url in sorted(self.urls):
                f.write(url + "\n")

    def export_burp_issues(self):
        """Export findings in a format suitable for Burp Issue Importer (with redaction)"""
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

        with open(os.path.join(self.dirs["exports"], "burp_issues.json"), "w", encoding="utf-8") as f:
            json.dump(issues, f, indent=2)

    def export_zap_urls(self):
        """Export URLs for OWASP ZAP Import"""
        out = os.path.join(self.dirs["exports"], "zap_urls.txt")
        context_out = self.files["zap_context"]

        with open(out, "w", encoding="utf-8") as f:
            for url in self.urls:
                f.write(url + "\n")

        # Simple ZAP Context
        context_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<configuration>
    <context>
        <name>ReconMaster_{self.target}</name>
        <desc/>
        <inscope>true</inscope>
        <incregexes>https?://{re.escape(self.target)}/.*</incregexes>
    </context>
</configuration>"""

        with open(context_out, "w", encoding="utf-8") as f:
            f.write(context_xml)


async def run_recon(recon, args):
    """Orchestrate the recon process"""
    start_time = time.time()

    # Discovery Phase
    await recon._send_notification(f"🚀 Starting recon on {recon.target}", "info")
    await recon.passive_subdomain_enum()

    if not args.passive_only:
        await recon.active_subdomain_enum()

    await recon._send_notification(f"🔍 Discovery finished. Found {len(recon.subdomains)} subdomains.", "info")

    # Analysis Phase
    await recon.resolve_live_hosts()

    if not args.passive_only and not recon.daily:
        # Full scan phase (can run some tasks concurrently)
        await asyncio.gather(
            recon.scan_vulnerabilities(),
            recon.take_screenshots(),
            recon.crawl_and_extract(),
            recon.discover_sensitive_files(),
            recon.fuzz_api_endpoints()
        )

        # Sequence dependent tasks
        await recon.find_parameters()
        await recon.port_scan()
        await recon.load_and_run_plugins()

    elif recon.daily:
        # Specialized light-weight automation mode
        await asyncio.gather(
            recon.scan_vulnerabilities(),
            recon.fuzz_api_endpoints()
        )
        # Daily diff MUST run after discovery and vulnerability scan
        recon.handle_daily_diff()
    else:
        # Minimal analysis for passive-only
        await recon.take_screenshots()

    # Post-processing and state management
    recon._save_state()
    recon.generate_report()

    await recon._send_notification(f"✅ Recon complete for {recon.target}. Risk Score: {recon._calculate_risk_score()}/100", "success")

    duration = time.time() - start_time
    print(f"\n{Colors.BOLD}{Colors.GREEN}[PRO] ReconMaster finished in {duration:.2f}s.{Colors.ENDC}")


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description=f"ReconMaster {VERSION} - Pro-Level Security Recon",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("-d", "--domain", 
                        default=os.getenv('RECON_TARGET') or os.getenv('RECON_DOMAIN') or os.getenv('TARGET_DOMAIN') or '',
                        required=not (os.getenv('RECON_TARGET') or os.getenv('RECON_DOMAIN') or os.getenv('TARGET_DOMAIN')),
                        type=str,
                        help="Target domain to scan (e.g., example.com)")
    parser.add_argument("-v", "--version", action="version", version=f"ReconMaster {VERSION}")
    parser.add_argument("-o", "--output", "--output-dir", default="./recon_results", help="Output directory")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Concurrency limit")
    parser.add_argument("-w", "--wordlist", help="Custom wordlist path")
    parser.add_argument("--passive-only", action="store_true", help="Skip active/intrusive scans")
    parser.add_argument("--dry-run", action="store_true", help="Preview commands without executing them")
    parser.add_argument("--webhook", help="Discord/Slack webhook URL for notifications")
    parser.add_argument("--include", help="Comma-separated list of domains/patterns to include")
    parser.add_argument("--exclude", help="Comma-separated list of domains/patterns to exclude")
    parser.add_argument("--resume", action="store_true", help="Resume from existing artifacts")
    parser.add_argument("--daily", action="store_true", help="Enable daily automation mode (light recon + diff)")
    parser.add_argument("--i-understand-this-requires-authorization", action="store_true", dest="authorized", help="Confirm you have permission to scan the target")

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

        recon.verify_tools()

        # Apply CLI args to recon instance
        if args.include:
            recon.include_list = [x.strip() for x in args.include.split(",")]
        if args.exclude:
            recon.exclude_list = [x.strip() for x in args.exclude.split(",")]

        recon.resume = args.resume
        recon.daily = args.daily
        recon.dry_run = getattr(args, 'dry_run', False)
        recon.webhook_url = args.webhook

        asyncio.run(run_recon(recon, args))

    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Scan aborted by user.{Colors.ENDC}")
    except Exception as e:
        logger.exception(f"Critical error: {e}")


if __name__ == "__main__":
    main()