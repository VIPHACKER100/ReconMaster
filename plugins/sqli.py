from plugins.base import ReconPlugin
import os
import asyncio
import logging
import re
from typing import List, Set

try:
    import aiohttp
    _HAVE_AIOHTTP = True
except ImportError:
    _HAVE_AIOHTTP = False

logger = logging.getLogger("ReconMaster.Plugins.SQLi")

class SQLiPlugin(ReconPlugin):
    name = "VIP SQLi Scanner"
    description = "Advanced SQL injection detection engine using heuristics and nuclei"

    # Common SQLi error patterns for various databases
    ERROR_PATTERNS = [
        r"sql syntax.*any useful error",
        r"valid MySQL result",
        r"check the manual that corresponds to your (MySQL|MariaDB|PostgreSQL) server",
        r"Unknown column",
        r"where clause",
        r"PostgreSQL.*ERROR",
        r"Warning.*mssql_query",
        r"Driver.* SQL Server",
        r"OLE DB.* SQL Server",
        r"ORA-[0-9]{5}",
        r"Oracle error",
        r"SQLite/JDBCDriver",
        r"SQLite.Exception",
        r"System.Data.SqlClient.SqlException",
        r"Microsoft OLE DB Provider for ODBC Drivers",
    ]

    async def run(self, recon):
        logger.info("Starting VIP SQLi Engine analysis...")
        
        # 1. Identify dynamic URLs
        dynamic_urls = self._get_dynamic_urls(recon.urls)
        if not dynamic_urls:
            logger.info("No dynamic URLs found for SQLi testing.")
            return

        logger.info(f"Detected {len(dynamic_urls)} dynamic targets. Running diagnostics...")

        # 2. Run Nuclei with SQLi tags specifically on these targets
        temp_file = os.path.join(recon.output_dir, "vulns", "sqli_targets.txt")
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        
        with open(temp_file, "w") as f:
            for url in dynamic_urls:
                f.write(url + "\n")

        sqli_results = os.path.join(recon.output_dir, "vulns", "sqli_nuclei.json")
        cmd = [
            "nuclei", "-l", temp_file,
            "-tags", "sqli,dast,injection",
            "-o", sqli_results,
            "-silent", "-severity", "critical,high,medium"
        ]
        
        # Run nuclei in background
        nuclei_task = recon._run_command(cmd)

        # 3. Native Heuristic Scanning (simulating VIP Engine)
        if _HAVE_AIOHTTP:
            heuristic_task = self._run_heuristic_scan(recon, dynamic_urls)
            await asyncio.gather(nuclei_task, heuristic_task)
        else:
            await nuclei_task

        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # Parse nuclei results into recon.vulns
        if os.path.exists(sqli_results):
            self._parse_results(recon, sqli_results)

    def _get_dynamic_urls(self, urls: Set[str]) -> List[str]:
        """Filter URLs that have query parameters"""
        dynamic = []
        for url in urls:
            if "?" in url and "=" in url:
                dynamic.append(url)
        return list(set(dynamic))

    async def _run_heuristic_scan(self, recon, urls: List[str]):
        """Perform light-weight heuristic SQLi checks (The 'VIP' logic)"""
        # Simple detection: append a single quote and check for errors
        payloads = ["'", "\"", "')"]
        
        connector = aiohttp.TCPConnector(ssl=False, limit=recon.threads)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for url in urls[:50]: # Limit heuristics for speed
                for p in payloads:
                    test_url = self._inject_payload(url, p)
                    tasks.append(self._check_url(session, test_url, recon))
            
            results = await asyncio.gather(*tasks)
            found_vulns = [r for r in results if r]
            
            if found_vulns:
                logger.warning(f"VIP Engine found {len(found_vulns)} potential SQLi vulnerabilities via heuristics!")
                # Write to specialized file
                sqli_file = os.path.join(recon.output_dir, "vulns", "sqli_findings_native.txt")
                with open(sqli_file, "a") as f:
                    for v in found_vulns:
                        f.write(f"Vulnerable URL: {v['url']}\nPattern: {v['pattern']}\n\n")

    def _inject_payload(self, url: str, payload: str) -> str:
        """Inject payload into the first found parameter"""
        if "=" not in url: return url
        parts = url.split("=", 1)
        return f"{parts[0]}={parts[1]}{payload}"

    async def _check_url(self, session, url, recon):
        if not await recon.circuit_breaker.check_can_proceed():
            return None
            
        try:
            async with session.get(url, timeout=10) as resp:
                text = await resp.text()
                for pattern in self.ERROR_PATTERNS:
                    if re.search(pattern, text, re.IGNORECASE):
                        vuln = {
                            "url": url,
                            "pattern": pattern,
                            "severity": "high"
                        }
                        recon.vulns.append({
                            "info": {"name": "SQL Injection (Heuristic)", "severity": "high", "description": f"Error pattern matched: {pattern}"},
                            "matched-at": url
                        })
                        return vuln
        except Exception:
            pass
        return None

    def _parse_results(self, recon, results_file):
        try:
            with open(results_file, "r") as f:
                import json
                for line in f:
                    try:
                        data = json.loads(line)
                        recon.vulns.append(data)
                    except:
                        continue
        except Exception as e:
            logger.error(f"Error parsing SQLi results: {e}")
