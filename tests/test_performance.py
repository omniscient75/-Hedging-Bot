import pytest
import time
import asyncio
from analytics.portfolio_analytics import PortfolioAnalytics
from hedging.execution import ExecutionManager

@pytest.mark.asyncio
async def test_portfolio_analytics_performance(mock_risk_manager):
    analytics = PortfolioAnalytics(mock_risk_manager)
    start = time.time()
    await analytics.calculate_portfolio_metrics()
    elapsed = time.time() - start
    assert elapsed < 1.0  # Should complete within 1 second

@pytest.mark.asyncio
async def test_execution_manager_performance(mock_exchange_manager, mock_risk_manager):
    manager = ExecutionManager(mock_exchange_manager, mock_risk_manager)
    start = time.time()
    await manager.execute_hedge('BTC/USDT', target_delta=1)
    elapsed = time.time() - start
    assert elapsed < 2.0  # Should complete within 2 seconds 