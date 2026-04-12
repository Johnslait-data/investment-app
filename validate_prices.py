"""
Validate live prices from yfinance against mock data
Uses SQLite cache to avoid rate limiting
"""
import time
from data.fetcher import fetch_stock_data
from data.cache import StockCache
from datetime import datetime
from pathlib import Path

# Initialize cache
cache_path = Path("data/stock_cache.db")
cache = StockCache(cache_path)

print("\n" + "="*70)
print("🔍 LIVE PRICE VALIDATION (with Smart Cache)")
print("="*70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Cache Location: {cache_path.absolute()}\n")

# Test with a few tickers
test_tickers = ["AAPL", "BRK.B", "MSFT", "GOOGL"]

successful = 0
from_cache = 0
failed = 0

for ticker in test_tickers:
    print(f"\n📊 {ticker}")
    print("-" * 50)

    # Try cache first (48h fresh)
    cached = cache.get_stock(ticker, max_age_hours=48)
    if cached:
        print(f"   📦 Using cached data (fresh)")
        data = cached
        from_cache += 1
    else:
        print(f"   🌐 Attempting live fetch from yfinance...")
        try:
            data = fetch_stock_data(ticker)

            # Cache if successful
            if data and "error" not in data:
                cache.set_stock(ticker, data)
                print(f"   ✅ Fetch successful & cached")
                successful += 1
            else:
                print(f"   ⚠️  No data returned (ticker may be invalid)")
                data = None
                failed += 1
        except Exception as e:
            print(f"   ❌ Fetch failed: {str(e)[:60]}")
            data = None
            failed += 1

    # Display data
    if data and "error" not in data:
        price = data.get("current_price")
        eps = data.get("eps")
        pe = data.get("pe_ratio")
        pb = data.get("pb_ratio")

        print(f"   Price:        ${price:.2f}" if price else "   Price:        N/A")
        print(f"   EPS:          {eps:.2f}" if eps else "   EPS:          N/A")
        print(f"   P/E:          {pe:.2f}" if pe else "   P/E:          N/A")
        print(f"   P/B:          {pb:.2f}" if pb else "   P/B:          N/A")
        if data.get("52week_high"):
            print(f"   52W High:     ${data.get('52week_high'):.2f}")
        if data.get("52week_low"):
            print(f"   52W Low:      ${data.get('52week_low'):.2f}")
    elif data:
        print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
    else:
        print(f"   ❌ No data available")

    # Small delay to avoid rate limiting
    time.sleep(0.5)

print("\n" + "="*70)
print("📊 SUMMARY")
print("="*70)
print(f"   ✅ Fresh fetches: {successful}")
print(f"   📦 From cache:    {from_cache}")
print(f"   ❌ Failed:        {failed}")
print(f"   📈 Total success: {successful + from_cache}/{len(test_tickers)}")
print()

if failed == len(test_tickers):
    print("⚠️  All fetches failed (Yahoo Finance likely rate-limited)")
    print("   Use demo_mock.py for testing, or try again later")
    print("   Cached data (if exists) will be used by dashboard for 48h")
else:
    print("✅ Dashboard will use this data for 48 hours (no new API calls)")

print("\n💡 Cache management:")
print("   View cached tickers: python3 -c \"from data.cache import StockCache; from pathlib import Path; cache=StockCache(Path('data/stock_cache.db')); print(cache.get_all_cached_tickers())\"")
print("   Clear all cache:     python3 -c \"from data.cache import StockCache; from pathlib import Path; StockCache(Path('data/stock_cache.db')).clear_cache()\"")
print()
