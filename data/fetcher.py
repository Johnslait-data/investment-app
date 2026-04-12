"""
Data fetcher using yfinance
Handles historical price data and current fundamentals
"""
import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Fetch stock data from yfinance"""

    @staticmethod
    def get_historical_data(ticker: str, period: str = "5y") -> pd.DataFrame:
        """
        Get historical price data

        Args:
            ticker: Stock ticker (e.g., 'AAPL')
            period: Period to fetch ('5y', '10y', '1y', etc.)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            data = yf.download(ticker, period=period, progress=False)
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return pd.DataFrame()
            logger.info(f"Fetched {len(data)} rows for {ticker}")
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_current_price(ticker: str) -> Optional[float]:
        """Get current stock price"""
        try:
            stock = yf.Ticker(ticker)
            price = stock.info.get("currentPrice") or stock.info.get("regularMarketPrice")
            if price:
                logger.info(f"{ticker}: ${price}")
                return price
            logger.warning(f"Could not get price for {ticker}")
            return None
        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {e}")
            return None

    @staticmethod
    def get_fundamentals(ticker: str) -> Dict:
        """
        Get fundamental data from yfinance

        Args:
            ticker: Stock ticker

        Returns:
            Dict with financial metrics
        """
        try:
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
            logger.error(f"Error fetching fundamentals for {ticker}: {e}")
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


def fetch_stock_data(ticker: str) -> Optional[Dict]:
    """
    Convenience function to fetch all data for a stock

    Args:
        ticker: Stock ticker

    Returns:
        Dict with price and fundamentals, or None if error
    """
    fetcher = StockDataFetcher()

    # Get fundamentals (skip validation, go straight to fetch)
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

    return fundamentals
