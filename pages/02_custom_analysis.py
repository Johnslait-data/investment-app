"""
Custom Stock Analysis — Ingresa datos REALES del Balance Sheet
Para acciones colombianas, LATAM, y stocks donde APIs fallan
Basado en datos verificables del Balance Sheet de la empresa
"""
import streamlit as st
import plotly.graph_objects as go
from analysis.graham import GrahamAnalyzer
from analysis.fundamentals import FundamentalsAnalyzer
from analysis.scoring import InvestmentScorer
from analysis.decision import InvestmentDecision
from analysis.validation import DataValidator
from analysis.risk import RiskAnalyzer

st.set_page_config(
    page_title="Custom Analysis",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Análisis Personalizado — Balance Sheet Real")
st.markdown("**Ingresa datos REALES del Balance Sheet para cualquier acción**")
st.markdown("---")

# Tabs for instructions and analysis
tab1, tab2 = st.tabs(["📝 Ingresa Datos", "📚 Cómo Obtener Datos"])

with tab2:
    st.subheader("📚 Guía: Dónde Obtener Datos del Balance Sheet")

    st.write("""
    ### **Paso 1: Encuentra el Balance Sheet**

    **Para acciones latinoamericanas:**
    - 🇨🇴 [BVC Colombia](https://www.bvc.com.co) → Busca empresa → Financial Statements
    - 📊 [Yahoo Finance](https://finance.yahoo.com) → Tab "Financials" → "Balance Sheet"
    - 💼 [Investing.com](https://investing.com) → Tab "Financial"
    - 🏢 **Investor Relations** de la empresa

    ### **Paso 2: Identifica estos números (del Balance Sheet)**

    ✅ **Total Shareholders' Equity** (también llamado "Total Equity", "Patrimonio")
    - Está al final del lado derecho del Balance Sheet
    - Fórmula: Assets - Liabilities

    ✅ **Shares Outstanding** (también "Acciones en Circulación")
    - En la sección "Share Information" del reporte
    - O en "Common Stock Outstanding"

    ✅ **Current Assets** (Activos Corrientes)
    - Dinero, cuentas por cobrar, inventarios que se pueden convertir en 1 año

    ✅ **Current Liabilities** (Pasivos Corrientes)
    - Deudas, impuestos que vencen en 1 año

    ✅ **Total Debt** (Deuda Total)
    - Suma de: Short-term debt + Long-term debt
    - O puedes usar: Assets - Equity

    ### **Paso 3: Obtén el Precio y EPS**

    ✅ **Precio Actual**: Yahoo Finance, Google Finance, o tu broker

    ✅ **EPS (TTM)**: Earnings per Share - Trailing 12 Months
    - Yahoo Finance → Statistics tab
    - O: Net Income (TTM) / Shares Outstanding

    ### **Ejemplo Real: Ecopetrol (ECOPETROL.CL)**

    ```
    Balance Sheet 12/31/2024 (en COP):
    ─────────────────────────────────
    Total Equity: 79,854,603,000 COP
    Shares Outstanding: 41,116,694.69 miles
    Current Assets: 60,659,805,000 COP
    Current Liabilities: 39,635,471,000 COP
    Total Debt: 119,965,031,000 COP

    Income Statement (TTM):
    ─────────────────────────────────
    Precio: 2,555.00 COP
    EPS: 219.59 COP

    Resultado:
    → BVPS = 79,854,603,000 / 41,116,694.69 = 1,942.89 COP
    → Score: 50/100 → VIGILA
    ```
    """)

with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📝 Datos de la Acción")

        st.write("**Info General**")
        ticker = st.text_input(
            "Ticker:",
            value="ECOPETROL.CL",
            placeholder="e.g., ECOPETROL.CL, AAPL",
            key="ticker_input"
        )
        company_name = st.text_input(
            "Nombre Empresa:",
            value="Ecopetrol S.A.",
            placeholder="e.g., Ecopetrol S.A.",
            key="company_input"
        )

        currency = st.selectbox("Moneda:", ["COP", "USD", "EUR"], index=0)

        st.write("---")
        st.write("**Precio & Earnings**")

        price = st.number_input(
            f"Precio Actual ({currency}):",
            value=2555.0,
            min_value=0.01,
            step=10.0,
            key="price_input"
        )

        eps = st.number_input(
            f"EPS (TTM) ({currency}):",
            value=219.59,
            min_value=0.01,
            step=10.0,
            key="eps_input"
        )

        st.write("---")
        st.write("**Balance Sheet Data**")
        st.caption("Números en miles (o unidades). El sistema los convierte automáticamente.")

        # Total Equity and Shares Outstanding
        total_equity = st.number_input(
            f"Total Shareholders' Equity ({currency} millones/miles):",
            value=79854603.0,
            min_value=0.01,
            step=1000.0,
            key="equity_input"
        )

        shares_outstanding = st.number_input(
            "Shares Outstanding (millones/miles):",
            value=41116.69,
            min_value=0.01,
            step=1.0,
            key="shares_input"
        )

        # Calculate BVPS automatically
        bvps = total_equity / shares_outstanding if shares_outstanding > 0 else 0

        st.metric(
            "📊 Book Value per Share (Calculado)",
            f"{bvps:,.2f} {currency}",
            f"({total_equity:,.0f} / {shares_outstanding:,.2f})"
        )

        st.write("---")
        st.write("**Ratios de Balance (Opcional)**")
        st.caption("Si no sabes los valores, déjalos en 0 y se saltarán.")

        current_assets = st.number_input(
            f"Current Assets ({currency} millones/miles):",
            value=60659.805,
            min_value=0.0,
            step=100.0,
            key="ca_input"
        )

        current_liabilities = st.number_input(
            f"Current Liabilities ({currency} millones/miles):",
            value=39635.471,
            min_value=0.0,
            step=100.0,
            key="cl_input"
        )

        total_debt = st.number_input(
            f"Total Debt ({currency} millones/miles):",
            value=119965.031,
            min_value=0.0,
            step=1000.0,
            key="debt_input"
        )

        st.write("---")
        analyze_button = st.button("🔍 Analizar con Graham", use_container_width=True, key="analyze_btn")

    # Results column
    with col2:
        if analyze_button:
            # Validate inputs
            if price <= 0 or eps <= 0 or bvps <= 0:
                st.error("❌ Error: Precio, EPS y BVPS deben ser mayores que 0")
            else:
                st.subheader(f"📊 {ticker} — {company_name}")
                st.markdown("---")

                # Convert units (assume input is in thousands)
                equity_units = total_equity * 1000
                shares_units = shares_outstanding * 1000
                ca_units = current_assets * 1000 if current_assets > 0 else None
                cl_units = current_liabilities * 1000 if current_liabilities > 0 else None
                debt_units = total_debt * 1000 if total_debt > 0 else None

                # Calculate Graham metrics
                graham_metrics = GrahamAnalyzer.analyze_stock(
                    ticker=ticker,
                    price=price,
                    eps=eps,
                    book_value_per_share=bvps,
                    current_assets=ca_units,
                    current_liabilities=cl_units,
                    total_liabilities=debt_units,
                    shares_outstanding=shares_units,
                )

                # Calculate fundamentals
                current_ratio = None
                if current_assets > 0 and current_liabilities > 0:
                    current_ratio = current_assets / current_liabilities

                roe = eps / bvps if bvps > 0 else None

                fundamentals = FundamentalsAnalyzer.analyze_stock(
                    ticker=ticker,
                    price=price,
                    eps=eps,
                    book_value=bvps,
                    current_assets=ca_units,
                    current_liabilities=cl_units,
                    total_debt=debt_units,
                    total_equity=equity_units,
                    roe=roe,
                )

                # 1. GRÁFICO: PRECIO VS GRAHAM NUMBER
                st.subheader("📈 Precio vs Valor Justo (Graham Number)")

                if graham_metrics.graham_number:
                    fig = go.Figure()

                    fig.add_hline(
                        y=price,
                        name="Precio Actual",
                        line_dash="solid",
                        line_color="blue",
                        annotation_text=f"Precio: ${price:,.2f}",
                        annotation_position="right",
                    )

                    fig.add_hline(
                        y=graham_metrics.graham_number,
                        name="Graham Number",
                        line_dash="dash",
                        line_color="green",
                        annotation_text=f"Graham #: ${graham_metrics.graham_number:,.2f}",
                        annotation_position="right",
                    )

                    if graham_metrics.ncav_per_share and graham_metrics.ncav_per_share > 0:
                        fig.add_hline(
                            y=graham_metrics.ncav_per_share * 0.67,
                            name="NCAV 67%",
                            line_dash="dot",
                            line_color="purple",
                            annotation_text=f"NCAV 67%: ${graham_metrics.ncav_per_share * 0.67:,.2f}",
                            annotation_position="right",
                        )

                    fig.update_layout(
                        title=f"{ticker} — Valuación",
                        yaxis_title=f"Precio ({currency})",
                        height=300,
                        margin=dict(r=220),
                    )

                    fig.update_xaxes(showticklabels=False)

                    st.plotly_chart(fig, use_container_width=True)

                    # Status
                    if price < graham_metrics.graham_number:
                        discount = (
                            (graham_metrics.graham_number - price) / graham_metrics.graham_number
                        ) * 100
                        st.success(f"✅ **GANGA**: {discount:.1f}% por debajo del Graham Number")
                    else:
                        premium = (
                            (price - graham_metrics.graham_number) / graham_metrics.graham_number
                        ) * 100
                        st.warning(f"⚠️ **CARO**: {premium:.1f}% por encima del Graham Number")
                else:
                    st.error("❌ No se puede calcular Graham Number. Verifica EPS y BVPS.")

                st.markdown("---")

                # 1B. DATA VALIDATION
                st.subheader("🔍 Validación de Datos")

                validation = DataValidator.validate_stock_data(
                    ticker=ticker,
                    price=price,
                    eps=eps,
                    bvps=bvps,
                    pe_ratio=fundamentals.pe_ratio if fundamentals.pe_ratio else 0,
                    pb_ratio=fundamentals.pb_ratio if fundamentals.pb_ratio else 0,
                    current_ratio=current_ratio,
                    de_ratio=(total_debt / total_equity) if total_equity > 0 else None,
                    roe=roe,
                )

                validation_icon = DataValidator.get_validation_status_icon(validation)
                st.write(f"**Estado:** {validation_icon} {validation['summary']}")

                if validation["errors"]:
                    st.error("**❌ Errores Encontrados:**")
                    for error in validation["errors"]:
                        st.write(f"• {error}")

                if validation["warnings"]:
                    st.warning("**⚠️ Advertencias:**")
                    for warning in validation["warnings"]:
                        st.write(f"• {warning}")

                st.markdown("---")

                # 2. SCORECARD
                st.subheader("✅ Scorecard de Métricas")

                metrics_checks = [
                    {
                        "name": "P/E Ratio",
                        "value": fundamentals.pe_ratio,
                        "is_good": fundamentals.pe_ratio <= 15 if fundamentals.pe_ratio else False,
                        "label": "≤ 15",
                    },
                    {
                        "name": "P/B Ratio",
                        "value": fundamentals.pb_ratio,
                        "is_good": fundamentals.pb_ratio <= 1.5 if fundamentals.pb_ratio else False,
                        "label": "≤ 1.5",
                    },
                    {
                        "name": "Current Ratio",
                        "value": current_ratio,
                        "is_good": current_ratio >= 1.5 if current_ratio else False,
                        "label": "≥ 1.5",
                    },
                    {
                        "name": "ROE",
                        "value": roe * 100 if roe else None,
                        "is_good": roe >= 0.10 if roe else False,
                        "label": "≥ 10%",
                    },
                ]

                cols = st.columns(4)
                for i, metric in enumerate(metrics_checks):
                    with cols[i]:
                        if metric["value"] is not None:
                            status_icon = "✅" if metric["is_good"] else "⚠️"
                            status_color = "green" if metric["is_good"] else "orange"
                            st.markdown(
                                f"""
                                <div style='background-color: {"#d4edda" if metric["is_good"] else "#fff3cd"};
                                            padding: 15px; border-radius: 8px; border-left: 4px solid {status_color}; text-align: center;'>
                                    <div style='font-size: 12px; color: gray;'>{metric['name']}</div>
                                    <div style='font-size: 20px; font-weight: bold; margin: 8px 0;'>{status_icon} {metric['value']:.1f}</div>
                                    <div style='font-size: 11px; color: gray;'>{metric['label']}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.info(f"{metric['name']}\n(no data)")

                st.markdown("---")

                # 3. GRAHAM METRICS DETAILS
                st.subheader("📊 Métricas Graham")

                metric_cols = st.columns(4)

                with metric_cols[0]:
                    if graham_metrics.graham_number:
                        st.metric("Graham Number", f"${graham_metrics.graham_number:,.2f}")
                    else:
                        st.metric("Graham Number", "N/A")

                with metric_cols[1]:
                    if graham_metrics.margin_of_safety:
                        mos = graham_metrics.margin_of_safety * 100
                        st.metric("Margin of Safety", f"{mos:+.1f}%")
                    else:
                        st.metric("Margin of Safety", "N/A")

                with metric_cols[2]:
                    if graham_metrics.ncav_per_share:
                        st.metric("NCAV/Share", f"${graham_metrics.ncav_per_share:,.2f}")
                    else:
                        st.metric("NCAV/Share", "N/A")

                with metric_cols[3]:
                    if graham_metrics.ncav_per_share and graham_metrics.ncav_per_share > 0:
                        discount = (
                            (graham_metrics.ncav_per_share - price) / graham_metrics.ncav_per_share
                        ) * 100
                        st.metric("NCAV Discount", f"{discount:+.1f}%")
                    else:
                        st.metric("NCAV Discount", "N/A")

                st.markdown("---")

                # 4. RISK ANALYSIS
                st.subheader("⚠️ Análisis de Riesgo")

                # Business Risks
                # Estimate competitive position based on PE and BVPS discount
                pe_ok = (fundamentals.pe_ratio <= 15) if fundamentals.pe_ratio else False
                pb_ok = (fundamentals.pb_ratio <= 1.5) if fundamentals.pb_ratio else False
                competitive_pos = "leader" if (pe_ok and pb_ok) else "competitive" if pe_ok else "weak"

                business_risks = RiskAnalyzer.analyze_business_risks(
                    business_description=company_name,
                    competitive_position=competitive_pos,
                    industry_trend="stable",
                )

                # Financial Risks
                financial_risks = RiskAnalyzer.analyze_financial_risks(
                    debt_to_equity=(total_debt / total_equity) if total_equity > 0 else 0,
                    current_ratio=current_ratio if current_ratio else 1.0,
                    roe=roe * 100 if roe else 0,
                )

                # Market Risks
                market_risks = RiskAnalyzer.analyze_market_risks(
                    price_vs_52w_high=0.5 if score >= 50 else 0.95,
                    price_vs_52w_low=5.0,
                    market_cap=None,
                )

                risk_cols = st.columns(3)

                with risk_cols[0]:
                    st.write(f"**Riesgo de Negocio:** {business_risks['risk_level']}")
                    st.metric("Score", business_risks['risk_score'])
                    if business_risks['risks']:
                        st.write("**Riesgos Identificados:**")
                        for risk in business_risks['risks']:
                            st.write(f"• {risk['risk']} ({risk['severity']})")

                with risk_cols[1]:
                    st.write(f"**Riesgo Financiero:** {financial_risks['risk_level']}")
                    st.metric("Score", financial_risks['risk_score'])
                    if financial_risks['risks']:
                        st.write("**Riesgos Identificados:**")
                        for risk in financial_risks['risks']:
                            st.write(f"• {risk['risk']} ({risk['severity']})")

                with risk_cols[2]:
                    st.write(f"**Riesgo de Mercado:** {market_risks['risk_level']}")
                    st.metric("Score", market_risks['risk_score'])
                    if market_risks['risks']:
                        st.write("**Riesgos Identificados:**")
                        for risk in market_risks['risks']:
                            st.write(f"• {risk['risk']} ({risk['severity']})")

                # Overall risk summary
                avg_risk_score = (
                    business_risks['risk_score'] + financial_risks['risk_score'] + market_risks['risk_score']
                ) / 3
                risk_summary = RiskAnalyzer.get_risk_summary(
                    business_risks, financial_risks, market_risks
                )
                st.write(f"**Riesgo General:** {risk_summary}")

                st.markdown("---")

                # 5. INVESTMENT SCORE
                st.subheader("🎯 Investment Score & Recomendación")

                score, recommendation = InvestmentScorer.calculate_score(graham_metrics, fundamentals)

                score_cols = st.columns(2)

                with score_cols[0]:
                    score_emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
                    st.metric("Puntuación", f"{score}/100", f"{score_emoji} {recommendation}")

                with score_cols[1]:
                    if recommendation == "BUY":
                        st.success("✅ **COMPRA** - Buena oportunidad")
                    elif recommendation == "WATCH":
                        st.warning("⏳ **VIGILA** - Monitorea para mejor precio")
                    else:
                        st.error("❌ **EVITA** - Sobrevalorada o fundamentals débiles")

                st.markdown("---")

                # 5. TARGET & STOP LOSS
                st.subheader("🎯 Targets & Stop Loss")

                if graham_metrics.graham_number:
                    targets = InvestmentDecision.calculate_targets(
                        graham_metrics.graham_number,
                        price,
                        profit_target_pct=0.20,
                        max_loss_pct=0.30,
                    )

                    target_cols = st.columns(4)

                    with target_cols[0]:
                        st.metric(
                            "🎯 Precio Target",
                            f"${targets['target_price']:,.2f}",
                            f"↑ {targets['upside_pct']:+.1f}%",
                        )

                    with target_cols[1]:
                        st.metric(
                            "🛑 Stop Loss",
                            f"${targets['stop_loss']:,.2f}",
                            f"↓ {targets['downside_pct']:+.1f}%",
                        )

                    with target_cols[2]:
                        st.metric(
                            "⚖️ Risk/Reward",
                            f"{targets['risk_reward_ratio']:.2f}x",
                            "Entre más alto = mejor",
                        )

                    with target_cols[3]:
                        st.write("")
                        st.write("**Estrategia:**")
                        st.write(f"Compra @ ${price:.2f}")
                        st.write(f"Vende @ ${targets['target_price']:.2f}")
                        st.write(f"Máx pérdida: {targets['downside_pct']:.1f}%")

                st.markdown("---")

                # 6. DECISION CHECKLIST
                st.subheader("✅ Checklist de Decisión Graham")

                checklist = InvestmentDecision.get_buy_checklist(
                    graham_metrics, fundamentals, price, score
                )

                # Visual checklist
                check_items = [
                    ("📊 Debajo de Graham Number", "below_graham_number"),
                    ("📈 P/E ≤ 15", "pe_ratio_ok"),
                    ("📉 P/B ≤ 1.5", "pb_ratio_ok"),
                    ("🛡️ Margen de Seguridad ≥ 30%", "margin_of_safety_ok"),
                    ("💧 Liquidez Buena", "liquidity_ok"),
                    ("⚙️ Deuda Baja (D/E ≤ 1.0)", "leverage_ok"),
                    ("💰 ROE ≥ 10%", "profitability_ok"),
                    ("🎯 Score ≥ 40", "score_ok"),
                ]

                check_cols = st.columns(2)
                for i, (label, key) in enumerate(check_items):
                    col = check_cols[i % 2]
                    status = "✅" if checklist["checklist"][key] else "❌"
                    col.markdown(f"{status} {label}")

                st.write("---")

                passing_pct = (checklist["passing"] / checklist["total"]) * 100
                st.metric(
                    f"Cumple {checklist['passing']}/{checklist['total']} Criterios",
                    f"{passing_pct:.0f}%",
                )

                st.markdown("---")

                # 7. RECOMMENDATION DETAILS
                details = InvestmentScorer.get_recommendation_details(graham_metrics, fundamentals, score)

                det_cols = st.columns(2)

                with det_cols[0]:
                    if details["strengths"]:
                        st.write("**✓ Fortalezas:**")
                        for strength in details["strengths"][:5]:
                            st.write(f"• {strength}")

                with det_cols[1]:
                    if details["concerns"]:
                        st.write("**⚠️ Preocupaciones:**")
                        for concern in details["concerns"][:5]:
                            st.write(f"• {concern}")

                st.markdown("---")

                # 8. FINAL DECISION SUMMARY
                st.subheader("🎬 DECISIÓN FINAL")

                summary = InvestmentDecision.get_decision_summary(
                    ticker, score, graham_metrics, fundamentals, price, targets, checklist
                )

                # Display as big colored box
                if "🟢" in checklist["decision"]:
                    st.success(summary)
                    add_to_portfolio = st.button(
                        "✅ AGREGAR A PORTAFOLIO", use_container_width=True, key="add_buy"
                    )
                elif "🟡" in checklist["decision"]:
                    st.warning(summary)
                    add_to_portfolio = st.button(
                        "📌 GUARDAR PARA VIGILAR", use_container_width=True, key="add_watch"
                    )
                else:
                    st.error(summary)
                    add_to_portfolio = False

                if add_to_portfolio:
                    st.info(
                        f"✅ Ir a **💼 Portfolio Tracker** para guardar esta decisión y monitorear"
                    )

        else:
            st.info(
                """
            ℹ️ **Cómo usar esta página:**

            1. **Lee la tab "Cómo Obtener Datos"** para saber dónde encontrar los números
            2. **Ingresa datos reales del Balance Sheet** en el panel izquierdo
            3. **Haz clic en "Analizar con Graham"**
            4. **Verás análisis completo** con gráficos y recomendaciones

            ---

            ### **Datos Necesarios (Mínimo):**
            - ✅ Precio Actual
            - ✅ EPS (TTM)
            - ✅ Total Shareholders' Equity
            - ✅ Shares Outstanding

            ### **Datos Opcionales (Pero recomendados):**
            - Current Assets
            - Current Liabilities
            - Total Debt

            ---

            **Ejemplo pre-cargado:** Ecopetrol S.A. (ECOPETROL.CL)
            Solo haz click en "Analizar con Graham" para ver el análisis.
            """
            )
