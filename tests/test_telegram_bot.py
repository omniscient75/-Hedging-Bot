import pytest
import asyncio
from telegram_bot.analytics_bot import AnalyticsBot
from unittest.mock import MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_start_command(mock_telegram_update, mock_telegram_context, mock_risk_manager):
    bot = AnalyticsBot(mock_risk_manager, analytics_manager=MagicMock())
    await bot.start_command(mock_telegram_update, mock_telegram_context)
    mock_telegram_update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_portfolio_analytics_command(mock_telegram_update, mock_telegram_context, mock_risk_manager):
    analytics_manager = MagicMock()
    analytics_manager.portfolio_analytics.calculate_portfolio_metrics = AsyncMock(return_value=MagicMock(total_value=10000, total_pnl=1000, pnl_percentage=10, sharpe_ratio=1.2, max_drawdown=-0.1, volatility=0.2, risk_metrics={'var_95': -0.05}))
    analytics_manager.portfolio_analytics.get_all_positions = AsyncMock(return_value={})
    analytics_manager.chart_generator.generate_portfolio_dashboard = AsyncMock(return_value=None)
    bot = AnalyticsBot(mock_risk_manager, analytics_manager)
    await bot.portfolio_analytics_command(mock_telegram_update, mock_telegram_context)
    mock_telegram_update.message.reply_text.assert_called() 