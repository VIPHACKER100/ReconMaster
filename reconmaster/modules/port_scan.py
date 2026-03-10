import os
import logging
from typing import Set
from ..core import ReconMaster

logger = logging.getLogger("ReconMaster.PortScan")

class PortScanModule:
    """Module for network port scanning and service discovery"""
    def __init__(self, recon: ReconMaster):
        self.recon = recon

    async def scan(self):
        """Perform Nmap port scanning on live targets"""
        if not self.recon.live_domains: return
        logger.info("Starting port scan with Nmap...")

        # Extract unique hostnames
        hosts = {url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0] for url in self.recon.live_domains}
        
        # Limit to top 5 for reconnaissance efficiency
        for host in list(hosts)[:5]:
            host_safe = host.replace(".", "_")
            out_file = os.path.join(self.recon.dirs["nmap"], f"{host_safe}.txt")
            cmd = ["nmap", "--top-ports", "1000", "-T4", "--open", host, "-oN", out_file]
            await self.recon.tools.run_command(cmd, timeout=300)
        
        logger.info("Port scan complete.")
        # [Future: Support Naabu for faster discovery]
