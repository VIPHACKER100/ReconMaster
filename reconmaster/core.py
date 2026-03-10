import os
import sys
import logging
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Set, Dict, Any, Optional

from .http_manager import HTTPManager
from .tool_manager import ToolManager
from .utils import safe_run, merge_and_dedupe_text_files, find_wordlist

logger = logging.getLogger("ReconMaster.Core")

class ReconMaster:
    """Core orchestrator for the ReconMaster framework"""
    def __init__(self, target: str, output_dir: str, threads: int = 10, wordlist: Optional[str] = None):
        self.target = self._validate_target(target)
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_dir = os.path.join(output_dir, f"{self.target}_{self.timestamp}")
        self.threads = threads
        
        # Initialize Managers
        self.http = HTTPManager(threads=threads)
        self.tools = ToolManager(user_agents=self.http.user_agents)
        self.tools.set_concurrency(threads)

        # State and Findings
        self.subdomains: Set[str] = set()
        self.live_domains: Set[str] = set()
        self.urls: Set[str] = set()
        self.js_files: Set[str] = set()
        self.vulns: List[Dict[str, Any]] = []
        self.tech_stack: Dict[str, List[str]] = {}
        
        self._setup_dirs()
        self._setup_files()
        self._setup_logging()

        # Wordlist configuration
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.wordlist = wordlist or os.path.join(base_path, "wordlists", "dns_common.txt")

    def _setup_files(self):
        """Map logical file keys to absolute paths"""
        self.files = {
            "summary": os.path.join(self.dirs["base"], "summary.json"),
            "executive_report": os.path.join(self.dirs["base"], "executive_report.md"),
            "full_report": os.path.join(self.dirs["base"], "full_report.html"),
            "all_subdomains": os.path.join(self.dirs["subdomains"], "all_subdomains.txt"),
            "live_subdomains": os.path.join(self.dirs["subdomains"], "live_subdomains.txt"),
            "alive": os.path.join(self.dirs["http"], "alive.txt"),
            "httpx_full": os.path.join(self.dirs["http"], "httpx_full.json"),
            "technologies": os.path.join(self.dirs["http"], "technologies.json"),
            "nuclei_results": os.path.join(self.dirs["vulns"], "nuclei_results.json"),
            "vuln_critical": os.path.join(self.dirs["vulns"], "critical.txt"),
            "vuln_high": os.path.join(self.dirs["vulns"], "high.txt"),
            "vuln_medium": os.path.join(self.dirs["vulns"], "medium.txt"),
            "vuln_low": os.path.join(self.dirs["vulns"], "low.txt"),
            "takeovers": os.path.join(self.dirs["subdomains"], "takeovers.txt"),
            "broken_links": os.path.join(self.dirs["endpoints"], "broken_links.txt"),
            "all_urls": os.path.join(self.dirs["endpoints"], "all_urls.txt"),
            "crawl_tree": os.path.join(self.dirs["endpoints"], "crawl_tree.json"),
            "javascript_files": os.path.join(self.dirs["js"], "javascript_files.txt"),
            "js_secrets": os.path.join(self.dirs["js"], "secrets.txt"),
            "js_endpoints": os.path.join(self.dirs["js"], "endpoints.txt"),
            "admin_panels": os.path.join(self.dirs["endpoints"], "admin_panels.txt")
        }

    def _calculate_risk_score(self) -> int:
        """Calculate a risk score (0-100) based on findings"""
        score = 0
        severity_map = {"critical": 30, "high": 15, "medium": 5, "low": 1}
        for v in self.vulns:
            sev = v.get("info", {}).get("severity", "info").lower()
            score += severity_map.get(sev, 0)
        return min(score, 100)

    def _generate_premium_html_report(self, duration: str, end_dt: datetime) -> str:
        """Return the HTML template for the premium dashboard"""
        from .report_templates import generate_premium_html_report
        return generate_premium_html_report(self, duration, end_dt)

    def _validate_target(self, target: str) -> str:
        """Sanitize and validate target domain"""
        target = target.strip().rstrip('.')
        if "://" in target:
            target = target.split("://")[-1]
        target = target.split("/")[0].strip()
        
        if not target or not re.match(r'^[a-zA-Z0-9.-]+$', target):
            raise ValueError(f"Invalid domain format: {target}")
            
        # Prevent private IP/localhost targeting
        private_patterns = [
            r'^localhost', r'^127\.', r'^192\.168\.', r'^10\.', 
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.', r'.*\.local$', r'.*\.internal$'
        ]
        for pattern in private_patterns:
            if re.match(pattern, target, re.IGNORECASE):
                raise ValueError(f"Security Restriction: Cannot scan private infrastructure: {target}")
        
        return target

    def _setup_dirs(self):
        """Create structured output directories"""
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
            "nmap": os.path.join(self.output_dir, "nmap") # Added nmap dir
        }
        for d in self.dirs.values():
            os.makedirs(d, exist_ok=True)

    def _setup_logging(self):
        """Initialize file logging for this scan instance"""
        log_file = os.path.join(self.dirs["logs"], "scan.log")
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logging.getLogger("ReconMaster").addHandler(fh)
        logger.info(f"Initialized scan for {self.target} in {self.output_dir}")

    async def cleanup(self):
        """Finalize managers and cleanup resources"""
        await self.http.close()
        logger.info("Scan cleanup complete.")
