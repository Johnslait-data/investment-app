"""
Portfolio Tracker — Monitor your investments
Track buy decisions, target prices, and performance
"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from analysis.alerts import AlertManager
from analysis.validation import DataValidator
from analysis.statistics import PortfolioStatistics

st.set_page_config(
    page_title="Portfolio Tracker",
    page_icon="💼",
    layout="wide",
)

st.title("💼 Portfolio Tracker")
st.markdown("**Monitorea tus decisiones de inversión Graham**")
st.markdown("---")

# Portfolio storage
PORTFOLIO_FILE = Path("data/portfolio.json")


def load_portfolio():
    """Load portfolio from JSON"""
    if PORTFOLIO_FILE.exists():
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {"positions": []}


def save_portfolio(portfolio):
    """Save portfolio to JSON"""
    PORTFOLIO_FILE.parent.mkdir(exist_ok=True)
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)


def calculate_performance(entry_price, current_price):
    """Calculate P&L"""
    if entry_price <= 0:
        return 0
    return ((current_price - entry_price) / entry_price) * 100


# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Mi Portafolio",
    "➕ Agregar Posición",
    "📋 Historial",
    "🔔 Alertas",
    "📈 Estadísticas"
])

with tab2:
    st.subheader("➕ Agregar Nueva Posición")

    col1, col2 = st.columns(2)

    with col1:
        ticker = st.text_input("Ticker:", placeholder="ECOPETROL.CL")
        company = st.text_input("Empresa:", placeholder="Ecopetrol S.A.")
        entry_price = st.number_input("Precio de Entrada ($):", min_value=0.01, step=10.0)

    with col2:
        shares = st.number_input("Cantidad de Acciones:", min_value=1, step=1)
        target_price = st.number_input("Precio Target ($):", min_value=0.01, step=10.0)
        stop_loss = st.number_input("Stop Loss ($):", min_value=0.01, step=10.0)

    decision = st.text_area(
        "Análisis/Decision:",
        placeholder="Ej: Compra porque P/E=11.6, Graham #=3098, Score=50",
        height=100,
    )

    if st.button("✅ Guardar Posición", use_container_width=True):
        portfolio = load_portfolio()

        position = {
            "id": datetime.now().isoformat(),
            "ticker": ticker.upper(),
            "company": company,
            "entry_date": datetime.now().strftime("%Y-%m-%d"),
            "entry_price": entry_price,
            "shares": shares,
            "total_invested": entry_price * shares,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "decision": decision,
            "status": "OPEN",
            "current_price": None,
            "current_value": None,
            "pnl_pct": None,
            "exit_price": None,
            "exit_date": None,
        }

        portfolio["positions"].append(position)
        save_portfolio(portfolio)
        st.success(f"✅ Posición {ticker} agregada al portafolio")
        st.rerun()

with tab1:
    portfolio = load_portfolio()

    if portfolio["positions"]:
        st.subheader("📊 Posiciones Abiertas")

        open_positions = [p for p in portfolio["positions"] if p["status"] == "OPEN"]

        if open_positions:
            for i, pos in enumerate(open_positions):
                with st.expander(f"**{pos['ticker']}** - {pos['company']}", expanded=False):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write("**Entrada**")
                        st.write(f"Fecha: {pos['entry_date']}")
                        st.write(f"Precio: ${pos['entry_price']:.2f}")
                        st.write(f"Acciones: {pos['shares']}")
                        st.write(f"Invertido: ${pos['total_invested']:,.0f}")

                    with col2:
                        st.write("**Targets**")
                        st.write(f"Target: ${pos['target_price']:.2f}")
                        st.write(f"Stop Loss: ${pos['stop_loss']:.2f}")
                        upside = (
                            (pos["target_price"] - pos["entry_price"])
                            / pos["entry_price"]
                        ) * 100
                        downside = (
                            (pos["entry_price"] - pos["stop_loss"])
                            / pos["entry_price"]
                        ) * 100
                        st.write(f"Upside: {upside:+.1f}%")
                        st.write(f"Downside: {downside:+.1f}%")

                    with col3:
                        st.write("**Decisión**")
                        st.write(pos["decision"][:200] + "..." if len(pos["decision"]) > 200 else pos["decision"])

                    st.write("---")

                    # Update price
                    new_price = st.number_input(
                        f"Precio Actual de {pos['ticker']} ($):",
                        value=pos["entry_price"],
                        step=10.0,
                        key=f"price_{i}",
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button(f"📈 Actualizar Precio", key=f"update_{i}", use_container_width=True):
                            pos["current_price"] = new_price
                            pos["current_value"] = new_price * pos["shares"]
                            pos["pnl_pct"] = calculate_performance(pos["entry_price"], new_price)
                            save_portfolio(portfolio)
                            st.success(f"Precio actualizado a ${new_price:.2f}")
                            st.rerun()

                    with col2:
                        if st.button(f"✅ Vender", key=f"sell_{i}", use_container_width=True):
                            st.session_state[f"selling_{i}"] = True

                    with col3:
                        if st.button(f"🗑️ Eliminar", key=f"delete_{i}", use_container_width=True):
                            portfolio["positions"].pop(i)
                            save_portfolio(portfolio)
                            st.success(f"Posición eliminada")
                            st.rerun()

                    # Sell dialog
                    if st.session_state.get(f"selling_{i}"):
                        exit_price = st.number_input(
                            "Precio de Venta ($):",
                            value=new_price,
                            step=10.0,
                        )
                        if st.button("Confirmar Venta"):
                            pos["status"] = "CLOSED"
                            pos["exit_price"] = exit_price
                            pos["exit_date"] = datetime.now().strftime("%Y-%m-%d")
                            pos["pnl_pct"] = calculate_performance(pos["entry_price"], exit_price)
                            save_portfolio(portfolio)
                            st.success(f"Venta registrada a ${exit_price:.2f}")
                            st.rerun()

        # Summary
        st.write("---")
        st.subheader("📊 Resumen")

        total_invested = sum(p["total_invested"] for p in open_positions)
        total_value = sum(p["current_value"] for p in open_positions if p["current_value"])
        total_pnl = total_value - total_invested if total_value else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Posiciones Abiertas", len(open_positions))
        with col2:
            st.metric("Invertido Total", f"${total_invested:,.0f}")
        with col3:
            st.metric("Valor Actual", f"${total_value:,.0f}" if total_value else "N/A")
        with col4:
            pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            st.metric("P&L", f"${total_pnl:,.0f}", f"{pnl_pct:+.1f}%")

    else:
        st.info("📌 No hay posiciones abiertas. Agrega una desde la tab '➕ Agregar Posición'")

with tab3:
    portfolio = load_portfolio()

    if portfolio["positions"]:
        closed = [p for p in portfolio["positions"] if p["status"] == "CLOSED"]

        if closed:
            st.subheader("📋 Posiciones Cerradas")
            for pos in closed:
                pnl_pct = (
                    (pos["exit_price"] - pos["entry_price"]) / pos["entry_price"] * 100
                )
                status_emoji = "✅" if pnl_pct > 0 else "❌"

                st.write(
                    f"{status_emoji} **{pos['ticker']}** | "
                    f"Entrada: ${pos['entry_price']:.2f} | "
                    f"Salida: ${pos['exit_price']:.2f} | "
                    f"Ganancia: {pnl_pct:+.1f}%"
                )
        else:
            st.info("Sin posiciones cerradas aún")
    else:
        st.info("Sin histórico")

with tab4:
    st.subheader("🔔 Alertas Activas")
    portfolio = load_portfolio()

    if portfolio["positions"]:
        open_positions = [p for p in portfolio["positions"] if p["status"] == "OPEN"]

        if open_positions:
            # Check for alerts
            alerts = AlertManager.check_alerts(open_positions)

            if alerts:
                st.warning(f"⚠️ {len(alerts)} Alerta(s) Detectada(s)")
                for alert in alerts:
                    if alert["type"] == "TARGET_HIT":
                        st.success(
                            f"🎯 **{alert['ticker']}** alcanzó target"
                            f"\nPrecio: ${alert['current_price']:.2f}"
                            f"\nGanancia: {alert['pnl_pct']:+.1f}%"
                        )
                    elif alert["type"] == "STOP_LOSS_HIT":
                        st.error(
                            f"🛑 **{alert['ticker']}** alcanzó stop loss"
                            f"\nPrecio: ${alert['current_price']:.2f}"
                            f"\nPérdida: {alert['pnl_pct']:+.1f}%"
                        )
            else:
                st.info("✅ No hay alertas activas. Todas las posiciones están en rango normal.")

            # Show position status
            st.markdown("---")
            st.subheader("📊 Estado de Posiciones")

            for pos in open_positions:
                if pos.get("current_price"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**{pos['ticker']}**")
                        st.write(f"Precio: ${pos['current_price']:.2f}")
                        st.write(f"Target: ${pos['target_price']:.2f}")

                    with col2:
                        st.write(f"Stop Loss: ${pos['stop_loss']:.2f}")
                        if pos["current_price"] >= pos["target_price"]:
                            st.success("✅ ENCIMA DE TARGET")
                        elif pos["current_price"] <= pos["stop_loss"]:
                            st.error("❌ BAJO STOP LOSS")
                        else:
                            pct_to_target = (
                                (pos["target_price"] - pos["current_price"])
                                / (pos["target_price"] - pos["stop_loss"])
                                * 100
                            )
                            st.info(f"📍 {pct_to_target:.0f}% del camino")

                    st.markdown("---")
        else:
            st.info("Sin posiciones abiertas para monitorear alertas")
    else:
        st.info("Sin portafolio. Agrega posiciones primero.")

with tab5:
    st.subheader("📈 Estadísticas del Portafolio")
    portfolio = load_portfolio()

    if portfolio["positions"]:
        # Calculate statistics
        all_positions = portfolio["positions"]
        stats = PortfolioStatistics.calculate_performance_stats(all_positions)
        portfolio_metrics = PortfolioStatistics.calculate_portfolio_metrics(
            [p for p in all_positions if p["status"] == "OPEN"]
        )

        # Tabs for different statistics views
        stats_tab1, stats_tab2 = st.tabs(["📊 Métricas Generales", "📈 Operaciones Cerradas"])

        with stats_tab1:
            st.subheader("Portafolio Actual")

            metric_cols = st.columns(4)
            with metric_cols[0]:
                st.metric("Posiciones Abiertas", portfolio_metrics["num_open_positions"])
            with metric_cols[1]:
                st.metric("Invertido Total", f"${portfolio_metrics['total_invested']:,.0f}")
            with metric_cols[2]:
                st.metric("Valor Actual", f"${portfolio_metrics['total_current_value']:,.0f}")
            with metric_cols[3]:
                st.metric(
                    "P&L Total",
                    f"${portfolio_metrics['total_pnl']:,.0f}",
                    f"{portfolio_metrics['total_pnl_pct']:+.1f}%"
                )

            st.markdown("---")
            st.subheader("Asignación de Portafolio")

            if portfolio_metrics["allocations"]:
                for alloc in portfolio_metrics["allocations"]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{alloc['ticker']}**")
                    with col2:
                        st.write(f"{alloc['allocation']:.1f}%")
                    st.progress(alloc['allocation'] / 100)

            st.write(f"**Concentración Top 3:** {portfolio_metrics['top_3_concentration']:.1f}%")

        with stats_tab2:
            if stats["total_trades"] > 0:
                st.subheader("Desempeño de Operaciones")

                perf_cols = st.columns(4)
                with perf_cols[0]:
                    st.metric("Total Operaciones", stats["total_trades"])
                with perf_cols[1]:
                    st.metric("Ganadoras", f"{stats['winning_trades']} ({stats['win_rate']:.0f}%)")
                with perf_cols[2]:
                    st.metric("Perdedoras", stats["losing_trades"])
                with perf_cols[3]:
                    st.metric("Profit Factor", f"{stats['profit_factor']:.2f}x")

                st.markdown("---")

                detail_cols = st.columns(3)
                with detail_cols[0]:
                    st.metric("Ganancia Promedio", f"{stats['avg_gain']:+.1f}%")
                with detail_cols[1]:
                    st.metric("Pérdida Promedio", f"{stats['avg_loss']:+.1f}%")
                with detail_cols[2]:
                    st.metric("P&L Total Realizado", f"${stats['total_realized_pnl']:,.0f}")

                st.markdown("---")

                best_worst_cols = st.columns(2)
                with best_worst_cols[0]:
                    if stats["best_trade"]:
                        st.success(
                            f"🏆 Mejor Trade\n"
                            f"**{stats['best_trade']['ticker']}**\n"
                            f"Ganancia: {stats['largest_gain']:+.1f}%"
                        )

                with best_worst_cols[1]:
                    if stats["worst_trade"]:
                        st.error(
                            f"📉 Peor Trade\n"
                            f"**{stats['worst_trade']['ticker']}**\n"
                            f"Pérdida: {stats['largest_loss']:+.1f}%"
                        )
            else:
                st.info("Sin operaciones cerradas aún para mostrar estadísticas.")
    else:
        st.info("Sin portafolio. Agrega posiciones primero para ver estadísticas.")
