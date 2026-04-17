"""
Data Validation - Check if input data is realistic and valid
"""
from typing import Dict, List, Tuple


class DataValidator:
    """Validate stock data for realistic values"""

    @staticmethod
    def validate_stock_data(
        ticker: str,
        price: float,
        eps: float,
        bvps: float,
        pe_ratio: float,
        pb_ratio: float,
        current_ratio: float = None,
        de_ratio: float = None,
        roe: float = None,
    ) -> Dict:
        """
        Validate if stock data looks realistic

        Returns dict with validation results and warnings
        """
        warnings = []
        errors = []

        # Check 1: Price should be positive
        if price is None or price <= 0:
            errors.append("❌ Precio debe ser positivo")
        elif price > 100000:
            warnings.append("⚠️ Precio muy alto (>100,000) - verifica moneda")
        elif price < 0.01:
            warnings.append("⚠️ Precio muy bajo (<0.01) - acciones de penique")

        # Check 2: EPS should be positive (usually)
        if eps is not None and eps <= 0:
            warnings.append("⚠️ EPS negativo o cero - empresa no es rentable (aún)")
        elif eps is not None and price is not None and eps > price * 2:
            warnings.append("⚠️ EPS muy alto vs precio - verifica datos")

        # Check 3: Book Value should be positive
        if bvps is not None and bvps <= 0:
            errors.append("❌ Book Value debe ser positivo")

        # Check 4: P/E Ratio
        if pe_ratio is not None and pe_ratio < 0:
            warnings.append("⚠️ P/E negativo - empresa es no rentable")
        elif pe_ratio is not None and pe_ratio > 100:
            warnings.append("⚠️ P/E muy alto (>100) - especulativo")
        elif pe_ratio is not None and pe_ratio > 0 and eps is not None and price is not None:
            calculated_pe = price / eps
            if abs(pe_ratio - calculated_pe) / pe_ratio > 0.01:  # 1% tolerance
                warnings.append("⚠️ P/E no coincide con Precio/EPS - verifica cálculo")

        # Check 5: P/B Ratio
        if pb_ratio is not None and pb_ratio < 0:
            errors.append("❌ P/B no puede ser negativo")
        elif pb_ratio is not None and pb_ratio > 50:
            warnings.append("⚠️ P/B muy alto (>50) - muy sobrevalorado")
        elif pb_ratio is not None and pb_ratio > 0 and bvps is not None and price is not None:
            calculated_pb = price / bvps
            if abs(pb_ratio - calculated_pb) / pb_ratio > 0.01:  # 1% tolerance
                warnings.append("⚠️ P/B no coincide con Precio/BVPS - verifica cálculo")

        # Check 6: Current Ratio
        if current_ratio is not None:
            if current_ratio < 0.5:
                warnings.append("⚠️ Current Ratio muy bajo (<0.5) - problemas de liquidez")
            elif current_ratio > 5:
                warnings.append("⚠️ Current Ratio muy alto (>5) - dinero ocioso")

        # Check 7: D/E Ratio
        if de_ratio is not None:
            if de_ratio < 0:
                errors.append("❌ D/E no puede ser negativo")
            elif de_ratio > 5:
                warnings.append("⚠️ D/E muy alto (>5) - empresa muy endeudada")

        # Check 8: ROE
        if roe is not None:
            if roe < -1 or roe > 1:
                if roe < 0:
                    warnings.append(f"⚠️ ROE negativo ({roe*100:.1f}%) - pérdidas")
                elif roe > 1:
                    warnings.append(f"⚠️ ROE muy alto (>100%) - verifica datos")

        # Check 9: Consistency P/E × P/B should ≈ price/assets
        if pe_ratio is not None and pb_ratio is not None and pe_ratio > 0 and pb_ratio > 0:
            ratio_product = pe_ratio * pb_ratio
            if ratio_product > 500:
                warnings.append(f"⚠️ P/E × P/B muy alto ({ratio_product:.1f}) - sobrevaluado")

        # Summary
        is_valid = len(errors) == 0
        is_suspicious = len(warnings) >= 3

        return {
            "is_valid": is_valid,
            "is_suspicious": is_suspicious,
            "errors": errors,
            "warnings": warnings,
            "summary": f"✅ Datos OK" if is_valid and not is_suspicious else "⚠️ Revisar datos",
        }

    @staticmethod
    def get_validation_status_icon(validation: Dict) -> str:
        """Get icon based on validation status"""
        if validation["errors"]:
            return "❌"
        elif validation["is_suspicious"]:
            return "⚠️"
        else:
            return "✅"

    @staticmethod
    def validate_portfolio_position(position: Dict) -> Tuple[bool, List]:
        """
        Validate a portfolio position

        Returns (is_valid, warnings)
        """
        warnings = []

        # Check entry > stop loss
        if position["entry_price"] <= position["stop_loss"]:
            warnings.append("Entry debe ser mayor que Stop Loss")

        # Check target > entry
        if position["target_price"] <= position["entry_price"]:
            warnings.append("Target debe ser mayor que Entry")

        # Check reasonable risk/reward
        upside = (position["target_price"] - position["entry_price"]) / position["entry_price"]
        downside = (position["entry_price"] - position["stop_loss"]) / position["entry_price"]

        if downside > 0 and upside / downside < 1:
            warnings.append("Risk/Reward < 1:1 - riesgo mayor que ganancia potencial")

        return len(warnings) == 0, warnings
