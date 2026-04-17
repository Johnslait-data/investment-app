"""
Financial Modeling Prep (FMP) API Fetcher
Alternative to yfinance with better rate limiting
250 requests/day free tier

OPTIMIZATION STRATEGY:
- Cache for 48-72 hours (less API calls)
- Batch multiple metrics in single request when possible
- Only fetch required fields
- Monitor API usage
"""
import requests
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
import os
from pathlib import Path
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

FMP_API_BASE = "https://financialmodelingprep.com/api/v3"

# API usage tracking
_api_calls_today = 0
_last_call_reset = datetime.now().date()
_call_times = []  # Track last 10 calls for rate limiting


def _track_api_call():
    """Track API calls for monitoring"""
    global _api_calls_today, _last_call_reset, _call_times

    today = datetime.now().date()
    if today != _last_call_reset:
        _api_calls_today = 0
        _call_times = []
        _last_call_reset = today

    _api_calls_today += 1
    _call_times.append(datetime.now())

    # Keep only last 10 calls
    if len(_call_times) > 10:
        _call_times.pop(0)

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


class FMPFetcher:
    """Fetch stock data from Financial Modeling Prep API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FMP fetcher

        Args:
            api_key: FMP API key. If None, reads from FMP_API_KEY env var
        """
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            logger.warning("FMP_API_KEY not found. FMP fetcher will not work.")
            logger.warning("Get free API key at: https://site.financialmodelingprep.com/register")

    def is_available(self) -> bool:
        """Check if API key is available"""
        return bool(self.api_key)

    def get_stock_profile(self, ticker: str) -> Optional[Dict]:
        """
        Get company profile

        Args:
            ticker: Stock ticker (e.g., 'AAPL')

        Returns:
            Dict with company info
        """
        if not self.api_key:
            return None

        try:
            _track_api_call()
            url = f"{FMP_API_BASE}/profile/{ticker}"
            params = {"apikey": self.api_key}

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

    def get_financial_ratios(self, ticker: str) -> Optional[Dict]:
        """
        Get financial ratios (P/E, P/B, etc.)

        Args:
            ticker: Stock ticker

        Returns:
            Dict with ratios
        """
        if not self.api_key:
            return None

        try:
            _track_api_call()
            url = f"{FMP_API_BASE}/ratios/{ticker}"
            params = {"apikey": self.api_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"Fetched ratios for {ticker}")
                return data[0]  # Most recent
            else:
                logger.warning(f"No ratio data for {ticker}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching ratios for {ticker}: {e}")
            return None

    def get_balance_sheet(self, ticker: str) -> Optional[Dict]:
        """
        Get balance sheet data

        Args:
            ticker: Stock ticker

        Returns:
            Dict with balance sheet
        """
        if not self.api_key:
            return None

        try:
            _track_api_call()
            url = f"{FMP_API_BASE}/balance-sheet-statement/{ticker}"
            params = {"apikey": self.api_key, "limit": 1}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"Fetched balance sheet for {ticker}")
                return data[0]  # Most recent
            else:
                logger.warning(f"No balance sheet data for {ticker}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching balance sheet for {ticker}: {e}")
            return None

    def get_income_statement(self, ticker: str) -> Optional[Dict]:
        """
        Get income statement data

        Args:
            ticker: Stock ticker

        Returns:
            Dict with income statement
        """
        if not self.api_key:
            return None

        try:
            _track_api_call()
            url = f"{FMP_API_BASE}/income-statement/{ticker}"
            params = {"apikey": self.api_key, "limit": 1}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"Fetched income statement for {ticker}")
                return data[0]  # Most recent
            else:
                logger.warning(f"No income statement data for {ticker}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching income statement for {ticker}: {e}")
            return None

    def get_quote(self, ticker: str) -> Optional[Dict]:
        """
        Get current price and market data

        Args:
            ticker: Stock ticker

        Returns:
            Dict with quote data
        """
        if not self.api_key:
            return None

        try:
            _track_api_call()
            url = f"{FMP_API_BASE}/quote/{ticker}"
            params = {"apikey": self.api_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"Fetched quote for {ticker}")
                return data[0]
            else:
                logger.warning(f"No quote data for {ticker}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching quote for {ticker}: {e}")
            return None

    def get_historical_prices(self, ticker: str, days: int = 252) -> Optional[Dict]:
        """
        Get historical prices (52-week range)

        Args:
            ticker: Stock ticker
            days: Number of days to fetch

        Returns:
            Dict with high/low prices
        """
        if not self.api_key:
            return None

        try:
            _track_api_call()
            url = f"{FMP_API_BASE}/historical-price-full/{ticker}"
            params = {"apikey": self.api_key, "serietype": "line"}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if "historical" in data and len(data["historical"]) > 0:
                # Calculate 52-week range
                prices = [p["close"] for p in data["historical"][:252]]
                logger.info(f"Fetched {len(prices)} historical prices for {ticker}")
                return {
                    "high_52w": max(prices),
                    "low_52w": min(prices),
                    "prices_count": len(prices),
                }
            else:
                logger.warning(f"No historical data for {ticker}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching historical prices for {ticker}: {e}")
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
            # Fetch all data in parallel-friendly way
            quote = self.get_quote(ticker)
            if not quote:
                logger.error(f"Could not fetch quote for {ticker}")
                return None

            profile = self.get_stock_profile(ticker)
            ratios = self.get_financial_ratios(ticker)
            balance_sheet = self.get_balance_sheet(ticker)
            income_statement = self.get_income_statement(ticker)
            historical = self.get_historical_prices(ticker)

            # Consolidate data
            result = {
                "ticker": ticker,
                "source": "FMP",
                "fetched_at": datetime.now().isoformat(),
                "current_price": quote.get("price"),
                "name": profile.get("companyName") if profile else quote.get("name"),
                "pe_ratio": quote.get("pe"),
                "pb_ratio": ratios.get("priceToBookRatio") if ratios else None,
                "eps": quote.get("eps"),
                "market_cap": quote.get("marketCap"),
                "52week_high": historical.get("high_52w") if historical else None,
                "52week_low": historical.get("low_52w") if historical else None,
            }

            # Add balance sheet data
            if balance_sheet:
                result["total_assets"] = balance_sheet.get("totalAssets")
                result["total_liabilities"] = balance_sheet.get("totalLiabilities")
                result["total_equity"] = balance_sheet.get("totalStockholdersEquity")
                result["current_assets"] = balance_sheet.get("totalCurrentAssets")
                result["current_liabilities"] = balance_sheet.get("totalCurrentLiabilities")

            # Add income statement data
            if income_statement:
                result["revenue"] = income_statement.get("revenue")
                result["net_income"] = income_statement.get("netIncome")

            # Add ratio data
            if ratios:
                result["current_ratio"] = ratios.get("currentRatio")
                result["debt_to_equity"] = ratios.get("debtEquityRatio")
                result["roe"] = ratios.get("returnOnEquity")
                result["roa"] = ratios.get("returnOnAssets")

            logger.info(f"Successfully consolidated data for {ticker}")
            return result

        except Exception as e:
            logger.error(f"Error consolidating data for {ticker}: {e}")
            return None
