import logging

class ReconPlugin:
    """Base class for all ReconMaster plugins"""
    name = "BasePlugin"
    description = "A base plugin template"
    version = "1.0.0"

    def __init__(self):
        self.logger = logging.getLogger(f"ReconMaster.Plugins.{self.name.replace(' ', '')}")

    async def run(self, recon):
        """Main execution point for the plugin"""
        raise NotImplementedError

    def _log(self, message: str, level: int = logging.INFO):
        """Unified logging for plugins"""
        self.logger.log(level, message)

    def _add_finding(self, recon, name: str, severity: str, matched_at: str, description: str = ""):
        """Helper to add a standard finding to the recon object"""
        recon.vulns.append({
            "info": {
                "name": name,
                "severity": severity,
                "description": description or self.description
            },
            "matched-at": matched_at,
            "plugin": self.name
        })
