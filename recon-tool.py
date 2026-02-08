#!/usr/bin/env python3
"""
Advanced Reconnaissance Tool

A comprehensive tool for performing security reconnaissance on domains, including
subdomain enumeration, port scanning, directory fuzzing, and more.
"""

import os
import sys
import argparse
import subprocess
import logging
import asyncio
import json
import re
import shutil
import time
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse
import signal
import configparser
import logging.handlers
# Use internal execution helpers; avoid importing unused utils here


class ReconTool:
    """Main class for the reconnaissance tool."""

    def __init__(
        self,
        target: str,
        output_dir: str = None,
        config_file: str = None,
        verbose: bool = False,
        threads: int = 10,
        wordlists_dir: str = None,
        verify_ssl: bool = True,
    ):
        """
        Initialize the ReconTool with the target domain and options.

        Args:
            target: The domain or URL to perform reconnaissance on
            output_dir: Directory to store results (default: ./results/<target>)
            config_file: Path to config file (default: None, uses built-in defaults)
            verbose: Enable verbose logging
            threads: Number of threads to use for concurrent operations
            wordlists_dir: Directory containing wordlists (default: None, uses built-in wordlists)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        # Validate target
        if not self._validate_target(target):
            raise ValueError(f"Invalid target: {target}")

        self.target = self._normalize_target(target)
        self.domain = self._extract_domain(target)
        self.threads = max(1, min(threads, 50))  # Limit threads between 1 and 50
        self.wordlists_dir = wordlists_dir
        self.verify_ssl = verify_ssl

        # Set up output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(f"./results/{self.domain}")

        # Create output directories
        self._setup_directories()

        # Set up logging
        self._setup_logging(verbose)

        # Load configuration
        self.config = self._load_config(config_file)

        # Add rate limiter
        max_rate = 10  # Default value
        if (
            hasattr(self, "config")
            and "scan" in self.config
            and "max_rate" in self.config["scan"]
        ):
            max_rate = self.config["scan"]["max_rate"]
        self.rate_limiter = RateLimiter(max_rate=max_rate)

        # Check for required tools
        self._check_tools()

        # Initialize results storage
        self.results = {
            "subdomains": set(),
            "live_hosts": set(),
            "ports": {},
            "directories": {},
            "vulnerabilities": [],
            "screenshots": [],
            "endpoints": set(),
            "params": {},
            "js_files": set(),
            "technologies": {},
            "social_media": {},
        }

        self.logger.info(f"Initialized recon tool for target: {self.target}")
        self.logger.info(f"Results will be stored in: {self.output_dir}")

    def _normalize_target(self, target: str) -> str:
        """Normalize the target to a standard format."""
        if not target:
            raise ValueError("Target cannot be empty")

        # Remove protocol if present
        if "://" in target:
            target = target.split("://")[1]

        # Remove path, query parameters, and fragments
        target = target.split("/")[0].split("?")[0].split("#")[0]

        # Handle cases where port might be specified
        if ":" in target:
            target = target.split(":")[0]

        return target.lower().strip()

    def _extract_domain(self, target: str) -> str:
        """Extract the base domain from a URL or subdomain."""
        parsed_url = urlparse(f"http://{self._normalize_target(target)}")
        domain_parts = parsed_url.netloc.split(".")

        # Handle common TLDs with multiple parts (e.g., co.uk)
        if (
            len(domain_parts) > 2
            and domain_parts[-2] in ["co", "com", "net", "org", "gov", "edu"]
            and domain_parts[-1] in ["uk", "au", "nz", "jp"]
        ):
            return f"{domain_parts[-3]}.{domain_parts[-2]}.{domain_parts[-1]}"
        elif len(domain_parts) >= 2:
            return f"{domain_parts[-2]}.{domain_parts[-1]}"
        else:
            return parsed_url.netloc

    def _validate_target(self, target: str) -> bool:
        """
        Validate that the target is a valid domain or URL.
        Uses stricter regex patterns for domain validation.
        """
        if not target:
            return False

        # Improved domain validation pattern
        domain_pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]$"

        # Improved URL validation pattern
        url_pattern = r"^(https?://)?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9](:[0-9]{1,5})?(\/[^\s]*)?$"

        normalized = self._normalize_target(target)
        return bool(
            re.match(domain_pattern, normalized) or re.match(url_pattern, target)
        )

    def _setup_directories(self) -> None:
        """Set up the directory structure for storing results."""
        # Create main output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different types of results
        subdirs = [
            "subdomains",
            "screenshots",
            "nmap",
            "fuzzing",
            "endpoints",
            "vulnerabilities",
            "js",
            "logs",
            "temp",
        ]

        for subdir in subdirs:
            (self.output_dir / subdir).mkdir(exist_ok=True)

        # Create path attributes for easy access
        self.subdomain_dir = self.output_dir / "subdomains"
        self.screenshot_dir = self.output_dir / "screenshots"
        self.nmap_dir = self.output_dir / "nmap"
        self.fuzzing_dir = self.output_dir / "fuzzing"
        self.endpoint_dir = self.output_dir / "endpoints"
        self.vuln_dir = self.output_dir / "vulnerabilities"
        self.js_dir = self.output_dir / "js"
        self.log_dir = self.output_dir / "logs"
        self.temp_dir = self.output_dir / "temp"

    def _setup_logging(self, verbose: bool) -> None:
        """Set up logging configuration with rotation."""
        log_file = self.log_dir / f"{self.domain}_recon_{int(time.time())}.log"

        log_level = logging.DEBUG if verbose else logging.INFO

        # Use RotatingFileHandler for log rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[file_handler, logging.StreamHandler()],
        )

        self.logger = logging.getLogger("ReconTool")
        self.logger.setLevel(log_level)

    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.

        Args:
            config_file: Path to configuration file (optional)

        Returns:
            Dictionary with configuration values
        """
        # Default configuration
        default_config = {
            "tools": {
                "subfinder": "subfinder",
                "assetfinder": "assetfinder",
                "amass": "amass",
                "ffuf": "ffuf",
                "httpx": "httpx",
                "gowitness": "gowitness",
                "katana": "katana",
                "arjun": "arjun",
                "nmap": "nmap",
                "socialhunter": "socialhunter",
            },
            "wordlists": {
                "subdomains": str(Path.home() / "wordlists" / "subdomains.txt"),
                "directories": str(Path.home() / "wordlists" / "directory-list.txt"),
                "parameters": str(Path.home() / "wordlists" / "parameters.txt"),
            },
            "scan": {
                "ports": "80,443,8080,8443,21,22,25,53,110,123,143,389,445,587,3306,3389,5432,6379,9000,9090,9200",
                "threads": self.threads,
                "timeout": 30,
                "retries": 3,
                "delay": 0.5,
                "max_rate": 100,
            },
        }

        # Load from config file if provided
        if config_file:
            config_path = Path(config_file)
            if not config_path.exists():
                self.logger.warning(
                    f"Config file {config_file} not found, using defaults"
                )
            else:
                try:
                    parser = configparser.ConfigParser()
                    parser.read(config_path)

                    # Parse config sections
                    if "tools" in parser:
                        for key, value in parser["tools"].items():
                            default_config["tools"][key] = value

                    if "wordlists" in parser:
                        for key, value in parser["wordlists"].items():
                            default_config["wordlists"][key] = value

                    if "scan" in parser:
                        for key, value in parser["scan"].items():
                            if key == "ports":
                                default_config["scan"][key] = value
                            elif key in ["threads", "timeout", "retries"]:
                                default_config["scan"][key] = int(value)
                            elif key in ["delay", "max_rate"]:
                                default_config["scan"][key] = float(value)

                    self.logger.info(f"Loaded configuration from {config_file}")
                except Exception as e:
                    self.logger.error(f"Error loading config file: {e}")

        # Override wordlist paths if wordlists_dir is provided
        if self.wordlists_dir:
            wordlists_path = Path(self.wordlists_dir)
            if wordlists_path.exists():
                for wl_type in ["subdomains", "directories", "parameters"]:
                    wl_path = wordlists_path / f"{wl_type}.txt"
                    if wl_path.exists():
                        default_config["wordlists"][wl_type] = str(wl_path)
                        self.logger.info(
                            f"Using custom wordlist for {wl_type}: {wl_path}"
                        )
                    else:
                        self.logger.warning(f"Custom wordlist not found: {wl_path}")
            else:
                self.logger.warning(f"Wordlists directory not found: {wordlists_path}")

        # Check and create default wordlists if they don't exist
        for wl_type, wl_path in default_config["wordlists"].items():
            wl_path_obj = Path(wl_path)
            if not wl_path_obj.exists():
                # Use built-in minimal wordlists
                if wl_type == "subdomains":
                    default_wl = Path(__file__).parent / "wordlists" / "subdomains.txt"
                elif wl_type == "directories":
                    default_wl = (
                        Path(__file__).parent / "wordlists" / "directory-list.txt"
                    )
                elif wl_type == "parameters":
                    default_wl = Path(__file__).parent / "wordlists" / "parameters.txt"

                if default_wl.exists():
                    default_config["wordlists"][wl_type] = str(default_wl)
                else:
                    self.logger.warning(
                        f"Wordlist for {wl_type} not found, some scans may be limited"
                    )

        return default_config

    def _check_tools(self) -> None:
        """Check if required external tools are installed."""
        missing_tools = []
        available_tools = {}

        for tool_name, command in self.config["tools"].items():
            if not self._is_tool_available(command):
                missing_tools.append(tool_name)
                self.logger.warning(f"Tool {tool_name} ({command}) not found in PATH")
            else:
                available_tools[tool_name] = command

        if missing_tools:
            self.logger.warning(
                f"Missing tools: {', '.join(missing_tools)}. Some functionality will be limited."
            )

        # Store available tools for future reference
        self.available_tools = available_tools

    def _is_tool_available(self, command: str) -> bool:
        """Check if a tool is available in PATH."""
        return shutil.which(command) is not None

    def _safe_execute(self, command: List[str], timeout: int = None) -> tuple:
        """
        Safely execute a command and return stdout, stderr, and return code.
        Prevents command injection by ensuring all arguments are properly handled.

        Args:
            command: List of command parts
            timeout: Timeout in seconds

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        self.logger.debug(f"Executing command: {' '.join(str(x) for x in command)}")

        # Validate command is list and all elements are strings or can be converted to strings
        if not isinstance(command, list):
            self.logger.error("Command must be a list")
            return "", "Command must be a list", 1

        # Force convert all command elements to strings and sanitize
        sanitized_command = []
        for x in command:
            if isinstance(x, str):
                # Remove any shell metacharacters
                item = re.sub(r"[;&|`$()\[\]{}]", "", str(x))
                sanitized_command.append(item)
            else:
                sanitized_command.append(str(x))

        try:
            if not timeout:
                timeout = self.config["scan"]["timeout"]

            # Use a process group to ensure all child processes are terminated
            process = subprocess.Popen(
                sanitized_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if os.name != "nt" else None,
            )

            # Store process for cleanup
            if not hasattr(self, "_child_processes"):
                self._child_processes = []
            self._child_processes.append(process)

            stdout, stderr = process.communicate(timeout=timeout)
            return stdout, stderr, process.returncode

        except subprocess.TimeoutExpired:
            self.logger.warning(
                f"Command timed out after {timeout}s: {' '.join(sanitized_command)}"
            )
            # Kill the entire process group
            if os.name != "nt":
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                process.kill()

            try:
                stdout, stderr = process.communicate(timeout=1)
                return stdout, stderr, 1
            except Exception:
                return "", "Command timed out and failed to terminate properly", 1

        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return "", str(e), 1

    def enumerate_subdomains(self) -> Set[str]:
        """
        Enumerate subdomains using multiple tools.

        Returns:
            Set of discovered subdomains
        """
        self.logger.info(f"Starting subdomain enumeration for {self.domain}")
        subdomains = set()

        # Ensure output files
        subfinder_output = self.subdomain_dir / f"{self.domain}_subfinder.txt"
        assetfinder_output = self.subdomain_dir / f"{self.domain}_assetfinder.txt"
        amass_output = self.subdomain_dir / f"{self.domain}_amass.txt"
        combined_output = self.subdomain_dir / f"{self.domain}_all_subdomains.txt"

        # Run subfinder
        if self._is_tool_available(self.config["tools"]["subfinder"]):
            self.logger.info("Running subfinder...")
            cmd = [
                self.config["tools"]["subfinder"],
                "-d",
                self.domain,
                "-o",
                str(subfinder_output),
            ]
            stdout, stderr, rc = self._safe_execute(cmd)

            if rc != 0:
                self.logger.warning(f"Subfinder error: {stderr}")
            elif subfinder_output.exists():
                with open(subfinder_output) as f:
                    subfinder_subs = {line.strip() for line in f if line.strip()}
                    self.logger.info(
                        f"Subfinder found {len(subfinder_subs)} subdomains"
                    )
                    subdomains.update(subfinder_subs)

        # Run assetfinder
        if self._is_tool_available(self.config["tools"]["assetfinder"]):
            self.logger.info("Running assetfinder...")
            cmd = [self.config["tools"]["assetfinder"], self.domain]
            stdout, stderr, rc = self._safe_execute(cmd)

            if rc != 0:
                self.logger.warning(f"Assetfinder error: {stderr}")
            else:
                with open(assetfinder_output, "w") as f:
                    f.write(stdout)

                assetfinder_subs = {
                    line.strip() for line in stdout.splitlines() if line.strip()
                }
                self.logger.info(
                    f"Assetfinder found {len(assetfinder_subs)} subdomains"
                )
                subdomains.update(assetfinder_subs)

        # Run amass
        if self._is_tool_available(self.config["tools"]["amass"]):
            self.logger.info("Running amass (passive mode)...")
            cmd = [
                self.config["tools"]["amass"],
                "enum",
                "-passive",
                "-d",
                self.domain,
                "-o",
                str(amass_output),
            ]
            stdout, stderr, rc = self._safe_execute(
                cmd, timeout=300
            )  # Longer timeout for amass

            if rc != 0:
                self.logger.warning(f"Amass error: {stderr}")
            elif amass_output.exists():
                with open(amass_output) as f:
                    amass_subs = {line.strip() for line in f if line.strip()}
                    self.logger.info(f"Amass found {len(amass_subs)} subdomains")
                    subdomains.update(amass_subs)

        # Enhanced filtering to avoid false positives
        filtered_subdomains = set()
        for sub in subdomains:
            if (
                sub == self.domain
                or (sub.endswith(f".{self.domain}") and re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$", sub.split(f".{self.domain}")[0]))
            ):
                filtered_subdomains.add(sub)

        # Write combined results
        with open(combined_output, "w") as f:
            for sub in sorted(filtered_subdomains):
                f.write(f"{sub}\n")

        self.logger.info(
            f"Found {len(filtered_subdomains)} unique subdomains for {self.domain}"
        )
        self.results["subdomains"] = filtered_subdomains
        return filtered_subdomains

    async def find_live_hosts(self, subdomains: Set[str] = None) -> Set[str]:
        """
        Find live hosts using httpx.

        Args:
            subdomains: Set of subdomains to check (uses enumerated subdomains if None)

        Returns:
            Set of live URLs with scheme
        """
        if subdomains is None:
            subdomains = self.results["subdomains"]

        if not subdomains:
            self.logger.warning("No subdomains to check for live hosts")
            return set()

        self.logger.info(f"Checking {len(subdomains)} subdomains for live hosts")

        # Prepare files
        domains_file = self.temp_dir / f"{self.domain}_domains_to_check.txt"
        httpx_output = self.subdomain_dir / f"{self.domain}_live_hosts.txt"

        # Write domains to file
        with open(domains_file, "w") as f:
            for domain in subdomains:
                f.write(f"{domain}\n")

        live_hosts = set()

        # Run httpx
        if self._is_tool_available(self.config["tools"]["httpx"]):
            self.logger.info("Running httpx to find live hosts...")
            cmd = [
                self.config["tools"]["httpx"],
                "-l",
                str(domains_file),
                "-o",
                str(httpx_output),
                "-status-code",
                "-title",
                "-tech-detect",
                "-follow-redirects",
                "-silent",
            ]

            stdout, stderr, rc = self._safe_execute(cmd)

            if rc != 0:
                self.logger.warning(f"httpx error: {stderr}")
            elif httpx_output.exists():
                with open(httpx_output) as f:
                    lines = [line.strip() for line in f if line.strip()]

                    for line in lines:
                        # Parse the httpx output format which includes status code, etc.
                        parts = line.split()
                        if parts:
                            url = parts[0]
                            live_hosts.add(url)

                            # Also parse technology information if available
                            tech_index = line.find("[")
                            if tech_index > 0:
                                tech_str = line[tech_index:]
                                techs = re.findall(r"\[(.*?)\]", tech_str)
                                if techs:
                                    for tech in techs[0].split(","):
                                        if ":" in tech:
                                            tech_name, tech_ver = tech.split(":", 1)
                                            self.results["technologies"][url] = {
                                                "name": tech_name.strip(),
                                                "version": tech_ver.strip(),
                                            }

                self.logger.info(f"Found {len(live_hosts)} live hosts")
        else:
            self.logger.warning("httpx not available, skipping live host discovery")

        self.results["live_hosts"] = live_hosts
        return live_hosts

    async def take_screenshots(self, urls: Set[str] = None) -> Dict[str, str]:
        """
        Take screenshots of live hosts using gowitness.

        Args:
            urls: Set of URLs to screenshot (uses live hosts if None)

        Returns:
            Dictionary mapping URLs to screenshot paths
        """
        if urls is None:
            urls = self.results["live_hosts"]

        if not urls:
            self.logger.warning("No live hosts to screenshot")
            return {}

        self.logger.info(f"Taking screenshots of {len(urls)} live hosts")

        screenshot_paths = {}

        # Check if gowitness is available
        if not self._is_tool_available(self.config["tools"]["gowitness"]):
            self.logger.warning("gowitness not available, skipping screenshots")
            return screenshot_paths

        # Prepare URL file
        urls_file = self.temp_dir / f"{self.domain}_urls_to_screenshot.txt"
        with open(urls_file, "w") as f:
            for url in urls:
                f.write(f"{url}\n")

        # Set up gowitness database and output directory
        gowitness_dir = self.screenshot_dir
        db_path = gowitness_dir / "gowitness.sqlite3"

        # Run gowitness
        self.logger.info("Running gowitness to take screenshots...")
        cmd = [
            self.config["tools"]["gowitness"],
            "file",
            "-f",
            str(urls_file),
            "--disable-logging",
            "--screenshot-path",
            str(gowitness_dir),
            "--db-path",
            str(db_path),
        ]

        stdout, stderr, rc = self._safe_execute(
            cmd, timeout=300
        )  # Longer timeout for screenshots

        if rc != 0:
            self.logger.warning(f"gowitness error: {stderr}")
        else:
            # Map URLs to screenshot paths
            for url in urls:
                # Normalize URL to match gowitness filename format
                url_hash = self._url_to_filename(url)
                screenshot_path = gowitness_dir / f"{url_hash}.png"

                if screenshot_path.exists():
                    screenshot_paths[url] = str(screenshot_path)
                    self.results["screenshots"].append(str(screenshot_path))

            self.logger.info(f"Took {len(screenshot_paths)} screenshots")

        return screenshot_paths

    def _url_to_filename(self, url: str) -> str:
        """Convert a URL to a filename format similar to gowitness."""
        # This is a simplified version of the hashing that gowitness uses
        import hashlib

        return hashlib.md5(url.encode()).hexdigest()

    async def scan_ports(self, hosts: Set[str] = None) -> Dict[str, List[int]]:
        """
        Scan ports using nmap.

        Args:
            hosts: Set of hosts to scan (uses live hosts if None)

        Returns:
            Dictionary mapping hosts to open ports
        """
        if hosts is None:
            # Extract hostnames from live hosts
            hosts = set()
            for url in self.results["live_hosts"]:
                parsed_url = urlparse(url)
                hosts.add(parsed_url.netloc)

        if not hosts:
            self.logger.warning("No hosts to scan ports")
            return {}

        self.logger.info(f"Scanning ports on {len(hosts)} hosts")

        # Check if nmap is available
        if not self._is_tool_available(self.config["tools"]["nmap"]):
            self.logger.warning("nmap not available, skipping port scanning")
            return {}

        port_results = {}
        port_spec = self.config["scan"]["ports"]

        # Prepare host file
        hosts_file = self.temp_dir / f"{self.domain}_hosts_to_scan.txt"
        with open(hosts_file, "w") as f:
            for host in hosts:
                f.write(f"{host}\n")

        # Run nmap
        self.logger.info(f"Running nmap with ports: {port_spec}")
        xml_output = self.nmap_dir / f"{self.domain}_nmap_scan.xml"

        cmd = [
            self.config["tools"]["nmap"],
            "-iL",
            str(hosts_file),
            "-p",
            port_spec,
            "-sV",  # Version detection
            "--open",  # Only show open ports
            "-oX",
            str(xml_output),
            "-T4",  # Timing template (higher is faster)
        ]

        stdout, stderr, rc = self._safe_execute(
            cmd, timeout=600
        )  # Longer timeout for nmap

        if rc != 0:
            self.logger.warning(f"nmap error: {stderr}")
        elif xml_output.exists():
            # Parse XML output
            try:
                import xml.etree.ElementTree as ET

                tree = ET.parse(xml_output)
                root = tree.getroot()

                for host_elem in root.findall(".//host"):
                    addr = host_elem.find(".//address").get("addr")
                    hostnames = host_elem.findall(".//hostname")
                    hostname = hostnames[0].get("name") if hostnames else addr

                    open_ports = []
                    for port_elem in host_elem.findall(".//port"):
                        if port_elem.find(".//state").get("state") == "open":
                            port_num = int(port_elem.get("portid"))
                            open_ports.append(port_num)

                            # Get service info
                            service_elem = port_elem.find(".//service")
                            if service_elem is not None:
                                service_name = service_elem.get("name", "unknown")
                                service_product = service_elem.get("product", "")
                                service_version = service_elem.get("version", "")

                                if hostname not in self.results["ports"]:
                                    self.results["ports"][hostname] = {}

                                self.results["ports"][hostname][port_num] = {
                                    "service": service_name,
                                    "product": service_product,
                                    "version": service_version,
                                }

                    port_results[hostname] = open_ports

                self.logger.info(
                    f"Completed port scanning on {len(port_results)} hosts"
                )
            except Exception as e:
                self.logger.error(f"Error parsing nmap XML: {e}")

        return port_results

    async def fuzz_directories(
        self, urls: Set[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fuzz directories using ffuf.

        Args:
            urls: Set of URLs to fuzz (uses live hosts if None)

        Returns:
            Dictionary mapping URLs to discovered directories
        """
        if urls is None:
            urls = self.results["live_hosts"]

        if not urls:
            self.logger.warning("No URLs to fuzz directories")
            return {}

        self.logger.info(f"Fuzzing directories on {len(urls)} URLs")

        # Check if ffuf is available
        if not self._is_tool_available(self.config["tools"]["ffuf"]):
            self.logger.warning("ffuf not available, skipping directory fuzzing")
            return {}

        # Check if wordlist exists
        wordlist_path = Path(self.config["wordlists"]["directories"])
        if not wordlist_path.exists():
            self.logger.warning(f"Directory wordlist not found: {wordlist_path}")
            return {}

        directory_results = {}

        # Use a thread pool to run ffuf on multiple targets concurrently
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(5, self.threads)
        ) as executor:
            futures = []

            for url in urls:
                # Only fuzz a sample of URLs to avoid excessive scanning
                if len(futures) >= 10:  # Limit to 10 URLs
                    break

                # Add rate limiting before submitting task
                await self.rate_limiter.acquire()
                futures.append(
                    executor.submit(self._fuzz_single_url, url, wordlist_path)
                )

            for future in concurrent.futures.as_completed(futures):
                try:
                    url, results = future.result()
                    if results:
                        directory_results[url] = results
                        self.results["directories"][url] = results
                except Exception as e:
                    self.logger.error(f"Error in directory fuzzing: {e}")

        self.logger.info(
            f"Completed directory fuzzing, found results for {len(directory_results)} URLs"
        )
        return directory_results

    def _fuzz_single_url(self, url: str, wordlist_path: Path) -> tuple:
        """
        Fuzz a single URL using ffuf and return results.

        Args:
            url: URL to fuzz
            wordlist_path: Path to wordlist

        Returns:
            Tuple of (url, results)
        """
        self.logger.info(f"Fuzzing directories on {url}")

        # Ensure URL ends with /
        if not url.endswith("/"):
            url += "/"

        # Use hashlib for consistent filenames that avoid path traversal
        import hashlib

        # Remove any URL parameters to avoid extremely long filenames
        clean_url = url.split("?")[0].split("#")[0]
        url_hash = hashlib.md5(clean_url.encode()).hexdigest()

        json_output = self.fuzzing_dir / f"{url_hash}_ffuf.json"

        cmd = [
            self.config["tools"]["ffuf"],
            "-u",
            f"{url}FUZZ",
            "-w",
            str(wordlist_path),
            "-mc",
            "200,204,301,302,307,401,403,405",  # Status codes to match
            "-o",
            str(json_output),
            "-of",
            "json",
            "-s",  # Silent mode
        ]

        stdout, stderr, rc = self._safe_execute(cmd, timeout=300)

        results = []
        if rc != 0:
            self.logger.warning(f"ffuf error on {url}: {stderr}")
        elif json_output.exists():
            try:
                # Use file lock to prevent race conditions
                with open(json_output, "r") as f:
                    if os.name != "nt":  # Unix/Linux
                        import fcntl

                        fcntl.flock(f, fcntl.LOCK_SH)
                    data = json.load(f)
                    if os.name != "nt":
                        fcntl.flock(f, fcntl.LOCK_UN)

                if "results" in data:
                    for result in data["results"]:
                        if "url" in result and "status" in result:
                            results.append(
                                {
                                    "path": result.get("url", ""),
                                    "status": result.get("status", 0),
                                    "size": result.get("length", 0),
                                    "words": result.get("words", 0),
                                    "lines": result.get("lines", 0),
                                }
                            )

                self.logger.info(f"Found {len(results)} directories/files on {url}")
            except Exception as e:
                self.logger.error(f"Error parsing ffuf results for {url}: {e}")

        return url, results

    async def crawl_endpoints(self, urls: Set[str] = None) -> Dict[str, List[str]]:
        """
        Crawl and discover endpoints using katana.

        Args:
            urls: Set of URLs to crawl (uses live hosts if None)

        Returns:
            Dictionary mapping domains to discovered endpoints
        """
        if urls is None:
            urls = self.results["live_hosts"]

        if not urls:
            self.logger.warning("No URLs to crawl for endpoints")
            return {}

        self.logger.info(f"Crawling {len(urls)} URLs for endpoints")

        # Check if katana is available
        if not self._is_tool_available(self.config["tools"]["katana"]):
            self.logger.warning("katana not available, skipping endpoint crawling")
            return {}

        endpoint_results = {}

        # Sample URLs to avoid excessive scanning
        sample_urls = list(urls)[:5]  # Limit to 5 URLs

        # Use a thread pool to run katana on multiple targets concurrently
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(3, self.threads)
        ) as executor:
            futures = []

            for url in sample_urls:
                futures.append(executor.submit(self._crawl_single_url, url))

            for future in concurrent.futures.as_completed(futures):
                try:
                    url, endpoints = future.result()
                    if endpoints:
                        endpoint_results[url] = endpoints
                        self.results["endpoints"].update(endpoints)
                except Exception as e:
                    self.logger.error(f"Error in endpoint crawling: {e}")

        self.logger.info(
            f"Completed endpoint crawling, found results for {len(endpoint_results)} URLs"
        )
        return endpoint_results

    def _crawl_single_url(self, url: str) -> tuple:
        """
        Crawl a single URL using katana and return endpoints.

        Args:
            url: URL to crawl

        Returns:
            Tuple of (url, endpoints)
        """
        self.logger.info(f"Crawling endpoints on {url}")

        output_file = self.endpoint_dir / f"{self._url_to_filename(url)}_katana.txt"

        cmd = [
            self.config["tools"]["katana"],
            "-u",
            url,
            "-o",
            str(output_file),
            "-silent",
            "-jc",  # Include JS comments
            "-jem",  # Extract JS endpoints
        ]

        stdout, stderr, rc = self._safe_execute(cmd, timeout=300)

        endpoints = set()
        if rc != 0:
            self.logger.warning(f"katana error on {url}: {stderr}")
        elif output_file.exists():
            try:
                with open(output_file) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            endpoints.add(line)

                self.logger.info(f"Found {len(endpoints)} endpoints on {url}")
            except Exception as e:
                self.logger.error(f"Error parsing katana results for {url}: {e}")

        # Also extract JS files
        js_files = {endpoint for endpoint in endpoints if endpoint.endswith(".js")}
        self.results["js_files"].update(js_files)

        return url, endpoints

    async def discover_parameters(self, urls: Set[str] = None) -> Dict[str, List[str]]:
        """
        Discover parameters using arjun.

        Args:
            urls: Set of URLs to check (uses sample of endpoints or live hosts if None)

        Returns:
            Dictionary mapping URLs to discovered parameters
        """
        if urls is None:
            # Use a sample of discovered endpoints or live hosts
            endpoints = list(self.results["endpoints"])
            if endpoints:
                urls = set(endpoints[:10])  # Limit to 10 endpoints
            else:
                urls = set(
                    list(self.results["live_hosts"])[:5]
                )  # Limit to 5 live hosts

        if not urls:
            self.logger.warning("No URLs to discover parameters")
            return {}

        self.logger.info(f"Discovering parameters on {len(urls)} URLs")

        # Check if arjun is available
        if not self._is_tool_available(self.config["tools"]["arjun"]):
            self.logger.warning("arjun not available, skipping parameter discovery")
            return {}

        param_results = {}

        # Use a thread pool to run arjun on multiple targets concurrently
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(3, self.threads)
        ) as executor:
            futures = []

            for url in urls:
                futures.append(executor.submit(self._discover_params_single_url, url))

            for future in concurrent.futures.as_completed(futures):
                try:
                    url, params = future.result()
                    if params:
                        param_results[url] = params
                        self.results["params"][url] = params
                except Exception as e:
                    self.logger.error(f"Error in parameter discovery: {e}")

        self.logger.info(
            f"Completed parameter discovery, found results for {len(param_results)} URLs"
        )
        return param_results

    def _discover_params_single_url(self, url: str) -> tuple:
        """
        Discover parameters for a single URL using arjun.

        Args:
            url: URL to check

        Returns:
            Tuple of (url, parameters)
        """
        self.logger.info(f"Discovering parameters on {url}")

        json_output = self.endpoint_dir / f"{self._url_to_filename(url)}_arjun.json"

        cmd = [
            self.config["tools"]["arjun"],
            "-u",
            url,
            "-t",
            str(min(10, self.config["scan"]["threads"])),
            "--json",
            str(json_output),
            "-silent",
        ]

        stdout, stderr, rc = self._safe_execute(cmd, timeout=300)

        params = []
        if rc != 0:
            self.logger.warning(f"arjun error on {url}: {stderr}")
        elif json_output.exists():
            try:
                with open(json_output) as f:
                    data = json.load(f)

                if isinstance(data, dict) and "params" in data:
                    params = data["params"]

                self.logger.info(f"Found {len(params)} parameters on {url}")
            except Exception as e:
                self.logger.error(f"Error parsing arjun results for {url}: {e}")

        return url, params

    async def scan_social_media(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Scan for social media references using socialhunter.

        Returns:
            Dictionary mapping domains to social media references
        """
        urls = self.results["live_hosts"]

        if not urls:
            self.logger.warning("No URLs to scan for social media references")
            return {}

        self.logger.info(f"Scanning {len(urls)} URLs for social media references")

        # Check if socialhunter is available
        if not self._is_tool_available(self.config["tools"]["socialhunter"]):
            self.logger.warning(
                "socialhunter not available, skipping social media scanning"
            )
            return {}

        social_results = {}

        # Prepare URL file
        urls_file = self.temp_dir / f"{self.domain}_urls_for_social.txt"
        with open(urls_file, "w") as f:
            for url in urls:
                f.write(f"{url}\n")

        json_output = self.output_dir / f"{self.domain}_social_media.json"

        cmd = [
            self.config["tools"]["socialhunter"],
            "-l",
            str(urls_file),
            "-o",
            str(json_output),
            "-j",  # JSON output
            "-s",  # Silent mode
        ]

        stdout, stderr, rc = self._safe_execute(cmd, timeout=300)

        if rc != 0:
            self.logger.warning(f"socialhunter error: {stderr}")
        elif json_output.exists():
            try:
                with open(json_output) as f:
                    data = json.load(f)

                for entry in data:
                    url = entry.get("url", "")
                    platform = entry.get("platform", "")
                    social_url = entry.get("social_url", "")

                    if url and platform and social_url:
                        if url not in social_results:
                            social_results[url] = []

                        social_results[url].append(
                            {"platform": platform, "url": social_url}
                        )

                        if url not in self.results["social_media"]:
                            self.results["social_media"][url] = []

                        self.results["social_media"][url].append(
                            {"platform": platform, "url": social_url}
                        )

                self.logger.info(
                    f"Found social media references for {len(social_results)} URLs"
                )
            except Exception as e:
                self.logger.error(f"Error parsing socialhunter results: {e}")

        return social_results

    async def run_all_scans(self) -> Dict[str, Any]:
        """
        Run all reconnaissance scans in optimal order.

        Returns:
            Dictionary with all scan results
        """
        self.logger.info(f"Starting full reconnaissance scan for {self.domain}")
        start_time = time.time()

        try:
            # Enumerate subdomains
            self.enumerate_subdomains()

            # Find live hosts
            await self.find_live_hosts()

            # Run concurrent tasks
            tasks = [
                self.take_screenshots(),
                self.scan_ports(),
                self.crawl_endpoints(),
                self.fuzz_directories(),
                self.scan_social_media(),
            ]

            await asyncio.gather(*tasks)

            # Discover parameters after endpoint discovery
            await self.discover_parameters()

            # Generate report
            self.generate_report()

            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"Reconnaissance completed in {duration:.2f} seconds")

            return self.results

        except Exception as e:
            self.logger.error(f"Error during reconnaissance: {e}")
            return self.results

    def generate_report(self) -> str:
        """
        Generate a comprehensive HTML report of all findings.

        Returns:
            Path to the generated report
        """
        self.logger.info("Generating reconnaissance report")

        report_path = self.output_dir / f"{self.domain}_recon_report.html"

        try:
            with open(report_path, "w") as f:
                # Write HTML header
                f.write(
                    f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reconnaissance Report: {self.domain}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .card {{
            background: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            padding: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Reconnaissance Report: {self.domain}</h1>
        <p>Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
                )

                # Summary section
                f.write(
                    f"""
        <div class="card">
            <h2>Summary</h2>
            <table>
                <tr>
                    <th>Target Domain</th>
                    <td>{self.domain}</td>
                </tr>
                <tr>
                    <th>Subdomains Found</th>
                    <td>{len(self.results["subdomains"])}</td>
                </tr>
                <tr>
                    <th>Live Hosts</th>
                    <td>{len(self.results["live_hosts"])}</td>
                </tr>
                <tr>
                    <th>Endpoints Discovered</th>
                    <td>{len(self.results["endpoints"])}</td>
                </tr>
            </table>
        </div>
"""
                )

                # Subdomains section
                f.write(
                    """
        <div class="card">
            <h2>Subdomains</h2>
            <table>
                <tr>
                    <th>#</th>
                    <th>Subdomain</th>
                </tr>
"""
                )

                for i, subdomain in enumerate(sorted(self.results["subdomains"]), 1):
                    f.write(
                        f"""
                <tr>
                    <td>{i}</td>
                    <td>{subdomain}</td>
                </tr>
"""
                    )

                f.write(
                    """
            </table>
        </div>
"""
                )

                # Live hosts section
                f.write(
                    """
        <div class="card">
            <h2>Live Hosts</h2>
            <table>
                <tr>
                    <th>#</th>
                    <th>URL</th>
                    <th>Technologies</th>
                </tr>
"""
                )

                for i, url in enumerate(sorted(self.results["live_hosts"]), 1):
                    tech_info = ""
                    if url in self.results["technologies"]:
                        tech = self.results["technologies"][url]
                        tech_info = f"{tech.get('name', '')} {tech.get('version', '')}"

                    f.write(
                        f"""
                <tr>
                    <td>{i}</td>
                    <td>{url}</td>
                    <td>{tech_info}</td>
                </tr>
"""
                    )

                f.write(
                    """
            </table>
        </div>
"""
                )

                # Ports section
                f.write(
                    """
        <div class="card">
            <h2>Open Ports</h2>
            <table>
                <tr>
                    <th>Host</th>
                    <th>Port</th>
                    <th>Service</th>
                    <th>Version</th>
                </tr>
"""
                )

                for host, ports in self.results["ports"].items():
                    for port, info in ports.items():
                        f.write(
                            f"""
                <tr>
                    <td>{host}</td>
                    <td>{port}</td>
                    <td>{info.get('service', '')}</td>
                    <td>{info.get('product', '')} {info.get('version', '')}</td>
                </tr>
"""
                        )

                f.write(
                    """
            </table>
        </div>
"""
                )

                # Directories section
                f.write(
                    """
        <div class="card">
            <h2>Directory Fuzzing Results</h2>
            <table>
                <tr>
                    <th>URL</th>
                    <th>Path</th>
                    <th>Status</th>
                    <th>Size</th>
                </tr>
"""
                )

                for url, dirs in self.results["directories"].items():
                    for dir_info in dirs:
                        f.write(
                            f"""
                <tr>
                    <td>{url}</td>
                    <td>{dir_info.get('path', '')}</td>
                    <td>{dir_info.get('status', '')}</td>
                    <td>{dir_info.get('size', '')}</td>
                </tr>
"""
                        )

                f.write(
                    """
            </table>
        </div>
"""
                )

                # Social media section
                f.write(
                    """
        <div class="card">
            <h2>Social Media References</h2>
            <table>
                <tr>
                    <th>URL</th>
                    <th>Platform</th>
                    <th>Social Media URL</th>
                </tr>
"""
                )

                for url, socials in self.results["social_media"].items():
                    for social in socials:
                        f.write(
                            f"""
                <tr>
                    <td>{url}</td>
                    <td>{social.get('platform', '')}</td>
                    <td>{social.get('url', '')}</td>
                </tr>
"""
                        )

                f.write(
                    """
            </table>
        </div>
"""
                )

                # Parameters section
                f.write(
                    """
        <div class="card">
            <h2>Discovered Parameters</h2>
            <table>
                <tr>
                    <th>URL</th>
                    <th>Parameters</th>
                </tr>
"""
                )

                for url, params in self.results["params"].items():
                    f.write(
                        f"""
                <tr>
                    <td>{url}</td>
                    <td>{', '.join(params)}</td>
                </tr>
"""
                    )

                f.write(
                    """
            </table>
        </div>
"""
                )

                # Footer
                f.write(
                    """
        <div class="footer">
            <p>Generated by Advanced Reconnaissance Tool</p>
        </div>
    </div>
</body>
</html>
"""
                )

            self.logger.info(f"Report generated: {report_path}")
            return str(report_path)

        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return ""

    def save_results(self) -> str:
        """
        Save all results to a JSON file.

        Returns:
            Path to the JSON file
        """
        json_path = self.output_dir / f"{self.domain}_recon_results.json"

        try:
            # Convert sets to lists for JSON serialization
            json_results = {
                "target": self.domain,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "subdomains": list(self.results["subdomains"]),
                "live_hosts": list(self.results["live_hosts"]),
                "endpoints": list(self.results["endpoints"]),
                "screenshots": self.results["screenshots"],
                "ports": self.results["ports"],
                "directories": self.results["directories"],
                "params": self.results["params"],
                "social_media": self.results["social_media"],
                "technologies": self.results["technologies"],
                "js_files": list(self.results["js_files"]),
                "vulnerabilities": self.results["vulnerabilities"],
            }

            with open(json_path, "w") as f:
                json.dump(json_results, f, indent=4)

            self.logger.info(f"Results saved to {json_path}")
            return str(json_path)

        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            return ""

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup."""
        self.cleanup()

    def cleanup(self) -> None:
        """Clean up temporary files and resources."""
        try:
            # Remove temp directory if it exists
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.logger.info("Temporary files cleaned up")

            # Close any open file handles
            for handler in self.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.close()

            # Terminate any remaining child processes
            if hasattr(self, "_child_processes"):
                for process in self._child_processes:
                    try:
                        if os.name != "nt":
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        else:
                            process.kill()
                    except Exception:
                        pass

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class RateLimiter:
    """Rate limiter to prevent excessive requests."""

    def __init__(self, max_rate=10, time_period=1.0):
        """
        Initialize rate limiter.

        Args:
            max_rate: Maximum number of requests per time_period
            time_period: Time period in seconds
        """
        self.max_rate = max_rate
        self.time_period = time_period
        self.tokens = max_rate
        self.last_check = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """
        Acquire permission to make a request, waiting if necessary.
        """
        async with self._lock:
            now = time.monotonic()
            time_passed = now - self.last_check
            self.last_check = now

            # Add tokens based on time passed
            self.tokens += time_passed * (self.max_rate / self.time_period)

            # Cap tokens at max_rate
            if self.tokens > self.max_rate:
                self.tokens = self.max_rate

            if self.tokens < 1:
                # Calculate the required wait time
                wait_time = (1 - self.tokens) * (self.time_period / self.max_rate)
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

    async def _run_concurrent_tasks(self, tasks_list, max_concurrent=None):
        """
        Run tasks concurrently with proper exception handling and resource management.

        Args:
            tasks_list: List of async coroutines to run
            max_concurrent: Maximum number of concurrent tasks

        Returns:
            List of task results
        """
        if not max_concurrent:
            # RateLimiter doesn't own a threads attribute; default to max_rate (as an int)
            try:
                max_concurrent = max(1, int(self.max_rate))
            except Exception:
                max_concurrent = 1

        semaphore = asyncio.Semaphore(max_concurrent)

        logger = logging.getLogger("ReconTool")

        async def task_wrapper(task):
            async with semaphore:
                try:
                    return await task
                except Exception as e:
                    logger.error(f"Error in task: {e}")
                    return None

        tasks = [task_wrapper(task) for task in tasks_list]
        return await asyncio.gather(*tasks)


def setup_argparse() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Advanced Reconnaissance Tool for security testing",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("target", help="Target domain or URL to scan")

    parser.add_argument(
        "-o", "--output", help="Output directory for results", default=None
    )

    parser.add_argument(
        "-c", "--config", help="Path to configuration file", default=None
    )

    parser.add_argument(
        "-t", "--threads", help="Number of threads to use", type=int, default=10
    )

    parser.add_argument(
        "-v", "--verbose", help="Enable verbose logging", action="store_true"
    )

    parser.add_argument(
        "--no-verify-ssl",
        help="Disable SSL certificate verification",
        action="store_true",
    )

    parser.add_argument(
        "--subdomain-only",
        help="Only perform subdomain enumeration",
        action="store_true",
    )

    parser.add_argument(
        "--no-port-scan", help="Skip port scanning", action="store_true"
    )

    parser.add_argument(
        "--no-screenshots", help="Skip taking screenshots", action="store_true"
    )

    parser.add_argument(
        "--no-fuzzing", help="Skip directory fuzzing", action="store_true"
    )

    parser.add_argument(
        "--wordlists",
        help="Path to directory containing wordlists (subdomains.txt, directory-list.txt, parameters.txt)",
        default=None,
    )

    return parser


async def main() -> None:
    """Main entry point for the tool."""
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        # Set up signal handler for graceful exit
        def signal_handler(sig, frame):
            print("\nExiting gracefully. Cleaning up...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Initialize the recon tool with context manager
        with ReconTool(
            target=args.target,
            output_dir=args.output,
            config_file=args.config,
            verbose=args.verbose,
            threads=args.threads,
            wordlists_dir=args.wordlists,
            verify_ssl=not args.no_verify_ssl,
        ) as recon:
            # Run scans based on arguments
            if args.subdomain_only:
                recon.enumerate_subdomains()
            else:
                # Enumerate subdomains first
                recon.enumerate_subdomains()

                # Find live hosts
                await recon.find_live_hosts()

                # Run concurrent tasks based on flags
                tasks = []

                if not args.no_screenshots:
                    tasks.append(recon.take_screenshots())

                if not args.no_port_scan:
                    tasks.append(recon.scan_ports())

                tasks.append(recon.crawl_endpoints())

                if not args.no_fuzzing:
                    tasks.append(recon.fuzz_directories())

                tasks.append(recon.scan_social_media())

                # Run all tasks concurrently
                await asyncio.gather(*tasks)

                # Discover parameters after endpoint discovery
                await recon.discover_parameters()

            # Generate report and save results
            report_path = recon.generate_report()
            json_path = recon.save_results()

            print("\nReconnaissance completed!")
            print(f"Report generated: {report_path}")
            print(f"Results saved: {json_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Create and run event loop
        if sys.version_info >= (3, 7):
            asyncio.run(main())
        else:
            # For Python 3.6 and below
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
            loop.close()
    except KeyboardInterrupt:
        print("\nExiting gracefully. Cleaning up...")
        sys.exit(0)
