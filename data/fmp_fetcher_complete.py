"""
Financial Modeling Prep (FMP) Complete Fetcher
Comprehensive data from all relevant endpoints for Graham analysis
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


class FMPCompleteDataFetcher:
    """Fetch comprehensive stock data from FMP for complete Graham analysis"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            logger.warning("FMP_API_KEY not found")

    def is_available(self) -> bool:
        """Check if API key is available"""
        return bool(self.api_key)

    def _get(self, endpoint: str, params: dict = None) -> Optional[Dict]:
        """Generic GET request with error handling"""
        if not self.api_key:
            return None

        try:
            _track_api_call()
            url = f"{FMP_API_BASE}{endpoint}"
            if params is None:
                params = {}
            params["apikey"] = self.api_key

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return None

    def get_profile(self, ticker: str) -> Optional[Dict]:
        """Get company profile"""
        cik = get_cik(ticker)
        if not cik:
            return None

        data = self._get("/profile-cik", {"cik": cik})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched profile for {ticker}")
            return data[0]
        return None

    def get_quote(self, ticker: str) -> Optional[Dict]:
        """Get current stock quote"""
        data = self._get("/quote", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched quote for {ticker}")
            return data[0]
        return None

    def get_income_statement(self, ticker: str) -> Optional[Dict]:
        """Get latest income statement (TTM)"""
        data = self._get("/income-statement-ttm", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched income statement for {ticker}")
            return data[0]
        return None

    def get_balance_sheet(self, ticker: str) -> Optional[Dict]:
        """Get latest balance sheet (TTM)"""
        data = self._get("/balance-sheet-statement-ttm", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched balance sheet for {ticker}")
            return data[0]
        return None

    def get_cash_flow(self, ticker: str) -> Optional[Dict]:
        """Get latest cash flow statement (TTM)"""
        data = self._get("/cash-flow-statement-ttm", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched cash flow for {ticker}")
            return data[0]
        return None

    def get_financial_ratios(self, ticker: str) -> Optional[Dict]:
        """Get financial ratios (TTM)"""
        data = self._get("/ratios-ttm", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched ratios for {ticker}")
            return data[0]
        return None

    def get_key_metrics(self, ticker: str) -> Optional[Dict]:
        """Get key metrics (TTM)"""
        data = self._get("/key-metrics-ttm", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched key metrics for {ticker}")
            return data[0]
        return None

    def get_financial_scores(self, ticker: str) -> Optional[Dict]:
        """Get financial health scores (Altman Z-Score, Piotroski, etc.)"""
        data = self._get("/financial-scores", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched financial scores for {ticker}")
            return data[0]
        return None

    def get_dividends(self, ticker: str) -> Optional[List[Dict]]:
        """Get dividend history"""
        data = self._get("/dividends", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched dividends for {ticker}")
            return data
        return None

    def get_historical_prices(self, ticker: str, limit: int = 252) -> Optional[List[Dict]]:
        """Get historical prices for 52-week range"""
        data = self._get(
            "/historical-price-eod/full",
            {"symbol": ticker, "limit": limit}
        )
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched {len(data)} historical prices for {ticker}")
            return data
        return None

    def get_owner_earnings(self, ticker: str) -> Optional[Dict]:
        """Get owner earnings (Graham's preferred metric)"""
        data = self._get("/owner-earnings", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched owner earnings for {ticker}")
            return data[0]
        return None

    def get_enterprise_value(self, ticker: str) -> Optional[Dict]:
        """Get enterprise value"""
        data = self._get("/enterprise-values", {"symbol": ticker})
        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Fetched enterprise value for {ticker}")
            return data[0]
        return None

    def get_all_data(self, ticker: str) -> Optional[Dict]:
        """
        Get COMPLETE data for comprehensive Graham analysis

        Fetches:
        - Company profile & quote
        - Financial statements (Income, Balance, Cash Flow)
        - Ratios & metrics
        - Financial health scores
        - Dividends & owner earnings
        - Historical prices
        """
        logger.info(f"Fetching COMPLETE data for {ticker}...")

        try:
            # Core data
            profile = self.get_profile(ticker)
            if not profile:
                logger.error(f"Could not fetch profile for {ticker}")
                return None

            quote = self.get_quote(ticker)
            income = self.get_income_statement(ticker)
            balance = self.get_balance_sheet(ticker)
            cash_flow = self.get_cash_flow(ticker)
            ratios = self.get_financial_ratios(ticker)
            metrics = self.get_key_metrics(ticker)
            scores = self.get_financial_scores(ticker)
            dividends = self.get_dividends(ticker)
            owner_earnings = self.get_owner_earnings(ticker)
            enterprise_value = self.get_enterprise_value(ticker)
            prices = self.get_historical_prices(ticker)

            # Calculate 52-week range
            week_52_high = None
            week_52_low = None
            if prices and len(prices) > 0:
                prices_list = [p.get("close") for p in prices if p.get("close")]
                if prices_list:
                    week_52_high = max(prices_list)
                    week_52_low = min(prices_list)

            # Consolidate everything
            result = {
                "ticker": ticker,
                "source": "FMP_COMPLETE",
                "fetched_at": datetime.now().isoformat(),

                # Profile & Quote
                "name": profile.get("companyName"),
                "symbol": profile.get("symbol"),
                "price": quote.get("price") if quote else profile.get("price"),
                "market_cap": profile.get("marketCap"),
                "beta": profile.get("beta"),
                "exchange": profile.get("exchange"),
                "currency": profile.get("currency"),
                "industry": profile.get("industry"),
                "website": profile.get("website"),

                # Financial Statements (TTM)
                "revenue": income.get("revenue") if income else None,
                "net_income": income.get("netIncome") if income else None,
                "eps": income.get("eps") if income else None,
                "total_assets": balance.get("totalAssets") if balance else None,
                "total_liabilities": balance.get("totalLiabilities") if balance else None,
                "total_equity": balance.get("totalStockholdersEquity") if balance else None,
                "current_assets": balance.get("totalCurrentAssets") if balance else None,
                "current_liabilities": balance.get("totalCurrentLiabilities") if balance else None,
                "cash": balance.get("cashAndCashEquivalents") if balance else None,
                "total_debt": balance.get("totalDebt") if balance else None,
                "operating_cash_flow": cash_flow.get("operatingCashFlow") if cash_flow else None,
                "free_cash_flow": cash_flow.get("freeCashFlow") if cash_flow else None,

                # Ratios (TTM)
                "pe_ratio": ratios.get("peRatio") if ratios else None,
                "pb_ratio": ratios.get("pbRatio") if ratios else None,
                "current_ratio": ratios.get("currentRatio") if ratios else None,
                "quick_ratio": ratios.get("quickRatio") if ratios else None,
                "debt_to_equity": ratios.get("debtEquityRatio") if ratios else None,
                "roe": ratios.get("returnOnEquity") if ratios else None,
                "roa": ratios.get("returnOnAssets") if ratios else None,
                "roic": ratios.get("returnOnCapitalEmployed") if ratios else None,

                # Key Metrics (TTM)
                "market_cap_metric": metrics.get("marketCap") if metrics else None,
                "pe_ratio_metric": metrics.get("peRatio") if metrics else None,
                "price_to_sales": metrics.get("priceToSalesRatio") if metrics else None,
                "dividend_yield": metrics.get("dividendYield") if metrics else None,
                "book_value_per_share": metrics.get("bookValuePerShare") if metrics else None,
                "revenue_per_share": metrics.get("revenuePerShare") if metrics else None,
                "net_income_per_share": metrics.get("netIncomePerShare") if metrics else None,

                # Financial Health Scores
                "altman_z_score": scores.get("altmanZScore") if scores else None,
                "piotroski_score": scores.get("piotroskiScore") if scores else None,

                # Graham Metrics
                "owner_earnings": owner_earnings.get("ownerEarnings") if owner_earnings else None,
                "enterprise_value": enterprise_value.get("enterpriseValue") if enterprise_value else None,

                # Price Data
                "week_52_high": week_52_high,
                "week_52_low": week_52_low,

                # Dividends
                "dividend_history": dividends[:5] if dividends else None,  # Last 5 dividends
            }

            logger.info(f"✅ Successfully compiled COMPLETE data for {ticker}")
            return result

        except Exception as e:
            logger.error(f"Error compiling complete data for {ticker}: {e}")
            return None
