"""
Unit tests for Graham analysis module
"""
import unittest
import math
from analysis.graham import GrahamAnalyzer, GrahamMetrics


class TestGrahamAnalyzer(unittest.TestCase):
    """Test Graham calculations with real stock examples"""

    def test_graham_number_calculation(self):
        """
        Test Graham Number calculation

        Formula: √(22.5 × EPS × BVPS)

        Real example: Apple 2024
        - EPS: ~6.05
        - Book Value per Share: ~45
        - Expected Graham Number: √(22.5 × 6.05 × 45) ≈ $248
        """
        eps = 6.05
        bvps = 45
        expected = math.sqrt(22.5 * eps * bvps)

        result = GrahamAnalyzer.calculate_graham_number(eps, bvps)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=1)
        self.assertGreater(result, 0)
        print(f"✓ Graham Number (AAPL): ${result:.2f}")

    def test_graham_number_invalid_inputs(self):
        """Test Graham Number with invalid inputs"""
        # Zero EPS
        result = GrahamAnalyzer.calculate_graham_number(0, 45)
        self.assertIsNone(result)

        # Negative values
        result = GrahamAnalyzer.calculate_graham_number(-5, 45)
        self.assertIsNone(result)

        # None values
        result = GrahamAnalyzer.calculate_graham_number(None, 45)
        self.assertIsNone(result)

    def test_ncav_calculation(self):
        """
        Test NCAV calculation

        NCAV = (Current Assets - Total Liabilities) / Shares Outstanding

        Example: Conservative industrial company
        - Current Assets: $1,000,000
        - Total Liabilities: $400,000
        - Shares Outstanding: 100,000
        - Expected NCAV per share: ($1,000,000 - $400,000) / 100,000 = $6.00
        """
        current_assets = 1_000_000
        total_liabilities = 400_000
        shares = 100_000
        expected = (current_assets - total_liabilities) / shares

        result = GrahamAnalyzer.calculate_ncav(current_assets, total_liabilities, shares)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=2)
        self.assertEqual(result, 6.0)
        print(f"✓ NCAV per share: ${result:.2f}")

    def test_margin_of_safety(self):
        """
        Test margin of safety calculation

        MOS = (Intrinsic Value - Current Price) / Intrinsic Value

        Example:
        - Intrinsic Value (Graham Number): $100
        - Current Price: $75
        - Expected MOS: ($100 - $75) / $100 = 0.25 (25%)
        """
        intrinsic_value = 100
        price = 75
        expected = (intrinsic_value - price) / intrinsic_value  # 0.25

        result = GrahamAnalyzer.calculate_margin_of_safety(price, intrinsic_value)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=3)
        self.assertEqual(result, 0.25)
        print(f"✓ Margin of Safety: {result*100:.1f}%")

    def test_margin_of_safety_negative(self):
        """
        Test margin of safety when price > intrinsic value

        This indicates the stock is overpriced
        """
        intrinsic_value = 100
        price = 125
        expected = (intrinsic_value - price) / intrinsic_value  # -0.25

        result = GrahamAnalyzer.calculate_margin_of_safety(price, intrinsic_value)

        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=3)
        self.assertLess(result, 0)  # Negative MOS = overpriced
        print(f"✓ Margin of Safety (overpriced): {result*100:.1f}%")

    def test_ncav_bargain_detection(self):
        """
        Test NCAV bargain detection

        Graham's rule: Buy at ≤ 67% of NCAV
        """
        ncav = 100

        # Bargain scenario
        price_bargain = 65
        self.assertTrue(GrahamAnalyzer.is_ncav_bargain(price_bargain, ncav))
        print(f"✓ ${price_bargain} is NCAV bargain (≤ ${ncav * 0.67:.2f})")

        # Not a bargain
        price_fair = 75
        self.assertFalse(GrahamAnalyzer.is_ncav_bargain(price_fair, ncav))
        print(f"✓ ${price_fair} is NOT NCAV bargain")

    def test_graham_discount_detection(self):
        """
        Test Graham Number discount detection
        """
        graham_number = 200

        # Below Graham Number (good)
        price_discount = 180
        self.assertTrue(GrahamAnalyzer.is_graham_discount(price_discount, graham_number))
        print(f"✓ ${price_discount} is below Graham Number (${graham_number})")

        # Above Graham Number (bad)
        price_premium = 220
        self.assertFalse(GrahamAnalyzer.is_graham_discount(price_premium, graham_number))
        print(f"✓ ${price_premium} is above Graham Number")

    def test_complete_graham_analysis(self):
        """
        Test complete Graham analysis with realistic Apple 2024 data

        AAPL 2024 approximate data:
        - Price: $232
        - EPS: $6.05
        - Book Value per Share: $45
        - Current Assets: $54B
        - Current Liabilities: $28.6B
        - Total Liabilities: $106B (includes long-term debt)
        - Shares Outstanding: ~15.6B

        Note: Total liabilities > current assets in Apple's case because they have long-term debt
        This means NCAV will be negative (which is normal for mature tech companies)
        """
        ticker = "AAPL"
        price = 232
        eps = 6.05
        bvps = 45
        current_assets = 54e9
        current_liabilities = 28.6e9
        total_liabilities = 106e9  # Includes long-term debt, which is why > current_assets
        shares = 15.6e9

        metrics = GrahamAnalyzer.analyze_stock(
            ticker=ticker,
            price=price,
            eps=eps,
            book_value_per_share=bvps,
            current_assets=current_assets,
            current_liabilities=current_liabilities,
            total_liabilities=total_liabilities,
            shares_outstanding=shares,
        )

        # Verify calculations
        self.assertEqual(metrics.ticker, ticker)
        self.assertEqual(metrics.price, price)
        self.assertIsNotNone(metrics.graham_number)
        self.assertIsNotNone(metrics.ncav_per_share)
        self.assertIsNotNone(metrics.margin_of_safety)

        # Graham Number should be around $78 based on actual formula
        # √(22.5 × 6.05 × 45) = √6126.5625 ≈ 78.27
        self.assertGreater(metrics.graham_number, 70)
        self.assertLess(metrics.graham_number, 90)
        print(f"✓ AAPL Graham Number: ${metrics.graham_number:.2f}")

        # NCAV is negative (total_liabilities > current_assets)
        # This is normal for mature tech companies with long-term debt
        # Apple: current_assets $54B - total_liabilities $106B = -$52B
        self.assertLess(metrics.ncav_per_share, 0)
        print(f"✓ AAPL NCAV per share: ${metrics.ncav_per_share:.2f} (negative = not an NCAV stock)")

        # Margin of safety should be negative (overpriced relative to Graham Number)
        # Price $232 >> Graham Number ~$78
        self.assertLess(metrics.margin_of_safety, 0)
        print(f"✓ AAPL Margin of Safety: {metrics.margin_of_safety*100:.1f}% (significantly overpriced)")

        # Apple is above Graham Number (expected for a growth/quality stock)
        self.assertFalse(GrahamAnalyzer.is_graham_discount(price, metrics.graham_number))
        print(f"✓ AAPL above Graham Number (not a buy for Graham, but OK for quality investors)")


class TestGrahamEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_zero_shares(self):
        """Test with zero shares outstanding"""
        result = GrahamAnalyzer.calculate_ncav(1_000_000, 400_000, 0)
        self.assertIsNone(result)

    def test_negative_shares(self):
        """Test with negative shares (shouldn't happen but handle gracefully)"""
        result = GrahamAnalyzer.calculate_ncav(1_000_000, 400_000, -100_000)
        self.assertIsNone(result)

    def test_zero_price(self):
        """Test with zero price"""
        result = GrahamAnalyzer.calculate_margin_of_safety(0, 100)
        self.assertIsNone(result)

    def test_zero_intrinsic_value(self):
        """Test with zero intrinsic value"""
        result = GrahamAnalyzer.calculate_margin_of_safety(50, 0)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
