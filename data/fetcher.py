"""
Data fetcher using yfinance
Handles historical price data and current fundamentals
With rate limiting protection and caching
"""
import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import logging
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting configuration
MIN_REQUEST_DELAY = 1.0  # Minimum seconds between requests
MAX_REQUEST_DELAY = 2.0  # Maximum seconds between requests
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2

# User agents to rotate (avoid being blocked)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

# Track last request time to enforce delays
_last_request_time = 0


def _enforce_rate_limit():
    """Enforce minimum delay between requests"""
    global _last_request_time
    now = time.time()
    if _last_request_time > 0:
        elapsed = now - _last_request_time
        delay_needed = MIN_REQUEST_DELAY - elapsed
        if delay_needed > 0:
            logger.debug(f"Rate limit: sleeping {delay_needed:.2f}s")
            time.sleep(delay_needed)
    _last_request_time = time.time()


def _get_random_user_agent() -> str:
    """Get a random user agent"""
    return random.choice(USER_AGENTS)


class StockDataFetcher:
    """Fetch stock data from yfinance"""

    @staticmethod
    def get_historical_data(ticker: str, period: str = "5y") -> pd.DataFrame:
        """
        Get historical price data with retry logic

        Args:
            ticker: Stock ticker (e.g., 'AAPL')
            period: Period to fetch ('5y', '10y', '1y', etc.)

        Returns:
            DataFrame with OHLCV data
        """
        for attempt in range(MAX_RETRIES):
            try:
                _enforce_rate_limit()
                data = yf.download(ticker, period=period, progress=False)
                if data.empty:
                    logger.warning(f"No data found for {ticker}")
                    return pd.DataFrame()
                logger.info(f"Fetched {len(data)} rows for {ticker}")
                return data
            except Exception as e:
                wait_time = (RETRY_BACKOFF_FACTOR ** attempt) + random.uniform(0, 1)
                logger.warning(f"Error fetching data for {ticker} (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch data for {ticker} after {MAX_RETRIES} attempts")
                    return pd.DataFrame()

    @staticmethod
    def get_current_price(ticker: str) -> Optional[float]:
        """Get current stock price with retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                _enforce_rate_limit()
                stock = yf.Ticker(ticker)
                price = stock.info.get("currentPrice") or stock.info.get("regularMarketPrice")
                if price:
                    logger.info(f"{ticker}: ${price}")
                    return price
                logger.warning(f"Could not get price for {ticker}")
                return None
            except Exception as e:
                wait_time = (RETRY_BACKOFF_FACTOR ** attempt) + random.uniform(0, 1)
                logger.warning(f"Error fetching price for {ticker} (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch price for {ticker} after {MAX_RETRIES} attempts")
                    return None

    @staticmethod
    def get_fundamentals(ticker: str) -> Dict:
        """
        Get fundamental data from yfinance with retry logic

        Args:
            ticker: Stock ticker

        Returns:
            Dict with financial metrics
        """
        for attempt in range(MAX_RETRIES):
            try:
                _enforce_rate_limit()
                stock = yf.Ticker(ticker)
                info = stock.info

                # Calculate total_equity safely
                total_assets = info.get("totalAssets")
                total_debt = info.get("totalDebt", 0)
                total_equity = None
                if total_assets and total_debt is not None:
                    total_equity = total_assets - total_debt

                fundamentals = {
                    "ticker": ticker,
                    "name": info.get("shortName", "N/A"),
                    "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                    "eps": info.get("trailingEps"),
                    "pe_ratio": info.get("trailingPE"),
                    "pb_ratio": info.get("priceToBook"),
                    "book_value_per_share": info.get("bookValue"),
                    "current_ratio": info.get("currentRatio"),
                    "total_debt": total_debt,
                    "total_equity": total_equity,
                    "current_assets": info.get("currentAssets"),
                    "current_liabilities": info.get("currentLiabilities"),
                    "shares_outstanding": info.get("sharesOutstanding"),
                    "roe": info.get("returnOnEquity"),
                    "roa": info.get("returnOnAssets"),
                    "revenue_per_share": info.get("revenuePerShare"),
                    "profit_margin": info.get("profitMargins"),
                }

                logger.info(f"Fetched fundamentals for {ticker}")
                return fundamentals

            except Exception as e:
                wait_time = (RETRY_BACKOFF_FACTOR ** attempt) + random.uniform(0, 1)
                logger.warning(f"Error fetching fundamentals for {ticker} (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.info(f"Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch fundamentals for {ticker} after {MAX_RETRIES} attempts")
                    return {"ticker": ticker, "error": str(e)}

    @staticmethod
    def get_quarterly_financials(ticker: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get quarterly balance sheet and income statement

        Args:
            ticker: Stock ticker

        Returns:
            Tuple of (balance_sheet_df, income_statement_df)
        """
        try:
            stock = yf.Ticker(ticker)
            bs = stock.quarterly_balance_sheet
            income = stock.quarterly_income_stmt

            logger.info(f"Fetched quarterly financials for {ticker}")
            return bs, income

        except Exception as e:
            logger.error(f"Error fetching quarterly financials for {ticker}: {e}")
            return pd.DataFrame(), pd.DataFrame()

    @staticmethod
    def validate_ticker(ticker: str) -> bool:
        """Check if ticker is valid"""
        try:
            stock = yf.Ticker(ticker)
            # Try to get historical data (more reliable than info)
            hist = stock.history(period="1d")
            return len(hist) > 0
        except:
            return False


def fetch_stock_data(ticker: str, use_cache: bool = True, cache_age_hours: int = 24) -> Optional[Dict]:
    """
    Fetch all data for a stock with caching support

    Args:
        ticker: Stock ticker
        use_cache: Whether to use cached data if available
        cache_age_hours: Max age of cached data in hours

    Returns:
        Dict with price and fundamentals, or None if error
    """
    from pathlib import Path
    from data.cache import StockCache

    fetcher = StockDataFetcher()

    # Try cache first
    if use_cache:
        cache = StockCache(Path("data/stock_cache.db"))
        cached_data = cache.get_stock(ticker, max_age_hours=cache_age_hours)
        if cached_data:
            logger.info(f"Using cached data for {ticker}")
            return cached_data

    # Get fundamentals
    fundamentals = fetcher.get_fundamentals(ticker)

    if "error" in fundamentals:
        logger.error(f"Could not fetch fundamentals for {ticker}")
        return None

    # Only try to get historical if we have a valid price
    if fundamentals.get("current_price"):
        try:
            historical = fetcher.get_historical_data(ticker, period="5y")

            # Calculate 52-week price range
            if len(historical) >= 52:
                fifty_two_week_high = float(historical["Close"].tail(252).max())
                fifty_two_week_low = float(historical["Close"].tail(252).min())
            else:
                fifty_two_week_high = float(historical["Close"].max()) if len(historical) > 0 else None
                fifty_two_week_low = float(historical["Close"].min()) if len(historical) > 0 else None

            fundamentals["52week_high"] = fifty_two_week_high
            fundamentals["52week_low"] = fifty_two_week_low
        except Exception as e:
            logger.warning(f"Could not fetch historical data for {ticker}: {e}")
            # Continue anyway, we have fundamentals

    # Cache the result
    if use_cache:
        try:
            cache.set_stock(ticker, fundamentals)
        except Exception as e:
            logger.warning(f"Could not cache data for {ticker}: {e}")

    return fundamentals
