"""
Decision Making Tools - Target price, Stop Loss, Buy/Sell signals
"""
from typing import Dict, Tuple
from analysis.graham import GrahamMetrics
from analysis.fundamentals import Fundamentals


class InvestmentDecision:
    """Calculate buy/sell targets and decision checklist"""

    @staticmethod
    def calculate_targets(
        graham_number: float,
        current_price: float,
        profit_target_pct: float = 0.20,
        max_loss_pct: float = 0.30,
    ) -> Dict:
        """
        Calculate target sell price and stop loss

        Args:
            graham_number: Fair value per Graham
            current_price: Current stock price
            profit_target_pct: Desired profit % (default 20%)
            max_loss_pct: Maximum acceptable loss % (default 30%)

        Returns:
            Dict with target_price, stop_loss, expected_gain/loss
        """
        target_price = graham_number * (1 + profit_target_pct)
        stop_loss = current_price * (1 - max_loss_pct)

        upside = ((target_price - current_price) / current_price) * 100
        downside = ((current_price - stop_loss) / current_price) * 100

        return {
            "target_price": target_price,
            "stop_loss": stop_loss,
            "upside_pct": upside,
            "downside_pct": downside,
            "risk_reward_ratio": upside / downside if downside > 0 else 0,
        }

    @staticmethod
    def get_buy_checklist(
        graham_metrics: GrahamMetrics,
        fundamentals: Fundamentals,
        current_price: float,
        score: int,
    ) -> Dict:
        """
        Generate buy/sell decision checklist

        Returns dict with checklist items and final decision
        """
        checks = {}

        # 1. Valuation - Graham Number
        checks["below_graham_number"] = (
            current_price < graham_metrics.graham_number
            if graham_metrics.graham_number
            else False
        )

        # 2. Valuation - P/E Ratio
        checks["pe_ratio_ok"] = (
            fundamentals.pe_ratio <= 15 if fundamentals.pe_ratio else False
        )

        # 3. Valuation - P/B Ratio
        checks["pb_ratio_ok"] = (
            fundamentals.pb_ratio <= 1.5 if fundamentals.pb_ratio else False
        )

        # 4. Margin of Safety
        checks["margin_of_safety_ok"] = (
            graham_metrics.margin_of_safety >= 0.30
            if graham_metrics.margin_of_safety
            else False
        )

        # 5. Liquidity
        checks["liquidity_ok"] = True  # Assumed from fundamentals

        # 6. Leverage
        checks["leverage_ok"] = (
            fundamentals.debt_equity <= 1.0
            if fundamentals.debt_equity
            else True
        )

        # 7. Profitability
        checks["profitability_ok"] = (
            fundamentals.roe >= 0.10 if fundamentals.roe else False
        )

        # 8. Investment Score
        checks["score_ok"] = score >= 40  # At least WATCH level

        # Count passing items
        passing = sum(1 for v in checks.values() if v)
        total = len(checks)

        # Make decision
        if passing >= 7 and score >= 70:
            decision = "🟢 COMPRA"
            reason = "Cumple criterios Graham, score alto"
        elif passing >= 6 and score >= 40:
            decision = "🟡 VIGILA"
            reason = "Candidato, pero espera mejor precio"
        else:
            decision = "🔴 NO COMPRES"
            reason = "No cumple suficientes criterios Graham"

        return {
            "checklist": checks,
            "passing": passing,
            "total": total,
            "decision": decision,
            "reason": reason,
        }

    @staticmethod
    def get_decision_summary(
        ticker: str,
        score: int,
        graham_metrics: GrahamMetrics,
        fundamentals: Fundamentals,
        current_price: float,
        targets: Dict,
        checklist: Dict,
    ) -> str:
        """
        Generate 3-line executive summary
        """
        decision = checklist["decision"]
        reason = checklist["reason"]

        if "COMPRA" in decision:
            action = f"Compra {ticker} a ${current_price:.2f}"
            target = f"Vende en ${targets['target_price']:.2f} ({targets['upside_pct']:+.1f}%)"
        elif "VIGILA" in decision:
            action = f"Monitorea {ticker}, espera caída"
            target = f"Compra ideal: ${targets['stop_loss']:.2f} o menos"
        else:
            action = f"Evita {ticker}, muy caro o fundamentals débiles"
            target = f"Necesitaría caer a ${graham_metrics.graham_number:.2f}"

        return f"{decision}\n{action}\n{target}"
