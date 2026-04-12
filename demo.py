"""
Quick demo of the Investment Analyzer system
Tests all components without Streamlit UI
"""
from data.fetcher import fetch_stock_data
from analysis.graham import GrahamAnalyzer
from analysis.fundamentals import FundamentalsAnalyzer
from analysis.scoring import InvestmentScorer
import json

print("\n" + "="*70)
print("📈 INVESTMENT ANALYZER — DEMO")
print("="*70)

# Demo tickers
demo_tickers = ["AAPL", "BRK.B"]

for ticker in demo_tickers:
    print(f"\n\n{'='*70}")
    print(f"📊 {ticker} Analysis")
    print(f"{'='*70}")

    # Fetch data
    print(f"\n🔄 Fetching {ticker} data...")
    data = fetch_stock_data(ticker)

    if data and "error" not in data:
        print(f"✅ Data fetched successfully")

        # Extract key metrics
        ticker_name = data.get("name", "N/A")
        price = data.get("current_price", 0)
        eps = data.get("eps")
        book_value = data.get("book_value_per_share")
        pe_ratio = data.get("pe_ratio")
        pb_ratio = data.get("pb_ratio")
        current_ratio = data.get("current_ratio")
        total_debt = data.get("total_debt")
        total_equity = data.get("total_equity")
        current_assets = data.get("current_assets")
        total_liabilities = data.get("total_liabilities")
        shares = data.get("shares_outstanding")
        roe = data.get("roe")

        # Display basic info
        print(f"\n📌 Basic Info:")
        print(f"   Company: {ticker_name}")
        print(f"   Price: ${price:.2f}" if price else "   Price: N/A")
        if pe_ratio:
            print(f"   P/E Ratio: {pe_ratio:.2f}" if pe_ratio else "   P/E: N/A")
        if pb_ratio:
            print(f"   P/B Ratio: {pb_ratio:.2f}" if pb_ratio else "   P/B: N/A")

        # Graham Analysis
        print(f"\n📊 Graham Analysis:")

        if eps and book_value:
            graham_metrics = GrahamAnalyzer.analyze_stock(
                ticker=ticker,
                price=price,
                eps=eps,
                book_value_per_share=book_value,
                current_assets=current_assets,
                current_liabilities=data.get("current_liabilities"),
                total_liabilities=total_liabilities,
                shares_outstanding=shares,
            )

            if graham_metrics.graham_number:
                print(f"   Graham Number: ${graham_metrics.graham_number:.2f}")
                if price and graham_metrics.graham_number:
                    discount = ((graham_metrics.graham_number - price) / graham_metrics.graham_number) * 100
                    print(f"   Price vs Graham: {discount:+.1f}%")

            if graham_metrics.ncav_per_share:
                print(f"   NCAV/Share: ${graham_metrics.ncav_per_share:.2f}")

            if graham_metrics.margin_of_safety:
                mos = graham_metrics.margin_of_safety * 100
                print(f"   Margin of Safety: {mos:+.1f}%")

        # Fundamentals Analysis
        print(f"\n💰 Fundamentals:")

        if pe_ratio:
            pe_health = "✓" if pe_ratio <= 15 else "⚠️"
            print(f"   P/E Ratio: {pe_health} {pe_ratio:.2f} (threshold: ≤15)")

        if pb_ratio:
            pb_health = "✓" if pb_ratio <= 1.5 else "⚠️"
            print(f"   P/B Ratio: {pb_health} {pb_ratio:.2f} (threshold: ≤1.5)")

        if current_ratio:
            cr_health = "✓" if current_ratio >= 1.5 else "⚠️"
            print(f"   Current Ratio: {cr_health} {current_ratio:.2f} (threshold: ≥1.5)")

        if total_debt is not None and total_equity is not None and total_equity > 0:
            de = total_debt / total_equity
            de_health = "✓" if de <= 1.0 else "⚠️"
            print(f"   D/E Ratio: {de_health} {de:.2f} (threshold: ≤1.0)")

        if roe:
            roe_health = "✓" if roe >= 0.10 else "⚠️"
            print(f"   ROE: {roe_health} {roe*100:.1f}% (threshold: ≥10%)")

        # 52-week range
        high_52w = data.get("52week_high")
        low_52w = data.get("52week_low")
        if high_52w and low_52w:
            print(f"\n📈 52-Week Range:")
            print(f"   High: ${high_52w:.2f}")
            print(f"   Current: ${price:.2f}")
            print(f"   Low: ${low_52w:.2f}")

            position = ((price - low_52w) / (high_52w - low_52w)) * 100 if high_52w != low_52w else 50
            print(f"   Position in range: {position:.0f}%")

    else:
        print(f"⚠️ Could not fetch data for {ticker}")
        if data and "error" in data:
            print(f"   Error: {data.get('error')}")

print(f"\n\n{'='*70}")
print("✅ DEMO COMPLETE")
print(f"{'='*70}")
print("\n📌 Next: Run 'streamlit run app.py' to start the dashboard")
print("🌐 Dashboard will open at: http://localhost:8501\n")
