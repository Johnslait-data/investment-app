"""
Portfolio Statistics - Calculate performance metrics and trading stats
"""
from typing import Dict, List
from datetime import datetime


class PortfolioStatistics:
    """Calculate portfolio-level performance statistics"""

    @staticmethod
    def calculate_performance_stats(positions: List[Dict]) -> Dict:
        """
        Calculate key performance statistics

        Args:
            positions: List of all positions (open and closed)

        Returns:
            Dict with performance metrics
        """
        closed_positions = [p for p in positions if p["status"] == "CLOSED"]
        open_positions = [p for p in positions if p["status"] == "OPEN"]

        if not closed_positions:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "avg_gain": 0,
                "avg_loss": 0,
                "profit_factor": 0,
                "best_trade": None,
                "worst_trade": None,
                "total_realized_pnl": 0,
                "largest_gain": 0,
                "largest_loss": 0,
            }

        total_trades = len(closed_positions)
        winning_trades = [p for p in closed_positions if p["pnl_pct"] > 0]
        losing_trades = [p for p in closed_positions if p["pnl_pct"] < 0]

        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0

        # Calculate average gains and losses
        gains = [p["pnl_pct"] for p in winning_trades]
        losses = [p["pnl_pct"] for p in losing_trades]

        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0

        # Profit factor = gross profit / gross loss (absolute value)
        gross_profit = sum(gains) if gains else 0
        gross_loss = abs(sum(losses)) if losses else 0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0

        # Best and worst trades
        best_trade = max(closed_positions, key=lambda p: p["pnl_pct"]) if closed_positions else None
        worst_trade = min(closed_positions, key=lambda p: p["pnl_pct"]) if closed_positions else None

        # Total realized P&L
        total_realized_pnl = sum(
            (p["exit_price"] - p["entry_price"]) * p["shares"] for p in closed_positions
        )

        largest_gain = best_trade["pnl_pct"] if best_trade else 0
        largest_loss = worst_trade["pnl_pct"] if worst_trade else 0

        return {
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "avg_gain": avg_gain,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "total_realized_pnl": total_realized_pnl,
            "largest_gain": largest_gain,
            "largest_loss": largest_loss,
        }

    @staticmethod
    def calculate_portfolio_metrics(positions: List[Dict]) -> Dict:
        """
        Calculate portfolio-level exposure and allocation

        Args:
            positions: List of all open positions

        Returns:
            Dict with portfolio metrics
        """
        open_positions = [p for p in positions if p["status"] == "OPEN"]

        total_invested = sum(p["total_invested"] for p in open_positions)
        total_current_value = sum(p["current_value"] for p in open_positions if p["current_value"])
        total_pnl = total_current_value - total_invested

        # Portfolio allocation
        allocations = []
        for pos in open_positions:
            allocation_pct = (pos["total_invested"] / total_invested * 100) if total_invested > 0 else 0
            allocations.append({
                "ticker": pos["ticker"],
                "allocation": allocation_pct,
                "invested": pos["total_invested"],
                "current_value": pos.get("current_value", pos["total_invested"]),
            })

        # Sort by allocation
        allocations.sort(key=lambda x: x["allocation"], reverse=True)

        # Concentration risk
        top_3_concentration = sum(a["allocation"] for a in allocations[:3]) if allocations else 0
        avg_position_size = (total_invested / len(open_positions)) if open_positions else 0

        return {
            "num_open_positions": len(open_positions),
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_pnl": total_pnl,
            "total_pnl_pct": (total_pnl / total_invested * 100) if total_invested > 0 else 0,
            "allocations": allocations,
            "top_3_concentration": top_3_concentration,
            "avg_position_size": avg_position_size,
        }

    @staticmethod
    def get_statistics_summary(stats: Dict) -> str:
        """Generate statistics summary"""
        if stats["total_trades"] == 0:
            return "📊 Sin operaciones cerradas aún"

        summary = f"""
        📊 RESUMEN DE OPERACIONES
        ────────────────────────
        Total: {stats['total_trades']} operaciones
        Ganadoras: {stats['winning_trades']} ({stats['win_rate']:.1f}%)
        Perdedoras: {stats['losing_trades']}

        Ganancia Promedio: {stats['avg_gain']:+.1f}%
        Pérdida Promedio: {stats['avg_loss']:+.1f}%
        Profit Factor: {stats['profit_factor']:.2f}x

        Mejor Trade: {stats['best_trade']['ticker']} ({stats['largest_gain']:+.1f}%)
        Peor Trade: {stats['worst_trade']['ticker']} ({stats['largest_loss']:+.1f}%)
        P&L Total Realizado: ${stats['total_realized_pnl']:,.0f}
        """
        return summary.strip()
