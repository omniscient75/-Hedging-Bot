import pytest
import asyncio
from hedging.execution import ExecutionManager

@pytest.mark.asyncio
async def test_execute_hedge_basic(mock_exchange_manager, mock_risk_manager):
    manager = ExecutionManager(mock_exchange_manager, mock_risk_manager)
    result = await manager.execute_hedge('BTC/USDT', target_delta=1)
    assert result['status'] in ['filled', 'partially_filled']
    assert result['hedge_size'] != 0
    assert 'cost_benefit' in result

@pytest.mark.asyncio
async def test_execute_hedge_zero_delta(mock_exchange_manager, mock_risk_manager):
    mock_risk_manager.get_position = asyncio.coroutine(lambda symbol: {'delta': 1, 'quantity': 1, 'entry_price': 10000})
    manager = ExecutionManager(mock_exchange_manager, mock_risk_manager)
    result = await manager.execute_hedge('BTC/USDT', target_delta=1)
    assert abs(result['hedge_size']) < 1e-6

@pytest.mark.asyncio
async def test_execute_hedge_error_handling(mock_exchange_manager, mock_risk_manager):
    mock_exchange_manager.place_order = asyncio.coroutine(lambda **kwargs: (_ for _ in ()).throw(Exception('Order failed')))
    manager = ExecutionManager(mock_exchange_manager, mock_risk_manager)
    result = await manager.execute_hedge('BTC/USDT', target_delta=1)
    assert result['status'] == 'failed'
    assert any('error' in r for r in result['execution_results']) 