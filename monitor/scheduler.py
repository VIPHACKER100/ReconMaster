#!/usr/bin/env python3
"""
ReconMaster Monitoring Scheduler
Automated reconnaissance scheduling and execution
Version: 2.0.0
Author: VIPHACKER100
"""

import os
import sys
import json
import yaml
import time
import schedule
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Fix encoding for Windows consoles
if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ANSI Color Codes
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_monitoring_banner():
    """Display monitoring system banner"""
    banner = f"""{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════╗
║  ReconMaster Monitoring System v2.0.0        ║
║  Continuous Security Reconnaissance          ║
╚═══════════════════════════════════════════════╝
{Colors.ENDC}"""
    print(banner)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor.diff_detector import DiffDetector
from monitor.alerting import AlertManager


class ReconScheduler:
    """Manages scheduled reconnaissance scans"""
    
    def __init__(self, config_path: str = "config/monitoring_config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.diff_detector = DiffDetector()
        self.alert_manager = AlertManager(self.config.get("alerting", {}))
        self.base_dir = Path(__file__).parent.parent
        self.monitor_dir = self.base_dir / "monitor_results"
        self.monitor_dir.mkdir(exist_ok=True)
        
    def load_config(self) -> Dict:
        """Load monitoring configuration"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            print(f"[!] Config file not found: {config_file}")
            print("[*] Using default configuration")
            return self.get_default_config()
        
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[!] Error loading config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Return default monitoring configuration"""
        return {
            "targets": [],
            "schedules": {
                "daily": [],
                "weekly": [],
                "hourly": []
            },
            "scan_options": {
                "passive_only": False,
                "threads": 10
            },
            "alerting": {
                "enabled": True,
                "email": {
                    "enabled": False
                },
                "slack": {
                    "enabled": False
                },
                "discord": {
                    "enabled": False
                }
            },
            "monitoring": {
                "detect_new_subdomains": True,
                "detect_takeovers": True,
                "detect_port_changes": True,
                "detect_ssl_changes": True
            }
        }
    
    def run_scan(self, target: str, scan_type: str = "full", passive_only_override: Optional[bool] = None) -> Optional[str]:
        """Execute a reconnaissance scan"""
        print(f"\n{Colors.GREEN}[+]{Colors.ENDC} Starting {scan_type} scan for {Colors.CYAN}{target}{Colors.ENDC}")
        print(f"{Colors.YELLOW}[*]{Colors.ENDC} Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Prepare command
        python_exe = sys.executable
        reconmaster_script = self.base_dir / "reconmaster.py"
        output_dir = self.monitor_dir / target / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        cmd = [
            python_exe,
            str(reconmaster_script),
            "-d", target,
            "-o", str(output_dir),
            "-t", str(self.config.get("scan_options", {}).get("threads", 10))
        ]
        
        # Add passive-only flag if configured or overridden
        is_passive = passive_only_override if passive_only_override is not None else self.config.get("scan_options", {}).get("passive_only", False)
        if is_passive:
            cmd.append("--passive-only")
        
        try:
            # Run the scan
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                print(f"[+] Scan completed successfully")
                print(f"[+] Results saved to: {output_dir}")
                return str(output_dir)
            else:
                print(f"[!] Scan failed with exit code {result.returncode}")
                print(f"[!] Error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"[!] Scan timed out after 1 hour")
            return None
        except Exception as e:
            print(f"[!] Error running scan: {e}")
            return None
    
    def process_scan_results(self, target: str, scan_dir: str):
        """Process scan results and detect changes"""
        print(f"\n[+] Processing scan results for {target}")
        
        # Get previous scan for comparison
        previous_scan = self.get_previous_scan(target, scan_dir)
        
        if not previous_scan:
            print("[*] No previous scan found - this is the baseline")
            self.save_scan_metadata(target, scan_dir, is_baseline=True)
            return
        
        # Detect changes
        changes = self.diff_detector.detect_changes(previous_scan, scan_dir, self.config.get("monitoring", {}))
        
        if changes:
            print(f"[!] Detected {len(changes)} changes!")
            for change in changes:
                print(f"  - {change['type']}: {change['description']}")
            
            # Send alerts
            self.alert_manager.send_alerts(target, changes, scan_dir)
        else:
            print("[+] No significant changes detected")
        
        # Save metadata
        self.save_scan_metadata(target, scan_dir, changes=changes)
    
    def get_previous_scan(self, target: str, current_scan: str) -> Optional[str]:
        """Get the most recent previous scan directory"""
        target_dir = self.monitor_dir / target
        if not target_dir.exists():
            return None
        
        # Get all scan directories except current
        scan_dirs = [
            d for d in target_dir.iterdir()
            if d.is_dir() and str(d) != current_scan
        ]
        
        if not scan_dirs:
            return None
        
        # Return most recent
        return str(sorted(scan_dirs)[-1])
    
    def save_scan_metadata(self, target: str, scan_dir: str, is_baseline: bool = False, changes: List = None):
        """Save scan metadata for tracking"""
        metadata = {
            "target": target,
            "scan_dir": scan_dir,
            "timestamp": datetime.now().isoformat(),
            "is_baseline": is_baseline,
            "changes": changes or []
        }
        
        metadata_file = Path(scan_dir) / "scan_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def schedule_scans(self):
        """Set up scheduled scans based on configuration"""
        schedules = self.config.get("schedules", {})
        
        # Hourly scans
        for target in schedules.get("hourly", []):
            schedule.every().hour.do(self.scheduled_scan, target=target, scan_type="hourly")
            print(f"[+] Scheduled hourly scan for {target}")
        
        # Daily scans
        for target in schedules.get("daily", []):
            schedule.every().day.at("02:00").do(self.scheduled_scan, target=target, scan_type="daily")
            print(f"[+] Scheduled daily scan for {target} at 02:00")
        
        # Weekly scans
        for target in schedules.get("weekly", []):
            schedule.every().monday.at("03:00").do(self.scheduled_scan, target=target, scan_type="weekly")
            print(f"[+] Scheduled weekly scan for {target} on Mondays at 03:00")
    
    def scheduled_scan(self, target: str, scan_type: str):
        """Execute a scheduled scan"""
        print(f"\n{'='*60}")
        print(f"[*] Executing scheduled {scan_type} scan")
        print(f"{'='*60}")
        
        scan_dir = self.run_scan(target, scan_type)
        if scan_dir:
            self.process_scan_results(target, scan_dir)
    
    def run_once(self, target: str, passive_only: Optional[bool] = None):
        """Run a single scan immediately"""
        scan_dir = self.run_scan(target, "manual", passive_only_override=passive_only)
        if scan_dir:
            self.process_scan_results(target, scan_dir)
    
    def start_monitoring(self):
        """Start the monitoring scheduler"""
        print_monitoring_banner()
        print(f"{Colors.GREEN}[+]{Colors.ENDC} Loaded configuration from: {Colors.CYAN}{self.config_path}{Colors.ENDC}")
        print(f"{Colors.GREEN}[+]{Colors.ENDC} Monitor results directory: {Colors.CYAN}{self.monitor_dir}{Colors.ENDC}")
        
        # Set up schedules
        self.schedule_scans()
        
        print(f"\n{Colors.GREEN}[+]{Colors.ENDC} Monitoring started. Press Ctrl+C to stop.")
        print(f"{Colors.YELLOW}[*]{Colors.ENDC} Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run scheduler
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[*]{Colors.ENDC} Monitoring stopped by user")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ReconMaster Monitoring Scheduler")
    parser.add_argument("-c", "--config", default="config/monitoring_config.yaml",
                       help="Path to monitoring configuration file")
    parser.add_argument("-t", "--target", help="Run single scan for target")
    parser.add_argument("--passive-only", action="store_true", help="Perform only passive reconnaissance")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as daemon with scheduled scans")
    
    args = parser.parse_args()
    
    scheduler = ReconScheduler(args.config)
    
    if args.target:
        # Run single scan
        scheduler.run_once(args.target, passive_only=args.passive_only)
    elif args.daemon:
        # Run as daemon
        scheduler.start_monitoring()
    else:
        print("Usage:")
        print("  Single scan:     python scheduler.py -t example.com")
        print("  Start daemon:    python scheduler.py --daemon")
        print("  Custom config:   python scheduler.py --daemon -c custom_config.yaml")


if __name__ == "__main__":
    main()
