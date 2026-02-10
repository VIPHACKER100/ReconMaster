from plugins.base import ReconPlugin
import os
import logging
import asyncio

try:
    import aiohttp
    _HAVE_AIOHTTP = True
except ImportError:
    _HAVE_AIOHTTP = False

logger = logging.getLogger("ReconMaster.Plugins.Cloud")

class CloudSecurityPlugin(ReconPlugin):
    name = "Cloud Security"
    description = "Checks for exposed cloud infrastructure (AWS/Azure/GCP) and probes bucket patterns"

    async def run(self, recon):
        cloud_techs = ["aws", "amazon", "azure", "gcp", "google cloud", "s3", "bucket", "blob"]
        
        # 1. Tech Stack Detection
        has_cloud = False
        for techs in recon.tech_stack.values():
            if any(t.lower() in cloud_techs for t in techs):
                has_cloud = True
                break
        
        # 2. Add Active Bucket Probing (Proactive Discovery)
        target_slug = recon.target.split(".")[0]
        potential_buckets = [
            f"{target_slug}-data", f"{target_slug}-dev", f"{target_slug}-staging",
            f"{target_slug}-assets", f"{target_slug}-backup", f"{target_slug}-logs",
            f"{target_slug}-public", f"{target_slug}-internal", f"test-{target_slug}"
        ]

        logger.info(f"Probing {len(potential_buckets)} cloud bucket patterns for '{target_slug}'...")

        # Run nuclei for detected tech
        if has_cloud:
            logger.info("Cloud infrastructure detected. Running nuclei-based cloud checks...")
            live_file = recon.files.get("live_subdomains", os.path.join(recon.output_dir, "subdomains", "live_hosts.txt"))
            cmd = [
                "nuclei", "-l", live_file,
                "-tags", "cloud,s3,exposure",
                "-o", os.path.join(recon.output_dir, "vulns", "cloud_exposure.json"),
                "-silent"
            ]
            await recon._run_command(cmd)

        # Active bucket checks
        if _HAVE_AIOHTTP:
            await self._probe_bucket_urls(recon, potential_buckets)

    async def _probe_bucket_urls(self, recon, buckets):
        providers = {
            "aws": "s3.amazonaws.com",
            "gcp": "storage.googleapis.com",
            "azure": "blob.core.windows.net"
        }
        
        # Limit concurrency for probes
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=5)) as session:
            tasks = []
            for b_name in buckets:
                # AWS S3
                tasks.append(self._check_bucket(session, f"https://{b_name}.{providers['aws']}", "AWS S3", recon))
                # GCP
                tasks.append(self._check_bucket(session, f"https://{providers['gcp']}/{b_name}", "GCP Bucket", recon))
                # Azure
                tasks.append(self._check_bucket(session, f"https://{b_name}.{providers['azure']}", "Azure Blob", recon))
            
            await asyncio.gather(*tasks)

    async def _check_bucket(self, session, url, provider, recon):
        try:
            async with session.head(url, allow_redirects=True) as resp:
                if resp.status in [200, 403]: # 403 means it exists but protected
                    msg = "Publicly Accessible" if resp.status == 200 else "Protected"
                    logger.warning(f"Cloud Bucket Identified ({provider}): {url} [{msg}]")
                    recon.vulns.append({
                        "info": {"name": f"Cloud Asset Identified ({provider})", "severity": "info" if resp.status == 403 else "medium"},
                        "matched-at": url
                    })
        except:
            pass
