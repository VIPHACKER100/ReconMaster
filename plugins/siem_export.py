from plugins.base import ReconPlugin
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("ReconMaster.Plugins.SIEM")

class SIEMExportPlugin(ReconPlugin):
    name = "SIEM Export"
    description = "Exports scan results to SIEM-ready JSON format (Elastic/Splunk)"

    async def run(self, recon):
        logger.info("Generating SIEM-ready export data...")
        
        siem_dir = os.path.join(recon.output_dir, "exports", "siem")
        os.makedirs(siem_dir, exist_ok=True)
        
        # 1. Prepare events
        events = []
        
        # Subdomain events
        for domain in recon.subdomains:
            events.append({
                "@timestamp": datetime.now().isoformat(),
                "event.category": "discovery",
                "event.type": "subdomain",
                "target.domain": recon.target,
                "host.name": domain,
                "reconmaster.version": "4.0.0-Titan"
            })
            
        # Vulnerability events
        for vuln in recon.vulns:
            info = vuln.get("info", {})
            events.append({
                "@timestamp": datetime.now().isoformat(),
                "event.category": "vulnerability",
                "event.type": "finding",
                "vulnerability.name": info.get("name"),
                "vulnerability.severity": info.get("severity"),
                "url.full": vuln.get("matched-at"),
                "target.domain": recon.target,
                "reconmaster.version": "4.0.0-Titan"
            })

        # 2. Write NDJSON (Newline Delimited JSON) for easy ingestion
        siem_file = os.path.join(siem_dir, f"recon_events_{recon.timestamp}.json")
        with open(siem_file, "w", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")
        
        logger.info(f"SIEM export completed: {siem_file}")
