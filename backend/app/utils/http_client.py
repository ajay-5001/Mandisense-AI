"""
MandiSense Shared Async HTTP Client
==================================
Manages connection pooling and lifecycle for outgoing API calls (Gemini, OpenWeather, Google Maps, Mandi Price API).
"""

import httpx
from typing import Optional

_async_client: Optional[httpx.AsyncClient] = None

def get_async_client() -> httpx.AsyncClient:
    """Get or initialize the global shared httpx.AsyncClient instance."""
    global _async_client
    if _async_client is None or _async_client.is_closed:
        # Initializing client with standard connection limits and timeouts
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=20)
        _async_client = httpx.AsyncClient(limits=limits, timeout=30.0)
    return _async_client

async def close_async_client() -> None:
    """Close the global client session upon app shutdown."""
    global _async_client
    if _async_client is not None and not _async_client.is_closed:
        await _async_client.aclose()
        _async_client = None
