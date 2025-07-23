
import asyncio
import sys

# Replace this line:
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# With this cross-platform version:
if sys.platform.startswith('win') and hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
elif sys.platform.startswith('win') and hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from config import *
from logger import logger
from exchanges import ExchangeManager
from risk import RiskManager
from telegram_bot import run_bot

async def setup_demo_positions(risk_manager: RiskManager):
    """Add some demo positions for testing"""
    # await risk_manager.update_position("BTC/USDT", "okx", 0.1, 45000.0)
    await risk_manager.update_position("ETH/USDT", "bybit", 1.0, 2800.0)
    logger.info("Demo positions added")

async def setup_risk(risk_manager: RiskManager):
    await setup_demo_positions(risk_manager)
    await risk_manager.calculate_real_time_risk()

def main():
    logger.info("Starting Crypto Hedging Bot...")
    
    # Initialize exchange manager
    exchange_manager = ExchangeManager()
    
    # Initialize risk manager
    risk_manager = RiskManager(exchange_manager)
    
    # Add demo positions and calculate initial risk
    asyncio.run(setup_risk(risk_manager))
    
    # Start Telegram bot with risk manager (blocks, manages its own event loop)
    run_bot(risk_manager)

if __name__ == "__main__":
    main()