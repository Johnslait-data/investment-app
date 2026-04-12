"""
Demo Mode — Test Dashboard with Mock Data
Perfect for testing the UI without API rate limits
"""
import streamlit as st
import plotly.graph_objects as go
from analysis.graham import GrahamAnalyzer
from analysis.fundamentals import FundamentalsAnalyzer
from analysis.scoring import InvestmentScorer

st.set_page_config(
    page_title="Investment Analyzer - Demo",
    page_icon="📈",
    layout="wide",
)

# Mock data (same as demo_mock.py)
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


def get_score_color(score):
    """Get color emoji based on score"""
    if score >= 70:
        return "🟢 BUY"
    elif score >= 40:
        return "🟡 WATCH"
    else:
        return "🔴 AVOID"


st.title("📊 Demo Mode — Test Dashboard")
st.markdown(
    "**Testing the interface with mock data** (no API calls needed)"
)
st.markdown("---")

# Select a stock from demo data
col1, col2 = st.columns([2, 1])
with col1:
    selected_stock = st.selectbox(
        "Select a stock to analyze:",
        [s["ticker"] for s in mock_stocks],
        label_visibility="collapsed",
    )

with col2:
    show_all = st.checkbox("Compare All")

# Find selected stock
stock = next((s for s in mock_stocks if s["ticker"] == selected_stock), None)

