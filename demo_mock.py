"""
Demo with mock data (no API calls needed)
Perfect for testing without hitting rate limits
"""
from analysis.graham import GrahamAnalyzer
from analysis.fundamentals import FundamentalsAnalyzer
from analysis.scoring import InvestmentScorer

print("\n" + "="*70)
print("📈 INVESTMENT ANALYZER — DEMO (Mock Data)")
print("="*70)

# Mock data for AAPL (April 2026)
mock_stocks = [
    {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "price": 260.48,
        "eps": 6.05,
        "book_value": 45.0,
        "pe_ratio": 43.0,
        "pb_ratio": 5.78,
        "current_ratio": 0.97,
        "total_debt": 106e9,
        "total_equity": 54e9,
        "roe": 1.52,
    },
    {
        "ticker": "BRK.B",
        "name": "Berkshire Hathaway Inc.",
        "price": 430.0,
        "eps": 42.5,
        "book_value": 50.0,
        "pe_ratio": 10.1,
        "pb_ratio": 1.35,
        "current_ratio": 1.8,
        "total_debt": 7e9,
        "total_equity": 900e9,
        "roe": 0.085,
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "price": 425.0,
        "eps": 13.1,
        "book_value": 25.0,
        "pe_ratio": 32.4,
        "pb_ratio": 16.2,
        "current_ratio": 1.2,
        "total_debt": 29e9,
        "total_equity": 100e9,
        "roe": 0.35,
    },
]

for stock in mock_stocks:
    print(f"\n\n{'='*70}")
    print(f"📊 {stock['ticker']} Analysis")
    print(f"{'='*70}")

    ticker = stock["ticker"]
    price = stock["price"]
    eps = stock["eps"]
    book_value = stock["book_value"]
    pe_ratio = stock["pe_ratio"]
    pb_ratio = stock["pb_ratio"]
    current_ratio = stock["current_ratio"]
    roe = stock["roe"]

    # Display basic info
    print(f"\n📌 Basic Info:")
    print(f"   Company: {stock['name']}")
    print(f"   Price: ${price:.2f}")
    print(f"   P/E Ratio: {pe_ratio:.2f}")
    print(f"   P/B Ratio: {pb_ratio:.2f}")

    # Graham Analysis
    print(f"\n📊 Graham Analysis:")

    graham_metrics = GrahamAnalyzer.analyze_stock(
        ticker=ticker,
        price=price,
        eps=eps,
        book_value_per_share=book_value,
        current_assets=stock["total_debt"] * 0.5,
        current_liabilities=stock["total_debt"] * 0.25,
        total_liabilities=stock["total_debt"],
        shares_outstanding=1e9,
    )

    if graham_metrics.graham_number:
        print(f"   Graham Number: ${graham_metrics.graham_number:.2f}")
        if price and graham_metrics.graham_number:
            discount = ((graham_metrics.graham_number - price) / graham_metrics.graham_number) * 100
            print(f"   Price vs Graham: {discount:+.1f}%")

    if graham_metrics.margin_of_safety:
        mos = graham_metrics.margin_of_safety * 100
        print(f"   Margin of Safety: {mos:+.1f}%")

    # Fundamentals Analysis
    print(f"\n💰 Fundamentals:")

    pe_health = "✓" if pe_ratio <= 15 else "⚠️"
    print(f"   P/E Ratio: {pe_health} {pe_ratio:.2f} (threshold: ≤15)")

    pb_health = "✓" if pb_ratio <= 1.5 else "⚠️"
    print(f"   P/B Ratio: {pb_health} {pb_ratio:.2f} (threshold: ≤1.5)")

    cr_health = "✓" if current_ratio >= 1.5 else "⚠️"
    print(f"   Current Ratio: {cr_health} {current_ratio:.2f} (threshold: ≥1.5)")

    roe_health = "✓" if roe >= 0.10 else "⚠️"
    print(f"   ROE: {roe_health} {roe*100:.1f}% (threshold: ≥10%)")

    # Scoring
    print(f"\n🎯 Investment Score:")

    fundamentals = FundamentalsAnalyzer.analyze_stock(
        ticker=ticker,
        price=price,
        eps=eps,
        book_value=book_value,
        current_assets=stock["total_debt"] * 0.5,
        current_liabilities=stock["total_debt"] * 0.25,
        total_debt=stock["total_debt"],
        total_equity=stock["total_equity"],
        roe=roe,
    )

    score, recommendation = InvestmentScorer.calculate_score(graham_metrics, fundamentals)
    print(f"   Score: {score}/100")
    print(f"   Recommendation: {recommendation}")

    # Details
    details = InvestmentScorer.get_recommendation_details(graham_metrics, fundamentals, score)
    if details["strengths"]:
        print(f"\n   ✓ Strengths:")
        for strength in details["strengths"][:3]:
            print(f"     • {strength}")
    if details["concerns"]:
        print(f"\n   ⚠️ Concerns:")
        for concern in details["concerns"][:3]:
            print(f"     • {concern}")

print(f"\n\n{'='*70}")
print("✅ DEMO COMPLETE")
print(f"{'='*70}")
print("\n📌 This demo uses mock data to avoid API rate limits")
print("🌐 For live data, run: streamlit run app.py\n")
