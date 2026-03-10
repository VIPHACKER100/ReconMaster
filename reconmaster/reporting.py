import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from .core import ReconMaster

logger = logging.getLogger("ReconMaster.Reporting")

class ReportingManager:
    """Manager for generating multi-format assessment reports"""
    def __init__(self, recon: ReconMaster):
        self.recon = recon

    def generate_all(self, duration: str):
        """Generate all report formats (JSON, MD, HTML)"""
        logger.info("Generating final reports...")
        self._generate_summary_json(duration)
        self._generate_executive_md()
        self._generate_premium_html(duration)
        logger.info(f"Reports available in: {self.recon.output_dir}")

    def _generate_summary_json(self, duration: str):
        """Standard JSON summary for automated processing"""
        summary = {
            "target": self.recon.target,
            "duration": duration,
            "timestamp": self.recon.timestamp,
            "vulnerabilities": {
                "total": len(self.recon.vulns),
                "critical": len([v for v in self.recon.vulns if v.get("info", {}).get("severity") == "critical"]),
                "high": len([v for v in self.recon.vulns if v.get("info", {}).get("severity") == "high"]),
                "medium": len([v for v in self.recon.vulns if v.get("info", {}).get("severity") == "medium"]),
                "low": len([v for v in self.recon.vulns if v.get("info", {}).get("severity") == "low"]),
            },
            "assets": {
                "subdomains": len(self.recon.subdomains),
                "live_hosts": len(self.recon.live_domains),
                "urls": len(self.recon.urls)
            }
        }
        with open(self.recon.files["summary"], "w", encoding='utf-8') as f:
            json.dump(summary, f, indent=4)

    def _generate_executive_md(self):
        """Markdown report for project documentation and quick review"""
        with open(self.recon.files["executive_report"], "w", encoding='utf-8') as f:
            f.write(f"# Executive Security Report: {self.recon.target}\n\n")
            f.write(f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Target:** {self.recon.target}\n\n")
            
            f.write("## 📊 Summary\n")
            f.write(f"- Subdomains: {len(self.recon.subdomains)}\n")
            f.write(f"- Live Hosts: {len(self.recon.live_domains)}\n")
            f.write(f"- Vulnerabilities: {len(self.recon.vulns)}\n\n")
            
            f.write("## ⚠️ Top Findings\n")
            if not self.recon.vulns:
                f.write("No high or critical vulnerabilities identified.\n")
            else:
                for v in self.recon.vulns[:15]:
                    info = v.get("info", {})
                    f.write(f"- **[{info.get('severity', 'INFO').upper()}]** {info.get('name', 'Finding')} -> {v.get('matched-at', 'N/A')}\n")

    def _generate_premium_html(self, duration: str):
        """Interactive HTML dashboard with charts and deep-dive capabilities"""
        # Note: In a real implementation, I'd bring over the full template from reconmaster.py
        # For brevity, I'll refer to the template logic here.
        temp_dt = datetime.now()
        html = self.recon._generate_premium_html_report(duration, temp_dt) # Temporary delegation back to core for now or move template here
        with open(self.recon.files["full_report"], "w", encoding="utf-8") as f:
            f.write(html)
