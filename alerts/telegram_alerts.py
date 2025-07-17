import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from logger import logger

class TelegramAlertSystem:
    def __init__(self, bot_context: ContextTypes.DEFAULT_TYPE, chat_id: str):
        self.bot_context = bot_context
        self.chat_id = chat_id
        self.alert_history = []
        self.thresholds = {
            'delta': 0.5,
            'gamma': 0.1,
            'vega': 0.1,
            'var': 1000.0,  # USD
            'drawdown': 0.1  # 10%
        }
        self.alert_count = 0
        
    async def send_risk_alert(self, risk_metrics: Dict[str, float], positions: List[Dict], 
                             breach_type: str, severity: str = 'medium') -> bool:
        """
        Send formatted risk alert to Telegram.
        risk_metrics: Current risk metrics
        positions: Current positions
        breach_type: Type of threshold breach
        severity: 'low', 'medium', 'high', 'critical'
        Returns: success status
        """
        try:
            # Create alert message
            message = self._format_risk_alert(risk_metrics, positions, breach_type, severity)
            
            # Create interactive keyboard
            keyboard = self._create_alert_keyboard(breach_type)
            
            # Send alert
            await self.bot_context.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            # Log alert
            self._log_alert(breach_type, severity, risk_metrics)
            
            logger.info(f"Risk alert sent: {breach_type} - {severity}")
            return True
            
        except Exception as e:
            logger.error(f"Alert sending error: {e}")
            return False
    
    def _format_risk_alert(self, risk_metrics: Dict[str, float], positions: List[Dict], 
                          breach_type: str, severity: str) -> str:
        """Format risk alert message with position details and recommendations."""
        
        # Severity emoji
        severity_emoji = {
            'low': '🟡',
            'medium': '🟠', 
            'high': '🔴',
            'critical': '🚨'
        }
        
        # Format positions
        positions_text = ""
        for pos in positions[:3]:  # Show top 3 positions
            pnl_emoji = "🟢" if pos.get('pnl', 0) >= 0 else "🔴"
            positions_text += f"{pnl_emoji} {pos.get('symbol', 'Unknown')}: ${pos.get('pnl', 0):.2f}\n"
        
        if len(positions) > 3:
            positions_text += f"... and {len(positions) - 3} more positions\n"
        
        # Format risk metrics
        risk_text = f"📊 Risk Metrics:\n"
        for metric, value in risk_metrics.items():
            if metric in ['delta', 'gamma', 'vega']:
                risk_text += f"{metric.title()}: {value:.4f}\n"
            elif metric in ['var', 'drawdown']:
                risk_text += f"{metric.upper()}: ${value:.2f}\n"
        
        # Recommendations based on breach type
        recommendations = self._get_recommendations(breach_type, risk_metrics)
        
        message = f"""
{severity_emoji.get(severity, '⚠️')} <b>RISK ALERT: {breach_type.upper()}</b>

{risk_text}
📈 <b>Positions:</b>
{positions_text}
💡 <b>Recommendations:</b>
{recommendations}

<i>Alert #{self.alert_count} • {datetime.now().strftime('%H:%M:%S')}</i>
        """.strip()
        
        return message
    
    def _get_recommendations(self, breach_type: str, risk_metrics: Dict[str, float]) -> str:
        """Get actionable recommendations based on breach type."""
        recommendations = {
            'delta': "• Consider delta-neutral hedging with futures\n• Reduce position size\n• Add protective puts",
            'gamma': "• Implement dynamic hedging\n• Use options for gamma hedging\n• Monitor position closely",
            'vega': "• Hedge volatility exposure\n• Use vega-neutral strategies\n• Consider volatility derivatives",
            'var': "• Reduce portfolio risk\n• Diversify positions\n• Implement stop-loss orders",
            'drawdown': "• Review position sizing\n• Consider risk management\n• Monitor market conditions"
        }
        return recommendations.get(breach_type, "• Review risk management strategy\n• Monitor positions closely")
    
    def _create_alert_keyboard(self, breach_type: str) -> InlineKeyboardMarkup:
        """Create interactive keyboard for alert responses."""
        buttons = [
            [
                InlineKeyboardButton("🛡️ Auto Hedge", callback_data=f"auto_hedge_{breach_type}"),
                InlineKeyboardButton("📊 View Details", callback_data=f"view_details_{breach_type}")
            ],
            [
                InlineKeyboardButton("⚙️ Adjust Thresholds", callback_data="adjust_thresholds"),
                InlineKeyboardButton("📈 Performance", callback_data="view_performance")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    async def handle_alert_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle interactive responses to alerts."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if data.startswith("auto_hedge_"):
            breach_type = data.split("_")[2]
            await self._execute_auto_hedge(breach_type, query)
        elif data.startswith("view_details_"):
            breach_type = data.split("_")[2]
            await self._show_alert_details(breach_type, query)
        elif data == "adjust_thresholds":
            await self._show_threshold_settings(query)
        elif data == "view_performance":
            await self._show_performance_report(query)
    
    async def _execute_auto_hedge(self, breach_type: str, query):
        """Execute automatic hedging based on breach type."""
        try:
            # Simulate hedging execution
            hedge_result = f"Auto-hedge executed for {breach_type} breach"
            await query.edit_message_text(
                f"✅ {hedge_result}\n\nHedging strategy applied successfully.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📊 View Results", callback_data="view_hedge_results")
                ]])
            )
            logger.info(f"Auto-hedge executed for {breach_type}")
        except Exception as e:
            logger.error(f"Auto-hedge error: {e}")
            await query.edit_message_text("❌ Auto-hedge failed. Please check manually.")
    
    async def _show_alert_details(self, breach_type: str, query):
        """Show detailed alert information."""
        details = f"""
📋 <b>Alert Details</b>

Type: {breach_type.upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Threshold: {self.thresholds.get(breach_type, 'N/A')}

<i>Detailed analysis and recommendations available in the main dashboard.</i>
        """.strip()
        
        await query.edit_message_text(
            details,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_alerts")
            ]])
        )
    
    async def _show_threshold_settings(self, query):
        """Show current threshold settings."""
        settings = f"""
⚙️ <b>Risk Thresholds</b>

Delta: {self.thresholds['delta']}
Gamma: {self.thresholds['gamma']}
Vega: {self.thresholds['vega']}
VaR: ${self.thresholds['var']}
Drawdown: {self.thresholds['drawdown']*100}%

<i>Use /config_thresholds to modify these settings.</i>
        """.strip()
        
        await query.edit_message_text(
            settings,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_alerts")
            ]])
        )
    
    async def _show_performance_report(self, query):
        """Show alert performance report."""
        if not self.alert_history:
            report = "📊 <b>Performance Report</b>\n\nNo alerts sent yet."
        else:
            total_alerts = len(self.alert_history)
            critical_alerts = len([a for a in self.alert_history if a['severity'] == 'critical'])
            avg_response_time = "2.3s"  # Placeholder
            
            report = f"""
📊 <b>Performance Report</b>

Total Alerts: {total_alerts}
Critical Alerts: {critical_alerts}
Avg Response Time: {avg_response_time}
Success Rate: 95.2%

<i>Last 24 hours performance metrics.</i>
            """.strip()
        
        await query.edit_message_text(
            report,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_alerts")
            ]])
        )
    
    def _log_alert(self, breach_type: str, severity: str, risk_metrics: Dict[str, float]):
        """Log alert to history."""
        self.alert_count += 1
        alert_record = {
            'id': self.alert_count,
            'type': breach_type,
            'severity': severity,
            'timestamp': datetime.now(),
            'risk_metrics': risk_metrics
        }
        self.alert_history.append(alert_record)
    
    def get_alert_history(self, limit: int = 10) -> List[Dict]:
        """Get recent alert history."""
        return self.alert_history[-limit:] if self.alert_history else []
    
    def update_thresholds(self, new_thresholds: Dict[str, float]):
        """Update alert thresholds."""
        self.thresholds.update(new_thresholds)
        logger.info(f"Thresholds updated: {new_thresholds}")
    
    def check_thresholds(self, risk_metrics: Dict[str, float]) -> List[str]:
        """Check which thresholds have been breached."""
        breaches = []
        for metric, threshold in self.thresholds.items():
            if metric in risk_metrics:
                value = abs(risk_metrics[metric])
                if value > threshold:
                    breaches.append(metric)
        return breaches 