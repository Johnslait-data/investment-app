"""
Financial Modeling Prep (FMP) API Fetcher v2
Updated for FMP's stable endpoints (post-August 2025)
Uses CIK-based endpoints which work reliably
"""
import requests
import logging
from typing import Optional, Dict
from datetime import datetime
import os
from dotenv import load_dotenv
from data.ticker_cik_mapper import get_cik

load_dotenv()

logger = logging.getLogger(__name__)

FMP_API_BASE = "https://financialmodelingprep.com/stable"

# API usage tracking
_api_calls_today = 0
_last_call_reset = datetime.now().date()


def _track_api_call():
    """Track API calls for monitoring"""
    global _api_calls_today, _last_call_reset

    today = datetime.now().date()
    if today != _last_call_reset:
        _api_calls_today = 0
        _last_call_reset = today

    _api_calls_today += 1
    logger.info(f"API Calls Today: {_api_calls_today}/250 ({_api_calls_today/250*100:.1f}%)")


def get_api_usage() -> Dict:
    """Get current API usage stats"""
    global _api_calls_today
    return {
        "calls_today": _api_calls_today,
        "calls_limit": 250,
        "calls_remaining": 250 - _api_calls_today,
        "usage_pct": (_api_calls_today / 250) * 100,
        "last_reset": _last_call_reset.isoformat(),
    }


class FMPFetcherV2:
    """Fetch stock data from FMP stable endpoints"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FMP fetcher

        Args:
            api_key: FMP API key. If None, reads from FMP_API_KEY env var
        """
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            logger.warning("FMP_API_KEY not found")

    def is_available(self) -> bool:
        """Check if API key is available"""
        return bool(self.api_key)

    def get_stock_profile(self, ticker: str) -> Optional[Dict]:
        """
        Get company profile using stable endpoint

        Args:
            ticker: Stock ticker (e.g., 'AAPL')

        Returns:
            Dict with company info
        """
        if not self.api_key:
            return None

        try:
            cik = get_cik(ticker)
            if not cik:
                logger.warning(f"No CIK mapping for {ticker}")
                return None

            _track_api_call()

            url = f"{FMP_API_BASE}/profile-cik"
            params = {"cik": cik, "apikey": self.api_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"Fetched profile for {ticker}")
                return data[0]
            else:
                logger.warning(f"No profile data for {ticker}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching profile for {ticker}: {e}")
            return None

    def get_all_data(self, ticker: str) -> Optional[Dict]:
        """
        Get all available data for a stock

        Args:
            ticker: Stock ticker

        Returns:
            Consolidated dict with all data
        """
        if not self.api_key:
            return None

        logger.info(f"Fetching all data for {ticker} from FMP...")

        try:
            profile = self.get_stock_profile(ticker)

            if not profile:
                logger.error(f"Could not fetch profile for {ticker}")
                return None

            # Consolidate profile data
            result = {
                "ticker": ticker,
                "source": "FMP",
                "fetched_at": datetime.now().isoformat(),
                "name": profile.get("companyName"),
                "symbol": profile.get("symbol"),
                "price": profile.get("price"),
                "market_cap": profile.get("marketCap"),
                "beta": profile.get("beta"),
                "pe_ratio": profile.get("pe"),  # Some endpoints include this
                "exchange": profile.get("exchange"),
                "currency": profile.get("currency"),
                "industry": profile.get("industry"),
                "website": profile.get("website"),
                "description": profile.get("description"),
                "52week_high": profile.get("range", "").split("-")[1] if profile.get("range") else None,
                "52week_low": profile.get("range", "").split("-")[0] if profile.get("range") else None,
            }

            # Clean up 52W prices
            if result["52week_high"]:
                try:
                    result["52week_high"] = float(result["52week_high"].strip())
                except:
                    result["52week_high"] = None

            if result["52week_low"]:
                try:
                    result["52week_low"] = float(result["52week_low"].strip())
                except:
                    result["52week_low"] = None

            logger.info(f"Successfully consolidated data for {ticker}")
            return result

        except Exception as e:
            logger.error(f"Error consolidating data for {ticker}: {e}")
            return None
