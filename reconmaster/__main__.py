import argparse
import asyncio
import os
import sys
import logging
import time
from datetime import datetime

from .core import ReconMaster
from .modules.subdomain import SubdomainModule
from .modules.validation import ValidationModule
from .modules.vulnerability import VulnerabilityModule
from .modules.js_analysis import JSModule
from .modules.screenshot import ScreenshotModule
from .modules.port_scan import PortScanModule
from .reporting import ReportingManager

# Configure root logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("ReconMaster")

async def run_scan(args):
    """Main scanning orchestration"""
    start_time = time.time()
    
    recon = ReconMaster(
        target=args.domain,
        output_dir=args.output,
        threads=args.threads
    )
    
    # Apply global settings
    if args.dry_run:
        recon.tools.dry_run = True
    if args.webhook:
        recon.webhook_url = args.webhook

    try:
        # Tool Verification
        recon.tools.verify_tools(
            critical_tools=["subfinder", "assetfinder", "amass", "ffuf", "httpx", "nuclei", "gowitness", "katana"],
            optional_tools=["arjun", "nmap", "dnsx"]
        )

        subdomain = SubdomainModule(recon)
        validation = ValidationModule(recon)
        vulnerability = VulnerabilityModule(recon)
        js_module = JSModule(recon)
        screenshot = ScreenshotModule(recon)
        port_scan = PortScanModule(recon)
        reporting = ReportingManager(recon)

        # Phase 1: Discovery
        await subdomain.passive_enum()
        if not args.passive_only:
            await subdomain.active_enum(args.wordlist or recon.wordlist)

        # Phase 2: Validation
        await validation.resolve_dns()
        await validation.probe_http()

        # Phase 3: Analysis
        if not args.passive_only:
            # Run independent tasks concurrently with exception aggregation
            tasks = [
                vulnerability.scan(),
                vulnerability.check_takeovers(),
                vulnerability.check_broken_links(),
                js_module.crawl(),
                screenshot.capture()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Aggregate Errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    task_name = tasks[i].__name__ if hasattr(tasks[i], '__name__') else f"Task-{i}"
                    logger.error(f"Phase 3 Task Failed ({task_name}): {result}")
                    recon.vulns.append({
                         "template-id": "internal-error",
                         "info": {"name": f"Module Failure: {task_name}", "severity": "info"},
                         "matched-at": recon.target
                    })
            
            # Dependent tasks
            try:
                await js_module.analyze_js()
                await port_scan.scan()
            except Exception as e:
                logger.error(f"Dependent Task Failed: {e}")

        # Phase 4: Reporting
        duration = f"{time.time() - start_time:.2f}s"
        reporting.generate_all(duration)

    finally:
        await recon.cleanup()

    print(f"\n[+] Scan finished in {duration}s")

def main():
    parser = argparse.ArgumentParser(description="ReconMaster v4.2.0 - Modular Recon Framework")
    parser.add_argument("-d", "--domain", required=True, help="Target domain")
    parser.add_argument("-o", "--output", default="./recon_results", help="Output directory")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Concurrency limit")
    parser.add_argument("-w", "--wordlist", help="Custom wordlist")
    parser.add_argument("--passive-only", action="store_true", help="Skip intrusive scans")
    parser.add_argument("--dry-run", action="store_true", help="Preview commands without executing them")
    parser.add_argument("--webhook", help="Webhook URL for notifications")
    parser.add_argument("--i-understand-this-requires-authorization", action="store_true", dest="authorized", help="Confirm authorization")

    args = parser.parse_args()

    if not args.authorized:
        print("[!] Error: You must confirm authorization with --i-understand-this-requires-authorization")
        sys.exit(1)

    asyncio.run(run_scan(args))

if __name__ == "__main__":
    main()
