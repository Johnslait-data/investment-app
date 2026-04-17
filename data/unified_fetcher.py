"""
Unified Stock Data Fetcher
Tries multiple sources: FMP → Cache → Demo Mock
Always has a fallback, never blocks

CACHING STRATEGY:
- FMP: First source (only 250 req/day)
- Cache: 48 hour TTL (reduce API calls)
- Mock: Fallback (never fails)
"""
import logging
from typing import Optional, Dict
from pathlib import Path
from data.fmp_fetcher_optimized import FMPOptimizedFetcher, get_api_usage
from data.cache import StockCache
from data.mock_data import MOCK_DATA

logger = logging.getLogger(__name__)


class UnifiedStockFetcher:
    """
    Unified fetcher that tries multiple sources in order:
    1. FMP API (if key available)
    2. SQLite Cache (if fresh)
    3. Demo Mock Data (as fallback)
    """

    def __init__(self):
        self.fmp = FMPOptimizedFetcher()
        self.cache = StockCache(Path("data/stock_cache.db"))
        self.use_fmp = self.fmp.is_available()

        if self.use_fmp:
            logger.info("✅ FMP API available (Optimized Free Tier) - will use for real data")
        else:
            logger.warning("⚠️  FMP API not available - will use cache + mock data")

    def get_stock_data(
        self,
        ticker: str,
        prefer_cache: bool = False,
        cache_max_age_hours: int = 24,
    ) -> Optional[Dict]:
        """
        Get stock data from best available source

        Priority:
        1. FMP (if available and prefer_cache=False)
        2. Cache (if available and fresh)
        3. Demo Mock (as fallback)

        Args:
            ticker: Stock ticker
            prefer_cache: Prefer cached data even if FMP available
            cache_max_age_hours: Max age of cached data

        Returns:
            Dict with stock data, or None if all sources fail
        """

        # Try FMP first (if available and not preferring cache)
        if self.use_fmp and not prefer_cache:
            logger.info(f"📡 Trying FMP API for {ticker}...")
            fmp_data = self.fmp.get_all_data(ticker)

            if fmp_data:
                # Cache the result for fallback
                try:
                    self.cache.set_stock(ticker, fmp_data)
                    logger.info(f"✅ Cached FMP data for {ticker}")
                except Exception as e:
                    logger.warning(f"Could not cache FMP data: {e}")

                return fmp_data

        # Try cache
        logger.info(f"💾 Checking cache for {ticker}...")
        cached_data = self.cache.get_stock(ticker, max_age_hours=cache_max_age_hours)
        if cached_data:
            logger.info(f"✅ Found fresh cache for {ticker}")
            return cached_data

        # Fall back to mock data
        logger.warning(f"⚠️  Using mock data for {ticker}")
        if ticker.upper() in MOCK_DATA:
            mock = MOCK_DATA[ticker.upper()].copy()
            mock["source"] = "MOCK"
            logger.info(f"✅ Using mock data for {ticker}")
            return mock
        else:
            logger.error(f"❌ No data available for {ticker}")
            return None

    def validate_data_source(self, ticker: str) -> Dict:
        """
        Check what data is available for a ticker

        Returns dict with availability status
        """
        result = {
            "ticker": ticker,
            "fmp_available": False,
            "cache_available": False,
            "mock_available": False,
        }

        # Check FMP
        if self.use_fmp:
            fmp_data = self.fmp.get_quote(ticker)
            result["fmp_available"] = fmp_data is not None

        # Check cache
        cache_data = self.cache.get_stock(ticker, max_age_hours=24)
        result["cache_available"] = cache_data is not None

        # Check mock
        result["mock_available"] = ticker.upper() in MOCK_DATA

        return result

    def list_available_tickers(self) -> Dict:
        """List all available tickers from all sources"""
        result = {
            "cache": self.cache.get_all_cached_tickers(),
            "mock": list(MOCK_DATA.keys()),
        }
        return result

    def refresh_all_cache(self) -> Dict:
        """
        Refresh cache with FMP data for all mock tickers

        Useful for keeping cache fresh

        Returns stats on refresh
        """
        if not self.use_fmp:
            logger.warning("FMP not available, skipping refresh")
            return {"refreshed": 0, "failed": 0}

        stats = {"refreshed": 0, "failed": 0}

        for ticker in MOCK_DATA.keys():
            logger.info(f"Refreshing {ticker}...")
            try:
                data = self.fmp.get_all_data(ticker)
                if data:
                    self.cache.set_stock(ticker, data)
                    stats["refreshed"] += 1
                    logger.info(f"✅ Refreshed {ticker}")
                else:
                    stats["failed"] += 1
                    logger.warning(f"❌ Failed to refresh {ticker}")
            except Exception as e:
                stats["failed"] += 1
                logger.error(f"Error refreshing {ticker}: {e}")

        return stats

    def get_api_usage_stats(self) -> Dict:
        """Get current API usage statistics"""
        return get_api_usage()
