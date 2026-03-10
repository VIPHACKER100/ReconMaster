#!/usr/bin/env python3
"""
ReconMaster Tool Connectivity Diagnostic Script
Tests all critical and optional tool integrations
Generates a detailed connectivity report
"""

import os
import sys
import shutil
import subprocess
import json
import platform
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

class ToolConnectivityDiagnostic:
    def __init__(self):
        self.report = {
            "scan_date": datetime.now().isoformat(),
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "tools": {},
            "libraries": {},
            "summary": {}
        }
        self.critical_tools = ["subfinder", "assetfinder", "amass", "ffuf", "httpx", "nuclei", "gowitness", "katana"]
        self.optional_tools = ["arjun", "nmap", "dnsx", "subjs"]
        self.required_libs = ["asyncio", "json", "re", "subprocess"]
        self.optional_libs = ["aiohttp", "yaml", "colorama"]

    def check_critical_tools(self) -> Dict:
        """Verify all critical tools are in PATH"""
        print(f"\n{Colors.CYAN}[*] Checking CRITICAL tools...{Colors.ENDC}")
        
        results = {}
        failed = []
        
        for tool in self.critical_tools:
            path = shutil.which(tool)
            if path:
                try:
                    result = subprocess.run(
                        [tool, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    version = result.stdout.split('\n')[0] if result.stdout else "Unknown version"
                    results[tool] = {
                        "status": "✅ INSTALLED",
                        "path": os.path.abspath(path),
                        "version": version.strip()
                    }
                    print(f"  {Colors.GREEN}✅ {tool:15} → {path}{Colors.ENDC}")
                except Exception as e:
                    results[tool] = {
                        "status": "⚠️ INSTALLED BUT ERROR",
                        "path": os.path.abspath(path),
                        "error": str(e)
                    }
                    failed.append(tool)
                    print(f"  {Colors.YELLOW}⚠️ {tool:15} → Found but error: {e}{Colors.ENDC}")
            else:
                results[tool] = {
                    "status": "❌ MISSING",
                    "path": None
                }
                failed.append(tool)
                print(f"  {Colors.RED}❌ {tool:15} → NOT FOUND IN PATH{Colors.ENDC}")
        
        self.report["tools"] = results
        if failed:
            print(f"\n{Colors.RED}[!] CRITICAL: {len(failed)}/{len(self.critical_tools)} tools missing!{Colors.ENDC}")
            print(f"{Colors.YELLOW}    Missing: {', '.join(failed)}{Colors.ENDC}")
            return {"status": "FAILED", "missing": failed}
        else:
            print(f"\n{Colors.GREEN}[✓] All critical tools available!{Colors.ENDC}")
            return {"status": "PASSED"}

    def check_optional_tools(self) -> Dict:
        """Verify optional tools"""
        print(f"\n{Colors.CYAN}[*] Checking OPTIONAL tools...{Colors.ENDC}")
        
        results = self.report.get("tools", {})
        available = []
        missing = []
        
        for tool in self.optional_tools:
            path = shutil.which(tool)
            if path:
                try:
                    result = subprocess.run(
                        [tool, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    version = result.stdout.split('\n')[0] if result.stdout else "Unknown version"
                    results[tool] = {
                        "status": "✅ INSTALLED",
                        "path": os.path.abspath(path),
                        "version": version.strip()
                    }
                    available.append(tool)
                    print(f"  {Colors.GREEN}✅ {tool:15} → {path}{Colors.ENDC}")
                except Exception as e:
                    results[tool] = {
                        "status": "⚠️ INSTALLED BUT ERROR",
                        "path": os.path.abspath(path),
                        "error": str(e)
                    }
                    print(f"  {Colors.YELLOW}⚠️ {tool:15} → Found but error: {e}{Colors.ENDC}")
            else:
                results[tool] = {
                    "status": "❌ NOT INSTALLED",
                    "path": None
                }
                missing.append(tool)
                print(f"  {Colors.YELLOW}⊘  {tool:15} → Not found (optional){Colors.ENDC}")
        
        self.report["tools"] = results
        if missing:
            print(f"\n{Colors.YELLOW}[!] {len(missing)} optional tools not installed: {', '.join(missing)}{Colors.ENDC}")
            print(f"     Some features will be limited without these tools.")
        if available:
            print(f"\n{Colors.GREEN}[✓] {len(available)} optional tools available{Colors.ENDC}")
        
        return {"status": "PASSED", "available": available, "missing": missing}

    def check_python_libraries(self) -> Dict:
        """Verify Python library availability"""
        print(f"\n{Colors.CYAN}[*] Checking Python libraries...{Colors.ENDC}")
        
        lib_results = {}
        
        print(f"\n  {Colors.BOLD}Required Libraries:{Colors.ENDC}")
        for lib in self.required_libs:
            try:
                __import__(lib)
                lib_results[lib] = {"status": "✅ AVAILABLE", "required": True}
                print(f"    {Colors.GREEN}✅ {lib:15} → Loaded{Colors.ENDC}")
            except ImportError:
                lib_results[lib] = {"status": "❌ MISSING", "required": True}
                print(f"    {Colors.RED}❌ {lib:15} → NOT AVAILABLE{Colors.ENDC}")
        
        print(f"\n  {Colors.BOLD}Optional Libraries:{Colors.ENDC}")
        for lib in self.optional_libs:
            try:
                mod = __import__(lib)
                version = getattr(mod, '__version__', 'unknown')
                lib_results[lib] = {"status": "✅ AVAILABLE", "version": version, "required": False}
                print(f"    {Colors.GREEN}✅ {lib:15} → v{version}{Colors.ENDC}")
            except ImportError:
                lib_results[lib] = {"status": "❌ MISSING", "required": False}
                print(f"    {Colors.YELLOW}⊘  {lib:15} → Not installed (optional){Colors.ENDC}")
        
        self.report["libraries"] = lib_results
        
        # Check for aiohttp critical warning
        if lib_results.get("aiohttp", {}).get("status") == "❌ MISSING":
            print(f"\n    {Colors.RED}[!] WARNING: aiohttp not installed!{Colors.ENDC}")
            print(f"        → Required for: JS analysis, sensitive file discovery, API fuzzing")
            print(f"        → Install: pip install aiohttp")
        
        return lib_results

    def check_environment_variables(self) -> Dict:
        """Check for critical environment variables"""
        print(f"\n{Colors.CYAN}[*] Checking environment variables...{Colors.ENDC}")
        
        env_vars = {
            "PATH": os.getenv('PATH', '').split(os.pathsep),
            "RECON_TARGET": os.getenv('RECON_TARGET'),
            "CENSYS_API_ID": "SET" if os.getenv('CENSYS_API_ID') else "NOT SET",
            "CENSYS_API_SECRET": "SET" if os.getenv('CENSYS_API_SECRET') else "NOT SET",
            "SECURITYTRAILS_API_KEY": "SET" if os.getenv('SECURITYTRAILS_API_KEY') else "NOT SET",
            "VIRUSTOTAL_API_KEY": "SET" if os.getenv('VIRUSTOTAL_API_KEY') else "NOT SET"
        }
        
        print(f"\n  {Colors.BOLD}API Credentials:{Colors.ENDC}")
        for var in ["CENSYS_API_ID", "CENSYS_API_SECRET", "SECURITYTRAILS_API_KEY", "VIRUSTOTAL_API_KEY"]:
            status = env_vars[var]
            if status == "SET":
                print(f"    {Colors.GREEN}✅ {var:30} → {status}{Colors.ENDC}")
            else:
                print(f"    {Colors.YELLOW}⊘  {var:30} → {status}{Colors.ENDC}")
        
        print(f"\n  {Colors.BOLD}PATH Configuration:{Colors.ENDC}")
        path_dirs = env_vars["PATH"]
        print(f"    {Colors.CYAN}Paths in PATH variable: {len(path_dirs)}{Colors.ENDC}")
        
        # Check for common Go bin directories
        go_paths = [d for d in path_dirs if 'go' in d.lower() or 'bin' in d.lower()]
        if go_paths:
            print(f"    {Colors.GREEN}✅ Go tool directories found:{Colors.ENDC}")
            for p in go_paths[:5]:
                print(f"       - {p}")
        else:
            print(f"    {Colors.YELLOW}⊘  No obvious Go/bin directories found{Colors.ENDC}")
        
        self.report["environment"] = {
            "api_credentials": {k: v for k, v in env_vars.items() if k != "PATH"},
            "path_count": len(path_dirs)
        }
        
        return env_vars

    def test_tool_api_connectivity(self) -> Dict:
        """Test if tools can make network requests"""
        print(f"\n{Colors.CYAN}[*] Testing network capabilities...{Colors.ENDC}")
        
        connectivity = {}
        
        # Test httpx connectivity
        if shutil.which("httpx"):
            print(f"  {Colors.CYAN}Testing httpx network capabilities...{Colors.ENDC}")
            try:
                result = subprocess.run(
                    ["httpx", "-u", "https://www.google.com", "-p", "-silent"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 or "https://www.google.com" in result.stdout:
                    connectivity["httpx"] = "✅ Network accessible"
                    print(f"    {Colors.GREEN}✅ httpx can reach external sites{Colors.ENDC}")
                else:
                    connectivity["httpx"] = "⚠️ Possible network issue"
                    print(f"    {Colors.YELLOW}⚠️ httpx network test uncertain{Colors.ENDC}")
            except subprocess.TimeoutExpired:
                connectivity["httpx"] = "⚠️ Timeout (possible network issue)"
                print(f"    {Colors.YELLOW}⚠️ httpx network test timed out{Colors.ENDC}")
            except Exception as e:
                connectivity["httpx"] = f"❌ Error: {e}"
                print(f"    {Colors.RED}❌ httpx network test failed: {e}{Colors.ENDC}")
        
        self.report["connectivity"] = connectivity
        return connectivity

    def check_wordlist_availability(self) -> Dict:
        """Check for reconnaissance wordlists"""
        print(f"\n{Colors.CYAN}[*] Checking wordlists...{Colors.ENDC}")
        
        wordlist_paths = [
            ("dns_common", "wordlists/dns_common.txt"),
            ("subdomains_new", "wordlists/subdomains_new.txt"),
            ("directory_list", "wordlists/directory-list.txt"),
            ("php_fuzz", "wordlists/php_fuzz.txt"),
            ("api_endpoints", "wordlists/api_endpoints.txt"),
            ("common", "wordlists/common.txt"),
            ("quickhits", "wordlists/quickhits.txt"),
            ("params", "wordlists/params.txt"),
        ]
        
        wordlists = {}
        found = 0
        
        for name, path in wordlist_paths:
            full_path = Path(path)
            if full_path.exists():
                size = full_path.stat().st_size / 1024  # KB
                wordlists[name] = {
                    "status": "✅ FOUND",
                    "path": str(full_path.absolute()),
                    "size_kb": round(size, 2),
                    "lines": sum(1 for _ in open(full_path, "r", encoding="utf-8", errors="ignore"))
                }
                found += 1
                print(f"  {Colors.GREEN}✅ {name:20} → {size:.1f}KB ({wordlists[name]['lines']} lines){Colors.ENDC}")
            else:
                wordlists[name] = {"status": "❌ NOT FOUND", "path": str(full_path.absolute())}
                print(f"  {Colors.YELLOW}⊘  {name:20} → Not found{Colors.ENDC}")
        
        self.report["wordlists"] = wordlists
        if found > 0:
            print(f"\n{Colors.GREEN}[✓] Found {found}/{len(wordlist_paths)} wordlists{Colors.ENDC}")
        else:
            print(f"\n{Colors.YELLOW}[!] No wordlists found. Recon functionality may be limited.{Colors.ENDC}")
        
        return wordlists

    def generate_connectivity_summary(self) -> Dict:
        """Generate comprehensive connectivity summary"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}  RECONMASTER TOOL CONNECTIVITY REPORT{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.ENDC}\n")
        
        critical_ready = sum(1 for t in self.report["tools"].values() 
                            if t.get("status") == "✅ INSTALLED")
        critical_total = len(self.critical_tools)
        
        optional_ready = sum(1 for t in self.report["tools"].values() 
                            if "optional" in str(t.get("status", "")).lower() or t.get("status") == "✅ INSTALLED")
        
        libs_ready = sum(1 for l in self.report["libraries"].values() 
                        if l.get("status") == "✅ AVAILABLE")
        libs_total = len(self.required_libs) + len(self.optional_libs)
        
        summary = {
            "critical_tools_ready": critical_ready,
            "critical_tools_total": critical_total,
            "optional_tools_ready": optional_ready,
            "libraries_ready": libs_ready,
            "libraries_total": libs_total,
            "overall_status": "READY" if critical_ready == critical_total else "INCOMPLETE"
        }
        
        print(f"{Colors.BOLD}TOOLS AVAILABILITY:{Colors.ENDC}")
        print(f"  Critical:  {critical_ready}/{critical_total} installed → ", end="")
        if critical_ready == critical_total:
            print(f"{Colors.GREEN}✅ READY{Colors.ENDC}")
        else:
            print(f"{Colors.RED}❌ MISSING {critical_total - critical_ready} tools{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}LIBRARIES STATUS:{Colors.ENDC}")
        print(f"  Python:    {libs_ready}/{libs_total} available")
        if self.report["libraries"].get("aiohttp", {}).get("status") == "✅ AVAILABLE":
            print(f"             {Colors.GREEN}✅ aiohttp found (JS analysis enabled){Colors.ENDC}")
        else:
            print(f"             {Colors.YELLOW}⚠️ aiohttp missing (some features disabled){Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}WORDLISTS:{Colors.ENDC}")
        wordlist_count = sum(1 for w in self.report.get("wordlists", {}).values() 
                            if w.get("status") == "✅ FOUND")
        print(f"  Available: {wordlist_count} wordlists")
        
        if critical_ready == critical_total:
            print(f"\n{Colors.BOLD}{Colors.GREEN}✅ SYSTEM READY FOR RECONNAISSANCE{Colors.ENDC}")
        else:
            print(f"\n{Colors.BOLD}{Colors.RED}❌ CRITICAL TOOLS MISSING - INSTALLATION REQUIRED{Colors.ENDC}")
        
        self.report["summary"] = summary
        return summary

    def generate_json_report(self, filepath: str = "reconmaster_connectivity_report.json"):
        """Export detailed report as JSON"""
        with open(filepath, "w") as f:
            json.dump(self.report, f, indent=2)
        print(f"\n{Colors.CYAN}[✓] Detailed report saved: {filepath}{Colors.ENDC}")
        return filepath

    def run_full_diagnostic(self):
        """Execute complete diagnostic suite"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}ReconMaster Tool Connectivity Diagnostic{Colors.ENDC}")
        print(f"{Colors.CYAN}Running on {self.report['platform']} with Python {self.report['python_version']}{Colors.ENDC}\n")
        
        # Run all checks
        self.check_critical_tools()
        self.check_optional_tools()
        self.check_python_libraries()
        self.check_environment_variables()
        self.test_tool_api_connectivity()
        self.check_wordlist_availability()
        
        # Generate summary
        self.generate_connectivity_summary()
        
        # Export report
        report_file = self.generate_json_report()
        
        # Final status
        if self.report["summary"]["critical_tools_ready"] == self.report["summary"]["critical_tools_total"]:
            print(f"\n{Colors.BOLD}{Colors.GREEN}[SUCCESS] All critical tools are properly connected!{Colors.ENDC}")
            print(f"{Colors.GREEN}You can now run ReconMaster reconnaissance scans.{Colors.ENDC}\n")
            return 0
        else:
            missing = self.report["summary"]["critical_tools_total"] - self.report["summary"]["critical_tools_ready"]
            print(f"\n{Colors.BOLD}{Colors.RED}[FAILURE] {missing} critical tool(s) missing!{Colors.ENDC}")
            print(f"\n{Colors.YELLOW}Installation Instructions:{Colors.ENDC}")
            print(f"  Linux/macOS:  ./install_reconmaster.sh")
            print(f"  Windows:      powershell -File install_tools_final.ps1")
            print(f"  Manual Go:    go install github.com/projectdiscovery/{{tool}}@latest\n")
            return 1

if __name__ == "__main__":
    diagnostic = ToolConnectivityDiagnostic()
    exit_code = diagnostic.run_full_diagnostic()
    sys.exit(exit_code)
