"""
Risk Analysis - Identify specific risks that could hurt investment
"""
from typing import Dict, List


class RiskAnalyzer:
    """Analyze specific risks for a stock investment"""

    @staticmethod
    def analyze_business_risks(
        business_description: str = "",
        competitive_position: str = "weak",
        industry_trend: str = "stable",
    ) -> Dict:
        """
        Analyze business-specific risks

        Args:
            business_description: What does the company do?
            competitive_position: "leader", "competitive", "weak"
            industry_trend: "growing", "stable", "declining"

        Returns:
            Dict with identified risks
        """
        risks = []
        score = 0  # 0-100, higher = more risky

        # Competitive position risk
        if competitive_position == "weak":
            risks.append({
                "category": "Competencia",
                "risk": "Posición competitiva débil",
                "severity": "ALTA",
                "mitigation": "Monitor a competidores, buscar diferenciación",
            })
            score += 30
        elif competitive_position == "leader":
            score -= 10  # Less risk

        # Industry trend risk
        if industry_trend == "declining":
            risks.append({
                "category": "Industria",
                "risk": "Sector en declive",
                "severity": "ALTA",
                "mitigation": "Busca empresa con innovación o pivote",
            })
            score += 25
        elif industry_trend == "growing":
            score -= 15  # Less risk

        # Business clarity risk
        if not business_description or len(business_description) < 20:
            risks.append({
                "category": "Claridad",
                "risk": "No entiendes el negocio",
                "severity": "ALTA",
                "mitigation": "Graham dice: 'no invertas en lo que no entiendes'",
            })
            score += 20

        return {
            "risks": risks,
            "risk_score": min(score, 100),
            "risk_level": "BAJO" if score < 30 else "MEDIO" if score < 60 else "ALTO",
        }

    @staticmethod
    def analyze_financial_risks(
        debt_to_equity: float = 0,
        current_ratio: float = 0,
        roe: float = 0,
    ) -> Dict:
        """
        Analyze financial/balance sheet risks

        Args:
            debt_to_equity: D/E ratio
            current_ratio: Current ratio
            roe: Return on Equity

        Returns:
            Dict with financial risks
        """
        risks = []
        score = 0

        # Leverage risk
        if debt_to_equity > 2:
            risks.append({
                "category": "Deuda",
                "risk": "Empresa muy endeudada (D/E > 2)",
                "severity": "ALTA",
                "detail": f"D/E = {debt_to_equity:.2f}",
            })
            score += 25
        elif debt_to_equity > 1:
            risks.append({
                "category": "Deuda",
                "risk": "Deuda moderada (D/E > 1)",
                "severity": "MEDIA",
                "detail": f"D/E = {debt_to_equity:.2f}",
            })
            score += 10

        # Liquidity risk
        if current_ratio > 0 and current_ratio < 1:
            risks.append({
                "category": "Liquidez",
                "risk": "Liquidez pobre (CR < 1)",
                "severity": "ALTA",
                "detail": f"Current Ratio = {current_ratio:.2f}",
            })
            score += 20
        elif current_ratio > 0 and current_ratio < 1.5:
            risks.append({
                "category": "Liquidez",
                "risk": "Liquidez limitada",
                "severity": "MEDIA",
                "detail": f"Current Ratio = {current_ratio:.2f}",
            })
            score += 10

        # Profitability risk
        if roe < 0:
            risks.append({
                "category": "Rentabilidad",
                "risk": "Empresa con pérdidas (ROE < 0)",
                "severity": "ALTA",
                "detail": f"ROE = {roe*100:.1f}%",
            })
            score += 25
        elif roe > 0 and roe < 0.10:
            risks.append({
                "category": "Rentabilidad",
                "risk": "ROE bajo (< 10%)",
                "severity": "MEDIA",
                "detail": f"ROE = {roe*100:.1f}%",
            })
            score += 10

        return {
            "risks": risks,
            "risk_score": min(score, 100),
            "risk_level": "BAJO" if score < 30 else "MEDIO" if score < 60 else "ALTO",
        }

    @staticmethod
    def analyze_market_risks(
        price_vs_52w_high: float = None,
        price_vs_52w_low: float = None,
        market_cap: float = None,
    ) -> Dict:
        """
        Analyze market/valuation risks

        Args:
            price_vs_52w_high: Current price / 52W high (0-1 = good, >0.9 = risky)
            price_vs_52w_low: Current price / 52W low (>10 = risky)
            market_cap: Market cap in millions

        Returns:
            Dict with market risks
        """
        risks = []
        score = 0

        # Peak price risk
        if price_vs_52w_high and price_vs_52w_high > 0.90:
            risks.append({
                "category": "Valuación",
                "risk": "Precio cerca del máximo de 52W",
                "severity": "MEDIA",
                "detail": f"Ratio: {price_vs_52w_high:.2f}",
                "mitigation": "Espera caída, mejor entry point",
            })
            score += 15

        # Valuation bottom risk
        if price_vs_52w_low and price_vs_52w_low > 10:
            risks.append({
                "category": "Valuación",
                "risk": "Precio muy por encima del mínimo",
                "severity": "BAJA",
                "detail": f"10x arriba del mínimo",
            })
            score += 5

        # Liquidity risk (market cap)
        if market_cap and market_cap < 100:  # Very small cap
            risks.append({
                "category": "Liquidez",
                "risk": "Micro-cap (< $100M)",
                "severity": "MEDIA",
                "mitigation": "Difícil de vender, spreads amplios",
            })
            score += 15

        return {
            "risks": risks,
            "risk_score": min(score, 100),
            "risk_level": "BAJO" if score < 30 else "MEDIO" if score < 60 else "ALTO",
        }

    @staticmethod
    def get_risk_summary(business_risks: Dict, financial_risks: Dict, market_risks: Dict) -> str:
        """Generate risk summary"""
        avg_score = (business_risks["risk_score"] + financial_risks["risk_score"] + market_risks["risk_score"]) / 3

        if avg_score < 30:
            return "🟢 RIESGO BAJO - Proyecto relativamente seguro"
        elif avg_score < 60:
            return "🟡 RIESGO MEDIO - Monitorea de cerca"
        else:
            return "🔴 RIESGO ALTO - Considera alternativas"
