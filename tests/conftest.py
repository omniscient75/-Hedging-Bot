import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from data.db_manager import DatabaseManager

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope='function')
async def db_manager(tmp_path):
    db_path = tmp_path / 'test.db'
    db = DatabaseManager(str(db_path))
    await db.connect()
    yield db
    await db.close()

@pytest.fixture
def mock_exchange_manager():
    mock = MagicMock()
    mock.get_market_data = AsyncMock(return_value={'last_price': 10000, 'volatility': 0.05, 'order_book_liquidity': 100000})
    mock.get_available_venues = AsyncMock(return_value=['okx', 'bybit', 'deribit'])
    mock.get_order_book = AsyncMock(return_value={'best_ask': 10001, 'best_bid': 9999, 'depth': 100000, 'fees': 0.0004, 'latency': 0.1})
    mock.place_order = AsyncMock(return_value={'filled': 1, 'cost': 10000, 'slippage': 1, 'fees': 4})
    return mock

@pytest.fixture
def mock_risk_manager():
    mock = MagicMock()
    mock.get_position = AsyncMock(return_value={'delta': 0, 'quantity': 1, 'entry_price': 10000})
    mock.get_all_positions = AsyncMock(return_value={})
    return mock

@pytest.fixture
def mock_telegram_update():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_photo = AsyncMock()
    update.callback_query = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    update.callback_query.message.chat_id = 123456
    return update

@pytest.fixture
def mock_telegram_context():
    context = MagicMock()
    context.bot.send_photo = AsyncMock()
    context.bot.send_message = AsyncMock()
    return context 