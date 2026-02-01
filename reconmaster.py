#!/usr/bin/env python3
"""
ReconMaster: Automated Reconnaissance Framework

A comprehensive reconnaissance automation tool that orchestrates multiple 
security tools for subdomain discovery, asset validation, and security analysis.

Author: viphacker100
License: MIT
Version: 1.0.0
"""

import os
import sys
import re
import argparse
import json
import time
import logging
from typing import Set, Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from utils import safe_run, merge_and_dedupe_text_files, find_wordlist
from rate_limiter import RateLimiter, AdaptiveRateLimiter


# Safe default constants
DEFAULT_THREADS = 10
DEFAULT_RATE_LIMIT = 10.0  # requests per second
DEFAULT_TIMEOUT = 300  # seconds
MAX_THREADS_WARNING = 50
BANNER = """
╔═══════════════════════════════════════════════════════╗
║          ReconMaster - Reconnaissance Framework       ║
║                    v1.0.0                             ║
║                 viphacker100 / MIT                    ║
╚═══════════════════════════════════════════════════════╝
"""


class InvalidDomainError(Exception):
    """Raised when domain validation fails."""
    pass


class InvalidOutputDirError(Exception):
    """Raised when output directory validation fails."""
    pass


class ToolNotFoundError(Exception):
    """Raised when required tool is not found in PATH."""
    pass


