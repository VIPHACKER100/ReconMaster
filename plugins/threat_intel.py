from plugins.base import ReconPlugin
import re

class ThreatIntelligencePlugin(ReconPlugin):
    name = "Threat Intelligence"
    description = "Heuristic-based threat prioritization and severity refinement"
    version = "1.0.0"

    # Prioritization weights (higher is more critical)
    PRIORITY_WEIGHTS = {
        "critical": 100,
        "high": 75,
        "medium": 40,
        "low": 10,
        "info": 1
    }

    async def run(self, recon):
        self._log("Starting threat intelligence analysis...")
        
        if not recon.vulns:
            self._log("No findings to analyze. Skipping.")
            return

        for vuln in recon.vulns:
            info = vuln.get("info", {})
            name = info.get("name", "").lower()
            severity = info.get("severity", "info").lower()
            
            # 1. Refine Severity based on critical keywords
            refined_severity = self._refine_severity(name, severity)
            if refined_severity != severity:
                self._log(f"Refined severity for '{name}': {severity} -> {refined_severity}")
                info["severity"] = refined_severity
            
            # 2. Add Exploitability Score
            score = self.PRIORITY_WEIGHTS.get(info["severity"], 1)
            
            # Boost score based on specific "hot" keywords
            if any(kw in name for kw in ["rce", "sqli", "lfi", "rfi", "ssrf", "overflow"]):
                score += 20
            if "cve-" in name:
                score += 15
            
            info["priority_score"] = min(score, 100)
            
            # 3. Add Remediation Guidance (if not already present)
            if not info.get("description") or info["description"] == self.description:
                info["description"] = self._get_remediation(name)

        # Sort vulns by priority score
        recon.vulns.sort(key=lambda x: x.get("info", {}).get("priority_score", 0), reverse=True)
        self._log(f"Analyzed and prioritized {len(recon.vulns)} findings.")

    def _refine_severity(self, name: str, current_severity: str) -> str:
        """Upgrade severity if critical keywords are present"""
        critical_keywords = ["remote code execution", "rce", "sql injection", "sqli", "command injection"]
        high_keywords = ["local file inclusion", "lfi", "ssrf", "unauthenticated", "hardcoded key"]
        
        if any(kw in name for kw in critical_keywords):
            return "critical"
        if any(kw in name for kw in high_keywords) and current_severity not in ["critical"]:
            return "high"
        
        return current_severity

    def _get_remediation(self, name: str) -> str:
        """Provide basic remediation advice based on finding type"""
        if "sql" in name:
            return "Use parameterized queries or prepared statements to prevent SQL injection."
        if "xss" in name:
            return "Implement robust output encoding and Content Security Policy (CSP)."
        if "exposure" in name or "secret" in name:
            return "Rotate the exposed credentials immediately and audit access logs."
        if "takeover" in name:
            return "Claim the dangling DNS record or remove the CNAME/Alias pointing to the expired service."
        if "broken link" in name:
            return "Remove the dead link to prevent social media hijacking."
        
        return "Review the finding and apply industry standard security patches or configuration hardening."
