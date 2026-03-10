import os
import json
import logging
import asyncio
import re
import random
from typing import List, Dict, Any, Optional, Set
from ..core import ReconMaster

logger = logging.getLogger("ReconMaster.JS")

class JSModule:
    """Module for deep crawling with Katana and JS secret analysis"""
    def __init__(self, recon: ReconMaster):
        self.recon = recon
        self.max_js = 100
        self.max_file_size_mb = 5

    async def crawl(self):
        """Crawl endpoints with Katana"""
        if not self.recon.live_domains: return
        logger.info("Starting deep crawling with Katana...")

        cmd = [
            "katana", "-list", self.recon.files["alive"], "-jc",
            "-o", self.recon.files["all_urls"], "-jsonl", "-oJ", self.recon.files["crawl_tree"],
            "-silent", "-concurrency", str(self.recon.threads), "-depth", "3"
        ]
        await self.recon.tools.run_command(cmd, timeout=1200)

        if os.path.exists(self.recon.files["all_urls"]):
            admin_panels = []
            with open(self.recon.files["all_urls"], "r") as f:
                for line in f:
                    url = line.strip()
                    if not url: continue
                    self.recon.urls.add(url)
                    if ".js" in url.lower().split("?")[0]:
                        self.recon.js_files.add(url)
                    
                    admin_keywords = ["admin", "login", "wp-admin", "dashboard"]
                    if any(kw in url.lower() for kw in admin_keywords) and not url.endswith((".js", ".css")):
                        admin_panels.append(url)

            if admin_panels:
                with open(self.recon.files["admin_panels"], "w") as f:
                    for panel in sorted(set(admin_panels)):
                        f.write(panel + "\n")

        if self.recon.js_files:
            with open(self.recon.files["javascript_files"], "w") as f:
                for js in sorted(self.recon.js_files):
                    f.write(js + "\n")

    async def analyze_js(self):
        """Analyze JS files for secrets and endpoints"""
        if not self.recon.js_files: return
        logger.info(f"Analyzing {len(self.recon.js_files)} JS files...")

        regex_list = {
            "google_api": r"AIza[0-9A-Za-z-_]{35}",
            "amazon_aws_key": r"AKIA[0-9A-Z]{16}",
            "slack_token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
            "stripe_api_key": r"sk_live_[0-9a-zA-Z]{24}",
            "endpoint": r"(?:https?://|/)[a-zA-Z0-9.\-_/]+(?:\?[a-zA-Z0-9.\-_=&]+)?"
        }

        async def scan_js(js_url):
            try:
                resp = await self.recon.http.request("GET", js_url, timeout=15)
                if resp and resp.status == 200:
                    content = await resp.text()
                    # Truncate if too large
                    if len(content) > self.max_file_size_mb * 1024 * 1024:
                        content = content[:self.max_file_size_mb * 1024 * 1024]

                    findings = []
                    for name, pattern in regex_list.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            matches = list(set(matches))
                            if name == "endpoint":
                                matches = [m for m in matches if len(m) > 5 and ("." in m or m.count("/") > 1)]
                            if matches:
                                findings.append((name, matches))
                    return js_url, findings
            except Exception as e:
                logger.debug(f"JS scan failed for {js_url}: {e}")
            return js_url, []

        js_list = list(self.recon.js_files)[:self.max_js]
        results = await asyncio.gather(*[scan_js(url) for url in js_list])

        with open(self.recon.files["js_secrets"], "w") as secret_f, open(self.recon.files["js_endpoints"], "w") as end_f:
            for url, findings in results:
                for name, matches in findings:
                    if name == "endpoint":
                        for m in matches: end_f.write(f"{m} (from {url})\n")
                    else:
                        for m in matches:
                            secret_f.write(f"[{name}] {m} (from {url})\n")
                            self.recon.vulns.append({"info": {"name": f"Exposed Secret ({name})", "severity": "medium"}, "matched-at": url})
