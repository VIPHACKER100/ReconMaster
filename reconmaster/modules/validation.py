import os
import json
import logging
import shutil
from ..core import ReconMaster

logger = logging.getLogger("ReconMaster.Validation")

class ValidationModule:
    """Module for DNS resolution and HTTP probing"""
    def __init__(self, recon: ReconMaster):
        self.recon = recon

    async def resolve_dns(self):
        """Resolve subdomains to IPs using dnsx"""
        all_subs = os.path.join(self.recon.dirs["subdomains"], "all_subdomains.txt")
        live_subs = os.path.join(self.recon.dirs["subdomains"], "live_subdomains.txt")
        
        # Save all subdomains to file first
        with open(all_subs, "w") as f:
            f.write("\n".join(sorted(self.recon.subdomains)) + "\n")

        if "dnsx" in self.recon.tools.tool_paths:
            logger.info("Resolving subdomains with dnsx")
            cmd = ["dnsx", "-l", all_subs, "-silent", "-o", live_subs]
            await self.recon.tools.run_command(cmd)
        else:
            shutil.copy(all_subs, live_subs)

    async def probe_http(self):
        """Probe for live web services using httpx"""
        live_subs = os.path.join(self.recon.dirs["subdomains"], "live_subdomains.txt")
        httpx_out = os.path.join(self.recon.dirs["http"], "httpx_results.json")
        alive_txt = os.path.join(self.recon.dirs["http"], "alive.txt")

        cmd = [
            "httpx", "-l", live_subs, "-json", "-o", httpx_out,
            "-status-code", "-title", "-tech-detect", "-follow-redirects", "-silent"
        ]
        await self.recon.tools.run_command(cmd, timeout=600)

        if os.path.exists(httpx_out):
            with open(httpx_out, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        url = data.get("url")
                        if url:
                            self.recon.live_domains.add(url)
                            self.recon.tech_stack[url] = data.get("tech", [])
                    except: continue

            with open(alive_txt, "w") as f:
                f.write("\n".join(sorted(self.recon.live_domains)) + "\n")
        
        logger.info(f"Validation finished. Found {len(self.recon.live_domains)} live hosts.")
