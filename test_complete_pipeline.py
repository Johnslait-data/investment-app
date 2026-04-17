#!/usr/bin/env python3
"""
Complete Pipeline Test
Verifies data fetching, caching, and analysis for multiple stocks
"""
import sys
from data.unified_fetcher import UnifiedStockFetcher
from analysis.graham import GrahamAnalyzer
from analysis.validation import DataValidator

# Test tickers: US stocks + Colombian ADR
TEST_TICKERS = [
    "AAPL",      # Apple - large cap tech
    "EC",        # Ecopetrol ADR - Colombian energy
    "BRK.B",     # Berkshire Hathaway - dividend stock
    "MSFT",      # Microsoft
]

def test_pipeline():
    """Test complete data → analysis pipeline"""
    fetcher = UnifiedStockFetcher()
    validator = DataValidator()
    analyzer = GrahamAnalyzer()

    print("=" * 70)
    print("COMPLETE PIPELINE TEST")
    print("=" * 70)
    print(f"\nAPI Usage at start: {fetcher.get_api_usage_stats()}")
    print()

    results = {}

    for ticker in TEST_TICKERS:
        print(f"\n{'─' * 70}")
        print(f"Testing: {ticker}")
        print('─' * 70)

        try:
            # Step 1: Fetch data
            print(f"  1️⃣  Fetching data...")
            data = fetcher.get_stock_data(ticker)

            if not data:
                print(f"     ❌ No data available")
                results[ticker] = {"status": "FAILED", "error": "No data"}
                continue

            # Show data source
            source = data.get("source", "UNKNOWN")
            print(f"     ✅ Source: {source}")

            # Step 2: Validate data
            print(f"  2️⃣  Validating data...")
            validation = validator.validate_stock_data(
                ticker=ticker,
                price=data.get("price") or data.get("current_price", 0),
                eps=data.get("eps", 0),
                bvps=data.get("book_value_per_share", 0),
                pe_ratio=data.get("pe_ratio", 0),
                pb_ratio=data.get("pb_ratio", 0),
                current_ratio=data.get("current_ratio"),
                de_ratio=data.get("debt_to_equity"),
                roe=data.get("roe"),
            )
            status_icon = validator.get_validation_status_icon(validation)
            status = "✅ Valid" if validation["is_valid"] else "⚠️ Suspicious" if validation["is_suspicious"] else "❌ Invalid"
            print(f"     {status_icon} {status}")

            if validation["warnings"]:
                for warning in validation["warnings"][:2]:  # Show first 2 warnings
                    print(f"     {warning}")

            # Step 3: Calculate Graham metrics
            print(f"  3️⃣  Calculating Graham metrics...")
            metrics_obj = analyzer.analyze_stock(
                ticker=ticker,
                price=data.get("price", 0),
                eps=data.get("eps"),
                book_value_per_share=data.get("book_value_per_share"),
                current_assets=data.get("current_assets"),
                current_liabilities=data.get("current_liabilities"),
                total_liabilities=data.get("total_liabilities"),
                shares_outstanding=data.get("shares_outstanding"),
            )

            if metrics_obj:
                graham_summary = analyzer.summarize_graham(metrics_obj)
                print(f"     ✅ Graham analysis complete")
                if graham_summary.get('graham_number'):
                    print(f"     • Graham Number: ${graham_summary['graham_number']:.2f}")
                if graham_summary.get('graham_discount'):
                    print(f"     • Graham Discount: {graham_summary['graham_discount']:.1%}")
                if graham_summary.get('margin_of_safety'):
                    print(f"     • Margin of Safety: {graham_summary['margin_of_safety']:.1%}")
                print(f"     • Is Graham Discount: {graham_summary.get('is_graham_discount', False)}")
                print(f"     • Is NCAV Bargain: {graham_summary.get('is_ncav_bargain', False)}")
            else:
                print(f"     ⚠️  Could not calculate Graham metrics")

            # Summary
            results[ticker] = {
                "status": "SUCCESS",
                "source": source,
                "validation": validation.get("summary", "Unknown"),
                "graham": graham_summary if metrics_obj else None,
                "data_keys": list(data.keys())
            }

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results[ticker] = {"status": "FAILED", "error": str(e)}

    # Final API usage
    print(f"\n{'═' * 70}")
    print("FINAL API USAGE:")
    api_usage = fetcher.get_api_usage_stats()
    print(f"  Calls made: {api_usage['calls_today']}/250")
    print(f"  Calls remaining: {api_usage['calls_remaining']}")
    print(f"  Usage: {api_usage['usage_pct']:.1f}%")

    # Summary table
    print(f"\n{'═' * 70}")
    print("SUMMARY:")
    print(f"{'Ticker':<10} {'Status':<12} {'Source':<10} {'Validation':<15}")
    print('─' * 50)

    success_count = 0
    for ticker, result in results.items():
        if result["status"] == "SUCCESS":
            success_count += 1
            source = result.get("source", "?")
            validation = result.get("validation", "?")
            print(f"{ticker:<10} {result['status']:<12} {source:<10} {validation:<15}")
        else:
            print(f"{ticker:<10} {result['status']:<12} {'N/A':<10} {'N/A':<15}")

    print(f"\n✅ Passed: {success_count}/{len(TEST_TICKERS)}")

    # Cache status
    print(f"\n{'═' * 70}")
    print("CACHE STATUS:")
    cache_list = fetcher.list_available_tickers()
    print(f"  Cached tickers: {cache_list['cache']}")
    print(f"  Mock tickers available: {cache_list['mock']}")

    return success_count == len(TEST_TICKERS)

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
