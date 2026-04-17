"""
FMP Optimized Fetcher
Uses ONLY free-tier endpoints that are available with free API key
"""
import requests
import logging
from typing import Optional, Dict, List
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
    """Track API calls"""
    global _api_calls_today, _last_call_reset
    today = datetime.now().date()
    if today != _last_call_reset:
        _api_calls_today = 0
        _last_call_reset = today
    _api_calls_today += 1
    logger.info(f"API: {_api_calls_today}/250")


def get_api_usage() -> Dict:
    """Get API usage"""
    global _api_calls_today
    return {
        "calls_today": _api_calls_today,
        "calls_limit": 250,
        "calls_remaining": 250 - _api_calls_today,
        "usage_pct": (_api_calls_today / 250) * 100,
        "last_reset": _last_call_reset.isoformat(),
    }


class FMPOptimizedFetcher:
    """Fetch data using only free-tier FMP endpoints"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            logger.warning("FMP_API_KEY not found")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _get(self, endpoint: str, params: dict = None) -> Optional[Dict]:
        """Generic GET request"""
        if not self.api_key:
            return None

        try:
            _track_api_call()
            url = f"{FMP_API_BASE}{endpoint}"
            if params is None:
                params = {}
            params["apikey"] = self.api_key

            response = requests.get(url, params=params, timeout=10)

            # Handle 402 (payment required) gracefully
            if response.status_code == 402:
                logger.debug(f"Endpoint {endpoint} requires payment")
                return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.debug(f"Error on {endpoint}: {e}")
            return None

    def get_profile(self, ticker: str) -> Optional[Dict]:
        """Get company profile (FREE)"""
        cik = get_cik(ticker)
        if not cik:
            return None
        data = self._get("/profile-cik", {"cik": cik})
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    def get_quote(self, ticker: str) -> Optional[Dict]:
        """Get current quote (FREE)"""
        data = self._get("/quote", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    def get_ratios(self, ticker: str) -> Optional[Dict]:
        """Get financial ratios - TTM version (tries free first) (FREE)"""
        # Try TTM first (sometimes free)
        data = self._get("/ratios-ttm", {"symbol": ticker})
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]

        # Fallback to regular ratios
        data = self._get("/ratios", {"symbol": ticker, "limit": 1})
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]

        return None

    def get_key_metrics(self, ticker: str) -> Optional[Dict]:
        """Get key metrics (FREE)"""
        data = self._get("/key-metrics", {"symbol": ticker, "limit": 1})
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    def get_financial_scores(self, ticker: str) -> Optional[Dict]:
        """Get financial health scores (FREE)"""
        data = self._get("/financial-scores", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    def get_dividends(self, ticker: str) -> Optional[List[Dict]]:
        """Get dividend history (FREE)"""
        data = self._get("/dividends", {"symbol": ticker})
        if isinstance(data, list):
            return data[:5]  # Last 5
        return None

    def get_historical_prices(self, ticker: str, limit: int = 252) -> Optional[List[Dict]]:
        """Get historical prices (FREE - EOD light)"""
        data = self._get("/historical-price-eod/light", {"symbol": ticker, "limit": limit})
        if isinstance(data, list):
            return data
        return None

    def get_all_data(self, ticker: str) -> Optional[Dict]:
        """Get complete data using ONLY free endpoints"""
        logger.info(f"Fetching optimized FREE data for {ticker}...")

        try:
            # Fetch all data
            profile = self.get_profile(ticker)
            if not profile:
                return None

            quote = self.get_quote(ticker)
            ratios = self.get_ratios(ticker)
            metrics = self.get_key_metrics(ticker)
            scores = self.get_financial_scores(ticker)
            dividends = self.get_dividends(ticker)
            prices = self.get_historical_prices(ticker)

            # Calculate 52W
            week_52_high = None
            week_52_low = None
            if prices:
                prices_list = [p.get("close") for p in prices if p.get("close")]
                if prices_list:
                    week_52_high = max(prices_list)
                    week_52_low = min(prices_list)

            # Build result
            result = {
                "ticker": ticker,
                "source": "FMP",
                "fetched_at": datetime.now().isoformat(),

                # Profile
                "name": profile.get("companyName"),
                "symbol": profile.get("symbol"),
                "price": profile.get("price"),
                "market_cap": profile.get("marketCap"),
                "beta": profile.get("beta"),
                "exchange": profile.get("exchange"),
                "currency": profile.get("currency"),
                "industry": profile.get("industry"),
                "website": profile.get("website"),
                "description": profile.get("description"),

                # Ratios (Available)
                "pe_ratio": ratios.get("peRatio") if ratios else None,
                "pb_ratio": ratios.get("pbRatio") if ratios else None,
                "current_ratio": ratios.get("currentRatio") if ratios else None,
                "quick_ratio": ratios.get("quickRatio") if ratios else None,
                "debt_to_equity": ratios.get("debtEquityRatio") if ratios else None,
                "roe": ratios.get("returnOnEquity") if ratios else None,
                "roa": ratios.get("returnOnAssets") if ratios else None,
                "roic": ratios.get("returnOnCapitalEmployed") if ratios else None,
                "debt_ratio": ratios.get("debtRatio") if ratios else None,

                # Key Metrics
                "earnings_yield": metrics.get("earningsYield") if metrics else None,
                "book_value_per_share": metrics.get("bookValuePerShare") if metrics else None,
                "revenue_per_share": metrics.get("revenuePerShare") if metrics else None,
                "dividend_yield": metrics.get("dividendYield") if metrics else None,
                "payout_ratio": metrics.get("payoutRatio") if metrics else None,
                "fcf_per_share": metrics.get("freeCashFlowPerShare") if metrics else None,

                # Financial Scores
                "altman_z_score": scores.get("altmanZScore") if scores else None,
                "piotroski_score": scores.get("piotroskiScore") if scores else None,

                # Price
                "week_52_high": week_52_high,
                "week_52_low": week_52_low,

                # Dividends
                "latest_dividend": dividends[0] if dividends else None,
                "dividend_count": len(dividends) if dividends else 0,
            }

            logger.info(f"✅ SUCCESS: Complete data for {ticker}")
            return result

        except Exception as e:
            logger.error(f"Error: {e}")
            return None