class ReconMaster:
    """
    Main reconnaissance orchestration class.
    
    Manages the complete reconnaissance workflow including passive/active
    subdomain discovery, domain validation, content discovery, and reporting.
    """
    
    def __init__(
        self,
        target: str,
        output_dir: str,
        threads: int = DEFAULT_THREADS,
        wordlist: Optional[str] = None,
        passive_only: bool = False,
        rate_limit: float = DEFAULT_RATE_LIMIT
    ) -> None:
        """
        Initialize ReconMaster instance.
        
        Args:
            target: Target domain to reconnaissance (e.g., 'example.com')
            output_dir: Base directory for output files
            threads: Number of concurrent threads (default: 10)
            wordlist: Custom wordlist path for brute forcing (optional)
            passive_only: Skip active scanning if True (default: False)
            rate_limit: Requests per second limit (default: 10.0)
            
        Raises:
            InvalidDomainError: If domain format is invalid
            InvalidOutputDirError: If output directory is invalid
        """
        # Validate inputs
        self.target = self._validate_domain(target)
        self.output_dir_base = self._validate_output_dir(output_dir)
        self.threads = self._validate_threads(threads)
        self.passive_only = passive_only
        self.rate_limit_value = max(0.1, rate_limit)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            rate=self.rate_limit_value,
            name=f"ReconMaster-{target}"
        )
        
        # Initialize timestamp and output directory
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = os.path.join(
            self.output_dir_base,
            f"{self.target}_{self.timestamp}"
        )
        
        # Initialize result storage
        self.subdomains: Set[str] = set()
        self.live_domains: Set[str] = set()
        self.urls: Set[str] = set()
        self.js_files: Set[str] = set()
        self.endpoints: Set[str] = set()
        self.parameters: Set[str] = set()
        self.tech_stack: Dict[str, List[str]] = {}
        self.takeovers: List[Dict] = []
        self.broken_links: List[str] = []
        
        # Resolve wordlist
        self.wordlist = self._resolve_wordlist(wordlist)
        
        # Create output directory structure
        self.create_dirs()
        
        self.logger.info(f"ReconMaster initialized for target: {self.target}")
        self.logger.info(f"Rate limit: {self.rate_limit_value} requests/sec")
        self.logger.info(f"Passive-only mode: {passive_only}")
    
    @staticmethod
    def _validate_domain(domain: str) -> str:
        """
        Validate domain format.
        
        Args:
            domain: Domain string to validate
            
        Returns:
            Validated domain string
            
        Raises:
            InvalidDomainError: If domain format is invalid
        """
        if not domain or not isinstance(domain, str):
            raise InvalidDomainError("Domain must be a non-empty string")
        
        domain = domain.strip().lower()
        
        # Remove protocol if present
        if domain.startswith(('http://', 'https://')):
            raise InvalidDomainError("Domain should not include protocol (http/https)")
        
        # Remove path if present
        if '/' in domain:
            raise InvalidDomainError("Domain should not include path")
        
        # Basic regex validation for domain format
        domain_pattern = r'^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*\.[a-z]{2,}$'
        if not re.match(domain_pattern, domain):
            raise InvalidDomainError(
                f"Invalid domain format: {domain}\n"
                f"Expected format: example.com or sub.example.com"
            )
        
        return domain
    
    @staticmethod
    def _validate_output_dir(output_dir: str) -> str:
        """
        Validate output directory path.
        
        Args:
            output_dir: Output directory path
            
        Returns:
            Absolute path to output directory
            
        Raises:
            InvalidOutputDirError: If directory is invalid
        """
        if not output_dir or not isinstance(output_dir, str):
            raise InvalidOutputDirError("Output directory must be a non-empty string")
        
        # Expand user home directory
        output_dir = os.path.expanduser(output_dir)
        
        # Get absolute path
        if not os.path.isabs(output_dir):
            output_dir = os.path.abspath(output_dir)
        
        # Check for dangerous paths
        dangerous_paths = ['/', '/etc', '/sys', '/proc', '/dev', '/bin', '/sbin']
        if output_dir in dangerous_paths:
            raise InvalidOutputDirError(
                f"Cannot use system directory as output: {output_dir}"
            )
        
        return output_dir
    
    @staticmethod
    def _validate_threads(threads: int) -> int:
        """
        Validate thread count parameter.
        
        Args:
            threads: Number of threads
            
        Returns:
            Validated thread count
            
        Raises:
            ValueError: If thread count is invalid
        """
        if not isinstance(threads, int):
            raise ValueError(f"Threads must be an integer, got {type(threads)}")
        
        if threads < 1:
            raise ValueError(f"Threads must be >= 1, got {threads}")
        
        if threads > MAX_THREADS_WARNING:
            print(
                f"[WARNING] {threads} threads is very high and may cause issues.\n"
                f"          Recommended maximum: {MAX_THREADS_WARNING} threads.\n"
                f"          Consider using --threads {MAX_THREADS_WARNING} or lower."
            )
        
        return threads
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging configuration.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(console_handler)
        
        return logger
    
    def _resolve_wordlist(self, custom_wordlist: Optional[str]) -> str:
        """
        Resolve wordlist path, checking custom path first, then common locations.
        
        Args:
            custom_wordlist: Custom wordlist path if provided
            
        Returns:
            Path to wordlist file
        """
        if custom_wordlist:
            if not os.path.exists(custom_wordlist):
                self.logger.warning(
                    f"Custom wordlist not found: {custom_wordlist}"
                )
            else:
                return custom_wordlist
        
        # Try common locations
        preferred_paths = [
            os.path.join(os.getcwd(), "wordlists", "subdomains.txt"),
            os.path.join(os.getcwd(), "wordlists", "subdomains_new.txt"),
            "/usr/share/seclists/Discovery/DNS/deepmagic.com-prefixes-top50000.txt",
            os.path.join(os.path.expanduser("~"), "wordlists", "subdomains.txt"),
        ]
        
        found = find_wordlist(preferred_paths)
        if found:
            self.logger.info(f"Using wordlist: {found}")
            return found
        
        # Return first path as fallback
        fallback = preferred_paths[0]
        self.logger.warning(
            f"Wordlist not found, will attempt to use: {fallback}"
        )
        return fallback

    def create_dirs(self) -> None:
        """
        Create output directory structure for all reconnaissance phases.
        
        Creates directories for:
        - subdomains: Subdomain enumeration results
        - screenshots: Visual captures of live domains
        - endpoints: URL and endpoint lists
        - js: JavaScript file analysis
        - params: Parameter discovery results
        - reports: Final reports and summaries
        
        Raises:
            OSError: If directory creation fails
        """
        try:
            dirs = [
                self.output_dir,
                os.path.join(self.output_dir, "subdomains"),
                os.path.join(self.output_dir, "screenshots"),
                os.path.join(self.output_dir, "endpoints"),
                os.path.join(self.output_dir, "js"),
                os.path.join(self.output_dir, "params"),
                os.path.join(self.output_dir, "reports"),
            ]

            for dir_path in dirs:
                os.makedirs(dir_path, exist_ok=True)

            self.logger.info(f"Created output directory structure at {self.output_dir}")
        except OSError as e:
            self.logger.error(f"Failed to create output directories: {e}")
            raise

    def passive_subdomain_enum(self) -> Set[str]:
        """
        Perform passive subdomain enumeration using OSINT sources.
        
        Uses multiple tools for comprehensive passive discovery:
        - subfinder: Passive subdomain enumeration
        - assetfinder: Asset discovery from OSINT sources
        - amass: DNS enumeration from public sources
        
        Rate limiting is applied to respect API rate limits and avoid overwhelming targets.
        
        Returns:
            Set of discovered subdomains
        """
        self.logger.info(f"Starting passive subdomain enumeration for {self.target}")
        
        try:
            # Rate limit before starting tool execution
            self.rate_limiter.acquire(1)
            self.logger.debug("Rate limit acquired for passive enumeration")

            # Subfinder
            subfinder_output = os.path.join(
                self.output_dir, "subdomains", "subfinder.txt"
            )
            self.logger.info("Running subfinder...")
            try:
                stdout, stderr, rc = safe_run(
                    ["subfinder", "-d", self.target, "-o", subfinder_output],
                    timeout=300
                )
                if rc != 0:
                    self.logger.warning(f"subfinder error: {stderr}")
            except FileNotFoundError:
                self.logger.warning("subfinder not found in PATH, skipping")
            except Exception as e:
                self.logger.warning(f"subfinder execution failed: {e}")

            # Rate limit between tools
            self.rate_limiter.acquire(1)

            # Assetfinder
            assetfinder_output = os.path.join(
                self.output_dir, "subdomains", "assetfinder.txt"
            )
            self.logger.info("Running assetfinder...")
            try:
                stdout, stderr, rc = safe_run(
                    ["assetfinder", "--subs-only", self.target],
                    timeout=300
                )
                if rc == 0 and stdout:
                    with open(assetfinder_output, "w", encoding="utf-8") as f:
                        f.write(stdout)
                else:
                    self.logger.warning(f"assetfinder error: {stderr}")
            except FileNotFoundError:
                self.logger.warning("assetfinder not found in PATH, skipping")
            except Exception as e:
                self.logger.warning(f"assetfinder execution failed: {e}")

            # Amass passive
            amass_output = os.path.join(
                self.output_dir, "subdomains", "amass.txt"
            )
            self.logger.info("Running amass passive enumeration...")
            try:
                stdout, stderr, rc = safe_run(
                    ["amass", "enum", "-passive", "-d", self.target, "-o", amass_output],
                    timeout=300
                )
                if rc != 0:
                    self.logger.warning(f"amass error: {stderr}")
            except FileNotFoundError:
                self.logger.warning("amass not found in PATH, skipping")
            except Exception as e:
                self.logger.warning(f"amass execution failed: {e}")

            # Combine results using python helper (cross-platform)
            all_subdomains = os.path.join(
                self.output_dir, "subdomains", "all_passive.txt"
            )
            try:
                merge_and_dedupe_text_files(
                    os.path.join(self.output_dir, "subdomains"),
                    "*.txt",
                    all_subdomains
                )
            except Exception as e:
                self.logger.error(f"Failed to merge subdomain files: {e}")
                return self.subdomains

            # Load subdomains
            try:
                with open(all_subdomains, "r", encoding="utf-8") as f:
                    self.subdomains = set(
                        [line.strip() for line in f if line.strip()]
                    )
                self.logger.info(
                    f"Found {len(self.subdomains)} unique subdomains via passive enumeration"
                )
            except FileNotFoundError:
                self.logger.warning("No subdomains found in passive enumeration")
                
        except Exception as e:
            self.logger.error(f"Passive subdomain enumeration failed: {e}")

        return self.subdomains

    def active_subdomain_enum(self) -> Set[str]:
        """
        Perform active subdomain enumeration using brute force.
        
        Uses ffuf for dictionary-based subdomain brute forcing against the target domain.
        Skipped if passive_only mode is enabled.
        
        Rate limiting is applied to avoid overwhelming target domain with requests.
        
        Returns:
            Set of brute-forced subdomains
        """
        if self.passive_only:
            self.logger.info("Skipping active subdomain enumeration (passive-only mode)")
            return self.subdomains
            
        self.logger.info(f"Starting active subdomain enumeration for {self.target}")

        try:
            if not os.path.exists(self.wordlist):
                self.logger.error(f"Wordlist not found: {self.wordlist}")
                return self.subdomains

            # Rate limit before brute forcing
            self.rate_limiter.acquire(1)
            self.logger.debug("Rate limit acquired for active enumeration")

            # Use ffuf for brute forcing subdomains
            ffuf_output = os.path.join(
                self.output_dir, "subdomains", "ffuf_brute.json"
            )
            
            self.logger.info(f"Running ffuf with wordlist: {self.wordlist}")
            try:
                stdout, stderr, rc = safe_run(
                    [
                        "ffuf",
                        "-u",
                        f"http://FUZZ.{self.target}",
                        "-w",
                        self.wordlist,
                        "-o",
                        ffuf_output,
                        "-of",
                        "json",
                        "-s",
                    ],
                    timeout=600
                )
                if rc != 0:
                    self.logger.warning(f"ffuf error: {stderr}")
            except FileNotFoundError:
                self.logger.warning("ffuf not found in PATH, skipping active enumeration")
                return self.subdomains
            except Exception as e:
                self.logger.warning(f"ffuf execution failed: {e}")
                return self.subdomains

            # Process ffuf results
            try:
                if not os.path.exists(ffuf_output):
                    self.logger.warning("ffuf output file not created")
                    return self.subdomains
                    
                with open(ffuf_output, "r", encoding="utf-8") as f:
                    ffuf_data = json.load(f)
                    for result in ffuf_data.get("results", []):
                        # ffuf JSON result has 'input'->'FUZZ' or 'value'
                        inp = result.get("input") or result.get("value")
                        if isinstance(inp, dict) and "FUZZ" in inp:
                            fuzz = inp.get("FUZZ")
                        else:
                            fuzz = result.get("input", "")
                        if fuzz:
                            subdomain = f"{fuzz}.{self.target}"
                            self.subdomains.add(subdomain)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                self.logger.error(f"Error processing ffuf results: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error processing ffuf output: {e}")

            # Update all subdomains file
            all_subdomains = os.path.join(
                self.output_dir, "subdomains", "all_subdomains.txt"
            )
            try:
                with open(all_subdomains, "w", encoding="utf-8") as f:
                    for subdomain in sorted(self.subdomains):
                        f.write(f"{subdomain}\n")
                        
                self.logger.info(
                    f"Total unique subdomains after brute forcing: {len(self.subdomains)}"
                )
            except IOError as e:
                self.logger.error(f"Failed to write subdomains file: {e}")

        except Exception as e:
            self.logger.error(f"Active subdomain enumeration failed: {e}")

        return self.subdomains

    def resolve_live_domains(self) -> Set[str]:
        """
        Verify and resolve live domains using HTTP probing.
        
        Uses httpx to probe all discovered subdomains and identify live/responsive domains.
        Extracts status codes and technology information.
        
        Rate limiting is applied to respect target rate limits during probing.
        
        Returns:
            Set of live domain URLs
        """
        self.logger.info("Resolving live domains with httpx")

        try:
            # Rate limit before probing live domains
            self.rate_limiter.acquire(1)
            self.logger.debug("Rate limit acquired for domain resolution")

            all_subdomains = os.path.join(
                self.output_dir, "subdomains", "all_subdomains.txt"
            )
            live_domains_file = os.path.join(
                self.output_dir, "subdomains", "live_domains.txt"
            )

            # First ensure we have the combined subdomain list
            if not os.path.exists(all_subdomains):
                self.logger.info("Creating subdomain list for httpx")
                try:
                    with open(all_subdomains, "w", encoding="utf-8") as f:
                        for subdomain in sorted(self.subdomains):
                            f.write(f"{subdomain}\n")
                except IOError as e:
                    self.logger.error(f"Failed to write subdomain list: {e}")
                    return self.live_domains

            # Run httpx
            try:
                cmd = [
                    "httpx",
                    "-l",
                    all_subdomains,
                    "-o",
                    live_domains_file,
                    "-status-code",
                    "-title",
                    "-tech-detect",
                    "-follow-redirects",
                ]
                stdout, stderr, rc = safe_run(cmd, timeout=600)
                if rc != 0:
                    self.logger.warning(f"httpx error: {stderr}")
            except FileNotFoundError:
                self.logger.warning("httpx not found in PATH")
                return self.live_domains
            except Exception as e:
                self.logger.warning(f"httpx execution failed: {e}")
                return self.live_domains

            # Load live domains
            try:
                if os.path.exists(live_domains_file):
                    with open(live_domains_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                # Extract domain URL (first token before space)
                                domain = line.strip().split(" ")[0]
                                if domain:
                                    self.live_domains.add(domain)
                    
                    self.logger.info(f"Found {len(self.live_domains)} live domains")
                else:
                    self.logger.warning("httpx output file not created")
            except IOError as e:
                self.logger.error(f"Failed to read live domains file: {e}")

        except Exception as e:
            self.logger.error(f"Domain resolution failed: {e}")

        return self.live_domains

    def take_screenshots(self) -> str:
        """
        Capture screenshots of live domains using gowitness.
        
        Takes visual snapshots of all live domains for manual review and documentation.
        
        Returns:
            Path to screenshots directory
        """
        self.logger.info("Taking screenshots with gowitness")

        try:
            if not self.live_domains:
                self.logger.warning("No live domains to screenshot")
                return ""

            live_domains_file = os.path.join(
                self.output_dir, "subdomains", "live_domains.txt"
            )
            screenshots_dir = os.path.join(self.output_dir, "screenshots")

            # Ensure live_domains.txt exists
            if not os.path.exists(live_domains_file):
                try:
                    with open(live_domains_file, "w", encoding="utf-8") as f:
                        for domain in sorted(self.live_domains):
                            f.write(f"{domain}\n")
                except IOError as e:
                    self.logger.error(f"Failed to write live domains file: {e}")
                    return ""

            # Run gowitness
            try:
                cmd = [
                    "gowitness",
                    "file",
                    "-f",
                    live_domains_file,
                    "-P",
                    screenshots_dir,
                    "--no-http",
                ]
                stdout, stderr, rc = safe_run(cmd, timeout=900)
                if rc != 0:
                    self.logger.warning(f"gowitness error: {stderr}")
            except FileNotFoundError:
                self.logger.warning("gowitness not found in PATH")
                return ""
            except Exception as e:
                self.logger.warning(f"gowitness execution failed: {e}")
                return ""

            self.logger.info(f"Screenshots saved to {screenshots_dir}")
            return screenshots_dir
            
        except Exception as e:
            self.logger.error(f"Screenshot capture failed: {e}")
            return ""

    def scan_for_takeovers(self) -> List[str]:
        """
        Scan for subdomain takeover vulnerabilities using subzy.
        
        Identifies potential subdomain takeover opportunities by checking for
        unclaimed resources referenced by CNAME records.
        
        Returns:
            List of vulnerable subdomains
        """
        self.logger.info("Scanning for subdomain takeovers with subzy")

        try:
            all_subdomains = os.path.join(
                self.output_dir, "subdomains", "all_subdomains.txt"
            )
            takeovers_file = os.path.join(
                self.output_dir, "subdomains", "takeovers.txt"
            )

            if not os.path.exists(all_subdomains):
                self.logger.warning("Subdomains file not found, skipping takeover scan")
                return self.takeovers

            # Run subzy
            try:
                cmd = [
                    "subzy",
                    "run",
                    "--targets",
                    all_subdomains,
                    "--concurrency",
                    str(self.threads),
                    "--output",
                    takeovers_file,
                ]
                stdout, stderr, rc = safe_run(cmd, timeout=600)
                if rc != 0:
                    self.logger.warning(f"subzy error: {stderr}")
            except FileNotFoundError:
                self.logger.warning("subzy not found in PATH")
                return self.takeovers
            except Exception as e:
                self.logger.warning(f"subzy execution failed: {e}")
                return self.takeovers

            # Read takeover results
            try:
                if os.path.exists(takeovers_file):
                    with open(takeovers_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                self.takeovers.append(line.strip())
                    
                    if self.takeovers:
                        self.logger.warning(
                            f"Found {len(self.takeovers)} potential subdomain takeover(s)"
                        )
            except IOError as e:
                self.logger.error(f"Failed to read takeovers file: {e}")
                
        except Exception as e:
            self.logger.error(f"Takeover scan failed: {e}")

        return self.takeovers

        # Run subzy
        cmd = ["subzy", "run", "--targets", all_subdomains, "--output", takeovers_file]
        stdout, stderr, rc = safe_run(cmd)
        if rc != 0:
            print(f"[!] subzy error: {stderr}")

        # Check results
        try:
            with open(takeovers_file, "r") as f:
                self.takeovers = [line.strip() for line in f if line.strip()]
            if self.takeovers:
                print(f"[+] Found {len(self.takeovers)} potential subdomain takeovers!")
            else:
                print("[+] No subdomain takeovers found")
        except FileNotFoundError:
            print("[+] No subdomain takeovers found")

    def crawl_endpoints(self) -> Set[str]:
        """
        Crawl websites to discover URLs and endpoints using katana.
        
        Crawls all live domains to depth 3, extracting URLs, JavaScript files,
        and form endpoints.
        
        Rate limiting is applied to avoid overwhelming target servers during crawling.
        
        Returns:
            Set of discovered URLs
        """
        self.logger.info("Crawling endpoints with katana")

        try:
            # Rate limit before crawling
            self.rate_limiter.acquire(1)
            self.logger.debug("Rate limit acquired for endpoint crawling")

            if not self.live_domains:
                self.logger.warning("No live domains for crawling")
                return self.urls

            live_domains_file = os.path.join(
                self.output_dir, "subdomains", "live_domains.txt"
            )
            urls_file = os.path.join(self.output_dir, "endpoints", "urls.txt")
            js_files = os.path.join(self.output_dir, "js", "js_files.txt")

            # Ensure live domains file exists
            if not os.path.exists(live_domains_file):
                try:
                    with open(live_domains_file, "w", encoding="utf-8") as f:
                        for domain in sorted(self.live_domains):
                            f.write(f"{domain}\n")
                except IOError as e:
                    self.logger.error(f"Failed to write live domains file: {e}")
                    return self.urls

            # Run katana to discover URLs
            self.logger.info("Running katana for URL discovery...")
            try:
                cmd = [
                    "katana",
                    "-list",
                    live_domains_file,
                    "-d",
                    "3",
                    "-jc",
                    "-kf",
                    "-aff",
                    "-o",
                    urls_file,
                ]
                stdout, stderr, rc = safe_run(cmd, timeout=900)
                if rc != 0:
                    self.logger.warning(f"katana error: {stderr}")
            except FileNotFoundError:
                self.logger.warning("katana not found in PATH")
                return self.urls
            except Exception as e:
                self.logger.warning(f"katana execution failed: {e}")
                return self.urls

            # Extract JS files
            self.logger.info("Extracting JavaScript files...")
            try:
                if os.path.exists(urls_file):
                    with open(urls_file, "r", encoding="utf-8") as src, open(
                        js_files, "w", encoding="utf-8"
                    ) as dst:
                        for line in src:
                            line = line.strip()
                            if line and (".js" in line):
                                dst.write(line + "\n")
                                self.js_files.add(line)
                    
                    self.logger.info(f"Found {len(self.js_files)} JavaScript files")
            except IOError as e:
                self.logger.error(f"Failed to extract JavaScript files: {e}")

            # Load URLs
            try:
                if os.path.exists(urls_file):
                    with open(urls_file, "r", encoding="utf-8") as f:
                        self.urls = set([line.strip() for line in f if line.strip()])
                    self.logger.info(f"Found {len(self.urls)} endpoints from crawling")
            except IOError as e:
                self.logger.error(f"Failed to read URLs file: {e}")
                
        except Exception as e:
            self.logger.error(f"Endpoint crawling failed: {e}")

        return self.urls

    def directory_bruteforce(self) -> Set[str]:
        """
        Brute force directories on live domains using ffuf.
        
        Tests for hidden directories and files on a sample of live domains.
        Skipped if passive_only mode is enabled.
        
        Returns:
            Set of discovered directories
        """
        if self.passive_only:
            self.logger.info("Skipping directory brute forcing (passive-only mode)")
            return set()
            
        self.logger.info("Brute forcing directories with ffuf")

        try:
            if not self.live_domains:
                self.logger.warning("No live domains for directory brute forcing")
                return set()

            # Sample domains to avoid excessive scanning time
            sample_domains = (
                list(self.live_domains)[:5]
                if len(self.live_domains) > 5
                else list(self.live_domains)
            )

            wordlist = os.path.join(os.getcwd(), "wordlists", "directory-list.txt")
            if not os.path.exists(wordlist):
                wordlist = os.path.join(os.getcwd(), "wordlists", "directory-list_new.txt")

            if not os.path.exists(wordlist):
                self.logger.warning(f"Directory wordlist not found: {wordlist}")
                return set()

            discovered = set()
            for domain in sample_domains:
                try:
                    output_file = os.path.join(
                        self.output_dir,
                        "endpoints",
                        f"{domain.replace('://', '_').replace('.', '_')}_dirs.json",
                    )
                    self.logger.info(f"Brute forcing directories for {domain}...")
                    cmd = [
                        "ffuf",
                        "-u",
                        f"{domain}/FUZZ",
                        "-w",
                        wordlist,
                        "-mc",
                        "200,204,301,302,307,401,403",
                        "-o",
                        output_file,
                        "-of",
                        "json",
                        "-s",
                        "-t",
                        str(self.threads),
                    ]
                    stdout, stderr, rc = safe_run(cmd, timeout=600)
                    if rc != 0:
                        self.logger.warning(f"ffuf error for {domain}: {stderr}")
                except Exception as e:
                    self.logger.warning(f"Directory brute forcing failed for {domain}: {e}")
                    
            self.logger.info("Directory brute forcing completed")
        except Exception as e:
            self.logger.error(f"Directory brute forcing failed: {e}")

        return discovered

    def find_parameters(self) -> Set[str]:
        """
        Discover GET/POST parameters using Arjun.
        
        Tests discovered endpoints for hidden parameters.
        Skipped if passive_only mode is enabled.
        
        Returns:
            Set of discovered parameters
        """
        if self.passive_only:
            self.logger.info("Skipping parameter discovery (passive-only mode)")
            return self.parameters
            
        self.logger.info("Finding parameters with Arjun")

        try:
            endpoints_file = os.path.join(self.output_dir, "endpoints", "urls.txt")
            if not os.path.exists(endpoints_file):
                self.logger.warning("No endpoints found for parameter discovery")
                return self.parameters

            # Sample a few URLs to avoid excessive time
            try:
                with open(endpoints_file, "r", encoding="utf-8") as f:
                    urls = [line.strip() for line in f if line.strip()][:20]
            except IOError as e:
                self.logger.error(f"Failed to read endpoints file: {e}")
                return self.parameters

            params_file = os.path.join(self.output_dir, "params", "parameters.txt")

            for url in urls:
                try:
                    self.logger.info(f"Finding parameters for {url}...")
                    cmd = [
                        "arjun",
                        "-u",
                        url,
                        "-oT",
                        params_file,
                        "--stable",
                        "-t",
                        str(self.threads),
                    ]
                    stdout, stderr, rc = safe_run(cmd, timeout=300)
                    if rc == 0 and stdout:
                        self.parameters.add(stdout)
                except FileNotFoundError:
                    self.logger.warning("arjun not found in PATH")
                    break
                except Exception as e:
                    self.logger.warning(f"Parameter discovery failed for {url}: {e}")

            self.logger.info("Parameter finding completed")
        except Exception as e:
            self.logger.error(f"Parameter discovery failed: {e}")

        return self.parameters

    def check_broken_links(self) -> List[str]:
        """
        Check for broken link hijacking opportunities using socialhunter.
        
        Identifies links that are broken or point to unclaimed resources.
        
        Returns:
            List of broken links found
        """
        self.logger.info("Checking for broken links with socialhunter")

        try:
            if not self.live_domains:
                self.logger.warning("No live domains for broken link checking")
                return self.broken_links

            live_domains_file = os.path.join(
                self.output_dir, "subdomains", "live_domains.txt"
            )
            broken_links_file = os.path.join(
                self.output_dir, "reports", "broken_links.txt"
            )

            # Ensure live domains file exists
            if not os.path.exists(live_domains_file):
                try:
                    with open(live_domains_file, "w", encoding="utf-8") as f:
                        for domain in sorted(self.live_domains):
                            f.write(f"{domain}\n")
                except IOError as e:
                    self.logger.error(f"Failed to write live domains file: {e}")
                    return self.broken_links

            # Run socialhunter
            try:
                cmd = ["socialhunter", "-l", live_domains_file, "-o", broken_links_file]
                stdout, stderr, rc = safe_run(cmd, timeout=600)
                if rc != 0:
                    self.logger.warning(f"socialhunter error: {stderr}")
            except FileNotFoundError:
                self.logger.warning("socialhunter not found in PATH")
                return self.broken_links
            except Exception as e:
                self.logger.warning(f"socialhunter execution failed: {e}")
                return self.broken_links

            # Check results
            try:
                if os.path.exists(broken_links_file):
                    with open(broken_links_file, "r", encoding="utf-8") as f:
                        self.broken_links = [line.strip() for line in f if line.strip()]
                    self.logger.info(f"Found {len(self.broken_links)} potential broken links")
            except IOError as e:
                self.logger.error(f"Failed to read broken links file: {e}")
        except Exception as e:
            self.logger.error(f"Broken link checking failed: {e}")

        return self.broken_links

    def port_scan(self) -> Dict[str, str]:
        """
        Scan ports on selected domains using nmap.
        
        Performs service detection and version scanning on open ports.
        Skipped if passive_only mode is enabled.
        Limited to 5 domains to avoid excessive scanning.
        
        Rate limiting is applied to prevent network overload during port scanning.
        
        Returns:
            Dictionary mapping hosts to nmap results
        """
        if self.passive_only:
            self.logger.info("Skipping port scanning (passive-only mode)")
            return {}
            
        self.logger.info("Scanning ports with nmap")

        results = {}
        try:
            # Rate limit before port scanning
            self.rate_limiter.acquire(1)
            self.logger.debug("Rate limit acquired for port scanning")

            if not self.live_domains:
                self.logger.warning("No live domains for port scanning")
                return results

            # Sample domains for port scanning
            sample_domains = (
                list(self.live_domains)[:5]
                if len(self.live_domains) > 5
                else list(self.live_domains)
            )

            for domain in sample_domains:
                try:
                    # Extract host from URL
                    host = domain.split("://")[1].split("/")[0]
                    output_file = os.path.join(
                        self.output_dir, "reports", f"{host}_nmap.txt"
                    )
                    self.logger.info(f"Scanning ports for {host}...")

                    cmd = [
                        "nmap",
                        "-p-",
                        "-T4",
                        "-sC",
                        "-sV",
                        "--max-retries",
                        "2",
                        host,
                        "-oN",
                        output_file,
                    ]
                    stdout, stderr, rc = safe_run(cmd, timeout=1800)
                    if rc == 0:
                        results[host] = output_file
                    else:
                        self.logger.warning(f"nmap error for {host}: {stderr}")
                except FileNotFoundError:
                    self.logger.warning("nmap not found in PATH")
                    break
                except Exception as e:
                    self.logger.warning(f"Port scanning failed for {domain}: {e}")

            self.logger.info("Port scanning completed")
        except Exception as e:
            self.logger.error(f"Port scanning failed: {e}")

        return results

    def generate_report(self) -> str:
        """
        Generate comprehensive markdown report of reconnaissance findings.
        
        Creates a detailed summary report with statistics, findings, and next steps.
        
        Returns:
            Path to generated report file
        """
        self.logger.info("Generating comprehensive report")

        try:
            report_file = os.path.join(
                self.output_dir, "reports", "summary_report.md"
            )

            with open(report_file, "w", encoding="utf-8") as f:
                f.write(f"# Reconnaissance Report for {self.target}\n\n")
                f.write(
                    f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )

                f.write("## Summary\n\n")
                f.write(f"- Target: {self.target}\n")
                f.write(f"- Total Subdomains Discovered: {len(self.subdomains)}\n")
                f.write(f"- Live Domains: {len(self.live_domains)}\n")
                f.write(f"- Potential Subdomain Takeovers: {len(self.takeovers)}\n")
                f.write(f"- URLs Discovered: {len(self.urls)}\n")
                f.write(f"- JavaScript Files: {len(self.js_files)}\n")
                f.write(f"- Broken Links: {len(self.broken_links)}\n\n")

                # Add subdomain takeovers if any
                if self.takeovers:
                    f.write("## Potential Subdomain Takeovers\n\n")
                    for takeover in self.takeovers:
                        f.write(f"- {takeover}\n")
                    f.write("\n")

                # Add broken links if any
                if self.broken_links:
                    f.write("## Broken Links\n\n")
                    for link in self.broken_links[:20]:
                        f.write(f"- {link}\n")
                    if len(self.broken_links) > 20:
                        f.write(
                            f"- ... and {len(self.broken_links) - 20} more\n"
                        )
                    f.write("\n")

                f.write("## Next Steps\n\n")
                f.write("1. Review subdomain takeover opportunities\n")
                f.write("2. Test discovered endpoints for vulnerabilities\n")
                f.write("3. Analyze JavaScript files for sensitive information\n")
                f.write("4. Test parameters for injection vulnerabilities\n")
                f.write("5. Check broken links for potential hijacking\n\n")

            self.logger.info(f"Report generated: {report_file}")
            return report_file
            
        except IOError as e:
            self.logger.error(f"Failed to generate report: {e}")
            return ""
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return ""

    def run_all(self) -> None:
        """
        Execute the complete reconnaissance workflow.
        
        Orchestrates all reconnaissance phases sequentially:
        1. Passive subdomain enumeration
        2. Active subdomain brute forcing
        3. Live domain resolution
        4. Screenshot capture
        5. Subdomain takeover scanning
        6. Endpoint crawling
        7. Directory brute forcing
        8. Parameter discovery
        9. Broken link checking
        10. Port scanning
        11. Report generation
        """
        try:
            start_time = time.time()
            self.logger.info(
                f"Starting comprehensive reconnaissance for {self.target}"
            )

            # Execute all recon steps
            self.passive_subdomain_enum()
            self.active_subdomain_enum()
            self.resolve_live_domains()
            self.take_screenshots()
            self.scan_for_takeovers()
            self.crawl_endpoints()
            self.directory_bruteforce()
            self.find_parameters()
            self.check_broken_links()
            self.port_scan()
            self.generate_report()

            end_time = time.time()
            duration = end_time - start_time

            self.logger.info(f"Reconnaissance completed in {duration:.2f} seconds")
            self.logger.info(f"Results saved to: {self.output_dir}")
            
        except KeyboardInterrupt:
            self.logger.warning("Reconnaissance interrupted by user")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Reconnaissance failed: {e}")
            sys.exit(1)


def _display_legal_warning() -> None:
    """
    Display legal warning and require acknowledgment before proceeding.
    
    Shows critical legal disclaimers and waits for user acknowledgment.
    This ensures users are aware of legal responsibilities before use.
    """
    warning = """
╔════════════════════════════════════════════════════════════════════════════════╗
║                          ⚠️  LEGAL DISCLAIMER  ⚠️                             ║
╚════════════════════════════════════════════════════════════════════════════════╝

ReconMaster is designed for AUTHORIZED security testing only.

CRITICAL WARNINGS:
  • Unauthorized access to computer systems is ILLEGAL
  • Federal penalties: 2-20+ years imprisonment and $250,000+ fines
  • Criminal liability applies - you are personally responsible
  • Civil liability applies - you can be sued for damages
  • You MUST have written authorization before scanning

LEGAL RISKS:
  • CFAA (USA): Up to 10 years imprisonment
  • GDPR (EU): Up to €20 million fines for privacy violations
  • Computer Misuse Act (UK): Up to 10 years imprisonment
  • Similar laws apply in ALL countries

REQUIRED BEFORE USE:
  ✓ Written authorization from system owner
  ✓ Clear scope of testing
  ✓ Legal review (strongly recommended)
  ✓ Professional insurance (if applicable)

For full legal terms, read: LEGAL.md

╔════════════════════════════════════════════════════════════════════════════════╗
    """
    print(warning)
    
    # Require explicit acknowledgment
    response = input("Do you have explicit written authorization? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\n[ERROR] You cannot use ReconMaster without authorization.")
        print("Please read LEGAL.md for more information.")
        sys.exit(1)
    
    print("[OK] Proceeding with reconnaissance...")
    print()


def main() -> None:
    """
    Main entry point for ReconMaster CLI.
    
    Displays legal warnings, parses command-line arguments, and orchestrates
    the reconnaissance workflow.
    """
    # Display legal warning and require acknowledgment
    _display_legal_warning()
    
    parser = argparse.ArgumentParser(
        description="ReconMaster: Automated Reconnaissance Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reconmaster.py -d example.com
  python reconmaster.py -d example.com -o ./results -t 20
  python reconmaster.py -d example.com --passive-only
  python reconmaster.py -d example.com -w /path/to/wordlist.txt

IMPORTANT: You must have explicit written authorization before scanning.
See LEGAL.md for legal terms and responsibilities.
        """
    )
    
    parser.add_argument(
        "-d", "--domain",
        required=True,
        help="Target domain to scan (e.g., example.com)"
    )
    parser.add_argument(
        "-o", "--output",
        default="./recon_results",
        help="Output directory for results (default: ./recon_results)"
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=10,
        help="Number of concurrent threads (default: 10)"
    )
    parser.add_argument(
        "-w", "--wordlist",
        help="Custom wordlist for subdomain brute forcing"
    )
    parser.add_argument(
        "--passive-only",
        action="store_true",
        help="Only perform passive reconnaissance (no active scanning)"
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=DEFAULT_RATE_LIMIT,
        help=f"Requests per second (default: {DEFAULT_RATE_LIMIT})"
    )

    try:
        args = parser.parse_args()

        # Create ReconMaster instance with validated parameters
        recon = ReconMaster(
            target=args.domain,
            output_dir=args.output,
            threads=args.threads,
            wordlist=args.wordlist,
            passive_only=args.passive_only,
            rate_limit=args.rate_limit,
        )

        # Execute reconnaissance
        if args.passive_only:
            recon.logger.info("Running in passive-only mode")
            recon.passive_subdomain_enum()
            recon.resolve_live_domains()
            recon.take_screenshots()
            recon.generate_report()
        else:
            recon.run_all()
            
    except InvalidDomainError as e:
        print(f"[ERROR] Domain validation failed: {e}", file=sys.stderr)
        sys.exit(1)
    except InvalidOutputDirError as e:
        print(f"[ERROR] Output directory validation failed: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[WARNING] Reconnaissance interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
