import pytest
import asyncio

@pytest.mark.asyncio
async def test_get_market_data(mock_exchange_manager):
    data = await mock_exchange_manager.get_market_data('BTC/USDT')
    assert data['last_price'] == 10000
    assert 'volatility' in data

@pytest.mark.asyncio
async def test_get_available_venues(mock_exchange_manager):
    venues = await mock_exchange_manager.get_available_venues('BTC/USDT')
    assert set(venues) == {'okx', 'bybit'}

@pytest.mark.asyncio
async def test_get_order_book(mock_exchange_manager):
    ob = await mock_exchange_manager.get_order_book('BTC/USDT', 'okx')
    assert ob['best_ask'] > ob['best_bid']
    assert ob['depth'] > 0

@pytest.mark.asyncio
async def test_place_order(mock_exchange_manager):
    result = await mock_exchange_manager.place_order(symbol='BTC/USDT', venue='okx', side='buy', quantity=1, price=10000, max_slippage=0.002)
    assert result['filled'] == 1
    assert result['cost'] == 10000
    assert result['fees'] == 4 