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
        for tool in critical_tools:
            path = shutil.which(tool)
            if not path:
                missing_critical.append(tool)
            else:
                self.tool_paths[tool] = os.path.abspath(path)

        for tool in optional_tools:
            path = shutil.which(tool)
            if path:
                self.tool_paths[tool] = os.path.abspath(path)
            else:
                logger.warning(f"Optional tool missing: {tool}")
        
        return missing_critical

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
