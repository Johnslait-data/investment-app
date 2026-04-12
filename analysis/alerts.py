"""
Alert System - Email notifications for price targets and stop losses
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os


class AlertManager:
    """Send email alerts for investment decisions"""

    @staticmethod
    def send_alert(
        email_to: str,
        ticker: str,
        alert_type: str,
        current_price: float,
        target_price: float,
        pnl_pct: float,
    ) -> bool:
        """
        Send email alert for price targets

        Args:
            email_to: Recipient email
            ticker: Stock ticker
            alert_type: "TARGET_HIT" or "STOP_LOSS_HIT"
            current_price: Current stock price
            target_price: Target or stop loss price
            pnl_pct: Profit/Loss percentage

        Returns:
            True if sent successfully, False otherwise
        """

        # For demo: just log the alert
        # In production, would use SMTP to send email

        if alert_type == "TARGET_HIT":
            subject = f"🎯 Target Alcanzado: {ticker} @ ${current_price:.2f}"
            body = f"""
            ¡Tu precio target para {ticker} ha sido alcanzado!

            Detalles:
            ✅ Ticker: {ticker}
            💰 Precio Actual: ${current_price:.2f}
            🎯 Target: ${target_price:.2f}
            📈 Ganancia: {pnl_pct:+.2f}%

            Recomendación: VENDER AHORA
            Acción: Ve a Portfolio Tracker y registra la venta

            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

        elif alert_type == "STOP_LOSS_HIT":
            subject = f"🛑 Stop Loss Alcanzado: {ticker} @ ${current_price:.2f}"
            body = f"""
            ⚠️ Tu stop loss para {ticker} ha sido alcanzado!

            Detalles:
            ❌ Ticker: {ticker}
            💰 Precio Actual: ${current_price:.2f}
            🛑 Stop Loss: ${target_price:.2f}
            📉 Pérdida: {pnl_pct:.2f}%

            Recomendación: SALIR INMEDIATAMENTE
            Acción: Limita pérdidas - vende ahora

            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        else:
            return False

        # Log alert (in production, send via SMTP)
        alert_log = {
            "timestamp": datetime.now().isoformat(),
            "email": email_to,
            "ticker": ticker,
            "alert_type": alert_type,
            "current_price": current_price,
            "target_price": target_price,
            "pnl_pct": pnl_pct,
            "subject": subject,
        }

        print(f"[ALERT] {alert_log}")
        return True

    @staticmethod
    def check_alerts(portfolio_positions: list, email: str = None) -> list:
        """
        Check all positions for alert conditions

        Args:
            portfolio_positions: List of position dicts
            email: Email to send alerts to (optional)

        Returns:
            List of triggered alerts
        """
        alerts = []

        for position in portfolio_positions:
            if position["status"] != "OPEN":
                continue

            current_price = position.get("current_price")
            if not current_price:
                continue

            # Check target hit
            if current_price >= position["target_price"]:
                pnl = (
                    (current_price - position["entry_price"]) / position["entry_price"] * 100
                )
                alert = {
                    "type": "TARGET_HIT",
                    "ticker": position["ticker"],
                    "current_price": current_price,
                    "target_price": position["target_price"],
                    "pnl_pct": pnl,
                }
                alerts.append(alert)

                if email:
                    AlertManager.send_alert(
                        email,
                        position["ticker"],
                        "TARGET_HIT",
                        current_price,
                        position["target_price"],
                        pnl,
                    )

            # Check stop loss hit
            if current_price <= position["stop_loss"]:
                pnl = (
                    (current_price - position["entry_price"]) / position["entry_price"] * 100
                )
                alert = {
                    "type": "STOP_LOSS_HIT",
                    "ticker": position["ticker"],
                    "current_price": current_price,
                    "target_price": position["stop_loss"],
                    "pnl_pct": pnl,
                }
                alerts.append(alert)

                if email:
                    AlertManager.send_alert(
                        email,
                        position["ticker"],
                        "STOP_LOSS_HIT",
                        current_price,
                        position["stop_loss"],
                        pnl,
                    )

        return alerts
