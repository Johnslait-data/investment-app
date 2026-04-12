"""
Risk Analysis — Detailed risk assessment for stocks
Identify business, financial, and market risks
"""
import streamlit as st
from analysis.risk import RiskAnalyzer

st.set_page_config(
    page_title="Risk Analysis",
    page_icon="⚠️",
    layout="wide",
)

st.title("⚠️ Análisis de Riesgo — Graham")
st.markdown("**Evalúa riesgos específicos antes de invertir**")
st.markdown("---")

# Input section
st.subheader("📝 Ingresa Datos de Riesgo")

col1, col2 = st.columns(2)

with col1:
    st.write("**Riesgo de Negocio**")
    ticker = st.text_input("Ticker:", value="ECOPETROL.CL")
    company = st.text_input("Empresa:", value="Ecopetrol S.A.")
    competitive_position = st.selectbox(
        "Posición Competitiva:",
        ["leader", "competitive", "weak"],
        format_func=lambda x: {"leader": "Líder", "competitive": "Competitiva", "weak": "Débil"}[x]
    )
    industry_trend = st.selectbox(
        "Tendencia Industrial:",
        ["growing", "stable", "declining"],
        format_func=lambda x: {"growing": "Creciente", "stable": "Estable", "declining": "Declinante"}[x]
    )

with col2:
    st.write("**Riesgo Financiero**")
    debt_to_equity = st.number_input(
        "Relación Deuda/Patrimonio:",
        value=1.5,
        min_value=0.0,
        step=0.1
    )
    current_ratio = st.number_input(
        "Current Ratio (Liquidez):",
        value=1.5,
        min_value=0.1,
        step=0.1
    )
    roe = st.number_input(
        "ROE (%):",
        value=12.0,
        min_value=-100.0,
        step=1.0
    )

st.write("---")
st.write("**Riesgo de Mercado**")

market_col1, market_col2, market_col3 = st.columns(3)

with market_col1:
    price_52w_high = st.number_input(
        "Precio / 52W High (ratio):",
        value=0.75,
        min_value=0.0,
        max_value=1.5,
        step=0.05
    )

with market_col2:
    price_52w_low = st.number_input(
        "Precio / 52W Low (ratio):",
        value=3.0,
        min_value=0.0,
        step=0.5
    )

with market_col3:
    market_cap = st.number_input(
        "Market Cap ($ millones):",
        value=50000.0,
        min_value=0.0,
        step=1000.0
    )

analyze_btn = st.button("🔍 Analizar Riesgos", use_container_width=True)

