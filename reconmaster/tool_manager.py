import os
import shutil
import asyncio
import logging
import random
from typing import List, Tuple, Dict, Optional
from .utils import safe_run

logger = logging.getLogger("ReconMaster.Tool")

class ToolManager:
    """Manager for external tool discovery and secure execution"""
    def __init__(self, user_agents: List[str]):
        self.tool_paths: Dict[str, str] = {}
        self.user_agents = user_agents
        self.semaphore = asyncio.Semaphore(10) # Default concurrency
        self.dry_run = False

    def set_concurrency(self, threads: int):
        self.semaphore = asyncio.Semaphore(threads)

    def verify_tools(self, critical_tools: List[str], optional_tools: List[str]) -> List[str]:
        """Verify presence of tools and resolve to absolute paths"""
        missing_critical = []
        
        # Helper for install instructions
        install_hints = {
            "subfinder": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
            "assetfinder": "go install github.com/tomnomnom/assetfinder@latest",
            "amass": "go install -v github.com/owasp-amass/amass/v4/...@master",
            "ffuf": "go install github.com/ffuf/ffuf/v2@latest",
            "httpx": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
            "nuclei": "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
            "gowitness": "go install github.com/sensepost/gowitness@latest",
            "katana": "go install github.com/projectdiscovery/katana/cmd/katana@latest"
        }

        for tool in critical_tools:
            path = shutil.which(tool)
            if not path:
                missing_critical.append(tool)
                hint = install_hints.get(tool, f"Please install {tool} manually")
                logger.error(f"CRITICAL Tool Missing: {tool}")
                logger.error(f"  -> Install constraint: {hint}")
            else:
                self.tool_paths[tool] = os.path.abspath(path)
                self._log_tool_version(tool, path)

        for tool in optional_tools:
            path = shutil.which(tool)
            if path:
                self.tool_paths[tool] = os.path.abspath(path)
                self._log_tool_version(tool, path)
            else:
                logger.warning(f"Optional tool missing: {tool}. Some features will be safely skipped.")
        
        return missing_critical

    def _log_tool_version(self, name: str, path: str):
        """Silently grab and log the tool version to aid debugging."""
        import subprocess
        try:
            flag = "-V" if name in ["amass", "arjun", "nmap"] else "-version"
            if name == "gowitness": flag = "version"
            if name == "assetfinder": return # Has no version flag
            
            res = subprocess.run([path, flag], capture_output=True, text=True, timeout=2)
            out = res.stdout.strip() or res.stderr.strip()
            # Grab first line as version
            version_str = out.split('\n')[0][:50]
            logger.debug(f"{name} path: {path} | ver: {version_str}")
        except Exception as e:
            logger.debug(f"Could not determine version for {name}: {e}")

    async def run_command(self, cmd: List[str], timeout: int = 300, env: Optional[Dict[str, str]] = None) -> Tuple[str, str, int]:
        """Execute tool commands asynchronously with security and timeout policies"""
        if not cmd:
            return "", "Empty command", -1

        tool_name = cmd[0].lower()
        processed_cmd = list(cmd)

        # Resolve to absolute path
        if tool_name in self.tool_paths:
            processed_cmd[0] = self.tool_paths[tool_name]

        # Inject User-Agent for known web-facing tools
        UA_TOOLS = {"httpx", "ffuf", "katana", "nuclei", "subfinder", "amass"}
        if tool_name in UA_TOOLS:
            ua = random.choice(self.user_agents)
            # Simple check to avoid double injection if the caller already added it
            if "-H" not in processed_cmd:
                 processed_cmd.extend(["-H", f"User-Agent: {ua}"])

        logger.debug(f"Executing: {' '.join(processed_cmd)}")

        if self.dry_run:
            print(f"[DRY-RUN] Would execute: {' '.join(processed_cmd)}")
            return "", "Dry Run", 0

        try:
            async with asyncio.timeout(timeout + 5):
                loop = asyncio.get_running_loop()
                async with self.semaphore:
                    stdout, stderr, rc = await loop.run_in_executor(
                        None, safe_run, processed_cmd, timeout, env or os.environ.copy()
                    )
            return stdout, stderr, rc
        except asyncio.TimeoutError:
            logger.error(f"Command timed out: {' '.join(processed_cmd)}")
            return "", "Timeout", -1
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return "", str(e), -1
