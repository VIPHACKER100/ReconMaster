from plugins.base import ReconPlugin
import os
import logging
import asyncio
import re

try:
    import aiohttp
    _HAVE_AIOHTTP = True
except ImportError:
    _HAVE_AIOHTTP = False

logger = logging.getLogger("ReconMaster.Plugins.SOAP")

class SOAPAnalysisPlugin(ReconPlugin):
    name = "SOAP API Analysis"
    description = "Discovers WSDL files and analyzes SOAP endpoints for misconfigurations"

    # Common WSDL/SOAP paths
    SOAP_PATHS = [
        "?wsdl", ".wsdl", "/service?wsdl", "/v1?wsdl",
        "/soap", "/SoapService", "/MessageService?wsdl"
    ]

    async def run(self, recon):
        logger.info("Starting SOAP API analysis module...")
        
        # Gather targets
        targets = set()
        for domain in recon.live_domains:
            targets.add(f"https://{domain}")
            targets.add(f"http://{domain}")
        
        for url in recon.urls:
            if url.endswith((".asmx", ".svc", ".php", ".jsp")):
                targets.add(url)

        logger.info(f"Probing {len(targets)} targets for SOAP/WSDL interfaces...")

        if _HAVE_AIOHTTP:
            await self._probe_soap_endpoints(recon, targets)

    async def _probe_soap_endpoints(self, recon, targets):
        connector = aiohttp.TCPConnector(ssl=False, limit=recon.threads, limit_per_host=30)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
            tasks = []
            for base_url in list(targets)[:50]:
                for path in self.SOAP_PATHS:
                    url = base_url + path if "?" not in base_url else base_url + path.replace("?", "&")
                    tasks.append(self._check_wsdl(session, url, recon))
            
            await asyncio.gather(*tasks)

    async def _check_wsdl(self, session, url, recon):
        if not await recon.circuit_breaker.check_can_proceed():
            return

        try:
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    if "wsdl:definitions" in text or "definitions" in text.lower() and "<soap:binding" in text.lower():
                        logger.warning(f"[!] SOAP/WSDL Endpoint Found: {url}")
                        
                        recon.vulns.append({
                            "info": {
                                "name": "SOAP/WSDL Endpoint Discovered",
                                "severity": "info",
                                "description": "Exposed WSDL file found, which may leak API structure."
                            },
                            "matched-at": url
                        })
                        
                        # Log to findings file
                        soap_file = os.path.join(recon.output_dir, "vulns", "soap_endpoints.txt")
                        os.makedirs(os.path.dirname(soap_file), exist_ok=True)
                        with open(soap_file, "a") as f:
                            f.write(f"WSDL: {url}\n")
        except:
            pass
