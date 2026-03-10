import os
import logging
import asyncio
from typing import List
from ..core import ReconMaster

logger = logging.getLogger("ReconMaster.Screenshot")

class ScreenshotModule:
    """Module for automated screenshot capture of live hosts"""
    def __init__(self, recon: ReconMaster):
        self.recon = recon

    async def capture(self):
        """Capture screenshots using Gowitness in chunks"""
        if not self.recon.live_domains:
            logger.warning("No live domains found for screenshots.")
            return

        logger.info(f"Capturing screenshots for {len(self.recon.live_domains)} live hosts...")
        
        live_list = list(self.recon.live_domains)
        chunk_size = 20
        # Gowitness chunking logic
        for i in range(0, len(live_list), chunk_size):
            chunk = live_list[i:i + chunk_size]
            temp_list = os.path.join(self.recon.output_dir, f"temp_ss_{i}.txt")
            try:
                with open(temp_list, "w") as f:
                    for url in chunk: f.write(url + "\n")
                
                cmd = ["gowitness", "file", "-f", temp_list, "-P", self.recon.dirs["screenshots"], "--no-http", "--timeout", "15"]
                await self.recon.tools.run_command(cmd, timeout=300)
            finally:
                if os.path.exists(temp_list): os.remove(temp_list)

        logger.info("Screenshot capture complete.")
