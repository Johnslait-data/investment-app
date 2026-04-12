"""
Standard financial ratios and analysis
"""
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class Fundamentals:
    """Standard financial metrics"""

    ticker: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    current_ratio: Optional[float] = None
    debt_equity: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    eps_growth: Optional[float] = None
    profit_margin: Optional[float] = None


class FundamentalsAnalyzer:
    """Analyze standard financial ratios"""

    # Graham thresholds
    PE_THRESHOLD = 15
    PB_THRESHOLD = 1.5
    CURRENT_RATIO_MIN = 1.5
    DEBT_EQUITY_MAX = 1.0
    ROE_MIN = 0.10  # 10%

    @staticmethod
    def calculate_pe_ratio(price: float, eps: Optional[float]) -> Optional[float]:
        """
        Calculate Price-to-Earnings ratio

        Args:
            price: Current stock price
            eps: Earnings per share

        Returns:
            P/E ratio or None
        """
        if not eps or eps <= 0:
            return None

        try:
            pe = price / eps
            return pe
        except Exception as e:
            logger.error(f"Error calculating P/E: {e}")
            return None

    @staticmethod
    def calculate_pb_ratio(price: float, book_value: Optional[float]) -> Optional[float]:
        """
        Calculate Price-to-Book ratio

        Args:
            price: Current stock price
            book_value: Book value per share

        Returns:
            P/B ratio or None
        """
        if not book_value or book_value <= 0:
            return None

        try:
            pb = price / book_value
            return pb
        except Exception as e:
            logger.error(f"Error calculating P/B: {e}")
            return None

    @staticmethod
    def calculate_current_ratio(
        current_assets: Optional[float], current_liabilities: Optional[float]
    ) -> Optional[float]:
        """
        Calculate Current Ratio (liquidity metric)

        Current Ratio = Current Assets / Current Liabilities
        Graham wants: ≥ 1.5

        Args:
            current_assets: Current assets
            current_liabilities: Current liabilities

        Returns:
            Current ratio or None
        """
        if not current_assets or not current_liabilities or current_liabilities <= 0:
            return None

        try:
            ratio = current_assets / current_liabilities
            return ratio
        except Exception as e:
            logger.error(f"Error calculating current ratio: {e}")
            return None

    @staticmethod
    def calculate_debt_equity(
        total_debt: Optional[float], total_equity: Optional[float]
    ) -> Optional[float]:
        """
        Calculate Debt-to-Equity ratio

        D/E = Total Debt / Total Equity
        Graham wants: ≤ 1.0

        Args:
            total_debt: Total debt
            total_equity: Total equity

        Returns:
            D/E ratio or None
        """
        if not total_debt or not total_equity or total_equity <= 0:
            return None

        try:
            de = total_debt / total_equity
            return de
        except Exception as e:
            logger.error(f"Error calculating D/E: {e}")
            return None

    @staticmethod
    def calculate_roe(net_income: Optional[float], equity: Optional[float]) -> Optional[float]:
        """
        Calculate Return on Equity

        ROE = Net Income / Equity
        Graham wants: ≥ 10% (0.1)

        Args:
            net_income: Net income
            equity: Total equity

        Returns:
            ROE as decimal (0.1 = 10%) or None
        """
        if not net_income or not equity or equity <= 0:
            return None

        try:
            roe = net_income / equity
            return roe
        except Exception as e:
            logger.error(f"Error calculating ROE: {e}")
            return None

    @staticmethod
    def calculate_roa(net_income: Optional[float], assets: Optional[float]) -> Optional[float]:
        """
        Calculate Return on Assets

        ROA = Net Income / Assets

        Args:
            net_income: Net income
            assets: Total assets

        Returns:
            ROA as decimal or None
        """
        if not net_income or not assets or assets <= 0:
            return None

        try:
            roa = net_income / assets
            return roa
        except Exception as e:
            logger.error(f"Error calculating ROA: {e}")
            return None

    @staticmethod
    def analyze_stock(
        ticker: str,
        price: float,
        eps: Optional[float] = None,
        book_value: Optional[float] = None,
        current_assets: Optional[float] = None,
        current_liabilities: Optional[float] = None,
        total_debt: Optional[float] = None,
        total_equity: Optional[float] = None,
        roe: Optional[float] = None,
        roa: Optional[float] = None,
        profit_margin: Optional[float] = None,
    ) -> Fundamentals:
        """
        Calculate all fundamental metrics for a stock

        Args:
            ticker: Stock ticker
            price: Current price
            eps: Earnings per share
            book_value: Book value per share
            current_assets: Current assets
            current_liabilities: Current liabilities
            total_debt: Total debt
            total_equity: Total equity
            roe: Return on equity (if already calculated)
            roa: Return on assets (if already calculated)
            profit_margin: Profit margin (if already calculated)

        Returns:
            Fundamentals object with all calculations
        """
        fundamentals = Fundamentals(ticker=ticker)

        # Calculate ratios
        fundamentals.pe_ratio = FundamentalsAnalyzer.calculate_pe_ratio(price, eps)
        fundamentals.pb_ratio = FundamentalsAnalyzer.calculate_pb_ratio(price, book_value)
        fundamentals.current_ratio = FundamentalsAnalyzer.calculate_current_ratio(
            current_assets, current_liabilities
        )
        fundamentals.debt_equity = FundamentalsAnalyzer.calculate_debt_equity(
            total_debt, total_equity
        )
        fundamentals.roe = roe
        fundamentals.roa = roa
        fundamentals.profit_margin = profit_margin

        return fundamentals

    @staticmethod
    def is_pe_healthy(pe_ratio: Optional[float], threshold: float = PE_THRESHOLD) -> bool:
        """Check if P/E ratio is healthy (below threshold)"""
        if not pe_ratio:
            return False
        return pe_ratio <= threshold

    @staticmethod
    def is_pb_healthy(pb_ratio: Optional[float], threshold: float = PB_THRESHOLD) -> bool:
        """Check if P/B ratio is healthy (below threshold)"""
        if not pb_ratio:
            return False
        return pb_ratio <= threshold

    @staticmethod
    def is_liquid(current_ratio: Optional[float], min_threshold: float = CURRENT_RATIO_MIN) -> bool:
        """Check if company has good liquidity"""
        if not current_ratio:
            return False
        return current_ratio >= min_threshold

    @staticmethod
    def is_leveraged(debt_equity: Optional[float], max_threshold: float = DEBT_EQUITY_MAX) -> bool:
        """Check if company is overleveraged"""
        if not debt_equity:
            return False
        return debt_equity <= max_threshold

    @staticmethod
    def is_profitable(roe: Optional[float], min_threshold: float = ROE_MIN) -> bool:
        """Check if company is profitable (good ROE)"""
        if not roe:
            return False
        return roe >= min_threshold
