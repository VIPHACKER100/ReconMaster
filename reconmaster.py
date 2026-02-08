#!/usr/bin/env python3
"""
ReconMaster - Automated Reconnaissance Framework
Version: 2.0.0
Author: VIPHACKER100
GitHub: https://github.com/VIPHACKER100/ReconMaster
"""

import os
import sys
import argparse
import json
import time
import re
from datetime import datetime
from utils import safe_run, merge_and_dedupe_text_files, find_wordlist

# Fix encoding for Windows consoles
if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        # Fallback for older versions
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Version Info
VERSION = "2.0.0"
AUTHOR = "VIPHACKER100"
GITHUB = "https://github.com/VIPHACKER100/ReconMaster"

def print_banner():
    """Display ReconMaster ASCII banner"""
    banner = f"""{Colors.CYAN}{Colors.BOLD}
╦═╗╔═╗╔═╗╔═╗╔╗╔╔╦╗╔═╗╔═╗╔╦╗╔═╗╦═╗
╠╦╝║╣ ║  ║ ║║║║║║║╠═╣╚═╗ ║ ║╣ ╠╦╝
╩╚═╚═╝╚═╝╚═╝╝╚╝╩ ╩╩ ╩╚═╝ ╩ ╚═╝╩╚═
{Colors.ENDC}{Colors.YELLOW}
    Automated Reconnaissance Framework v{VERSION}
    {Colors.CYAN}Author: {Colors.GREEN}{AUTHOR}
    {Colors.CYAN}GitHub: {Colors.BLUE}{GITHUB}
{Colors.ENDC}
{Colors.RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}
    """
    print(banner)


