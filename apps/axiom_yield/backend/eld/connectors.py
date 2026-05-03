"""
backend/eld/connectors.py – ELD Provider API Client
Axiom Yield Broker / LUMINARK Overwatch Integration

Handles async API connections to ELD providers using a shared aiohttp.ClientSession
for connection pooling. This prevents socket exhaustion under high concurrent load.

SINGLETON SCOPE NOTE:
  ELDClient._session is a CLASS-level singleton — it is shared across ALL instances
  of ELDClient regardless of provider. This is intentional: a single connection pool
  serves all outbound ELD requests from this process. The pool reuses TCP connections
  to the same host, improving throughput and reducing latency.

SUPPORTED PROVIDERS:
  - samsara : Full HOS implementation
  - motive  : Base URL registered; HOS implementation pending (raises NotImplementedError)
  - geotab  : Base URL registered; HOS implementation pending (raises NotImplementedError)

CORRECTIONS APPLIED (vs submitted document):
  [1] Documented singleton scope clearly — class-level, not per-provider.
  [3] Motive and Geotab now raise NotImplementedError instead of returning {}
      silently, preventing downstream silent data corruption.
  [4] URLs were wrapped in markdown link syntax in the original — corrected to
      bare URL strings that aiohttp can actually connect to.
  [5] is_evasive false-positive fixed: duty_status is checked first so that
      a missing driveRemainingMinutes key does not flag OFF_DUTY drivers.
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ELDClient:
    """
    Async ELD API client with shared connection pool.

    Usage:
        client = ELDClient("samsara", api_key)
        eld_data = await client.get_hos(driver_id)
    """

    # Class-level session — shared across all ELDClient instances in this process.
    # Reuses TCP connections to the same ELD host, preventing socket exhaustion
    # under high FastAPI concurrency. [FIX 1: documented scope]
    _session: Optional[aiohttp.ClientSession] = None

    def __init__(self, provider: str, api_key: str):
        self.provider   = provider.lower().strip()
        self.api_key    = api_key
        self.base_url   = self._get_base_url()

    def _get_base_url(self) -> str:
        # FIX [4]: bare URL strings, no markdown link wrapping
        urls = {
            "samsara": "https://api.samsara.com/fleet",
            "motive":  "https://api.gomotive.com/v1",
            "geotab":  "https://my.geotab.com/apiv1",
        }
        return urls.get(self.provider, "")

    @classmethod
    def get_session(cls) -> aiohttp.ClientSession:
        """
        Return the shared aiohttp session, creating it if needed.
        Session is recreated if it has been explicitly closed.
        5-second total timeout is set to prevent hung connections.
        """
        if cls._session is None or cls._session.closed:
            timeout = aiohttp.ClientTimeout(total=5)
            cls._session = aiohttp.ClientSession(timeout=timeout)
        return cls._session

    @classmethod
    async def close_session(cls) -> None:
        """
        Gracefully close the shared session.
        Call this from FastAPI's shutdown lifecycle event.
        """
        if cls._session and not cls._session.closed:
            await cls._session.close()
            cls._session = None

    async def get_hos(self, driver_id: str) -> Dict[str, Any]:
        """
        Fetch Hours of Service data for a driver.

        Returns a normalised dict with keys:
            drive_remaining  : float — hours of drive time remaining
            shift_remaining  : float — hours of shift time remaining
            cycle_remaining  : float — hours of cycle time remaining
            duty_status      : str   — OFF_DUTY | SLEEPER_BERTH | DRIVING | ON_DUTY_NOT_DRIVING
            violations       : int   — number of active HOS violations
            is_evasive       : bool  — True if driving with zero time remaining (HOS fraud)

        Raises
        ------
        ValueError          : Unsupported provider string
        NotImplementedError : Provider registered but not yet implemented
        Exception           : Non-200 response from ELD API
        """
        if not self.base_url:
            raise ValueError(
                f"Unsupported ELD provider: '{self.provider}'. "
                f"Supported: samsara, motive, geotab"
            )

        if self.provider == "samsara":
            return await self._get_hos_samsara(driver_id)

        # FIX [3]: raise NotImplementedError instead of silently returning {}
        # which would cause NSDTBuilder to operate on empty data without warning
        if self.provider in ("motive", "geotab"):
            raise NotImplementedError(
                f"ELD provider '{self.provider}' is registered but HOS integration "
                f"is not yet implemented. Use 'samsara' or implement the adapter."
            )

        raise ValueError(f"Unknown provider: '{self.provider}'")

    async def _get_hos_samsara(self, driver_id: str) -> Dict[str, Any]:
        """Fetch and normalise HOS data from Samsara Fleet API."""
        session = self.get_session()
        url     = f"{self.base_url}/drivers/{driver_id}/hos"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with session.get(url, headers=headers) as resp:
            if resp.status == 404:
                raise Exception(f"Driver '{driver_id}' not found in Samsara fleet")
            if resp.status == 401:
                raise Exception("Samsara API key invalid or expired")
            if resp.status != 200:
                raise Exception(
                    f"Samsara ELD API returned HTTP {resp.status} for driver {driver_id}"
                )
            data = await resp.json()
            return self._normalize_samsara(data)

    def _normalize_samsara(self, raw: Dict) -> Dict[str, Any]:
        """
        Translate raw Samsara HOS response to normalised LUMINARK format.

        Samsara response shape (relevant fields):
            clocks.driveRemainingMinutes : int
            clocks.shiftRemainingMinutes : int
            clocks.cycleRemainingMinutes : int
            dutyStatus                   : str
            violations                   : list
        """
        clocks       = raw.get("clocks", {})
        duty_status  = raw.get("dutyStatus", "OFF_DUTY")
        drive_mins   = clocks.get("driveRemainingMinutes")

        # FIX [5]: check duty_status FIRST to avoid false-positive evasive flag
        # when driveRemainingMinutes key is absent (defaults to 0 in original code)
        is_evasive = (
            duty_status == "DRIVING" and
            drive_mins is not None and
            drive_mins == 0
        )

        return {
            "drive_remaining": (drive_mins or 0) / 60.0,
            "shift_remaining": (clocks.get("shiftRemainingMinutes") or 0) / 60.0,
            "cycle_remaining": (clocks.get("cycleRemainingMinutes") or 0) / 60.0,
            "duty_status":     duty_status,
            "violations":      len(raw.get("violations", [])),
            "is_evasive":      is_evasive,
        }
