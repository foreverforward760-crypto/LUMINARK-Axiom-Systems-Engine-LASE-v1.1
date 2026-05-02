from typing import List, Dict, Optional
import re


class ThreatIntel:
    """
    Cybersecurity encyclopedia–driven threat scanner.

    Scans asset mentions for pump-and-dump schemes, deepfake impersonations,
    ransomware/breach events, and social-engineering scams.

    In production: wire `_fetch_mentions` to NewsAPI, Reddit, Twitter/X, etc.
    """

    THREAT_PATTERNS: Dict[str, Dict] = {
        "pump_dump": {
            "keywords": [
                "pump", "dump", "to the moon", "group buy", "group signal",
                "telegram", "discord", "signal group", "short squeeze",
                "coordinated", "100x",
            ],
            "severity": "high",
            "description": (
                "Coordinated pump-and-dump language detected. "
                "Retail price manipulation can cause rapid drawdowns once insiders exit."
            ),
        },
        "scam": {
            "keywords": [
                "scam", "fake", "fraud", "ponzi", "pyramid",
                "rug pull", "exit scam", "honeypot",
            ],
            "severity": "critical",
            "description": (
                "Scam indicators found. Asset may be fraudulent or associated with "
                "known bad actors."
            ),
        },
        "deepfake": {
            "keywords": [
                "deepfake", "fake video", "impersonation", "ai-generated",
                "fabricated", "synthetic media",
            ],
            "severity": "high",
            "description": (
                "Deepfake / impersonation content in circulation. "
                "Verify executive statements through official channels only."
            ),
        },
        "ransomware": {
            "keywords": [
                "ransomware", "cyber attack", "data breach", "hack",
                "malware", "phishing", "credential theft", "supply chain attack",
            ],
            "severity": "critical",
            "description": (
                "Cybersecurity incident detected. Operational disruption may impact "
                "revenue, stock price, and regulatory standing."
            ),
        },
        "social_engineering": {
            "keywords": [
                "fake giveaway", "free tokens", "send crypto", "double your money",
                "wallet drain", "airdrop scam",
            ],
            "severity": "medium",
            "description": (
                "Social-engineering campaign targeting investors of this asset. "
                "Do not click unsolicited links related to this ticker."
            ),
        },
    }

    SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    # ---------------------------------------------------------------------------
    # Internal data fetch (mock – replace with real APIs in production)
    # ---------------------------------------------------------------------------

    def _fetch_mentions(self, ticker: str) -> List[str]:
        """
        Returns a list of raw text mentions for the ticker.
        Replace with real API calls (NewsAPI, Reddit, Twitter) in production.
        """
        # Mock mentions – in production these come from external APIs
        mock_db: Dict[str, List[str]] = {
            "GME": [
                "GME pumping on Telegram – join the group now!",
                "GME short squeeze coordinated on Discord",
            ],
            "AAPL": [
                "AAPL CEO deepfake video circulating on social media",
                "AAPL supplier hit by ransomware attack, supply chain disrupted",
            ],
            "DEFAULT": [
                f"{ticker} mentioned in fake giveaway campaign",
            ],
        }
        return mock_db.get(ticker.upper(), mock_db["DEFAULT"])

    # ---------------------------------------------------------------------------
    # Threat matching
    # ---------------------------------------------------------------------------

    def _match_threats(self, text: str) -> Optional[Dict]:
        lower = text.lower()
        for threat_type, meta in self.THREAT_PATTERNS.items():
            if any(kw in lower for kw in meta["keywords"]):
                return {
                    "threat_type": threat_type,
                    "severity": meta["severity"],
                    "pattern_description": meta["description"],
                    "raw_mention": text,
                }
        return None

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def scan_asset(self, ticker: str) -> List[Dict]:
        """
        Scan all recent mentions of `ticker` and return a list of threat alerts,
        sorted by severity (critical → low).
        """
        mentions = self._fetch_mentions(ticker)
        alerts: List[Dict] = []

        for mention in mentions:
            match = self._match_threats(mention)
            if match:
                match["ticker"] = ticker.upper()
                alerts.append(match)

        # De-duplicate by threat_type (keep highest severity)
        seen: Dict[str, Dict] = {}
        for alert in alerts:
            tt = alert["threat_type"]
            if tt not in seen or (
                self.SEVERITY_ORDER[alert["severity"]]
                < self.SEVERITY_ORDER[seen[tt]["severity"]]
            ):
                seen[tt] = alert

        return sorted(seen.values(), key=lambda a: self.SEVERITY_ORDER[a["severity"]])

    def scan_portfolio(self, tickers: List[str]) -> List[Dict]:
        """Scan every ticker and aggregate alerts."""
        all_alerts: List[Dict] = []
        for ticker in tickers:
            all_alerts.extend(self.scan_asset(ticker))
        return all_alerts
