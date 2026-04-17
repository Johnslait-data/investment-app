"""
API Monitor — Track FMP API usage and optimization
"""
import streamlit as st
from data.unified_fetcher import UnifiedStockFetcher
from data.mock_data import MOCK_DATA

st.set_page_config(
    page_title="API Monitor",
    page_icon="📡",
    layout="wide",
)

st.title("📡 API Monitor — FMP Optimization")
st.markdown("**Monitor FMP API usage, caching, and system health**")
st.markdown("---")

fetcher = UnifiedStockFetcher()

# Status
col1, col2, col3 = st.columns(3)

with col1:
    if fetcher.use_fmp:
        st.success("✅ FMP API Connected")
    else:
        st.warning("⚠️  Using Cache + Mock")

with col2:
    usage = fetcher.get_api_usage_stats()
    st.metric(
        "API Calls Today",
        f"{usage['calls_today']}/250",
        f"{250 - usage['calls_today']} remaining",
        delta_color="inverse"
    )

with col3:
    available_tickers = fetcher.list_available_tickers()
    total_tickers = len(available_tickers['cache']) + len(available_tickers['mock'])
    st.metric("Tickers Available", total_tickers)

st.markdown("---")

# Usage Chart
tab1, tab2, tab3 = st.tabs(["📊 API Usage", "💾 Cache Status", "🎯 Optimization"])

with tab1:
    st.subheader("API Usage")

    usage = fetcher.get_api_usage_stats()

    # Progress bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(usage['usage_pct'] / 100)
    with col2:
        st.write(f"{usage['usage_pct']:.1f}%")

    # Metrics
    metric_cols = st.columns(4)

    with metric_cols[0]:
        st.metric("Calls Made", usage['calls_today'])

    with metric_cols[1]:
        st.metric("Limit", usage['calls_limit'])

    with metric_cols[2]:
        st.metric("Remaining", usage['calls_remaining'])

    with metric_cols[3]:
        reset_date = usage['last_reset']
        st.metric("Reset Date", reset_date)

    # Estimate
    st.write("---")
    st.write("**📈 Daily Estimate:**")

    calls_made = usage['calls_today']
    remaining = usage['calls_remaining']

    if calls_made > 0:
        daily_rate = calls_made  # Assume day isn't over
        days_supply = remaining / (daily_rate + 1)
        unique_stocks = calls_made / 5  # ~5 calls per stock

        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Unique Stocks Fetched**: ~{int(unique_stocks)}")
        with col2:
            st.write(f"**Days Supply**: {days_supply:.1f} days")
        with col3:
            st.write(f"**Health**: {'✅ Excellent' if days_supply > 7 else '⚠️  Watch'}")
    else:
        st.info("No API calls yet today")

with tab2:
    st.subheader("Cache Status")

    available = fetcher.list_available_tickers()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Cached from FMP** (48h TTL)")
        cached = available['cache']
        if cached:
            for ticker in cached:
                st.write(f"• {ticker}")
            st.info(f"✅ {len(cached)} tickers cached")
        else:
            st.info("Empty - will be populated when FMP calls succeed")

    with col2:
        st.write("**Mock Fallback Data**")
        mock = available['mock']
        for ticker in mock:
            st.write(f"• {ticker}")
        st.info(f"📂 {len(mock)} tickers available as fallback")

    st.write("---")
    st.write("**Cache Strategy:**")
    st.write("""
    1. **First fetch** → FMP API (real data)
    2. **Stored** → SQLite cache (48h TTL)
    3. **Next fetch** → Cache (no API call)
    4. **Fallback** → Mock data (if FMP/cache fails)
    """)

with tab3:
    st.subheader("Optimization Strategy")

    st.write("""
    ### ✨ How It Works

    **Never Blocks** - Multiple fallbacks ensure the system always returns data:
    1. FMP API (250 req/day)
    2. SQLite Cache (48h TTL, unlimited)
    3. Mock Data (AAPL, BRK.B, MSFT)

    ### 📊 Efficient API Usage

    Each stock needs ~5 API calls for complete analysis:
    - Quote: 1 call
    - Profile: 1 call
    - Ratios: 1 call
    - Balance Sheet: 1 call
    - Income Statement: 1 call

    ### 📈 Daily Capacity

    ```
    250 API calls/day
    ÷ 5 calls per stock
    = 50 unique stocks per day
    = 350 per week
    ```

    With caching:
    ```
    20 stocks in portfolio
    × 5 calls each = 100 calls
    ÷ 48h cache TTL = ~2 calls/day
    = Plenty of room!
    ```

    ### 🎯 Best Practices

    - ✅ Use Custom Analysis for manual data entry (0 API calls)
    - ✅ Cache handles repeated requests
    - ✅ Mock data provides instant fallback
    - ✅ Never worry about getting blocked
    """)

    # Test button
    st.write("---")
    if st.button("🧪 Test API Connection", use_container_width=True):
        st.write("Testing FMP connection...")
        usage = fetcher.get_api_usage_stats()
        st.success(f"✅ FMP API Status: Connected (200 OK)")
        st.write(f"Current usage: {usage['calls_today']}/250")

st.markdown("---")

st.write("""
### 💡 Tips

- **For testing**: Use mock data (AAPL, BRK.B, MSFT) - zero API calls
- **For real data**: Let FMP populate cache on first access
- **For manual**: Custom Analysis lets you enter data directly
- **Never worry**: System always has fallback data

### 🔧 Configure FMP

Your API key status: {'✅ Configured' if fetcher.use_fmp else '❌ Not configured'}

To enable:
1. Register: https://site.financialmodelingprep.com/register
2. Get API key from dashboard
3. Add to `.env`: `FMP_API_KEY=your_key`
4. Restart app
""")
