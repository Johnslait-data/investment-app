#!/usr/bin/env python3
"""
Safe API testing script
Tests real API with rate limiting protections
"""
import sys
import logging
from pathlib import Path
from data.fetcher import StockDataFetcher, fetch_stock_data
from data.cache import StockCache
from analysis.validation import DataValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test tickers (start with small batch)
TEST_TICKERS = ["AAPL", "BRK.B", "MSFT"]

def test_with_cache():
    """Test with cached data first"""
    print("\n" + "="*70)
    print("🔄 FASE 1: Testing with Cache (Safe)")
    print("="*70)

    cache = StockCache(Path("data/stock_cache.db"))
    cached_tickers = cache.get_all_cached_tickers()

    print(f"\n📊 Tickers in cache: {len(cached_tickers)}")
    if cached_tickers:
        print(f"   {', '.join(cached_tickers[:5])}")

    # Test with first cached ticker if available
    if cached_tickers:
        ticker = cached_tickers[0]
        print(f"\n✓ Testing cache retrieval with {ticker}")
        data = cache.get_stock(ticker, max_age_hours=24)
        if data:
            print(f"  ✅ Cache hit: {ticker}")
            print(f"     Price: {data.get('current_price')}")
            print(f"     P/E: {data.get('pe_ratio')}")
        else:
            print(f"  ❌ Cache miss or stale: {ticker}")

def test_with_api_safe():
    """Test with real API using rate limiting"""
    print("\n" + "="*70)
    print("🌐 FASE 2: Testing with Real API (With Rate Limiting)")
    print("="*70)

    fetcher = StockDataFetcher()

    # Test one ticker at a time with delays
    for i, ticker in enumerate(TEST_TICKERS, 1):
        print(f"\n[{i}/{len(TEST_TICKERS)}] Testing {ticker}...")

        try:
            # Get current price
            print(f"  → Fetching price...")
            price = fetcher.get_current_price(ticker)
            if price:
                print(f"     ✅ Price: ${price:.2f}")
            else:
                print(f"     ⚠️  No price data")
                continue

            # Get fundamentals
            print(f"  → Fetching fundamentals...")
            fundamentals = fetcher.get_fundamentals(ticker)

            if "error" in fundamentals:
                print(f"     ❌ Error: {fundamentals['error']}")
                continue

            print(f"     ✅ Got fundamentals")
            print(f"        P/E: {fundamentals.get('pe_ratio')}")
            print(f"        P/B: {fundamentals.get('pb_ratio')}")

            # Get historical data
            print(f"  → Fetching historical data...")
            hist = fetcher.get_historical_data(ticker, period="1y")
            if not hist.empty:
                print(f"     ✅ Got {len(hist)} rows of historical data")
            else:
                print(f"     ⚠️  No historical data")

        except Exception as e:
            print(f"     ❌ Error: {e}")

def test_validation():
    """Test data validation"""
    print("\n" + "="*70)
    print("✅ FASE 3: Testing Data Validation")
    print("="*70)

    # Example data
    test_data = {
        "ticker": "AAPL",
        "price": 260.48,
        "eps": 6.05,
        "bvps": 45.0,
        "pe_ratio": 43.0,
        "pb_ratio": 5.78,
        "current_ratio": 0.97,
        "de_ratio": 1.5,
        "roe": 1.52,
    }

    print(f"\nValidating: {test_data['ticker']}")
    validation = DataValidator.validate_stock_data(**test_data)

    print(f"Status: {validation['summary']}")
    print(f"Valid: {validation['is_valid']}")
    print(f"Suspicious: {validation['is_suspicious']}")

    if validation['errors']:
        print("\n❌ Errors:")
        for error in validation['errors']:
            print(f"   • {error}")

    if validation['warnings']:
        print("\n⚠️  Warnings:")
        for warning in validation['warnings']:
            print(f"   • {warning}")

def test_full_fetch():
    """Test full fetch with cache"""
    print("\n" + "="*70)
    print("📦 FASE 4: Testing Full Fetch with Cache")
    print("="*70)

    ticker = "BRK.B"
    print(f"\nFetching {ticker} with cache enabled...")

    try:
        data = fetch_stock_data(ticker, use_cache=True, cache_age_hours=24)

        if data and "error" not in data:
            print(f"✅ Success!")
            print(f"   Name: {data.get('name')}")
            print(f"   Price: ${data.get('current_price')}")
            print(f"   P/E: {data.get('pe_ratio')}")
            print(f"   52W High: ${data.get('52week_high')}")
            print(f"   52W Low: ${data.get('52week_low')}")
        else:
            print(f"❌ Failed: {data.get('error') if data else 'No data'}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 SAFE API TEST SCRIPT")
    print("="*70)
    print("Testing with rate limiting protection (1-2s delays between requests)")

    # Run tests in order
    test_with_cache()
    test_with_api_safe()
    test_validation()
    test_full_fetch()

    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