if not show_all and stock:
    # Single stock analysis
    st.subheader(f"{stock['ticker']} — {stock['name']}")
    st.markdown("---")

    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Price", f"${stock['price']:.2f}")

    with col2:
        st.metric("P/E Ratio", f"{stock['pe_ratio']:.1f}", "⚠️" if stock["pe_ratio"] > 15 else "✓")

    with col3:
        st.metric("P/B Ratio", f"{stock['pb_ratio']:.2f}", "⚠️" if stock["pb_ratio"] > 1.5 else "✓")

    with col4:
        st.metric(
            "Current Ratio",
            f"{stock['current_ratio']:.2f}",
            "✓" if stock["current_ratio"] >= 1.5 else "⚠️",
        )

    st.markdown("---")

    # 1. PRECIO VS GRAHAM NUMBER (GRÁFICO)
    st.subheader("📈 Precio vs Valor Justo (Graham Number)")

    graham_metrics = GrahamAnalyzer.analyze_stock(
        ticker=stock["ticker"],
        price=stock["price"],
        eps=stock["eps"],
        book_value_per_share=stock["book_value"],
        current_assets=stock["total_debt"] * 0.5,
        current_liabilities=stock["total_debt"] * 0.25,
        total_liabilities=stock["total_debt"],
        shares_outstanding=1e9,
    )

    # Create visualization
    fig = go.Figure()

    # Current price (horizontal line)
    fig.add_hline(
        y=stock["price"],
        name="Current Price",
        line_dash="solid",
        line_color="blue",
        annotation_text=f"Precio Actual: ${stock['price']:.2f}",
        annotation_position="right",
    )

    # Graham Number (horizontal line)
    if graham_metrics.graham_number:
        fig.add_hline(
            y=graham_metrics.graham_number,
            name="Graham Number (Fair Value)",
            line_dash="dash",
            line_color="green",
            annotation_text=f"Graham #: ${graham_metrics.graham_number:.2f}",
            annotation_position="right",
        )

        # NCAV line if exists
        if graham_metrics.ncav_per_share:
            fig.add_hline(
                y=graham_metrics.ncav_per_share * 0.67,
                name="NCAV 67% (Bargain)",
                line_dash="dot",
                line_color="purple",
                annotation_text=f"NCAV 67%: ${graham_metrics.ncav_per_share * 0.67:.2f}",
                annotation_position="right",
            )

    fig.update_layout(
        title=f"{stock['ticker']} — Análisis de Valoración",
        yaxis_title="Precio ($)",
        xaxis_title="",
        height=350,
        showlegend=True,
        hovermode="y unified",
        margin=dict(r=200),
    )

    fig.update_xaxes(showticklabels=False)

    st.plotly_chart(fig, use_container_width=True)

    # Status indicator
    if stock["price"] < graham_metrics.graham_number:
        discount = (
            (graham_metrics.graham_number - stock["price"]) / graham_metrics.graham_number
        ) * 100
        st.success(
            f"✅ **GANGA**: Precio está {discount:.1f}% por debajo del Graham Number"
        )
    else:
        premium = (
            (stock["price"] - graham_metrics.graham_number) / graham_metrics.graham_number
        ) * 100
        st.warning(f"⚠️ **CARO**: Precio está {premium:.1f}% por encima del Graham Number")

    st.markdown("---")

    # Graham Analysis Details
    st.subheader("📊 Graham Analysis Details")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if graham_metrics.graham_number:
            st.metric("Graham Number", f"${graham_metrics.graham_number:.2f}")

    with col2:
        if graham_metrics.margin_of_safety:
            mos = graham_metrics.margin_of_safety * 100
            st.metric("Margin of Safety", f"{mos:+.1f}%")

    with col3:
        if graham_metrics.ncav_per_share:
            st.metric("NCAV/Share", f"${graham_metrics.ncav_per_share:.2f}")

    with col4:
        if graham_metrics.ncav_per_share and stock["price"]:
            discount = (
                (graham_metrics.ncav_per_share - stock["price"])
                / graham_metrics.ncav_per_share
            ) * 100
            st.metric("NCAV Discount", f"{discount:+.1f}%")

    st.markdown("---")

    # 2. SCORECARD DE MÉTRICAS (VISUAL CHECKLIST)
    st.subheader("✅ Scorecard de Métricas")

    col1, col2, col3 = st.columns(3)

    metrics_checks = [
        {
            "name": "P/E Ratio",
            "value": stock["pe_ratio"],
            "threshold": 15,
            "is_good": stock["pe_ratio"] <= 15,
            "label": "≤ 15",
        },
        {
            "name": "P/B Ratio",
            "value": stock["pb_ratio"],
            "threshold": 1.5,
            "is_good": stock["pb_ratio"] <= 1.5,
            "label": "≤ 1.5",
        },
        {
            "name": "Current Ratio",
            "value": stock["current_ratio"],
            "threshold": 1.5,
            "is_good": stock["current_ratio"] >= 1.5,
            "label": "≥ 1.5",
        },
        {
            "name": "ROE",
            "value": stock["roe"] * 100,
            "threshold": 10,
            "is_good": stock["roe"] >= 0.10,
            "label": "≥ 10%",
        },
    ]

    # Display in grid
    cols = st.columns(4)
    for i, metric in enumerate(metrics_checks):
        with cols[i]:
            status_icon = "✅" if metric["is_good"] else "⚠️"
            status_color = "green" if metric["is_good"] else "orange"
            st.markdown(
                f"""
                <div style='background-color: {"#d4edda" if metric["is_good"] else "#fff3cd"};
                            padding: 15px; border-radius: 8px; border-left: 4px solid {status_color}; text-align: center;'>
                    <div style='font-size: 12px; color: gray;'>{metric['name']}</div>
                    <div style='font-size: 24px; font-weight: bold; margin: 8px 0;'>{status_icon} {metric['value']:.1f}</div>
                    <div style='font-size: 11px; color: gray;'>Objetivo: {metric['label']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Fundamentals Analysis
    st.subheader("💰 Fundamentals Analysis")

    fundamentals = FundamentalsAnalyzer.analyze_stock(
        ticker=stock["ticker"],
        price=stock["price"],
        eps=stock["eps"],
        book_value=stock["book_value"],
        current_assets=stock["total_debt"] * 0.5,
        current_liabilities=stock["total_debt"] * 0.25,
        total_debt=stock["total_debt"],
        total_equity=stock["total_equity"],
        roe=stock["roe"],
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**P/E Ratio Analysis**")
        pe_status = "✓ Healthy" if stock["pe_ratio"] <= 15 else "⚠️ Expensive"
        st.write(f"{pe_status} ({stock['pe_ratio']:.1f})")
        st.write(f"Threshold: ≤15")

    with col2:
        st.write("**P/B Ratio Analysis**")
        pb_status = "✓ Healthy" if stock["pb_ratio"] <= 1.5 else "⚠️ Expensive"
        st.write(f"{pb_status} ({stock['pb_ratio']:.2f})")
        st.write(f"Threshold: ≤1.5")

    with col3:
        st.write("**ROE Analysis**")
        roe_status = "✓ Strong" if stock["roe"] >= 0.10 else "⚠️ Weak"
        st.write(f"{roe_status} ({stock['roe']*100:.1f}%)")
        st.write(f"Threshold: ≥10%")

    st.markdown("---")

    # Investment Score
    st.subheader("🎯 Investment Score")

    score, recommendation = InvestmentScorer.calculate_score(graham_metrics, fundamentals)

    col1, col2 = st.columns(2)

    with col1:
        # Display score with color
        score_emoji = get_score_color(score)
        st.metric("Investment Score", f"{score}/100", score_emoji)

    with col2:
        st.metric("Recommendation", recommendation)

    st.markdown("---")

    # 3. CALCULADORA DE PRECIO TARGET
    st.subheader("🎯 Calculadora: ¿A qué Precio Vale la Pena?")

    with st.expander("📊 Calcular Precio Target", expanded=False):
        calc_col1, calc_col2 = st.columns(2)

        with calc_col1:
            st.write("**¿Qué P/E quieres?**")
            target_pe = st.slider(
                "Target P/E Ratio:",
                min_value=5,
                max_value=30,
                value=15,
                step=1,
                label_visibility="collapsed",
            )
            target_price_pe = stock["eps"] * target_pe
            st.metric(f"Precio a P/E={target_pe}", f"${target_price_pe:.2f}")

        with calc_col2:
            st.write("**¿Qué descuento quieres?**")
            discount_pct = st.slider(
                "Descuento al Graham Number (%):",
                min_value=0,
                max_value=50,
                value=30,
                step=5,
                label_visibility="collapsed",
            )
            if graham_metrics.graham_number:
                target_price_discount = graham_metrics.graham_number * (1 - discount_pct / 100)
                st.metric(f"Precio con {discount_pct}% descuento", f"${target_price_discount:.2f}")

        # Show current status vs targets
        st.write("---")
        st.write("**Análisis de Precio:**")

        target_buy_price = min(target_price_pe, target_price_discount if graham_metrics.graham_number else target_price_pe)

        status_cols = st.columns(3)
        with status_cols[0]:
            st.metric("Precio Actual", f"${stock['price']:.2f}")
        with status_cols[1]:
            st.metric("Precio Target", f"${target_buy_price:.2f}")
        with status_cols[2]:
            discount_needed = (
                (target_buy_price - stock["price"]) / stock["price"] * 100
            )
            if discount_needed < 0:
                st.metric(
                    "Caída Necesaria",
                    f"{discount_needed:.1f}%",
                    f"Ya está {abs(discount_needed):.1f}% arriba",
                )
            else:
                st.metric("Caída Necesaria", f"{discount_needed:.1f}%", "Esperar baja")

    st.markdown("---")

    # Detailed Assessment
    details = InvestmentScorer.get_recommendation_details(graham_metrics, fundamentals, score)

    col1, col2 = st.columns(2)

    with col1:
        if details["strengths"]:
            st.write("**✓ Strengths:**")
            for strength in details["strengths"][:5]:
                st.write(f"• {strength}")

    with col2:
        if details["concerns"]:
            st.write("**⚠️ Concerns:**")
            for concern in details["concerns"][:5]:
                st.write(f"• {concern}")

else:
    # Show all stocks in comparison table
    st.subheader("📊 All Stocks Comparison")

    comparison_data = []

    for s in mock_stocks:
        graham_metrics = GrahamAnalyzer.analyze_stock(
            ticker=s["ticker"],
            price=s["price"],
            eps=s["eps"],
            book_value_per_share=s["book_value"],
            current_assets=s["total_debt"] * 0.5,
            current_liabilities=s["total_debt"] * 0.25,
            total_liabilities=s["total_debt"],
            shares_outstanding=1e9,
        )

        fundamentals = FundamentalsAnalyzer.analyze_stock(
            ticker=s["ticker"],
            price=s["price"],
            eps=s["eps"],
            book_value=s["book_value"],
            current_assets=s["total_debt"] * 0.5,
            current_liabilities=s["total_debt"] * 0.25,
            total_debt=s["total_debt"],
            total_equity=s["total_equity"],
            roe=s["roe"],
        )

        score, recommendation = InvestmentScorer.calculate_score(graham_metrics, fundamentals)

        comparison_data.append(
            {
                "Ticker": s["ticker"],
                "Price": f"${s['price']:.2f}",
                "P/E": f"{s['pe_ratio']:.1f}",
                "P/B": f"{s['pb_ratio']:.2f}",
                "Graham #": f"${graham_metrics.graham_number:.2f}" if graham_metrics.graham_number else "N/A",
                "MOS": f"{graham_metrics.margin_of_safety*100:+.1f}%" if graham_metrics.margin_of_safety else "N/A",
                "Score": f"{score}/100",
                "Recommendation": get_score_color(score),
            }
        )

    st.dataframe(comparison_data, use_container_width=True)

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    Demo Mode | Investment Analyzer v1.0 | Graham's Entrepreneurial Investor Principles
    </div>
    """,
    unsafe_allow_html=True,
)
