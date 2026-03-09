from plugins.base import ReconPlugin
import os
import logging
import asyncio
import re

try:
    import aiohttp
    _HAVE_AIOHTTP = True
except ImportError:
    _HAVE_AIOHTTP = False

logger = logging.getLogger("ReconMaster.Plugins.GraphQL")

class GraphQLDiscoveryPlugin(ReconPlugin):
    name = "GraphQL Discovery"
    description = "Detects GraphQL endpoints and attempts introspection"

    # Common GraphQL paths
    GRAPHQL_PATHS = [
        "/graphql", "/graphiql", "/graphql/console", "/v1/graphql",
        "/api/graphql", "/api/v1/graphql", "/query", "/playground",
        "/gql"
    ]

    async def run(self, recon):
        logger.info("Starting GraphQL discovery module...")
        
        # 1. Gather all potential targets (subdomains + crawled URLs)
        targets = set()
        for domain in recon.live_domains:
            targets.add(f"https://{domain}")
            targets.add(f"http://{domain}")
        
        for url in recon.urls:
            # Add base URL of crawled endpoints
            parts = url.split("/", 3)
            if len(parts) >= 3:
                targets.add("/".join(parts[:3]))

        logger.info(f"Probing {len(targets)} targets for GraphQL interfaces...")

        # 2. Run high-speed path probing
        if _HAVE_AIOHTTP:
            await self._probe_graphql_endpoints(recon, targets)
        else:
            logger.warning("aiohttp not found. Skipping GraphQL probing.")

    async def _probe_graphql_endpoints(self, recon, targets):
        connector = aiohttp.TCPConnector(ssl=False, limit=recon.threads, limit_per_host=30)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
            tasks = []
            for base_url in list(targets)[:100]: # Safety limit
                for path in self.GRAPHQL_PATHS:
                    tasks.append(self._check_endpoint(session, f"{base_url.rstrip('/')}{path}", recon))
            
            await asyncio.gather(*tasks)

    async def _check_endpoint(self, session, url, recon):
        if not await recon.circuit_breaker.check_can_proceed():
            return

        try:
            # Query to check if it's a GraphQL endpoint
            query = {"query": "{ __typename }"}
            async with session.post(url, json=query, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "data" in data and "__typename" in data["data"]:
                        logger.warning(f"[!] GraphQL Endpoint Found: {url}")
                        
                        # Attempt introspection
                        introspection_query = {"query": "{__schema{queryType{name}}}"}
                        async with session.post(url, json=introspection_query) as intro_resp:
                            intro_data = await intro_resp.json()
                            is_introspectable = "data" in intro_data
                            
                            severity = "medium" if is_introspectable else "info"
                            msg = "GraphQL Endpoint Discovered (Introspection Enabled)" if is_introspectable else "GraphQL Endpoint Discovered"
                            
                            recon.vulns.append({
                                "info": {
                                    "name": msg,
                                    "severity": severity,
                                    "description": f"Found at {url}. Introspection: {'YES' if is_introspectable else 'NO'}"
                                },
                                "matched-at": url
                            })
                            
                            # Log to findings file
                            gql_file = os.path.join(recon.output_dir, "vulns", "graphql_endpoints.txt")
                            os.makedirs(os.path.dirname(gql_file), exist_ok=True)
                            with open(gql_file, "a") as f:
                                f.write(f"Endpoint: {url} | Introspection: {is_introspectable}\n")
        except:
            pass