class ReconMaster:
    def __init__(self, target, output_dir, threads=10, wordlist=None):
        self.target = target
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_dir = output_dir
        self.output_dir = os.path.join(output_dir, f"{target}_{self.timestamp}")
        self.threads = threads
        self.subdomains = set()
        self.live_domains = set()
        self.urls = set()
        self.js_files = set()
        self.endpoints = set()
        self.parameters = set()
        self.tech_stack = {}
        self.takeovers = []
        self.broken_links = []

        # Default wordlist if none specified
        # Prefer provided wordlist, otherwise try common locations and bundled fallback
        if wordlist:
            self.wordlist = wordlist
        else:
            preferred = [
                os.path.join(os.getcwd(), "wordlists", "subdomains.txt"),
                os.path.join(os.getcwd(), "wordlists", "dns_common.txt"),
            ]
            found = find_wordlist(preferred)
            self.wordlist = found if found else preferred[0]

        # Create output directory structure
        self.create_dirs()

    def create_dirs(self):
        """Create directory structure for outputs"""
        dirs = [
            self.output_dir,
            f"{self.output_dir}/subdomains",
            f"{self.output_dir}/screenshots",
            f"{self.output_dir}/endpoints",
            f"{self.output_dir}/js",
            f"{self.output_dir}/params",
            f"{self.output_dir}/reports",
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

        print(f"{Colors.GREEN}[+]{Colors.ENDC} Created output directory structure at {Colors.CYAN}{self.output_dir}{Colors.ENDC}")

    def passive_subdomain_enum(self):
        """Perform passive subdomain enumeration"""
        print(f"\n[+] Starting passive subdomain enumeration for {self.target}")
        # Subfinder
        subfinder_output = os.path.join(self.output_dir, "subdomains", "subfinder.txt")
        print("[*] Running subfinder...")
        stdout, stderr, rc = safe_run(
            ["subfinder", "-d", self.target, "-o", subfinder_output]
        )
        if rc != 0:
            print(f"[!] subfinder error: {stderr}")

        # Assetfinder (capture stdout into file)
        assetfinder_output = os.path.join(
            self.output_dir, "subdomains", "assetfinder.txt"
        )
        print("[*] Running assetfinder...")
        stdout, stderr, rc = safe_run(["assetfinder", "--subs-only", self.target])
        if rc == 0 and stdout:
            with open(assetfinder_output, "w", encoding="utf-8") as f:
                f.write(stdout)
        else:
            print(f"[!] assetfinder error: {stderr}")

        # Amass passive
        amass_output = os.path.join(self.output_dir, "subdomains", "amass.txt")
        print("[*] Running amass passive (5m timeout)...")
        # For Amass 4.x, 'enum -passive' is used.
        stdout, stderr, rc = safe_run(
            ["amass", "enum", "-passive", "-d", self.target],
            timeout=300
        )
        if rc == 0 and stdout:
            with open(amass_output, "w", encoding="utf-8") as f:
                f.write(stdout)
        elif rc != 0:
            print(f"[!] amass error: {stderr}")

        # Combine results using python helper (cross-platform)
        all_passive_raw = os.path.join(self.output_dir, "subdomains", "all_passive_raw.txt")
        merge_and_dedupe_text_files(
            os.path.join(self.output_dir, "subdomains"), "*.txt", all_passive_raw
        )

        # Smart extraction: find anything matching subdomains of target
        print("[*] Extracting and cleaning subdomains...")
        cleaned_subdomains = set()
        subdomain_regex = re.compile(rf"([a-z0-9.-]+\.{re.escape(self.target)})", re.IGNORECASE)
        
        try:
            with open(all_passive_raw, "r", encoding="utf-8") as f:
                for line in f:
                    matches = subdomain_regex.findall(line)
                    for match in matches:
                        cleaned_subdomains.add(match.lower())
        except FileNotFoundError:
            pass

        # Save cleaned results
        all_passive = os.path.join(self.output_dir, "subdomains", "all_passive.txt")
        with open(all_passive, "w", encoding="utf-8") as f:
            for sub in sorted(cleaned_subdomains):
                f.write(sub + "\n")

        self.subdomains.update(cleaned_subdomains)
        print(f"[+] Found {len(cleaned_subdomains)} unique subdomains via passive enumeration")

        return self.subdomains

    def active_subdomain_enum(self):
        """Perform active subdomain enumeration using brute force"""
        print(f"\n[+] Starting active subdomain enumeration for {self.target}")

        # Use ffuf for brute forcing subdomains
        ffuf_output = os.path.join(self.output_dir, "subdomains", "ffuf_brute.json")
        print(f"[*] Running ffuf with wordlist {self.wordlist}...")

        print(f"[*] Running ffuf with wordlist {self.wordlist}...")
        stdout, stderr, rc = safe_run(
            [
                "ffuf",
                "-u",
                f"http://FUZZ.{self.target}",
                "-w",
                self.wordlist,
                "-o",
                ffuf_output,
                "-of",
                "json",
                "-s",
            ]
        )
        if rc != 0:
            print(f"[!] ffuf error: {stderr}")

        # Process ffuf results
        try:
            with open(ffuf_output, "r", encoding="utf-8") as f:
                ffuf_data = json.load(f)
                for result in ffuf_data.get("results", []):
                    # ffuf JSON result has 'input'->'FUZZ' or 'value'
                    inp = result.get("input") or result.get("value")
                    if isinstance(inp, dict) and "FUZZ" in inp:
                        fuzz = inp.get("FUZZ")
                    else:
                        fuzz = result.get("input", "")
                    if fuzz:
                        subdomain = f"{fuzz}.{self.target}"
                        self.subdomains.add(subdomain)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[!] Error processing ffuf results: {e}")

        # Update all subdomains file
        all_subdomains = os.path.join(
            self.output_dir, "subdomains", "all_subdomains.txt"
        )
        with open(all_subdomains, "w") as f:
            for subdomain in sorted(self.subdomains):
                f.write(f"{subdomain}\n")

        print(
            f"[+] Total unique subdomains after brute forcing: {len(self.subdomains)}"
        )
        return self.subdomains

    def resolve_live_domains(self):
        """Resolve live domains using httpx"""
        print("\n[+] Resolving live domains with httpx")

        all_subdomains = os.path.join(
            self.output_dir, "subdomains", "all_subdomains.txt"
        )
        live_domains_file = os.path.join(
            self.output_dir, "subdomains", "live_domains.txt"
        )

        # First ensure we have the combined subdomain list
        if not os.path.exists(all_subdomains):
            with open(all_subdomains, "w") as f:
                for subdomain in sorted(self.subdomains):
                    f.write(f"{subdomain}\n")

        # Run httpx (use safe_run wrapper)
        cmd = [
            "httpx",
            "-list",
            all_subdomains,
            "-o",
            live_domains_file,
            "-status-code",
            "-title",
            "-tech-detect",
            "-follow-redirects",
        ]
        stdout, stderr, rc = safe_run(cmd)
        if rc != 0:
            print(f"[!] httpx error: {stderr}")

        # Load live domains
        try:
            with open(live_domains_file, "r") as f:
                for line in f:
                    if line.strip():
                        domain = line.strip().split(" ")[0]
                        self.live_domains.add(domain)
            print(f"[+] Found {len(self.live_domains)} live domains")
        except FileNotFoundError:
            print("[!] No live domains found")

        return self.live_domains

    def take_screenshots(self):
        """Take screenshots of live domains using gowitness"""
        print("\n[+] Taking screenshots with gowitness")

        if not self.live_domains:
            print("[!] No live domains to screenshot. Run resolve_live_domains first.")
            return

        live_domains_file = os.path.join(
            self.output_dir, "subdomains", "live_domains.txt"
        )
        screenshots_dir = os.path.join(self.output_dir, "screenshots")

        # Run gowitness v3
        cmd = [
            "gowitness",
            "scan",
            "file",
            "--file",
            live_domains_file,
            "-s",
            screenshots_dir,
            "--no-http",
        ]
        stdout, stderr, rc = safe_run(cmd)
        if rc != 0:
            print(f"[!] gowitness error: {stderr}")

        print(f"[+] Screenshots saved to {screenshots_dir}")

    def scan_for_takeovers(self):
        """Scan for subdomain takeovers using nuclei"""
        print("\n[+] Scanning for subdomain takeovers with nuclei")

        all_subdomains = os.path.join(
            self.output_dir, "subdomains", "all_subdomains.txt"
        )
        takeovers_file = os.path.join(self.output_dir, "subdomains", "takeovers.txt")

        # Run nuclei with takeover templates
        cmd = ["nuclei", "-l", all_subdomains, "-t", "takeovers", "-o", takeovers_file]
        stdout, stderr, rc = safe_run(cmd)
        if rc != 0:
            print(f"[!] nuclei error: {stderr}")

        # Check results
        try:
            with open(takeovers_file, "r") as f:
                self.takeovers = [line.strip() for line in f if line.strip()]
            if self.takeovers:
                print(f"[+] Found {len(self.takeovers)} potential subdomain takeovers!")
            else:
                print("[+] No subdomain takeovers found")
        except FileNotFoundError:
            print("[+] No subdomain takeovers found")

    def crawl_endpoints(self):
        """Crawl endpoints using katana"""
        print("\n[+] Crawling endpoints with katana")

        if not self.live_domains:
            print("[!] No live domains for crawling. Run resolve_live_domains first.")
            return

        live_domains_file = os.path.join(
            self.output_dir, "subdomains", "live_domains.txt"
        )
        urls_file = os.path.join(self.output_dir, "endpoints", "urls.txt")
        js_files = os.path.join(self.output_dir, "js", "js_files.txt")

        # Run katana to discover URLs
        print("[*] Running katana for URL discovery...")
        cmd = ["katana", "-list", live_domains_file, "-jc", "-o", urls_file]
        stdout, stderr, rc = safe_run(cmd)
        if rc != 0:
            print(f"[!] katana error: {stderr}")

        # Extract JS files (pure-Python)
        print("[*] Extracting JavaScript files...")
        try:
            with open(urls_file, "r", encoding="utf-8") as src, open(
                js_files, "w", encoding="utf-8"
            ) as dst:
                for line in src:
                    line = line.strip()
                    if line.endswith(".js") or ".js?" in line or ".js#" in line:
                        dst.write(line + "\n")
        except FileNotFoundError:
            pass

        # Run LinkFinder on JS files for endpoint discovery (invoke per-file)
        print("[*] Running LinkFinder on JS files...")
        endpoints_file = os.path.join(self.output_dir, "endpoints", "js_endpoints.txt")
        try:
            with open(js_files, "r", encoding="utf-8") as f:
                for url in [line.strip() for line in f if line.strip()]:
                    cmd = [
                        sys.executable,
                        os.path.join(os.getcwd(), "tools", "LinkFinder", "linkfinder.py"),
                        "-i",
                        url,
                        "-o",
                        "cli",
                    ]
                    stdout, stderr, rc = safe_run(cmd)
                    if rc == 0 and stdout:
                        with open(endpoints_file, "a", encoding="utf-8") as ef:
                            ef.write(stdout + "\n")
        except FileNotFoundError:
            pass

        # Load results
        try:
            with open(urls_file, "r") as f:
                self.urls = set([line.strip() for line in f])
            with open(js_files, "r") as f:
                self.js_files = set([line.strip() for line in f])
            print(
                f"[+] Discovered {len(self.urls)} URLs and {len(self.js_files)} JavaScript files"
            )
        except FileNotFoundError:
            print("[!] Issue loading crawled endpoints")

    def directory_bruteforce(self):
        """Brute force directories using ffuf"""
        print("\n[+] Brute forcing directories with ffuf")

        if not self.live_domains:
            print(
                "[!] No live domains for directory brute forcing. Run resolve_live_domains first."
            )
            return

        # Using a smaller list of domains for dir bruteforcing to avoid excessive time
        sample_domains = (
            list(self.live_domains)[:5]
            if len(self.live_domains) > 5
            else list(self.live_domains)
        )

        wordlist = os.path.join(os.getcwd(), "wordlists", "directory-list.txt")
        for domain in sample_domains:
            output_file = os.path.join(
                self.output_dir,
                "endpoints",
                f"{domain.replace('://', '_').replace('.', '_')}_dirs.json",
            )
            print(f"[*] Brute forcing directories for {domain}...")
            cmd = [
                "ffuf",
                "-u",
                f"{domain}/FUZZ",
                "-w",
                wordlist,
                "-mc",
                "200,204,301,302,307,401,403",
                "-o",
                output_file,
                "-of",
                "json",
                "-s",
            ]
            stdout, stderr, rc = safe_run(cmd)
            if rc != 0:
                print(f"[!] ffuf error for {domain}: {stderr}")

        print("[+] Directory brute forcing completed")

    def find_parameters(self):
        """Find parameters using Arjun"""
        print("\n[+] Finding parameters with Arjun")

        endpoints_file = os.path.join(self.output_dir, "endpoints", "urls.txt")
        if not os.path.exists(endpoints_file):
            print(
                "[!] No endpoints found for parameter discovery. Run crawl_endpoints first."
            )
            return

        # Sample a few URLs to avoid excessive time
        with open(endpoints_file, "r") as f:
            urls = [line.strip() for line in f][:20]  # Limit to 20 URLs

        params_file = os.path.join(self.output_dir, "params", "parameters.txt")

        for url in urls:
            print(f"[*] Finding parameters for {url}...")
            cmd = ["arjun", "-u", url, "-oT", params_file, "--passive", "-t", "10"]
            stdout, stderr, rc = safe_run(cmd)
            if rc != 0:
                print(f"[!] arjun error for {url}: {stderr}")

        print("[+] Parameter finding completed")

    def check_broken_links(self):
        """Placeholder for broken link checking (socialhunter is deprecated)"""
        print("\n[+] Skipping broken link check (tool unavailable)")
        return

    def port_scan(self):
        """Scan ports using nmap"""
        print("\n[+] Scanning ports with nmap")

        if not self.live_domains:
            print(
                "[!] No live domains for port scanning. Run resolve_live_domains first."
            )
            return

        # Sample domains for port scanning to avoid excessive time
        sample_domains = (
            list(self.live_domains)[:5]
            if len(self.live_domains) > 5
            else list(self.live_domains)
        )
        for domain in sample_domains:
            host = domain.split("://")[1].split("/")[0]
            output_file = os.path.join(self.output_dir, "reports", f"{host}_nmap.txt")
            print(f"[*] Scanning ports for {host} (Top 1000)...")

            cmd = ["nmap", "--top-ports", "1000", "-T4", "-sC", "-sV", host, "-o", output_file]
            stdout, stderr, rc = safe_run(cmd)
            if rc != 0:
                print(f"[!] nmap error for {host}: {stderr}")

        print("[+] Port scanning completed")

    def generate_report(self):
        """Generate a comprehensive report"""
        print("\n[+] Generating comprehensive report")

        report_file = os.path.join(self.output_dir, "reports", "summary_report.md")

        with open(report_file, "w") as f:
            f.write(f"# Reconnaissance Report for {self.target}\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Summary\n\n")
            f.write(f"- Target: {self.target}\n")
            f.write(f"- Total Subdomains Discovered: {len(self.subdomains)}\n")
            f.write(f"- Live Domains: {len(self.live_domains)}\n")
            f.write(f"- Potential Subdomain Takeovers: {len(self.takeovers)}\n")
            f.write(f"- URLs Discovered: {len(self.urls)}\n")
            f.write(f"- JavaScript Files: {len(self.js_files)}\n")
            f.write(f"- Broken Links: {len(self.broken_links)}\n\n")

            # Add subdomain takeovers if any
            if self.takeovers:
                f.write("## Potential Subdomain Takeovers\n\n")
                for takeover in self.takeovers:
                    f.write(f"- {takeover}\n")
                f.write("\n")

            # Add broken links if any
            if self.broken_links:
                f.write("## Broken Links\n\n")
                for link in self.broken_links[:20]:  # Limit to 20 to avoid huge reports
                    f.write(f"- {link}\n")
                if len(self.broken_links) > 20:
                    f.write(f"- ... and {len(self.broken_links) - 20} more\n")
                f.write("\n")

            f.write("## Next Steps\n\n")
            f.write("1. Review subdomain takeover opportunities\n")
            f.write("2. Test discovered endpoints for vulnerabilities\n")
            f.write("3. Analyze JavaScript files for sensitive information\n")
            f.write("4. Test parameters for injection vulnerabilities\n")
            f.write("5. Check broken links for potential hijacking\n")

        print(f"[+] Report generated: {report_file}")

    def run_all(self):
        """Run the complete reconnaissance process"""
        start_time = time.time()
        print(
            f"Starting comprehensive reconnaissance for {self.target} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Execute all recon steps
        self.passive_subdomain_enum()
        self.active_subdomain_enum()
        self.resolve_live_domains()
        self.take_screenshots()
        self.scan_for_takeovers()
        self.crawl_endpoints()
        self.directory_bruteforce()
        self.find_parameters()
        self.check_broken_links()
        self.port_scan()
        self.generate_report()

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n[+] Reconnaissance completed in {duration:.2f} seconds")
        print(f"[+] Results saved to: {self.output_dir}")


def main():
    # Display banner
    print_banner()
    
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}ReconMaster{Colors.ENDC}: Automated Reconnaissance Framework v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CYAN}Examples:{Colors.ENDC}
  {Colors.GREEN}Passive scan:{Colors.ENDC}     python reconmaster.py -d example.com --passive-only
  {Colors.GREEN}Full scan:{Colors.ENDC}        python reconmaster.py -d example.com
  {Colors.GREEN}Custom output:{Colors.ENDC}    python reconmaster.py -d example.com -o ./scans -t 20

{Colors.YELLOW}For monitoring:{Colors.ENDC}   python monitor/scheduler.py -t example.com

{Colors.CYAN}Documentation:{Colors.ENDC} README.md | MONITORING.md | QUICKSTART.md
{Colors.BLUE}GitHub:{Colors.ENDC} {GITHUB}
        """
    )
    parser.add_argument("-d", "--domain", required=True, help="Target domain to scan")
    parser.add_argument(
        "-o", "--output", default="./recon_results", help="Output directory for results"
    )
    parser.add_argument(
        "-t", "--threads", type=int, default=10, help="Number of threads to use"
    )
    parser.add_argument(
        "-w", "--wordlist", help="Custom wordlist for subdomain brute forcing"
    )
    parser.add_argument(
        "--passive-only",
        action="store_true",
        help="Only perform passive reconnaissance",
    )

    args = parser.parse_args()

    recon = ReconMaster(
        target=args.domain,
        output_dir=args.output,
        threads=args.threads,
        wordlist=args.wordlist,
    )

    if args.passive_only:
        recon.passive_subdomain_enum()
        recon.resolve_live_domains()
        recon.take_screenshots()
        recon.generate_report()
    else:
        recon.run_all()


if __name__ == "__main__":
    main()
