#!/usr/bin/env python3
"""
ReconMaster Diff Detector
Detects changes between reconnaissance scans
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set


class DiffDetector:
    """Detects and reports changes between scans"""
    
    def __init__(self):
        self.changes = []
    
    def detect_changes(self, previous_scan: str, current_scan: str, monitoring_config: Dict) -> List[Dict]:
        """
        Detect changes between two scans
        
        Args:
            previous_scan: Path to previous scan directory
            current_scan: Path to current scan directory
            monitoring_config: Configuration for what to monitor
            
        Returns:
            List of detected changes
        """
        self.changes = []
        previous = Path(previous_scan)
        current = Path(current_scan)
        
        # Check what to monitor
        if monitoring_config.get("detect_new_subdomains", True):
            self._check_subdomains(previous, current)
        
        if monitoring_config.get("detect_takeovers", True):
            self._check_takeovers(previous, current)
        
        if monitoring_config.get("detect_port_changes", True):
            self._check_ports(previous, current)
        
        if monitoring_config.get("detect_ssl_changes", True):
            self._check_ssl(previous, current)
        
        if monitoring_config.get("detect_new_vulnerabilities", True):
            self._check_vulnerabilities(previous, current)
        
        return self.changes
    
    def _check_subdomains(self, previous: Path, current: Path):
        """Check for new or removed subdomains"""
        prev_subs = self._load_subdomains(previous)
        curr_subs = self._load_subdomains(current)
        
        # New subdomains
        new_subs = curr_subs - prev_subs
        if new_subs:
            self.changes.append({
                "type": "new_subdomains",
                "severity": "medium",
                "description": f"Found {len(new_subs)} new subdomain(s)",
                "details": list(new_subs)
            })
        
        # Removed subdomains
        removed_subs = prev_subs - curr_subs
        if removed_subs:
            self.changes.append({
                "type": "removed_subdomains",
                "severity": "low",
                "description": f"{len(removed_subs)} subdomain(s) no longer responding",
                "details": list(removed_subs)
            })
    
    def _check_takeovers(self, previous: Path, current: Path):
        """Check for new subdomain takeover vulnerabilities"""
        prev_takeovers = self._load_takeovers(previous)
        curr_takeovers = self._load_takeovers(current)
        
        # New takeover vulnerabilities
        new_takeovers = curr_takeovers - prev_takeovers
        if new_takeovers:
            self.changes.append({
                "type": "new_takeover_vulnerability",
                "severity": "critical",
                "description": f"🚨 CRITICAL: {len(new_takeovers)} new subdomain takeover vulnerability detected!",
                "details": list(new_takeovers)
            })
        
        # Resolved takeovers
        resolved_takeovers = prev_takeovers - curr_takeovers
        if resolved_takeovers:
            self.changes.append({
                "type": "resolved_takeover",
                "severity": "info",
                "description": f"✅ {len(resolved_takeovers)} takeover vulnerability resolved",
                "details": list(resolved_takeovers)
            })
    
    def _check_ports(self, previous: Path, current: Path):
        """Check for changes in open ports"""
        prev_ports = self._load_port_summary(previous)
        curr_ports = self._load_port_summary(current)
        
        for host in curr_ports:
            if host not in prev_ports:
                continue
            
            prev_open = set(prev_ports[host])
            curr_open = set(curr_ports[host])
            
            # New open ports
            new_ports = curr_open - prev_open
            if new_ports:
                self.changes.append({
                    "type": "new_open_ports",
                    "severity": "high",
                    "description": f"New port(s) opened on {host}",
                    "details": {
                        "host": host,
                        "ports": list(new_ports)
                    }
                })
            
            # Closed ports
            closed_ports = prev_open - curr_open
            if closed_ports:
                self.changes.append({
                    "type": "closed_ports",
                    "severity": "low",
                    "description": f"Port(s) closed on {host}",
                    "details": {
                        "host": host,
                        "ports": list(closed_ports)
                    }
                })
    
    def _check_ssl(self, previous: Path, current: Path):
        """Check for SSL certificate changes"""
        # This would parse nmap output for SSL cert changes
        # Simplified implementation for now
        pass
    
    def _load_subdomains(self, scan_dir: Path) -> Set[str]:
        """Load subdomains from scan directory"""
        subdomains = set()
        
        # Try to load from live_subdomains.txt (Titan Standard)
        live_file = scan_dir / "subdomains" / "live_subdomains.txt"
        if live_file.exists():
            try:
                with open(live_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            # Extract domain if it's a URL
                            if "://" in line:
                                domain = line.split("://")[1].split("/")[0]
                            else:
                                domain = line
                            subdomains.add(domain)
            except Exception as e:
                print(f"[!] Error loading subdomains: {e}")
        
        # Also try all_passive.txt
        passive_file = scan_dir / "subdomains" / "all_passive.txt"
        if passive_file.exists():
            try:
                with open(passive_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            subdomains.add(line)
            except Exception:
                pass
        
        return subdomains
    
    def _load_takeovers(self, scan_dir: Path) -> Set[str]:
        """Load takeover vulnerabilities from scan directory"""
        takeovers = set()
        
        takeover_file = scan_dir / "subdomains" / "takeovers.txt"
        if takeover_file.exists():
            try:
                with open(takeover_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            takeovers.add(line)
            except Exception as e:
                print(f"[!] Error loading takeovers: {e}")
        
        return takeovers
    
    def _load_port_summary(self, scan_dir: Path) -> Dict[str, List[int]]:
        """Load port scan summary"""
        port_summary = {}
        
        nmap_dir = scan_dir / "nmap"
        if not nmap_dir.exists():
            return port_summary
        
        # Parse nmap output files (Titan Standard)
        for nmap_file in nmap_dir.glob("*.txt"):
            try:
                host = nmap_file.stem
                open_ports = []
                
                with open(nmap_file, 'r') as f:
                    for line in f:
                        # Look for lines like "80/tcp  open  http"
                        if "/tcp" in line and "open" in line:
                            try:
                                port = int(line.split("/")[0].strip())
                                open_ports.append(port)
                            except:
                                continue
                
                if open_ports:
                    port_summary[host] = open_ports
                    
            except Exception as e:
                print(f"[!] Error parsing {nmap_file}: {e}")
        
        return port_summary
    
    def generate_diff_report(self, output_file: str):
        """Generate a detailed diff report"""
        if not self.changes:
            return
        
        with open(output_file, 'w') as f:
            f.write("# Reconnaissance Scan Changes Report\n\n")
            f.write(f"**Total Changes Detected:** {len(self.changes)}\n\n")
            
            # Group by severity
            critical = [c for c in self.changes if c.get("severity") == "critical"]
            high = [c for c in self.changes if c.get("severity") == "high"]
            medium = [c for c in self.changes if c.get("severity") == "medium"]
            low = [c for c in self.changes if c.get("severity") == "low"]
            
            if critical:
                f.write("## 🚨 Critical Changes\n\n")
                for change in critical:
                    f.write(f"- **{change['description']}**\n")
                    if change.get("details"):
                        f.write(f"  - Details: {change['details']}\n")
                f.write("\n")
            
            if high:
                f.write("## ⚠️ High Priority Changes\n\n")
                for change in high:
                    f.write(f"- {change['description']}\n")
                    if change.get("details"):
                        f.write(f"  - Details: {change['details']}\n")
                f.write("\n")
            
            if medium:
                f.write("## 📊 Medium Priority Changes\n\n")
                for change in medium:
                    f.write(f"- {change['description']}\n")
                f.write("\n")
            
            if low:
                f.write("## ℹ️ Low Priority Changes\n\n")
                for change in low:
                    f.write(f"- {change['description']}\n")
                f.write("\n")

    def _check_vulnerabilities(self, previous: Path, current: Path):
        """Check for new critical/high vulnerabilities using summary.json"""
        prev_summary = self._load_json(previous / "summary.json")
        curr_summary = self._load_json(current / "summary.json")
        
        if not prev_summary or not curr_summary:
            return

        prev_vulns = prev_summary.get("findings", {})
        curr_vulns = curr_summary.get("findings", {})
        
        # If total critical or high increased
        if curr_vulns.get("critical", 0) > prev_vulns.get("critical", 0):
            diff = curr_vulns["critical"] - prev_vulns["critical"]
            self.changes.append({
                "type": "new_critical_vulnerability",
                "severity": "critical",
                "description": f"🚨 ALERT: {diff} new CRITICAL vulnerability detected since last scan!",
            })
            
        if curr_vulns.get("high", 0) > prev_vulns.get("high", 0):
            diff = curr_vulns["high"] - prev_vulns["high"]
            self.changes.append({
                "type": "new_high_vulnerability",
                "severity": "high",
                "description": f"⚠️ ALERT: {diff} new HIGH vulnerability detected since last scan!",
            })

    def _load_json(self, path: Path) -> Optional[Dict]:
        """Utility to load JSON safely"""
        if not path.exists():
            return None
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return None
