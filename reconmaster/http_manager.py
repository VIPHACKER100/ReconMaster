import asyncio
import time
import random
import logging
import aiohttp
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger("ReconMaster.HTTP")

class CircuitBreaker:
    """Unified circuit breaker for all HTTP operations to prevent rate limiting and saturation"""
    def __init__(self, threshold: int = 10, timeout: int = 60):
        self.error_count = 0
        self.threshold = threshold
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.open_time = 0.0
        self.timeout = timeout
        self.lock = asyncio.Lock()
    
    async def record_error(self, status_code: int):
        """Record failed request and potentially open the circuit"""
        async with self.lock:
            if status_code in [403, 429, 503]:
                self.error_count += 1
                logger.warning(f"Circuit breaker alert: {self.error_count}/{self.threshold} errors recorded.")
                
                if self.error_count >= self.threshold and self.state == "CLOSED":
                    self.state = "OPEN"
                    self.open_time = time.time()
                    logger.error(f"🚫 CIRCUIT BREAKER OPENED - Rate limiting detected. Cooling down for {self.timeout}s.")
                
    async def record_success(self):
        """Record successful request and recovery"""
        async with self.lock:
            if self.error_count > 0:
                self.error_count = max(0, self.error_count - 1)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                logger.info("✅ Circuit breaker CLOSED - System recovered.")
    
    async def check_can_proceed(self) -> bool:
        """Check if requests can proceed based on current state"""
        async with self.lock:
            if self.state == "CLOSED":
                return True
            
            if self.state == "OPEN":
                elapsed = time.time() - self.open_time
                if elapsed > self.timeout:
                    self.state = "HALF_OPEN"
                    logger.info("🔌 Circuit breaker Entering HALF_OPEN - testing connectivity.")
                    return True
                return False
            
            # HALF_OPEN - allow requests but monitor closely
            return True

class HTTPManager:
    """Centralized manager for HTTP sessions, circuit breakers, and security policies"""
    def __init__(self, threads: int = 10, timeout: int = 20, verify_ssl: bool = True):
        self.threads = threads
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.verify_ssl = verify_ssl
        self.circuit_breaker = CircuitBreaker()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        ]
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Initialize or return the existing ClientSession"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl, limit=self.threads, limit_per_host=30)
            self._session = aiohttp.ClientSession(timeout=self.timeout, connector=connector)
        return self._session

    async def close(self):
        """Close the active session"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(self, method: str, url: str, **kwargs) -> Optional[aiohttp.ClientResponse]:
        """Perform an HTTP request with circuit breaker protection"""
        if not await self.circuit_breaker.check_can_proceed():
            logger.warning(f"Circuit breaker OPEN/COOLDOWN - skipping request: {url}")
            return None

        session = await self.get_session()
        
        # Inject random User-Agent if not provided
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        if 'User-Agent' not in kwargs['headers']:
            kwargs['headers']['User-Agent'] = random.choice(self.user_agents)

        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status in [403, 429, 503]:
                    await self.circuit_breaker.record_error(response.status)
                else:
                    await self.circuit_breaker.record_success()
                
                # Consume content to allow connection reuse if needed
                await response.read()
                return response
        except Exception as e:
            logger.debug(f"HTTP request failed for {url}: {e}")
            await self.circuit_breaker.record_error(500)
            return None
