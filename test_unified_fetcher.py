#!/usr/bin/env python3
"""
Test Unified Fetcher
Tests FMP API with fallback to cache/mock
"""
import logging
from data.unified_fetcher import UnifiedStockFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_unified_fetcher():
    """Test unified fetcher with all fallbacks"""
    print("\n" + "="*70)
    print("🧪 UNIFIED FETCHER TEST")
    print("="*70)

    fetcher = UnifiedStockFetcher()

    print(f"\n🔍 FMP API Available: {'✅ Yes' if fetcher.use_fmp else '❌ No'}")

    if not fetcher.use_fmp:
        print("   → To use FMP, set FMP_API_KEY in .env")
        print("   → Get free key at: https://site.financialmodelingprep.com/register")

    # Test data availability
    print("\n" + "="*70)
    print("📊 DATA AVAILABILITY CHECK")
    print("="*70)

    available = fetcher.list_available_tickers()
    print(f"\n✅ Mock tickers available: {len(available['mock'])}")
    print(f"   {', '.join(available['mock'])}")

    print(f"\n💾 Cached tickers: {len(available['cache'])}")
    if available['cache']:
        print(f"   {', '.join(available['cache'][:5])}")
    else:
        print("   (empty)")

    # Test each mock ticker
    print("\n" + "="*70)
    print("🧲 FETCHING DATA FOR MOCK TICKERS")
    print("="*70)

    for ticker in available['mock']:
        print(f"\n[{ticker}]")

        # Check availability
        status = fetcher.validate_data_source(ticker)
        print(f"  Sources: ", end="")
        sources = []
        if status['fmp_available']:
            sources.append("🟦 FMP")
        if status['cache_available']:
            sources.append("💾 Cache")
        if status['mock_available']:
            sources.append("📂 Mock")
        print(", ".join(sources))

        # Fetch data
        print(f"  → Fetching (FMP → Cache → Mock)...")
        data = fetcher.get_stock_data(ticker)

        if data:
            print(f"  ✅ Success!")
            print(f"     Source: {data.get('source', 'unknown')}")
            print(f"     Price: ${data.get('current_price', 'N/A')}")
            print(f"     P/E: {data.get('pe_ratio', 'N/A')}")
            print(f"     P/B: {data.get('pb_ratio', 'N/A')}")
        else:
            print(f"  ❌ Failed to fetch")

    # Test prefer cache
    print("\n" + "="*70)
    print("⚙️  TESTING CACHE PREFERENCE")
    print("="*70)

    ticker = "AAPL"
    print(f"\nFetching {ticker} with prefer_cache=True...")
    data = fetcher.get_stock_data(ticker, prefer_cache=True)
    if data:
        print(f"✅ Got data from source: {data.get('source', 'unknown')}")
    else:
        print("❌ No data")

    # Summary
    print("\n" + "="*70)
    print("✨ SUMMARY")
    print("="*70)

    if fetcher.use_fmp:
        print("""
✅ FMP API is configured and ready!
   • 250 requests/day limit (free tier)
   • Real data will be fetched from FMP
   • Automatically cached as fallback
   • Never blocks or fails completely
        """)
    else:
        print("""
⚠️  FMP API not configured
   • To enable: Set FMP_API_KEY in .env
   • Currently using: Cache + Mock data
   • System always has fallback data
   • Production-ready even without FMP
        """)

if __name__ == "__main__":
    test_unified_fetcher()
