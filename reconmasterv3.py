#!/usr/bin/env python3
import os
import argparse
import concurrent.futures
import json
import time
import asyncio

try:
    import aiohttp

    _HAVE_AIOHTTP = True
except Exception:
    aiohttp = None
    _HAVE_AIOHTTP = False
import logging
from datetime import datetime
import re
# lru_cache removed (unused)
import signal
from utils import safe_run, merge_and_dedupe_text_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ReconMaster")


class ReconMaster:
    def __init__(self, target, output_dir, threads=20, wordlist=None, timeout=30):
        self.target = target
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_dir = output_dir
        self.output_dir = os.path.join(output_dir, f"{target}_{self.timestamp}")
        self.threads = threads
        self.timeout = timeout
        self.subdomains = set()
        self.live_domains = set()
        self.urls = set()
        self.js_files = set()
        self.endpoints = set()
        self.parameters = set()
        self.tech_stack = {}
        self.takeovers = []
        self.broken_links = []
        self.rate_limiter = asyncio.Semaphore(10)  # Limit concurrent requests

        # Default wordlist
        self.wordlist = (
            wordlist if wordlist else "/path/to/n0kovo_subdomains/n0kovo_subdomains.txt"
        )

        # Create output directory structure
        self.create_dirs()

        # Set timeout handler
        signal.signal(signal.SIGALRM, self._timeout_handler)

    def _timeout_handler(self, signum, frame):
        raise TimeoutError("Operation timed out")

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

        os.makedirs(self.output_dir, exist_ok=True)

        # Create directories in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(dirs)) as executor:
            executor.map(lambda d: os.makedirs(d, exist_ok=True), dirs)

        logger.info(f"Created output directory structure at {self.output_dir}")

    async def _run_cmd_async(self, cmd, timeout=None):
        """Run command asynchronously with timeout"""
        try:
            timeout = timeout or self.timeout
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
                return (
                    stdout.decode().strip(),
                    stderr.decode().strip(),
                    process.returncode,
                )
            except asyncio.TimeoutError:
                process.kill()
                logger.warning(f"Command timed out after {timeout}s: {cmd}")
                return "", f"Timeout after {timeout}s", 1

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return "", str(e), 1

    def _run_cmd(self, cmd, timeout=None):
        """Run synchronous command with timeout"""
        try:
            timeout = timeout or self.timeout
            stdout, stderr, rc = safe_run(cmd, timeout=timeout)

            class _R:
                pass

            r = _R()
            r.stdout = stdout
            r.returncode = rc
            return r
        except Exception as e:
            logger.error(f"Command execution error: {e}")

            class _R:
                pass

            r = _R()
            r.stdout = ""
            r.returncode = 1
            return r

    async def passive_subdomain_enum(self):
        """Perform passive subdomain enumeration concurrently"""
        logger.info(f"Starting passive subdomain enumeration for {self.target}")

        subfinder_output = os.path.join(self.output_dir, "subdomains", "subfinder.txt")
        assetfinder_output = os.path.join(
            self.output_dir, "subdomains", "assetfinder.txt"
        )
        amass_output = os.path.join(self.output_dir, "subdomains", "amass.txt")

        # Run tools concurrently
        tasks = [
            self._run_cmd_async(
                f"subfinder -d {self.target} -o {subfinder_output} -silent"
            ),
            self._run_cmd_async(
                f"assetfinder --subs-only {self.target} > {assetfinder_output}"
            ),
            self._run_cmd_async(
                f"amass enum -passive -d {self.target} -o {amass_output}", timeout=300
            ),  # Longer timeout for amass
        ]

        await asyncio.gather(*tasks)

        # Combine results efficiently (cross-platform)
        all_subdomains = os.path.join(self.output_dir, "subdomains", "all_passive.txt")
        merge_and_dedupe_text_files(
            os.path.join(self.output_dir, "subdomains"), "*.txt", all_subdomains
        )

        # Load subdomains
        try:
            with open(all_subdomains, "r") as f:
                self.subdomains = set([line.strip() for line in f if line.strip()])
            logger.info(
                f"Found {len(self.subdomains)} unique subdomains via passive enumeration"
            )
        except FileNotFoundError:
            logger.warning("No subdomains found in passive enumeration")

        return self.subdomains

    async def active_subdomain_enum(self):
        """Perform active subdomain enumeration using brute force with optimized chunks"""
        logger.info(f"Starting active subdomain enumeration for {self.target}")

        # Split wordlist into chunks for parallel processing
        chunk_size = 5000
        ffuf_output_dir = os.path.join(self.output_dir, "subdomains", "ffuf_chunks")
        os.makedirs(ffuf_output_dir, exist_ok=True)

        # Get wordlist line count (pure-Python, cross-platform)
        try:
            total_lines = 0
            with open(self.wordlist, "r", encoding="utf-8", errors="ignore") as wl:
                for _ in wl:
                    total_lines += 1
            chunks = (total_lines // chunk_size) + 1 if total_lines > 0 else 10
        except Exception:
            chunks = 10

        logger.info(f"Splitting wordlist into {chunks} chunks for parallel processing")

        # Create temporary wordlist chunks
        chunk_files = []
        for i in range(chunks):
            chunk_file = f"{ffuf_output_dir}/chunk_{i}.txt"
            start = i * chunk_size + 1
            end = (i + 1) * chunk_size

            # Create chunk files using pure-Python slicing
            try:
                with open(
                    self.wordlist, "r", encoding="utf-8", errors="ignore"
                ) as wl, open(chunk_file, "w", encoding="utf-8") as cf:
                    for lineno, line in enumerate(wl, start=1):
                        if lineno < start:
                            continue
                        if lineno > end:
                            break
                        cf.write(line)
                chunk_files.append(chunk_file)
            except Exception:
                # If creating chunk fails, skip it
                continue

        # Run ffuf on each chunk concurrently
        async def process_chunk(chunk_file, chunk_num):
            output_file = f"{ffuf_output_dir}/ffuf_chunk_{chunk_num}.json"
            cmd = f"ffuf -u http://FUZZ.{self.target} -w {chunk_file} -o {output_file} -of json -s -t 50 -rate 100"
            await self._run_cmd_async(cmd, timeout=300)  # 5 minutes per chunk
            return output_file

        # Process chunks in parallel
        tasks = [
            process_chunk(chunk_file, i) for i, chunk_file in enumerate(chunk_files)
        ]
        chunk_outputs = await asyncio.gather(*tasks)

        # Process results
        new_subdomains = set()
        for output_file in chunk_outputs:
            try:
                with open(output_file, "r") as f:
                    ffuf_data = json.load(f)
                    for result in ffuf_data.get("results", []):
                        if "input" in result and "FUZZ" in result["input"]:
                            subdomain = f"{result['input']['FUZZ']}.{self.target}"
                            new_subdomains.add(subdomain)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"Error processing ffuf results from {output_file}: {e}")

        # Update subdomains
        self.subdomains.update(new_subdomains)

        # Update all subdomains file
        all_subdomains = os.path.join(
            self.output_dir, "subdomains", "all_subdomains.txt"
        )
        with open(all_subdomains, "w") as f:
            for subdomain in sorted(self.subdomains):
                f.write(f"{subdomain}\n")

        logger.info(
            f"Total unique subdomains after brute forcing: {len(self.subdomains)}"
        )

        # Clean up chunk files (cross-platform)
        try:
            for fname in os.listdir(ffuf_output_dir):
                if fname.startswith("chunk_") and fname.endswith(".txt"):
                    try:
                        os.remove(os.path.join(ffuf_output_dir, fname))
                    except Exception:
                        pass
        except FileNotFoundError:
            pass

        return self.subdomains

    async def resolve_live_domains(self):
        """Resolve live domains using httpx with optimized settings"""
        logger.info("Resolving live domains with httpx")

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

        # Run httpx with optimized settings
        cmd = f"httpx -l {all_subdomains} -o {live_domains_file} -status-code -title -tech-detect -follow-redirects -silent -rate-limit 150 -threads {self.threads} -timeout 10"
        await self._run_cmd_async(cmd, timeout=600)  # 10 minutes timeout

        # Load live domains
        try:
            with open(live_domains_file, "r") as f:
                for line in f:
                    if line.strip():
                        domain = line.strip().split(" ")[0]
                        self.live_domains.add(domain)

                        # Extract tech stack info if available
                        parts = line.strip().split(" ")
                        for part in parts:
                            if part.startswith("[") and part.endswith("]"):
                                tech = part[1:-1]
                                if domain not in self.tech_stack:
                                    self.tech_stack[domain] = []
                                self.tech_stack[domain].append(tech)

            logger.info(f"Found {len(self.live_domains)} live domains")
        except FileNotFoundError:
            logger.warning("No live domains found")

        return self.live_domains

    async def take_screenshots(self):
        """Take screenshots of live domains using gowitness with concurrency"""
        logger.info("Taking screenshots with gowitness")

        if not self.live_domains:
            logger.warning(
                "No live domains to screenshot. Run resolve_live_domains first."
            )
            return

        live_domains_file = os.path.join(
            self.output_dir, "subdomains", "live_domains.txt"
        )
        screenshots_dir = os.path.join(self.output_dir, "screenshots")

        # Split domains into chunks for parallel processing
        with open(live_domains_file, "r") as f:
            domains = [line.strip().split(" ")[0] for line in f if line.strip()]

        if not domains:
            logger.warning("No domains found in live domains file")
            return

        # Determine chunk size based on number of domains
        chunk_size = max(5, min(50, len(domains) // (self.threads // 2)))
        chunks = [
            domains[i : i + chunk_size] for i in range(0, len(domains), chunk_size)
        ]

        # Process each chunk with gowitness
        async def process_chunk(chunk, chunk_id):
            chunk_file = os.path.join(self.output_dir, f"chunk_{chunk_id}.txt")
            with open(chunk_file, "w") as f:
                for domain in chunk:
                    f.write(f"{domain}\n")

            # Run gowitness on chunk
            cmd = f"gowitness file -f {chunk_file} -P {screenshots_dir} --no-http --timeout 20"
            await self._run_cmd_async(cmd, timeout=300)

            # Clean up chunk file
            os.remove(chunk_file)

        # Process chunks concurrently
        tasks = [process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        await asyncio.gather(*tasks)

        logger.info(f"Screenshots saved to {screenshots_dir}")

    async def scan_for_takeovers(self):
        """Scan for subdomain takeovers using subzy with optimized settings"""
        logger.info("Scanning for subdomain takeovers with subzy")

        all_subdomains = os.path.join(
            self.output_dir, "subdomains", "all_subdomains.txt"
        )
        takeovers_file = os.path.join(self.output_dir, "subdomains", "takeovers.txt")

        # Run subzy with concurrency
        cmd = f"subzy run --targets {all_subdomains} --output {takeovers_file} --concurrency {self.threads} --timeout 30"
        await self._run_cmd_async(cmd, timeout=600)  # 10 minutes timeout

        # Check results
        try:
            with open(takeovers_file, "r") as f:
                self.takeovers = [line.strip() for line in f if line.strip()]
            if self.takeovers:
                logger.info(
                    f"Found {len(self.takeovers)} potential subdomain takeovers!"
                )
            else:
                logger.info("No subdomain takeovers found")
        except FileNotFoundError:
            logger.info("No subdomain takeovers found")

    async def crawl_endpoints(self):
        """Crawl endpoints using katana with optimized settings"""
        logger.info("Crawling endpoints with katana")

        if not self.live_domains:
            logger.warning(
                "No live domains for crawling. Run resolve_live_domains first."
            )
            return

        live_domains_file = os.path.join(
            self.output_dir, "subdomains", "live_domains.txt"
        )
        urls_file = os.path.join(self.output_dir, "endpoints", "urls.txt")
        js_files = os.path.join(self.output_dir, "js", "js_files.txt")

        # Run optimized katana
        cmd = f"katana -list {live_domains_file} -jc -silent -concurrency {self.threads} -timeout 20 -rate-limit 100 -o {urls_file}"
        await self._run_cmd_async(cmd, timeout=1200)  # 20 minutes timeout

        # Extract JS files efficiently (cross-platform)
        try:
            with open(urls_file, "r", encoding="utf-8") as src, open(
                js_files, "w", encoding="utf-8"
            ) as dst:
                for line in src:
                    line = line.strip()
                    if line and (".js" in line):
                        dst.write(line + "\n")
        except FileNotFoundError:
            pass

        # Process JS files in batches
        endpoints_file = os.path.join(self.output_dir, "endpoints", "js_endpoints.txt")

        # Efficient JS file processing with batched approach
        try:
            with open(js_files, "r") as f:
                js_urls = [line.strip() for line in f if line.strip()]

            if not js_urls:
                logger.info("No JavaScript files found")
                return

            logger.info(f"Processing {len(js_urls)} JavaScript files for endpoints")

            # Process in smaller batches
            batch_size = min(50, max(10, len(js_urls) // 10))
            batches = [
                js_urls[i : i + batch_size] for i in range(0, len(js_urls), batch_size)
            ]

            async def process_js_batch(batch):
                batch_results = []
                for url in batch:
                    async with self.rate_limiter:
                        cmd = f'python3 /path/to/LinkFinder/linkfinder.py -i "{url}" -o cli'
                        stdout, stderr, _ = await self._run_cmd_async(cmd, timeout=30)
                        if stdout:
                            batch_results.append(stdout)
                return batch_results

            # Process batches concurrently but with rate limiting
            tasks = [process_js_batch(batch) for batch in batches]
            batch_results = await asyncio.gather(*tasks)

            # Combine and write results
            with open(endpoints_file, "w") as f:
                for batch_result in batch_results:
                    for result in batch_result:
                        f.write(f"{result}\n")

            # Load data into memory
            with open(urls_file, "r") as f:
                self.urls = set([line.strip() for line in f if line.strip()])
            self.js_files = set(js_urls)

            logger.info(
                f"Discovered {len(self.urls)} URLs and {len(self.js_files)} JavaScript files"
            )
        except Exception as e:
            logger.error(f"Error processing JavaScript files: {e}")

    async def directory_bruteforce(self):
        """Brute force directories using ffuf with optimized approach"""
        logger.info("Brute forcing directories with ffuf")

        if not self.live_domains:
            logger.warning(
                "No live domains for directory brute forcing. Run resolve_live_domains first."
            )
            return

        # Sample domains intelligently - prioritize with interesting tech stacks
        sample_domains = []

        # First add domains with tech stacks of interest
        interesting_techs = [
            "wordpress",
            "joomla",
            "drupal",
            "php",
            "tomcat",
            "jenkins",
        ]
        for domain, techs in self.tech_stack.items():
            if any(tech.lower() in interesting_techs for tech in techs):
                sample_domains.append(domain)

        # Then add other domains up to a maximum
        remaining_slots = min(10, self.threads // 2)
        other_domains = [d for d in self.live_domains if d not in sample_domains]
        sample_domains.extend(other_domains[:remaining_slots])

        # Deduplicate and limit
        sample_domains = list(set(sample_domains))[:10]

        if not sample_domains:
            logger.warning("No domains selected for directory brute forcing")
            return

        logger.info(
            f"Selected {len(sample_domains)} domains for directory brute forcing"
        )

        # Using a more efficient wordlist
        wordlist = "/path/to/n0kovo_subdomains/fuzz/directory-list.txt"

        # Process domains concurrently
        async def brute_domain(domain):
            output_file = os.path.join(
                self.output_dir,
                "endpoints",
                f"{domain.replace('://', '_').replace('.', '_').replace('/', '_')}_dirs.json",
            )

            cmd = (
                f"ffuf -u {domain}/FUZZ -w {wordlist} -mc 200,204,301,302,307,401,403 "
                f"-o {output_file} -of json -s -t 40 -rate 100 -c"
            )
            await self._run_cmd_async(cmd, timeout=300)  # 5 minutes per domain

            # Return interesting paths
            try:
                with open(output_file, "r") as f:
                    data = json.load(f)
                    return [
                        (domain, result.get("url", ""), result.get("status", 0))
                        for result in data.get("results", [])
                    ]
            except (FileNotFoundError, json.JSONDecodeError):
                return []

        # Run brute force tasks
        tasks = [brute_domain(domain) for domain in sample_domains]
        results = await asyncio.gather(*tasks)

        # Flatten and process interesting findings
        interesting_dirs = []
        for domain_results in results:
            for domain, url, status in domain_results:
                if status in (200, 401, 403):  # Interesting status codes
                    interesting_dirs.append((domain, url, status))

        # Save interesting directories
        if interesting_dirs:
            interesting_dirs_file = os.path.join(
                self.output_dir, "endpoints", "interesting_dirs.txt"
            )
            with open(interesting_dirs_file, "w") as f:
                for domain, url, status in interesting_dirs:
                    f.write(f"{status} - {url}\n")

            logger.info(f"Found {len(interesting_dirs)} interesting directories")
        else:
            logger.info("No interesting directories found")

    async def find_parameters(self):
        """Find parameters using Arjun with optimized settings"""
        logger.info("Finding parameters with Arjun")

        endpoints_file = os.path.join(self.output_dir, "endpoints", "urls.txt")
        if not os.path.exists(endpoints_file):
            logger.warning(
                "No endpoints found for parameter discovery. Run crawl_endpoints first."
            )
            return

        params_file = os.path.join(self.output_dir, "params", "parameters.txt")

        # Filter interesting URLs for parameter discovery
        # Look for specific patterns that likely accept parameters
        filtered_urls_file = os.path.join(
            self.output_dir, "endpoints", "param_candidate_urls.txt"
        )

        # Filter promising URLs using Python regex instead of grep
        try:
            import re

            pattern = re.compile(
                r"\.(php|aspx|jsp|do|cgi|pl|py)([?#]|$)|"
                r"(search|query|find|login|register|admin|dashboard|api|get|list|view)",
                re.IGNORECASE,
            )
            with open(endpoints_file, "r", encoding="utf-8") as src, open(
                filtered_urls_file, "w", encoding="utf-8"
            ) as dst:
                for line in src:
                    if line and pattern.search(line):
                        dst.write(line)
        except FileNotFoundError:
            pass

        # Sample filtered URLs
        try:
            with open(filtered_urls_file, "r") as f:
                urls = [line.strip() for line in f if line.strip()]

            if not urls:
                logger.warning("No suitable URLs found for parameter discovery")
                return

            # Limit to a reasonable number, prioritizing URLs with query indicators
            urls.sort(key=lambda u: "?" in u or "=" in u, reverse=True)
            sample_urls = urls[: min(30, len(urls))]

            logger.info(f"Selected {len(sample_urls)} URLs for parameter discovery")

            # Process URLs concurrently with rate limiting
            async def find_params(url):
                temp_file = os.path.join(
                    self.output_dir, "params", f"params_{hash(url) % 10000}.txt"
                )
                cmd = f"arjun -u {url} -oT {temp_file} --passive -t 5 --silent"
                async with self.rate_limiter:
                    await self._run_cmd_async(cmd, timeout=60)
                return temp_file

            # Run in parallel with limit
            tasks = [find_params(url) for url in sample_urls]
            param_files = await asyncio.gather(*tasks)

            # Combine results (pure-Python merge + dedupe)
            params_set = set()
            for temp_file in param_files:
                try:
                    with open(temp_file, "r", encoding="utf-8", errors="ignore") as tf:
                        for line in tf:
                            line = line.strip()
                            if line:
                                params_set.add(line)
                except FileNotFoundError:
                    continue

            try:
                os.makedirs(os.path.dirname(params_file), exist_ok=True)
                with open(params_file, "w", encoding="utf-8") as out:
                    for p in sorted(params_set):
                        out.write(p + "\n")
            except Exception as e:
                logger.error(f"Failed to write params file: {e}")

            # Clean up temp files
            for temp_file in param_files:
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

            # Count parameters
            with open(params_file, "r") as f:
                param_count = sum(1 for _ in f)
            logger.info(f"Found {param_count} unique parameters")

        except Exception as e:
            logger.error(f"Error during parameter discovery: {e}")

    async def check_broken_links(self):
        """Check for broken link hijacking opportunities with optimization"""
        logger.info("Checking for broken links")

        if not self.live_domains:
            logger.warning(
                "No live domains for broken link checking. Run resolve_live_domains first."
            )
            return

        if not _HAVE_AIOHTTP:
            logger.warning("aiohttp is not installed; skipping broken link checks")
            self.broken_links = []
            return

        # Select a subset of domains to avoid excessive time
        sample_size = min(20, len(self.live_domains))
        sample_domains = list(self.live_domains)[:sample_size]

        sample_domains_file = os.path.join(
            self.output_dir, "subdomains", "sample_live_domains.txt"
        )
        with open(sample_domains_file, "w") as f:
            for domain in sample_domains:
                f.write(f"{domain}\n")

        broken_links_file = os.path.join(self.output_dir, "reports", "broken_links.txt")

        # Custom link checking with concurrency and rate limiting
        urls_to_check = []

        # First crawl for external links (pure-Python; aiohttp)
        href_re = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
        for domain in sample_domains:
            try:
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(domain, timeout=30) as resp:
                            try:
                                text = await resp.text()
                            except Exception:
                                text = ""
                    except Exception:
                        # Skip domains that fail to respond
                        continue
            except Exception:
                continue

            if not text:
                continue

            for match in href_re.findall(text):
                # Normalize and filter
                link = match.strip()
                if not link:
                    continue
                if link.startswith("#") or link.lower().startswith("javascript:"):
                    continue
                if link.startswith("/"):
                    # Convert relative links to absolute if the domain contains scheme
                    try:
                        from urllib.parse import urljoin

                        link = urljoin(domain, link)
                    except Exception:
                        pass
                if link.startswith("http") and self.target not in link:
                    urls_to_check.append(link)

        # Check each link
        broken_links = []

        async def check_url(url):
            async with aiohttp.ClientSession() as session:
                try:
                    async with self.rate_limiter:
                        async with session.head(
                            url, allow_redirects=True, timeout=10
                        ) as response:
                            if response.status >= 400:
                                return url, response.status
                except Exception:
                    return url, 0  # Connection error
                return None

        # Process in batches
        batch_size = 50
        for i in range(0, len(urls_to_check), batch_size):
            batch = urls_to_check[i : i + batch_size]
            tasks = [check_url(url) for url in batch]
            results = await asyncio.gather(*tasks)

            # Filter and add broken links
            for result in results:
                if result is not None:
                    url, status = result
                    broken_links.append(f"{status} - {url}")

        # Save results
        with open(broken_links_file, "w") as f:
            for link in broken_links:
                f.write(f"{link}\n")

        self.broken_links = broken_links
        logger.info(f"Found {len(self.broken_links)} potential broken links")

    async def port_scan(self):
        """Scan ports using nmap with optimization"""
        logger.info("Scanning ports with nmap")

        if not self.live_domains:
            logger.warning(
                "No live domains for port scanning. Run resolve_live_domains first."
            )
            return

        # Sample domains more intelligently
        # Select domains from different IP ranges for better coverage
        ips = set()
        selected_domains = []

        # First get IPs for all domains
        cmd = "dig +short "
        for domain in self.live_domains:
            # Extract hostname
            try:
                host = domain.split("://")[1].split("/")[0]
                dig_cmd = f"{cmd} {host}"
                stdout, _, _ = await self._run_cmd_async(dig_cmd, timeout=5)

                if stdout:
                    ip = stdout.split("\n")[0]
                    ip_prefix = ".".join(
                        ip.split(".")[:2]
                    )  # Use first two octets as prefix

                    if ip_prefix not in ips:
                        ips.add(ip_prefix)
                        selected_domains.append((host, ip))

                        # Limit to reasonable number
                        if len(selected_domains) >= 8:
                            break
            except Exception:
                continue

        # If we couldn't get enough domains by IP diversity, add more
        if len(selected_domains) < 5:
            for domain in self.live_domains:
                try:
                    host = domain.split("://")[1].split("/")[0]
                    if not any(host == d[0] for d in selected_domains):
                        selected_domains.append((host, ""))
                        if len(selected_domains) >= 5:
                            break
                except Exception:
                    continue

        logger.info(f"Selected {len(selected_domains)} diverse hosts for port scanning")

        # Process domains concurrently
        async def scan_host(host_info):
            host, ip = host_info
            output_file = os.path.join(
                self.output_dir, "reports", f"{host.replace('.', '_')}_nmap.txt"
            )

            # Optimize nmap scan: first do a quick scan of common ports
            quick_cmd = f"nmap -T4 -F -oN {output_file}.quick {host}"
            await self._run_cmd_async(quick_cmd, timeout=1200)

            # Then do a more thorough scan of top ports
            full_cmd = f"nmap -p- -T4 --top-ports 1000 -oN {output_file} {host}"
            await self._run_cmd_async(full_cmd, timeout=3000)

            # Combine results (pure-Python): append quick output into final output and remove temp
            try:
                quick_path = f"{output_file}.quick"
                if os.path.exists(quick_path):
                    with open(
                        quick_path, "r", encoding="utf-8", errors="ignore"
                    ) as qf, open(output_file, "a", encoding="utf-8") as of:
                        of.write(qf.read())
                    try:
                        os.remove(quick_path)
                    except Exception:
                        pass
            except Exception:
                pass

            return output_file

        # Run scans with limit
        tasks = [scan_host(host_info) for host_info in selected_domains]
        await asyncio.gather(*tasks)

        logger.info("Port scanning completed")

    async def generate_report(self):
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

    async def run_all(self):
        """Run the complete reconnaissance process"""
        start_time = time.time()
        print(
            f"Starting comprehensive reconnaissance for {self.target} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Execute all recon steps with await
        await self.passive_subdomain_enum()
        await self.active_subdomain_enum()
        await self.resolve_live_domains()
        await self.take_screenshots()
        await self.scan_for_takeovers()
        await self.crawl_endpoints()
        await self.directory_bruteforce()
        await self.find_parameters()
        await self.check_broken_links()
        await self.port_scan()
        await self.generate_report()

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

    # Create and run async loop
    loop = asyncio.get_event_loop()

    if args.passive_only:
        # Run passive recon tasks
        loop.run_until_complete(
            asyncio.gather(
                recon.passive_subdomain_enum(),
                recon.resolve_live_domains(),
                recon.take_screenshots(),
            )
        )
    else:
        # Run the full async function
        loop.run_until_complete(recon.run_all())


if __name__ == "__main__":
    main()
