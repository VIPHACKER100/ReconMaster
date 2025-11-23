#!/usr/bin/env python3
import os
import argparse
import subprocess
import json
import time
from datetime import datetime

try:
    import tqdm
except Exception:
    # Minimal fallback so scripts can run without the 'tqdm' package installed
    class _DummyTqdmModule:
        def tqdm(self, *args, **kwargs):
            class _D:
                def __init__(self, *a, **k):
                    pass

                def update(self, n=1):
                    pass

                def close(self):
                    pass

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

            return _D()

    tqdm = _DummyTqdmModule()
from utils import safe_run, merge_and_dedupe_text_files


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

        # Default wordlist using n0kovo_subdomains instead of seclists
        self.wordlist = (
            wordlist if wordlist else "/path/to/n0kovo_subdomains/n0kovo_subdomains.txt"
        )

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

        # Progress bar for directory creation
        with tqdm.tqdm(
            total=len(dirs),
            desc="Creating directories",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
        ) as pbar:
            for dir_path in dirs:
                os.makedirs(dir_path, exist_ok=True)
                pbar.update(1)

        print(f"[+] Created output directory structure at {self.output_dir}")

    def passive_subdomain_enum(self):
        """Perform passive subdomain enumeration"""
        print(f"\n[+] Starting passive subdomain enumeration for {self.target}")

        # Tools to run for passive enumeration
        tools = [
            {
                "name": "subfinder",
                "cmd": f"subfinder -d {self.target} -o {os.path.join(self.output_dir, 'subdomains', 'subfinder.txt')}",
            },
            {
                "name": "assetfinder",
                "cmd": f"assetfinder --subs-only {self.target} > {os.path.join(self.output_dir, 'subdomains', 'assetfinder.txt')}",
            },
            {
                "name": "amass passive",
                "cmd": f"amass enum -passive -d {self.target} -o {os.path.join(self.output_dir, 'subdomains', 'amass.txt')}",
            },
        ]

        # Run tools with progress bar
        with tqdm.tqdm(
            total=len(tools),
            desc="Passive enumeration",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        ) as pbar:
            for tool in tools:
                print(f"[*] Running {tool['name']}...")
                stdout, stderr, rc = safe_run(tool["cmd"])
                if rc != 0:
                    print(f"[!] {tool['name']} error: {stderr}")
                pbar.update(1)

        # Combine results (cross-platform)
        all_subdomains = os.path.join(self.output_dir, "subdomains", "all_passive.txt")
        merge_and_dedupe_text_files(
            os.path.join(self.output_dir, "subdomains"), "*.txt", all_subdomains
        )

        # Load subdomains
        try:
            with open(all_subdomains, "r") as f:
                self.subdomains = set([line.strip() for line in f])
            print(
                f"[+] Found {len(self.subdomains)} unique subdomains via passive enumeration"
            )
        except FileNotFoundError:
            print("[!] No subdomains found in passive enumeration")

        return self.subdomains

    def active_subdomain_enum(self):
        """Perform active subdomain enumeration using brute force"""
        print(f"\n[+] Starting active subdomain enumeration for {self.target}")

        # Use ffuf for brute forcing subdomains
        ffuf_output = os.path.join(self.output_dir, "subdomains", "ffuf_brute.json")
        print(f"[*] Running ffuf with wordlist {self.wordlist}...")

        # Count lines in wordlist for progress estimation
        try:
            stdout, stderr, rc = safe_run(["wc", "-l", self.wordlist])
            if rc == 0 and stdout:
                total_words = int(stdout.strip().split()[0])
            else:
                total_words = 50000
        except Exception:
            total_words = 50000  # Default estimation if wc fails

        # Create progress bar
        progress_bar = tqdm.tqdm(
            total=total_words,
            desc="Brute forcing subdomains",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        # Run ffuf with progress monitoring
        # Run ffuf (blocking via safe_run) -- keep blocking behaviour for now
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

        # ffuf run completed (blocking). Update progress bar to completion.
        try:
            progress_bar.update(total_words - progress_bar.n)
        except Exception:
            pass
        progress_bar.close()

        # Process ffuf results
        try:
            with open(ffuf_output, "r") as f:
                ffuf_data = json.load(f)
                for result in ffuf_data.get("results", []):
                    if "input" in result and "FUZZ" in result["input"]:
                        subdomain = f"{result['input']['FUZZ']}.{self.target}"
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

        # Count subdomains to resolve
        try:
            with open(all_subdomains, "r") as f:
                subdomain_count = sum(1 for _ in f)
        except Exception:
            subdomain_count = len(self.subdomains) if self.subdomains else 100

        # Create progress bar
        progress_bar = tqdm.tqdm(
            total=subdomain_count,
            desc="Resolving domains",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        # Run httpx
        stdout, stderr, rc = safe_run(
            [
                "httpx",
                "-l",
                all_subdomains,
                "-o",
                live_domains_file,
                "-status-code",
                "-title",
                "-tech-detect",
                "-follow-redirects",
            ]
        )

        # httpx run completed (blocking). Update progress bar to completion.
        try:
            progress_bar.update(subdomain_count - progress_bar.n)
        except Exception:
            pass
        progress_bar.close()

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

        # Count live domains
        try:
            with open(live_domains_file, "r") as f:
                domain_count = sum(1 for _ in f)
        except Exception:
            domain_count = len(self.live_domains)

        # Create progress bar
        progress_bar = tqdm.tqdm(
            total=domain_count,
            desc="Taking screenshots",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        # Run gowitness
        stdout, stderr, rc = safe_run(
            [
                "gowitness",
                "file",
                "-f",
                live_domains_file,
                "-P",
                screenshots_dir,
                "--no-http",
            ]
        )

        # gowitness run completed (blocking). Update progress bar to completion.
        try:
            progress_bar.update(domain_count - progress_bar.n)
        except Exception:
            pass
        progress_bar.close()

        print(f"[+] Screenshots saved to {screenshots_dir}")

    def scan_for_takeovers(self):
        """Scan for subdomain takeovers using subzy"""
        print("\n[+] Scanning for subdomain takeovers with subzy")

        all_subdomains = os.path.join(
            self.output_dir, "subdomains", "all_subdomains.txt"
        )
        takeovers_file = os.path.join(self.output_dir, "subdomains", "takeovers.txt")

        # Count subdomains to check
        try:
            with open(all_subdomains, "r") as f:
                subdomain_count = sum(1 for _ in f)
        except Exception:
            subdomain_count = len(self.subdomains) if self.subdomains else 100

        # Create progress bar
        progress_bar = tqdm.tqdm(
            total=subdomain_count,
            desc="Scanning for takeovers",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        # Run subzy
        stdout, stderr, rc = safe_run(
            [
                "subzy",
                "run",
                "--targets",
                all_subdomains,
                "--output",
                takeovers_file,
            ]
        )

        # subzy run completed (blocking). Update progress bar to completion.
        try:
            progress_bar.update(subdomain_count - progress_bar.n)
        except Exception:
            pass
        progress_bar.close()

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

        # Count live domains
        try:
            with open(live_domains_file, "r") as f:
                domain_count = sum(1 for _ in f)
        except Exception:
            domain_count = len(self.live_domains)

        # Create progress bar for katana
        progress_bar = tqdm.tqdm(
            total=domain_count,
            desc="Crawling endpoints",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        # Run katana to discover URLs
        print("[*] Running katana for URL discovery...")
        process = subprocess.Popen(
            ["katana", "-list", live_domains_file, "-jc", "-o", urls_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Monitor process and update progress bar
        while process.poll() is None:
            time.sleep(1)
            # Estimate progress based on time (rough estimation)
            progress = min(progress_bar.n + 1, domain_count)
            progress_bar.update(progress - progress_bar.n)

        progress_bar.close()

        # Extract JS files (cross-platform)
        print("[*] Extracting JavaScript files...")
        try:
            with open(urls_file, "r", encoding="utf-8") as src, open(
                js_files, "w", encoding="utf-8"
            ) as dst:
                for line in src:
                    line = line.strip()
                    if line and (
                        line.endswith(".js") or ".js?" in line or ".js#" in line
                    ):
                        dst.write(line + "\n")
        except FileNotFoundError:
            pass

        # Run LinkFinder on JS files for endpoint discovery
        try:
            with open(js_files, "r") as f:
                js_file_list = [line.strip() for line in f]
        except Exception:
            js_file_list = []

        if js_file_list:
            print("[*] Running LinkFinder on JS files...")
            endpoints_file = os.path.join(
                self.output_dir, "endpoints", "js_endpoints.txt"
            )

            # Progress bar for LinkFinder
            with tqdm.tqdm(
                total=len(js_file_list),
                desc="Analyzing JS files",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            ) as js_pbar:
                for js_file in js_file_list:
                    # Run LinkFinder and append stdout to endpoints_file (no shell redirect)
                    try:
                        result = subprocess.run(
                            [
                                "python3",
                                "/path/to/LinkFinder/linkfinder.py",
                                "-i",
                                js_file,
                                "-o",
                                "cli",
                            ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                        )
                        if result.stdout:
                            try:
                                with open(endpoints_file, "a", encoding="utf-8") as ef:
                                    ef.write(result.stdout)
                            except Exception:
                                pass
                    except Exception:
                        pass
                    js_pbar.update(1)

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

        # Using n0kovo_subdomains/fuzz directory wordlist instead of seclists
        wordlist = "/path/to/n0kovo_subdomains/fuzz/directory-list.txt"

        # Count words in wordlist (pure-Python)
        try:
            word_count = 0
            with open(wordlist, "r", encoding="utf-8", errors="ignore") as wl:
                for _ in wl:
                    word_count += 1
            if word_count == 0:
                word_count = 10000
        except Exception:
            word_count = 10000  # Default estimation if counting fails

        # Progress bar for all domains
        with tqdm.tqdm(
            total=len(sample_domains),
            desc="Directory bruteforce progress",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} domains [{elapsed}<{remaining}]",
        ) as domain_pbar:

            for domain in sample_domains:
                output_file = os.path.join(
                    self.output_dir,
                    "endpoints",
                    f"{domain.replace('://', '_').replace('.', '_')}_dirs.json",
                )
                print(f"[*] Brute forcing directories for {domain}...")

                # Progress bar for current domain
                with tqdm.tqdm(
                    total=word_count,
                    desc=f"Domain: {domain}",
                    leave=False,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
                ) as word_pbar:

                    process = subprocess.Popen(
                        [
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
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    # Monitor process and update progress bar
                    while process.poll() is None:
                        time.sleep(1)
                        # Estimate progress based on time (rough estimation)
                        progress = min(word_pbar.n + 100, word_count)
                        word_pbar.update(progress - word_pbar.n)

                domain_pbar.update(1)

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

        # Progress bar for parameter finding
        with tqdm.tqdm(
            total=len(urls),
            desc="Finding parameters",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} URLs [{elapsed}<{remaining}]",
        ) as url_pbar:

            for url in urls:
                print(f"[*] Finding parameters for {url}...")
                try:
                    subprocess.run(
                        [
                            "arjun",
                            "-u",
                            url,
                            "-oT",
                            params_file,
                            "--passive",
                            "-t",
                            "10",
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                except Exception:
                    pass
                url_pbar.update(1)

        print("[+] Parameter finding completed")

    def check_broken_links(self):
        """Check for broken link hijacking opportunities"""
        print("\n[+] Checking for broken links with socialhunter")

        if not self.live_domains:
            print(
                "[!] No live domains for broken link checking. Run resolve_live_domains first."
            )
            return

        live_domains_file = os.path.join(
            self.output_dir, "subdomains", "live_domains.txt"
        )
        broken_links_file = os.path.join(self.output_dir, "reports", "broken_links.txt")

        # Count live domains
        try:
            with open(live_domains_file, "r") as f:
                domain_count = sum(1 for _ in f)
        except Exception:
            domain_count = len(self.live_domains)

        # Create progress bar
        progress_bar = tqdm.tqdm(
            total=domain_count,
            desc="Checking for broken links",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        # Run socialhunter
        process = subprocess.Popen(
            ["socialhunter", "-l", live_domains_file, "-o", broken_links_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Monitor process and update progress bar
        while process.poll() is None:
            time.sleep(1)
            # Estimate progress based on time (rough estimation)
            progress = min(progress_bar.n + 2, domain_count)
            progress_bar.update(progress - progress_bar.n)

        progress_bar.close()

        # Check results
        try:
            with open(broken_links_file, "r") as f:
                self.broken_links = [line.strip() for line in f if line.strip()]
            print(f"[+] Found {len(self.broken_links)} potential broken links")
        except FileNotFoundError:
            print("[+] No broken links found")

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

        # Progress bar for port scanning
        with tqdm.tqdm(
            total=len(sample_domains),
            desc="Port scanning progress",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} hosts [{elapsed}<{remaining}]",
        ) as domain_pbar:

            for domain in sample_domains:
                # Extract host from URL
                host = domain.split("://")[1].split("/")[0]
                output_file = os.path.join(
                    self.output_dir, "reports", f"{host}_nmap.txt"
                )
                print(f"[*] Scanning ports for {host}...")

                # Run nmap
                process = subprocess.Popen(
                    ["nmap", "-p-", "-T4", "-sC", "-sV", host, "-o", output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Wait for completion
                process.wait()
                domain_pbar.update(1)

        print("[+] Port scanning completed")

    def generate_report(self):
        """Generate a comprehensive report"""
        print("\n[+] Generating comprehensive report")

        report_file = os.path.join(self.output_dir, "reports", "summary_report.md")

        # Progress bar for report generation
        with tqdm.tqdm(
            total=5,
            desc="Generating report",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} sections [{elapsed}<{remaining}]",
        ) as report_pbar:

            with open(report_file, "w") as f:
                f.write(f"# Reconnaissance Report for {self.target}\n\n")
                f.write(
                    f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
                report_pbar.update(1)

                f.write("## Summary\n\n")
                f.write(f"- Target: {self.target}\n")
                f.write(f"- Total Subdomains Discovered: {len(self.subdomains)}\n")
                f.write(f"- Live Domains: {len(self.live_domains)}\n")
                f.write(f"- Potential Subdomain Takeovers: {len(self.takeovers)}\n")
                f.write(f"- URLs Discovered: {len(self.urls)}\n")
                f.write(f"- JavaScript Files: {len(self.js_files)}\n")
                f.write(f"- Broken Links: {len(self.broken_links)}\n\n")
                report_pbar.update(1)

                # Add subdomain takeovers if any
                if self.takeovers:
                    f.write("## Potential Subdomain Takeovers\n\n")
                    for takeover in self.takeovers:
                        f.write(f"- {takeover}\n")
                    f.write("\n")
                report_pbar.update(1)

                # Add broken links if any
                if self.broken_links:
                    f.write("## Broken Links\n\n")
                    for link in self.broken_links[
                        :20
                    ]:  # Limit to 20 to avoid huge reports
                        f.write(f"- {link}\n")
                    if len(self.broken_links) > 20:
                        f.write(f"- ... and {len(self.broken_links) - 20} more\n")
                    f.write("\n")
                report_pbar.update(1)

                f.write("## Next Steps\n\n")
                f.write("1. Review subdomain takeover opportunities\n")
                f.write("2. Test discovered endpoints for vulnerabilities\n")
                f.write("3. Analyze JavaScript files for sensitive information\n")
                f.write("4. Test parameters for injection vulnerabilities\n")
                f.write("5. Check broken links for potential hijacking\n")
                report_pbar.update(1)

        print(f"[+] Report generated: {report_file}")

    def run_all(self):
        """Run the complete reconnaissance process"""
        start_time = time.time()
        print(
            f"Starting comprehensive reconnaissance for {self.target} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Define all steps
        steps = [
            ("Passive Subdomain Enumeration", self.passive_subdomain_enum),
            ("Active Subdomain Enumeration", self.active_subdomain_enum),
            ("Resolving Live Domains", self.resolve_live_domains),
            ("Taking Screenshots", self.take_screenshots),
            ("Scanning for Takeovers", self.scan_for_takeovers),
            ("Crawling Endpoints", self.crawl_endpoints),
            ("Directory Bruteforcing", self.directory_bruteforce),
            ("Finding Parameters", self.find_parameters),
            ("Checking Broken Links", self.check_broken_links),
            ("Port Scanning", self.port_scan),
            ("Generating Report", self.generate_report),
        ]

        # Overall progress bar
        with tqdm.tqdm(
            total=len(steps),
            desc="Overall Progress",
            position=0,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} steps [{elapsed}<{remaining}]",
        ) as overall_pbar:

            # Execute all steps
            for step_name, step_func in steps:
                print(f"\n[+] Step: {step_name}")
                step_func()
                overall_pbar.update(1)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n[+] Reconnaissance completed in {duration:.2f} seconds")
        print(f"[+] Results saved to: {self.output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="ReconMaster: Automated Reconnaissance Framework"
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
    else:
        recon.run_all()


if __name__ == "__main__":
    main()
