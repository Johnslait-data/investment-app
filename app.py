"""
Investment Analyzer — Graham Entrepreneurial Dashboard
Main Streamlit application entry point
"""
import streamlit as st
import json
from pathlib import Path
from config import WATCHLIST_FILE, CACHE_DB
from data.cache import StockCache
from data.fetcher import fetch_stock_data

# Page configuration
st.set_page_config(
    page_title="Investment Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .buy-signal {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .watch-signal {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .avoid-signal {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_watchlist():
    """Load watchlist from JSON file"""
    if WATCHLIST_FILE.exists():
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    return {"tickers": []}


def save_watchlist(watchlist):
    """Save watchlist to JSON file"""
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f, indent=2)


def get_stock_score_color(score):
    """Get color based on score"""
    if score >= 70:
        return "🟢 BUY"
    elif score >= 40:
        return "🟡 WATCH"
    else:
        return "🔴 AVOID"


def get_stock_data_with_cache(ticker: str, cache: StockCache):
    """
    Get stock data with 48-hour cache optimization
    Reduces API calls dramatically
    """
    # Try cache first (48 hours)
    cached = cache.get_stock(ticker, max_age_hours=48)
    if cached:
        return cached

    # Not in cache or stale, fetch fresh data
    data = fetch_stock_data(ticker)

    # Cache if successful
    if data and "error" not in data:
        cache.set_stock(ticker, data)

    return data


# Header
st.title("📈 Investment Analyzer")
st.markdown("**Graham Entrepreneurial Investor Dashboard**")
st.markdown("---")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Page:",
        ["📋 Watchlist", "🔍 Stock Details", "⚖️ Compare Stocks"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.subheader("About")
    st.markdown(
        """
    This dashboard analyzes stocks using Benjamin Graham's
    **Entrepreneurial Investor** principles:

    - **NCAV**: Net Current Asset Value (buy at ≤67%)
    - **Graham Number**: √(22.5 × EPS × Book Value)
    - **Margin of Safety**: ≥30% protection
    - **Fundamentals**: P/E, P/B, Liquidity, Leverage

    **Score: 0-100**
    - 🟢 70+: BUY
    - 🟡 40-69: WATCH
    - 🔴 <40: AVOID
    """
    )


# Page: Watchlist
if page == "📋 Watchlist":
    st.header("Your Watchlist")

    col1, col2 = st.columns([3, 1])

    with col1:
        new_ticker = st.text_input(
            "Add ticker to watchlist:",
            placeholder="e.g., AAPL, BRK.B, EC",
            label_visibility="collapsed",
        ).upper()

    with col2:
        add_button = st.button("Add to Watchlist", use_container_width=True)

    # Load current watchlist
    watchlist = load_watchlist()

    if add_button and new_ticker:
        if new_ticker not in watchlist["tickers"]:
            watchlist["tickers"].append(new_ticker)
            save_watchlist(watchlist)
            st.success(f"✅ Added {new_ticker}")
            st.rerun()
        else:
            st.warning(f"⚠️ {new_ticker} already in watchlist")

    st.markdown("---")

    if watchlist["tickers"]:
        st.subheader("Analysis Summary")

        cache = StockCache(CACHE_DB)
        analysis_data = []

        # Fetch data for all tickers (with 48h cache)
        progress_bar = st.progress(0)
        for i, ticker in enumerate(watchlist["tickers"]):
            with st.spinner(f"Fetching {ticker}..."):
                data = get_stock_data_with_cache(ticker, cache)

                if data and "error" not in data:
                    analysis_data.append(
                        {
                            "ticker": ticker,
                            "price": data.get("current_price"),
                            "pe_ratio": data.get("pe_ratio"),
                            "pb_ratio": data.get("pb_ratio"),
                            "current_ratio": data.get("current_ratio"),
                        }
                    )

            progress_bar.progress((i + 1) / len(watchlist["tickers"]))

        # Display table
        if analysis_data:
            col_ticker, col_price, col_pe, col_pb, col_current, col_action = st.columns(
                6
            )

            with col_ticker:
                st.markdown("**Ticker**")
            with col_price:
                st.markdown("**Price**")
            with col_pe:
                st.markdown("**P/E**")
            with col_pb:
                st.markdown("**P/B**")
            with col_current:
                st.markdown("**Current Ratio**")
            with col_action:
                st.markdown("**Action**")

            st.markdown("---")

            for item in analysis_data:
                col_ticker, col_price, col_pe, col_pb, col_current, col_action = (
                    st.columns(6)
                )

                with col_ticker:
                    st.markdown(f"**{item['ticker']}**")
                with col_price:
                    price = item["price"]
                    st.markdown(f"${price:.2f}" if price else "N/A")
                with col_pe:
                    pe = item["pe_ratio"]
                    status = "✓" if pe and pe <= 15 else "⚠️"
                    st.markdown(f"{status} {pe:.1f}" if pe else "N/A")
                with col_pb:
                    pb = item["pb_ratio"]
                    status = "✓" if pb and pb <= 1.5 else "⚠️"
                    st.markdown(f"{status} {pb:.2f}" if pb else "N/A")
                with col_current:
                    cr = item["current_ratio"]
                    status = "✓" if cr and cr >= 1.5 else "⚠️"
                    st.markdown(f"{status} {cr:.2f}" if cr else "N/A")
                with col_action:
                    if st.button("View", key=f"view_{item['ticker']}", use_container_width=True):
                        st.session_state["selected_ticker"] = item["ticker"]
                        st.rerun()

                    col_delete = st.columns(1)[0]
                    if st.button("Remove", key=f"delete_{item['ticker']}", use_container_width=True):
                        watchlist["tickers"].remove(item["ticker"])
                        save_watchlist(watchlist)
                        st.success(f"Removed {item['ticker']}")
                        st.rerun()
        else:
            st.info("Could not fetch data. Make sure your API keys are configured.")

    else:
        st.info("📌 Add a stock ticker to get started!")


# Page: Stock Details
elif page == "🔍 Stock Details":
    st.header("Stock Analysis")

    watchlist = load_watchlist()

    if watchlist["tickers"]:
        ticker = st.selectbox(
            "Select a stock:",
            watchlist["tickers"],
            label_visibility="collapsed",
        )

        if ticker:
            with st.spinner(f"Analyzing {ticker}..."):
                cache = StockCache(CACHE_DB)
                data = get_stock_data_with_cache(ticker, cache)

                if data and "error" not in data:
                    # Display header
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Stock Name",
                            data.get("name", "N/A"),
                        )

                    with col2:
                        st.metric(
                            "Current Price",
                            f"${data.get('current_price', 'N/A'):.2f}"
                            if data.get("current_price")
                            else "N/A",
                        )

                    with col3:
                        pe = data.get("pe_ratio")
                        pe_status = "✓ Good" if pe and pe <= 15 else "⚠️ High" if pe else "N/A"
                        st.metric("P/E Ratio", f"{pe:.1f}" if pe else "N/A", pe_status)

                    st.markdown("---")

                    # Graham Metrics
                    st.subheader("Graham Metrics")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        pb = data.get("pb_ratio")
                        st.metric(
                            "P/B Ratio",
                            f"{pb:.2f}" if pb else "N/A",
                            "✓" if pb and pb <= 1.5 else "⚠️",
                        )

                    with col2:
                        cr = data.get("current_ratio")
                        st.metric(
                            "Current Ratio",
                            f"{cr:.2f}" if cr else "N/A",
                            "✓" if cr and cr >= 1.5 else "⚠️",
                        )

                    with col3:
                        de = None
                        if data.get("total_debt") and data.get("total_equity"):
                            de = data.get("total_debt") / data.get("total_equity")
                        st.metric(
                            "D/E Ratio",
                            f"{de:.2f}" if de else "N/A",
                            "✓" if de and de <= 1.0 else "⚠️" if de else "N/A",
                        )

                    with col4:
                        roe = data.get("roe")
                        st.metric(
                            "ROE",
                            f"{roe*100:.1f}%" if roe else "N/A",
                            "✓" if roe and roe >= 0.10 else "⚠️" if roe else "N/A",
                        )

                    st.markdown("---")

                    # 52-week range
                    st.subheader("Price Range (52-week)")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        high = data.get("52week_high")
                        st.metric("52-Week High", f"${high:.2f}" if high else "N/A")

                    with col2:
                        current = data.get("current_price")
                        st.metric(
                            "Current",
                            f"${current:.2f}" if current else "N/A",
                        )

                    with col3:
                        low = data.get("52week_low")
                        st.metric("52-Week Low", f"${low:.2f}" if low else "N/A")

                else:
                    st.error(f"Could not fetch data for {ticker}")

    else:
        st.info("📌 Add stocks to your watchlist first!")


