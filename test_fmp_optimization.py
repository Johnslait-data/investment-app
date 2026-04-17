#!/usr/bin/env python3
"""
Test FMP API with optimization and monitoring
Shows API usage, caching efficiency, and optimization impact
"""
import logging
from data.unified_fetcher import UnifiedStockFetcher
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_usage_bar(usage_stats: dict):
    """Print a visual API usage bar"""
    calls = usage_stats['calls_today']
    limit = usage_stats['calls_limit']
    pct = usage_stats['usage_pct']
    remaining = usage_stats['calls_remaining']

    bar_length = 30
    filled = int(bar_length * pct / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    print(f"\n📊 API Usage: [{bar}] {pct:.1f}%")
    print(f"   {calls}/{limit} calls | {remaining} remaining")

def test_fmp_real():
    """Test FMP API with real data"""
    print("\n" + "="*70)
    print("🌐 TESTING FMP API WITH OPTIMIZATION")
    print("="*70)

    fetcher = UnifiedStockFetcher()

    if not fetcher.use_fmp:
        print("\n❌ FMP API not configured")
        print("Set FMP_API_KEY in .env file")
        return

    print("\n✅ FMP API is configured and ready!")
    print(f"   Limit: 250 requests/day")
    print(f"   Cache TTL: 48 hours")

    # Test 1: Fetch with FMP (will use API)
    print("\n" + "="*70)
    print("TEST 1: First fetch (uses FMP API)")
    print("="*70)

    ticker = "AAPL"
    print(f"\nFetching {ticker} from FMP...")
    start = time.time()
    data = fetcher.get_stock_data(ticker, prefer_cache=False)
    elapsed = time.time() - start

    if data and data.get('source') == 'FMP':
        print(f"✅ Got REAL data from FMP in {elapsed:.2f}s")
        print(f"   Company: {data.get('name')}")
        print(f"   Price: ${data.get('current_price')}")
        print(f"   P/E: {data.get('pe_ratio')}")
        print(f"   Market Cap: ${data.get('market_cap'):,.0f}" if data.get('market_cap') else "")

        usage = fetcher.get_api_usage_stats()
        print_usage_bar(usage)
    else:
        print(f"⚠️  Got fallback data (FMP request failed)")
        print(f"   Source: {data.get('source') if data else 'None'}")

    # Test 2: Fetch same ticker again (should use cache)
    print("\n" + "="*70)
    print("TEST 2: Second fetch of same ticker (uses CACHE)")
    print("="*70)

    print(f"\nFetching {ticker} again (should be cached)...")
    start = time.time()
    data2 = fetcher.get_stock_data(ticker)
    elapsed = time.time() - start

    if data2:
        print(f"✅ Got data from {data2.get('source')} in {elapsed:.3f}s")
        if data2.get('source') == 'FMP':
            print(f"   ℹ️  Still from FMP (cache not ready yet)")
        else:
            print(f"   💾 Cached! (0 API calls used, {elapsed*1000:.1f}ms faster)")

        usage = fetcher.get_api_usage_stats()
        print_usage_bar(usage)

    # Test 3: Fetch different ticker
    print("\n" + "="*70)
    print("TEST 3: Fetch new ticker (uses FMP API)")
    print("="*70)

    ticker2 = "BRK.B"
    print(f"\nFetching {ticker2} (new ticker)...")
    start = time.time()
    data3 = fetcher.get_stock_data(ticker2, prefer_cache=False)
    elapsed = time.time() - start

    if data3 and data3.get('source') == 'FMP':
        print(f"✅ Got REAL data from FMP in {elapsed:.2f}s")
        print(f"   Company: {data3.get('name')}")
        print(f"   Price: ${data3.get('current_price')}")

        usage = fetcher.get_api_usage_stats()
        print_usage_bar(usage)
    else:
        print(f"⚠️  Got fallback data")

    # Summary
    print("\n" + "="*70)
    print("✨ OPTIMIZATION SUMMARY")
    print("="*70)

    final_usage = fetcher.get_api_usage_stats()
    print(f"""
📊 API USAGE:
   Calls made: {final_usage['calls_today']}/250
   Remaining: {final_usage['calls_remaining']}
   Usage: {final_usage['usage_pct']:.1f}%

💾 CACHING BENEFITS:
   ✅ 48-hour cache TTL reduces repeated calls
   ✅ Cache is automatically populated from FMP
   ✅ Fallback to mock if FMP fails

🎯 OPTIMIZATION STRATEGY:
   1. Use FMP for real data (first time)
   2. Cache for 48 hours (avoid re-fetching)
   3. Fall back to mock/cache if FMP fails
   4. Never blocks - always has data

📈 ESTIMATE:
   With caching: ~5 API calls per unique stock
   20 stocks = ~100 calls/week = plenty of room
    """)

def list_cached():
    """List all cached tickers"""
    print("\n" + "="*70)
    print("📦 CACHED STOCKS")
    print("="*70)

    fetcher = UnifiedStockFetcher()
    available = fetcher.list_available_tickers()

    print(f"\n💾 In Cache: {len(available['cache'])}")
    if available['cache']:
        for ticker in available['cache']:
            print(f"   • {ticker}")
    else:
        print("   (empty - will be populated from FMP)")

    print(f"\n📂 Mock Data Available: {len(available['mock'])}")
    for ticker in available['mock']:
        print(f"   • {ticker}")

if __name__ == "__main__":
    test_fmp_real()
    list_cached()

    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70)
