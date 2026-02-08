from plugins.base import ReconPlugin
import os
import logging

logger = logging.getLogger("ReconMaster.Plugins.WordPress")

class WordPressPlugin(ReconPlugin):
    name = "WordPress Scanner"
    description = "Specialized scanning for WordPress sites"

    async def run(self, recon):
        # Check if WordPress is in tech stack
        wp_targets = []
        for url, techs in recon.tech_stack.items():
            if any(x.lower() in ["wordpress", "wp"] for x in techs):
                wp_targets.append(url)
        
        if not wp_targets:
            return

        logger.info(f"WordPress detected on {len(wp_targets)} targets. Running specialized templates...")
        
        # Save targets to temp file
        temp_file = os.path.join(recon.output_dir, "vulns", "wp_targets.txt")
        with open(temp_file, "w") as f:
            for t in wp_targets:
                f.write(t + "\n")

        cmd = [
            "nuclei", "-l", temp_file,
            "-tags", "wordpress,wp-plugin",
            "-o", os.path.join(recon.output_dir, "vulns", "wp_nuclei.json"),
            "-silent"
        ]
        await recon._run_command(cmd)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
