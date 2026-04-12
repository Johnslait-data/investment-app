"""
SQLite cache for stock data
Prevents unnecessary API calls to yfinance
"""
import sqlite3
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class StockCache:
    """SQLite cache for stock fundamentals and prices"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create stocks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY,
                    ticker TEXT UNIQUE,
                    data TEXT,  -- JSON serialized fundamentals
                    fetched_at TIMESTAMP
                )
            """
            )

            # Create price history table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY,
                    ticker TEXT,
                    date DATE,
                    close_price REAL,
                    UNIQUE(ticker, date)
                )
            """
            )

            conn.commit()
            conn.close()
            logger.info(f"Cache initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Error initializing cache: {e}")

    def get_stock(self, ticker: str, max_age_hours: int = 24) -> dict or None:
        """
        Get cached stock data if fresh enough

        Args:
            ticker: Stock ticker
            max_age_hours: Max age of cache in hours

        Returns:
            Stock data dict or None if not cached or stale
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT data, fetched_at FROM stocks
                WHERE ticker = ?
                ORDER BY fetched_at DESC LIMIT 1
            """,
                (ticker,),
            )

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            data_json, fetched_at_str = row
            fetched_at = datetime.fromisoformat(fetched_at_str)

            # Check if cache is fresh
            if datetime.now() - fetched_at < timedelta(hours=max_age_hours):
                logger.info(f"Cache hit for {ticker}")
                return json.loads(data_json)
            else:
                logger.info(f"Cache stale for {ticker}")
                return None

        except Exception as e:
            logger.error(f"Error getting cache for {ticker}: {e}")
            return None

    def set_stock(self, ticker: str, data: dict):
        """
        Cache stock data

        Args:
            ticker: Stock ticker
            data: Stock fundamentals dict
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO stocks (ticker, data, fetched_at)
                VALUES (?, ?, ?)
            """,
                (ticker, json.dumps(data), datetime.now().isoformat()),
            )

            conn.commit()
            conn.close()
            logger.info(f"Cached data for {ticker}")

        except Exception as e:
            logger.error(f"Error caching {ticker}: {e}")

    def clear_cache(self, ticker: str = None):
        """
        Clear cache for a ticker or all

        Args:
            ticker: Specific ticker to clear, or None to clear all
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if ticker:
                cursor.execute("DELETE FROM stocks WHERE ticker = ?", (ticker,))
            else:
                cursor.execute("DELETE FROM stocks")

            conn.commit()
            conn.close()
            logger.info(f"Cache cleared for {ticker or 'all'}")

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_all_cached_tickers(self) -> list:
        """Get list of all tickers in cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT DISTINCT ticker FROM stocks
                ORDER BY fetched_at DESC
            """
            )

            tickers = [row[0] for row in cursor.fetchall()]
            conn.close()

            return tickers

        except Exception as e:
            logger.error(f"Error getting cached tickers: {e}")
            return []
