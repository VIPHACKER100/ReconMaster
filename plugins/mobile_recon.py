from plugins.base import ReconPlugin
import re

class MobileReconPlugin(ReconPlugin):
    name = "Mobile Reconnaissance"
    description = "Discovers mobile-specific endpoints, deep links, and manifest files"
    version = "1.0.0"

    # Patterns for mobile-specific assets and endpoints
    MOBILE_PATTERNS = {
        "deep_link_scheme": r"([a-z0-9][a-z0-9+.-]*://[^\s\"']+)",
        "android_package": r"com\.[a-z0-9]+\.[a-z0-9.]+",
        "apple_app_id": r"id[0-9]{9,10}",
    }

    MOBILE_FILES = [
        "apple-app-site-association",
        ".well-known/apple-app-site-association",
        "assetlinks.json",
        ".well-known/assetlinks.json",
        "app-ads.txt"
    ]

    async def run(self, recon):
        self._log("Starting mobile reconnaissance...")
        
        # 1. Search in crawled URLs for deep links and mobile patterns
        found_links = set()
        for url in recon.urls:
            # Check for deep links in the URL itself (unlikely but possible in some formats)
            for name, pattern in self.MOBILE_PATTERNS.items():
                matches = re.findall(pattern, url)
                if matches:
                    for m in matches:
                        found_links.add((name, m))

        # 2. Probe for mobile manifest files on live domains
        if recon.live_domains:
            await self._probe_mobile_files(recon)

        # 3. Add findings
        for link_type, value in found_links:
            self._add_finding(recon, f"Mobile {link_type.replace('_', ' ').title()}", "info", value)
            
        self._log(f"Mobile reconnaissance finished. Found {len(found_links)} mobile-specific indicators.")

    async def _probe_mobile_files(self, recon):
        """Check for common mobile-web association files"""
        import aiohttp
        connector = aiohttp.TCPConnector(ssl=False, limit=recon.threads)
        async with aiohttp.ClientSession(connector=connector) as session:
            for domain in list(recon.live_domains)[:20]: # Limit for performance
                base_url = f"https://{domain}" if not domain.startswith("http") else domain
                for file_path in self.MOBILE_FILES:
                    target = f"{base_url.rstrip('/')}/{file_path}"
                    try:
                        async with session.get(target, timeout=5) as resp:
                            if resp.status == 200:
                                self._log(f"Found mobile association file: {target}")
                                self._add_finding(recon, "Mobile Association File Found", "info", target, 
                                                description=f"File {file_path} found on {domain}. This helps map mobile app to web domain.")
                    except:
                        pass
