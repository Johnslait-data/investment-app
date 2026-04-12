"""
Investment scoring system (0-100)
Based on Graham principles + fundamentals
"""
from typing import Dict, Tuple
from analysis.graham import GrahamAnalyzer, GrahamMetrics
from analysis.fundamentals import FundamentalsAnalyzer, Fundamentals
from config import SCORING_CONFIG, RECOMMENDATIONS
import logging

logger = logging.getLogger(__name__)


class InvestmentScorer:
    """Calculate investment score based on Graham principles"""

    @staticmethod
    def calculate_score(
        graham_metrics: GrahamMetrics,
        fundamentals: Fundamentals,
    ) -> Tuple[int, str]:
        """
        Calculate investment score (0-100)

        Scoring breakdown:
        - NCAV bargain (price ≤ 67% NCAV): +30 (max signal)
        - Below Graham Number: +20
        - Margin of Safety ≥ 30%: +15
        - P/E ≤ 15: +10
        - P/B ≤ 1.5: +10
        - Current Ratio ≥ 1.5: +10
        - D/E ≤ 1.0: +5
        Total: 100

        Args:
            graham_metrics: Graham analysis metrics
            fundamentals: Fundamental metrics

        Returns:
            Tuple of (score: int, recommendation: str)
        """
        score = 0

        # NCAV bargain (max signal for entrepreneurial investor)
        if graham_metrics.ncav_per_share:
            if GrahamAnalyzer.is_ncav_bargain(graham_metrics.price, graham_metrics.ncav_per_share):
                score += SCORING_CONFIG["ncav_ganja"]
                logger.info(f"NCAV bargain detected: +{SCORING_CONFIG['ncav_ganja']}")

        # Below Graham Number
        if graham_metrics.graham_number:
            if GrahamAnalyzer.is_graham_discount(graham_metrics.price, graham_metrics.graham_number):
                score += SCORING_CONFIG["graham_number"]
                logger.info(f"Below Graham Number: +{SCORING_CONFIG['graham_number']}")

        # Margin of safety
        if graham_metrics.margin_of_safety and graham_metrics.margin_of_safety >= 0.30:
            score += SCORING_CONFIG["margin_safety"]
            logger.info(f"Good margin of safety: +{SCORING_CONFIG['margin_safety']}")

        # P/E ratio
        if fundamentals.pe_ratio and FundamentalsAnalyzer.is_pe_healthy(fundamentals.pe_ratio):
            score += SCORING_CONFIG["pe_ratio"]
            logger.info(f"Healthy P/E: +{SCORING_CONFIG['pe_ratio']}")

        # P/B ratio
        if fundamentals.pb_ratio and FundamentalsAnalyzer.is_pb_healthy(fundamentals.pb_ratio):
            score += SCORING_CONFIG["pb_ratio"]
            logger.info(f"Healthy P/B: +{SCORING_CONFIG['pb_ratio']}")

        # Current ratio (liquidity)
        if fundamentals.current_ratio and FundamentalsAnalyzer.is_liquid(fundamentals.current_ratio):
            score += SCORING_CONFIG["current_ratio"]
            logger.info(f"Good liquidity: +{SCORING_CONFIG['current_ratio']}")

        # D/E ratio (leverage)
        if fundamentals.debt_equity and FundamentalsAnalyzer.is_leveraged(fundamentals.debt_equity):
            score += SCORING_CONFIG["debt_equity"]
            logger.info(f"Healthy leverage: +{SCORING_CONFIG['debt_equity']}")

        # Cap at 100
        score = min(score, SCORING_CONFIG["total"])

        # Get recommendation
        recommendation = InvestmentScorer.get_recommendation(score)

        logger.info(f"Final Score: {score}/100 → {recommendation}")
        return score, recommendation

    @staticmethod
    def get_recommendation(score: int) -> str:
        """
        Get recommendation based on score

        Args:
            score: Score from 0-100

        Returns:
            Recommendation string
        """
        if score >= RECOMMENDATIONS["buy"]:
            return "BUY"
        elif score >= RECOMMENDATIONS["watch"]:
            return "WATCH"
        else:
            return "AVOID"

    @staticmethod
    def get_recommendation_details(
        graham_metrics: GrahamMetrics, fundamentals: Fundamentals, score: int
    ) -> Dict:
        """
        Get detailed recommendation with reasons

        Args:
            graham_metrics: Graham metrics
            fundamentals: Fundamental metrics
            score: Final score

        Returns:
            Dict with recommendation details
        """
        reasons = []
        strengths = []
        concerns = []

        # Graham metrics
        if graham_metrics.ncav_per_share:
            if GrahamAnalyzer.is_ncav_bargain(graham_metrics.price, graham_metrics.ncav_per_share):
                strengths.append(
                    f"NCAV Bargain: ${graham_metrics.price:.2f} < ${graham_metrics.ncav_per_share:.2f} "
                    f"({graham_metrics.ncav_discount*100:.1f}% below NCAV)"
                )
            else:
                concerns.append(
                    f"Not an NCAV bargain: ${graham_metrics.price:.2f} > "
                    f"${graham_metrics.ncav_per_share*0.67:.2f} (67% of NCAV)"
                )

        if graham_metrics.graham_number:
            if GrahamAnalyzer.is_graham_discount(graham_metrics.price, graham_metrics.graham_number):
                strengths.append(
                    f"Below Graham Number: ${graham_metrics.price:.2f} < ${graham_metrics.graham_number:.2f} "
                    f"(Discount: {graham_metrics.graham_discount*100:.1f}%)"
                )
            else:
                concerns.append(
                    f"Above Graham Number: ${graham_metrics.price:.2f} > "
                    f"${graham_metrics.graham_number:.2f}"
                )

        if graham_metrics.margin_of_safety:
            if graham_metrics.margin_of_safety >= 0.30:
                strengths.append(
                    f"Good Margin of Safety: {graham_metrics.margin_of_safety*100:.1f}% "
                    f"(≥30% target)"
                )
            else:
                concerns.append(
                    f"Low Margin of Safety: {graham_metrics.margin_of_safety*100:.1f}% "
                    f"(<30% target)"
                )

        # Fundamental metrics
        if fundamentals.pe_ratio:
            if FundamentalsAnalyzer.is_pe_healthy(fundamentals.pe_ratio):
                strengths.append(f"Healthy P/E Ratio: {fundamentals.pe_ratio:.2f} (≤15)")
            else:
                concerns.append(f"High P/E Ratio: {fundamentals.pe_ratio:.2f} (>15)")

        if fundamentals.pb_ratio:
            if FundamentalsAnalyzer.is_pb_healthy(fundamentals.pb_ratio):
                strengths.append(f"Healthy P/B Ratio: {fundamentals.pb_ratio:.2f} (≤1.5)")
            else:
                concerns.append(f"High P/B Ratio: {fundamentals.pb_ratio:.2f} (>1.5)")

        if fundamentals.current_ratio:
            if FundamentalsAnalyzer.is_liquid(fundamentals.current_ratio):
                strengths.append(f"Good Liquidity: Current Ratio {fundamentals.current_ratio:.2f} (≥1.5)")
            else:
                concerns.append(f"Poor Liquidity: Current Ratio {fundamentals.current_ratio:.2f} (<1.5)")

        if fundamentals.debt_equity:
            if FundamentalsAnalyzer.is_leveraged(fundamentals.debt_equity):
                strengths.append(f"Conservative Leverage: D/E {fundamentals.debt_equity:.2f} (≤1.0)")
            else:
                concerns.append(f"High Leverage: D/E {fundamentals.debt_equity:.2f} (>1.0)")

        return {
            "score": score,
            "recommendation": InvestmentScorer.get_recommendation(score),
            "strengths": strengths,
            "concerns": concerns,
        }
