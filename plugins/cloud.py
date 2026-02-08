from plugins.base import ReconPlugin
import os
import logging

logger = logging.getLogger("ReconMaster.Plugins.Cloud")

class CloudSecurityPlugin(ReconPlugin):
    name = "Cloud Security"
    description = "Checks for exposed cloud infrastructure (AWS/Azure/GCP)"

    async def run(self, recon):
        cloud_techs = ["aws", "amazon", "azure", "gcp", "google cloud", "s3", "bucket", "blob"]
        
        has_cloud = False
        for techs in recon.tech_stack.values():
            if any(t.lower() in cloud_techs for t in techs):
                has_cloud = True
                break
        
        if not has_cloud:
            return

        logger.info("Cloud infrastructure detected. Running cloud-specific checks...")
        
        live_file = os.path.join(recon.output_dir, "subdomains", "live_hosts.txt")
        cmd = [
            "nuclei", "-l", live_file,
            "-tags", "cloud,s3,exposure",
            "-o", os.path.join(recon.output_dir, "vulns", "cloud_exposure.json"),
            "-silent"
        ]
        await recon._run_command(cmd)
