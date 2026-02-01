#!/usr/bin/env python3
"""
Rate Limiting Module for ReconMaster

Implements token bucket algorithm for request rate limiting to prevent
overwhelming targets and avoid detection/blocking.

Author: viphacker100
License: MIT
"""

import time
import threading
from typing import Optional, Callable
from datetime import datetime, timedelta


class RateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    
    Implements the token bucket algorithm to allow bursts while
    maintaining average rate limit. Thread-safe for concurrent usage.
    """
    
    def __init__(
        self,
        rate: float = 10.0,
        capacity: Optional[float] = None,
        name: str = "RateLimiter"
    ) -> None:
        """
        Initialize rate limiter.
        
        Args:
            rate: Tokens per second (default: 10.0)
            capacity: Maximum tokens in bucket (default: same as rate)
            name: Name for logging/identification
        """
        self.rate = max(0.1, rate)  # Minimum 0.1 tokens/sec
        self.capacity = capacity if capacity else self.rate
        self.tokens = float(self.capacity)
        self.name = name
        self.lock = threading.Lock()
        self.last_update = time.time()
    
    def _refill(self) -> None:
        """
        Refill tokens based on elapsed time.
        
        Called internally before checking/consuming tokens.
        """
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now
    
    def acquire(
        self,
        tokens: float = 1.0,
        blocking: bool = True,
        timeout: Optional[float] = None
    ) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire (default: 1.0)
            blocking: Wait for tokens if necessary (default: True)
            timeout: Maximum time to wait in seconds (default: None)
            
        Returns:
            True if tokens acquired, False if timeout or non-blocking
        """
        if tokens < 0:
            raise ValueError(f"tokens must be >= 0, got {tokens}")
        
        if tokens == 0:
            return True
        
        deadline = time.time() + (timeout or float('inf'))
        
        with self.lock:
            while True:
                self._refill()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True
                
                if not blocking:
                    return False
                
                # Calculate wait time
                wait_time = (tokens - self.tokens) / self.rate
                if time.time() + wait_time > deadline:
                    return False
                
                # Release lock during wait
                self.lock.release()
                time.sleep(min(wait_time, 0.1))  # Wake up every 100ms
                self.lock.acquire()
    
    def try_acquire(self, tokens: float = 1.0) -> bool:
        """
        Try to acquire tokens without blocking.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens acquired immediately, False otherwise
        """
        return self.acquire(tokens, blocking=False)
    
    def reset(self) -> None:
        """Reset bucket to full capacity."""
        with self.lock:
            self.tokens = self.capacity
            self.last_update = time.time()
    
    def get_available(self) -> float:
        """Get number of available tokens without acquiring."""
        with self.lock:
            self._refill()
            return self.tokens
    
    def get_rate(self) -> float:
        """Get current rate in tokens per second."""
        return self.rate
    
    def set_rate(self, rate: float) -> None:
        """
        Change rate limit.
        
        Args:
            rate: New rate in tokens per second
        """
        with self.lock:
            self._refill()
            self.rate = max(0.1, rate)
    
    def __repr__(self) -> str:
        """String representation of rate limiter."""
        available = self.get_available()
        return (
            f"RateLimiter(name='{self.name}', "
            f"rate={self.rate:.1f}/sec, "
            f"available={available:.1f}/{self.capacity})"
        )


class AdaptiveRateLimiter(RateLimiter):
    """
    Adaptive rate limiter that adjusts rate based on response times.
    
    Automatically reduces rate if requests are slow, increases if fast.
    Useful for avoiding overwhelming targets while maintaining efficiency.
    """
    
    def __init__(
        self,
        initial_rate: float = 10.0,
        min_rate: float = 1.0,
        max_rate: float = 50.0,
        adjustment_factor: float = 0.9,
        name: str = "AdaptiveRateLimiter"
    ) -> None:
        """
        Initialize adaptive rate limiter.
        
        Args:
            initial_rate: Starting rate in tokens per second
            min_rate: Minimum allowed rate
            max_rate: Maximum allowed rate
            adjustment_factor: Factor to adjust rate (0-1)
            name: Identifier for logging
        """
        super().__init__(rate=initial_rate, name=name)
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.adjustment_factor = adjustment_factor
        self.request_times: list = []
        self.slow_requests = 0
        self.fast_requests = 0
    
    def record_request(self, duration: float) -> None:
        """
        Record response time and adjust rate if needed.
        
        Args:
            duration: Time taken for request in seconds
        """
        self.request_times.append(duration)
        
        # Keep only last 100 requests
        if len(self.request_times) > 100:
            self.request_times.pop(0)
        
        # Adjust rate based on average response time
        if len(self.request_times) >= 10:
            avg_time = sum(self.request_times) / len(self.request_times)
            
            if avg_time > 5.0:  # Slow responses
                self.slow_requests += 1
                new_rate = self.rate * self.adjustment_factor
                self.set_rate(max(self.min_rate, new_rate))
            elif avg_time < 0.5 and self.slow_requests == 0:  # Fast responses
                self.fast_requests += 1
                if self.fast_requests >= 5:  # Need consistent fast responses
                    new_rate = min(self.max_rate, self.rate / self.adjustment_factor)
                    self.set_rate(new_rate)
                    self.fast_requests = 0
    
    def get_stats(self) -> dict:
        """Get adaptation statistics."""
        if not self.request_times:
            return {}
        
        return {
            'current_rate': self.rate,
            'avg_response_time': sum(self.request_times) / len(self.request_times),
            'min_response_time': min(self.request_times),
            'max_response_time': max(self.request_times),
            'total_requests': len(self.request_times) + self.slow_requests + self.fast_requests
        }


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


def rate_limit_decorator(
    limiter: RateLimiter,
    tokens: float = 1.0,
    timeout: float = 10.0
):
    """
    Decorator to apply rate limiting to functions.
    
    Args:
        limiter: RateLimiter instance
        tokens: Tokens to consume per call
        timeout: Max time to wait for tokens
        
    Returns:
        Decorated function with rate limiting
        
    Example:
        limiter = RateLimiter(rate=5.0)
        
        @rate_limit_decorator(limiter, tokens=1.0)
        def make_request(url):
            return requests.get(url)
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            if not limiter.acquire(tokens, timeout=timeout):
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {func.__name__}: "
                    f"could not acquire {tokens} token(s) within {timeout}s"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
