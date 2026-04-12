"""
Graham's principles for stock analysis
Entrepreneurial investor profile: seeks undervalued stocks (NCAV, Graham Number, margin of safety)
"""
import math
from typing import Optional, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class GrahamMetrics:
    """Graham analysis metrics"""

    ticker: str
    price: float
    eps: Optional[float]
    book_value_per_share: Optional[float]
    current_assets: Optional[float]
    current_liabilities: Optional[float]
    total_liabilities: Optional[float]
    shares_outstanding: Optional[float]

    # Calculated metrics
    graham_number: Optional[float] = None
    ncav_per_share: Optional[float] = None
    margin_of_safety: Optional[float] = None
    ncav_discount: Optional[float] = None
    graham_discount: Optional[float] = None


class GrahamAnalyzer:
    """Analyze stocks using Graham principles"""

    @staticmethod
    def calculate_graham_number(eps: float, book_value_per_share: float) -> Optional[float]:
        """
        Calculate Graham Number

        Formula: √(22.5 × EPS × BVPS)
        This is the "fair value" according to Graham

        Args:
            eps: Earnings per share
            book_value_per_share: Book value per share

        Returns:
            Graham Number or None if inputs invalid
        """
        if not eps or not book_value_per_share or eps <= 0 or book_value_per_share <= 0:
            return None

        try:
            graham_number = math.sqrt(22.5 * eps * book_value_per_share)
            logger.info(f"Graham Number: ${graham_number:.2f}")
            return graham_number
        except Exception as e:
            logger.error(f"Error calculating Graham Number: {e}")
            return None

    @staticmethod
    def calculate_ncav(
        current_assets: float, total_liabilities: float, shares_outstanding: float
    ) -> Optional[float]:
        """
        Calculate Net Current Asset Value (NCAV) per share

        NCAV = (Current Assets - Total Liabilities) / Shares Outstanding

        Graham's rule: Buy at ≤ 67% of NCAV for a "margin of safety"

        Args:
            current_assets: Total current assets
            total_liabilities: Total liabilities
            shares_outstanding: Shares outstanding

        Returns:
            NCAV per share or None
        """
        if not current_assets or not total_liabilities or not shares_outstanding:
            return None

        if shares_outstanding <= 0:
            return None

        try:
            ncav = (current_assets - total_liabilities) / shares_outstanding
            logger.info(f"NCAV per share: ${ncav:.2f}")
            return ncav
        except Exception as e:
            logger.error(f"Error calculating NCAV: {e}")
            return None

    @staticmethod
    def calculate_margin_of_safety(current_price: float, intrinsic_value: float) -> Optional[float]:
        """
        Calculate margin of safety

        MOS = (Intrinsic Value - Current Price) / Intrinsic Value

        Graham wanted at least 30-50% margin of safety

        Args:
            current_price: Current stock price
            intrinsic_value: Calculated intrinsic value (Graham Number or NCAV)

        Returns:
            Margin of safety as percentage (0.3 = 30%) or None
        """
        if not current_price or not intrinsic_value or intrinsic_value <= 0:
            return None

        try:
            mos = (intrinsic_value - current_price) / intrinsic_value
            logger.info(f"Margin of Safety: {mos*100:.2f}%")
            return mos
        except Exception as e:
            logger.error(f"Error calculating margin of safety: {e}")
            return None

    @staticmethod
    def is_ncav_bargain(price: float, ncav: float) -> bool:
        """
        Check if stock is an NCAV bargain

        Graham's rule: Buy at ≤ 67% of NCAV

        Args:
            price: Current price
            ncav: NCAV per share

        Returns:
            True if price ≤ 67% of NCAV
        """
        if not price or not ncav or ncav <= 0:
            return False

        return price <= ncav * 0.67

    @staticmethod
    def is_graham_discount(price: float, graham_number: float) -> bool:
        """
        Check if stock is trading below Graham Number

        Args:
            price: Current price
            graham_number: Calculated Graham Number

        Returns:
            True if price < Graham Number
        """
        if not price or not graham_number or graham_number <= 0:
            return False

        return price < graham_number

    @staticmethod
    def analyze_stock(
        ticker: str,
        price: float,
        eps: Optional[float],
        book_value_per_share: Optional[float],
        current_assets: Optional[float],
        current_liabilities: Optional[float],
        total_liabilities: Optional[float],
        shares_outstanding: Optional[float],
    ) -> GrahamMetrics:
        """
        Complete Graham analysis of a stock

        Args:
            ticker: Stock ticker
            price: Current price
            eps: Earnings per share
            book_value_per_share: Book value per share
            current_assets: Current assets
            current_liabilities: Current liabilities
            total_liabilities: Total liabilities
            shares_outstanding: Shares outstanding

        Returns:
            GrahamMetrics object with all calculations
        """
        metrics = GrahamMetrics(
            ticker=ticker,
            price=price,
            eps=eps,
            book_value_per_share=book_value_per_share,
            current_assets=current_assets,
            current_liabilities=current_liabilities,
            total_liabilities=total_liabilities,
            shares_outstanding=shares_outstanding,
        )

        # Calculate Graham Number
        if eps and book_value_per_share:
            metrics.graham_number = GrahamAnalyzer.calculate_graham_number(eps, book_value_per_share)

        # Calculate NCAV
        if current_assets is not None and total_liabilities is not None and shares_outstanding:
            metrics.ncav_per_share = GrahamAnalyzer.calculate_ncav(
                current_assets, total_liabilities, shares_outstanding
            )

        # Calculate margin of safety (prefer Graham Number, fall back to NCAV)
        if metrics.graham_number:
            metrics.margin_of_safety = GrahamAnalyzer.calculate_margin_of_safety(
                price, metrics.graham_number
            )
            metrics.graham_discount = (metrics.graham_number - price) / metrics.graham_number

        if metrics.ncav_per_share and not metrics.margin_of_safety:
            metrics.margin_of_safety = GrahamAnalyzer.calculate_margin_of_safety(
                price, metrics.ncav_per_share
            )
            metrics.ncav_discount = (metrics.ncav_per_share - price) / metrics.ncav_per_share

        return metrics

    @staticmethod
    def summarize_graham(metrics: GrahamMetrics) -> Dict:
        """
        Summarize Graham analysis as a dict

        Returns:
            Dict with key Graham metrics
        """
        summary = {
            "ticker": metrics.ticker,
            "price": metrics.price,
            "graham_number": metrics.graham_number,
            "graham_discount": metrics.graham_discount,
            "ncav_per_share": metrics.ncav_per_share,
            "ncav_discount": metrics.ncav_discount,
            "margin_of_safety": metrics.margin_of_safety,
            "is_ncav_bargain": (
                GrahamAnalyzer.is_ncav_bargain(metrics.price, metrics.ncav_per_share)
                if metrics.ncav_per_share
                else False
            ),
            "is_graham_discount": (
                GrahamAnalyzer.is_graham_discount(metrics.price, metrics.graham_number)
                if metrics.graham_number
                else False
            ),
        }

        return summary