if analyze_btn:
    st.markdown("---")
    st.subheader(f"📊 Análisis de Riesgo: {ticker}")

    # Analyze all risk types
    business_risks = RiskAnalyzer.analyze_business_risks(
        business_description=company,
        competitive_position=competitive_position,
        industry_trend=industry_trend,
    )

    financial_risks = RiskAnalyzer.analyze_financial_risks(
        debt_to_equity=debt_to_equity,
        current_ratio=current_ratio,
        roe=roe,
    )

    market_risks = RiskAnalyzer.analyze_market_risks(
        price_vs_52w_high=price_52w_high,
        price_vs_52w_low=price_52w_low,
        market_cap=market_cap,
    )

    # Display results in columns
    risk_tabs = st.tabs(["🏢 Riesgo de Negocio", "💰 Riesgo Financiero", "📈 Riesgo de Mercado", "📊 Resumen General"])

    with risk_tabs[0]:
        st.subheader(f"Riesgo de Negocio: {business_risks['risk_level']}")
        st.metric("Score", business_risks['risk_score'], f"(0-100)")

        if business_risks['risks']:
            st.write("**Riesgos Identificados:**")
            for risk in business_risks['risks']:
                status_color = "🔴" if risk['severity'] == "ALTA" else "🟡" if risk['severity'] == "MEDIA" else "🟢"
                st.write(f"{status_color} **{risk['category']}**: {risk['risk']}")
                if 'mitigation' in risk:
                    st.write(f"   → Mitigación: {risk['mitigation']}")
        else:
            st.success("✅ No hay riesgos significativos de negocio.")

        st.write("---")
        st.write("**Análisis:**")
        st.write(f"• Posición Competitiva: {competitive_position.upper()}")
        st.write(f"• Tendencia Industrial: {industry_trend.upper()}")

    with risk_tabs[1]:
        st.subheader(f"Riesgo Financiero: {financial_risks['risk_level']}")
        st.metric("Score", financial_risks['risk_score'], f"(0-100)")

        if financial_risks['risks']:
            st.write("**Riesgos Identificados:**")
            for risk in financial_risks['risks']:
                status_color = "🔴" if risk['severity'] == "ALTA" else "🟡" if risk['severity'] == "MEDIA" else "🟢"
                st.write(f"{status_color} **{risk['category']}**: {risk['risk']}")
                if 'detail' in risk:
                    st.write(f"   → {risk['detail']}")
        else:
            st.success("✅ No hay riesgos significativos financieros.")

        st.write("---")
        st.write("**Métricas de Salud Financiera:**")

        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("Deuda/Patrimonio", f"{debt_to_equity:.2f}", "Menor = Mejor")
        with metric_cols[1]:
            st.metric("Current Ratio", f"{current_ratio:.2f}", "1.5+ = Saludable")
        with metric_cols[2]:
            st.metric("ROE", f"{roe:.1f}%", "Mayor = Mejor")

    with risk_tabs[2]:
        st.subheader(f"Riesgo de Mercado: {market_risks['risk_level']}")
        st.metric("Score", market_risks['risk_score'], f"(0-100)")

        if market_risks['risks']:
            st.write("**Riesgos Identificados:**")
            for risk in market_risks['risks']:
                status_color = "🔴" if risk['severity'] == "ALTA" else "🟡" if risk['severity'] == "MEDIA" else "🟢"
                st.write(f"{status_color} **{risk['category']}**: {risk['risk']}")
                if 'detail' in risk:
                    st.write(f"   → {risk['detail']}")
                if 'mitigation' in risk:
                    st.write(f"   → {risk['mitigation']}")
        else:
            st.success("✅ No hay riesgos significativos de mercado.")

        st.write("---")
        st.write("**Posicionamiento de Precio:**")

        position_cols = st.columns(3)
        with position_cols[0]:
            st.metric("vs 52W High", f"{price_52w_high:.2f}x", "Menor = Mejor")
        with position_cols[1]:
            st.metric("vs 52W Low", f"{price_52w_low:.2f}x", "Menor = Mejor")
        with position_cols[2]:
            st.metric("Market Cap", f"${market_cap:,.0f}M", "Mayor = Mejor")

    with risk_tabs[3]:
        st.subheader("Resumen General de Riesgos")

        # Overall risk summary
        avg_risk_score = (
            business_risks['risk_score'] + financial_risks['risk_score'] + market_risks['risk_score']
        ) / 3

        risk_summary = RiskAnalyzer.get_risk_summary(
            business_risks, financial_risks, market_risks
        )

        st.write(f"## {risk_summary}")

        # Summary metrics
        summary_cols = st.columns(3)
        with summary_cols[0]:
            st.metric("Riesgo de Negocio", business_risks['risk_score'])
        with summary_cols[1]:
            st.metric("Riesgo Financiero", financial_risks['risk_score'])
        with summary_cols[2]:
            st.metric("Riesgo de Mercado", market_risks['risk_score'])

        st.write("---")
        st.write(f"**Puntuación Promedio de Riesgo:** {avg_risk_score:.0f}/100")

        # Recommendations
        st.write("---")
        st.subheader("💡 Recomendaciones")

        if avg_risk_score >= 70:
            st.error(
                "🔴 **ALTO RIESGO**\n\n"
                "Esta inversión presenta riesgos significativos. Considera:\n"
                "• Reducir tamaño de posición\n"
                "• Esperar a mejoría en los fundamentales\n"
                "• Explorar alternativas más seguras"
            )
        elif avg_risk_score >= 50:
            st.warning(
                "🟡 **RIESGO MEDIO**\n\n"
                "Hay algunos riesgos a considerar. Recomendaciones:\n"
                "• Monitorear de cerca los riesgos identificados\n"
                "• Usar stop loss adecuado\n"
                "• Posición de tamaño moderado"
            )
        else:
            st.success(
                "🟢 **RIESGO BAJO**\n\n"
                "Los riesgos son manejables. Sin embargo:\n"
                "• Mantén vigilancia regular\n"
                "• Asegúrate de diversificación\n"
                "• Revisa posición cada trimestre"
            )

else:
    st.info(
        """
        ## 📚 Cómo usar esta página

        1. **Ingresa datos** sobre la empresa y sus riesgos
        2. **Haz clic** en "Analizar Riesgos"
        3. **Revisa** los tres tipos de riesgo:
           - 🏢 **Riesgo de Negocio**: Posición competitiva, tendencias
           - 💰 **Riesgo Financiero**: Deuda, liquidez, rentabilidad
           - 📈 **Riesgo de Mercado**: Valuación, capitalización

        ---

        ### **Datos por Defecto:**
        Los valores iniciales son para Ecopetrol S.A. (ECOPETROL.CL).
        Cámbialos según sea necesario.
        """
    )