# Page: Compare Stocks
elif page == "⚖️ Compare Stocks":
    st.header("Compare Stocks")

    watchlist = load_watchlist()

    if len(watchlist["tickers"]) >= 2:
        selected_tickers = st.multiselect(
            "Select up to 4 stocks to compare:",
            watchlist["tickers"],
            max_selections=4,
            label_visibility="collapsed",
        )

        if selected_tickers:
            comparison_data = []
            cache = StockCache(CACHE_DB)

            with st.spinner("Fetching data..."):
                for ticker in selected_tickers:
                    data = get_stock_data_with_cache(ticker, cache)
                    if data and "error" not in data:
                        comparison_data.append(data)

            if comparison_data:
                # Create comparison table
                st.subheader("Metrics Comparison")

                comparison_table = []
                for data in comparison_data:
                    comparison_table.append(
                        {
                            "Ticker": data.get("ticker"),
                            "Price": f"${data.get('current_price', 'N/A'):.2f}"
                            if data.get("current_price")
                            else "N/A",
                            "P/E": f"{data.get('pe_ratio', 'N/A'):.1f}",
                            "P/B": f"{data.get('pb_ratio', 'N/A'):.2f}",
                            "Current Ratio": f"{data.get('current_ratio', 'N/A'):.2f}",
                            "ROE": f"{data.get('roe', 'N/A')*100:.1f}%"
                            if data.get("roe")
                            else "N/A",
                        }
                    )

                st.dataframe(comparison_table, use_container_width=True)

            else:
                st.error("Could not fetch data for selected stocks")

    else:
        st.info(f"📌 Add at least 2 stocks to your watchlist to compare (currently {len(watchlist['tickers'])})")


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    Investment Analyzer v1.0 | Based on Benjamin Graham's Principles
    </div>
    """,
    unsafe_allow_html=True,
)
