import asyncio
from typing import List, Dict, Optional
from .bybit import BybitClient
from .base import OrderBook, MarketInfo

class ExchangeManager:
    def __init__(self):
        self.bybit = BybitClient()
        self.exchanges = {
            'bybit': self.bybit
        }

    async def fetch_orderbook(self, exchange: str, symbol: str) -> Optional[OrderBook]:
        try:
            return await self.exchanges[exchange].fetch_orderbook(symbol)
        except Exception as e:
            print(f"Error fetching orderbook from {exchange}: {e}")
            return None

    async def fetch_orderbook_with_fallback(self, symbol: str) -> Optional[OrderBook]:
        # Only Bybit is available
        try:
            return await self.bybit.fetch_orderbook(symbol)
        except Exception as e:
            print(f"Error fetching orderbook from bybit: {e}")
        return None

    async def fetch_all_orderbooks(self, symbol: str) -> Dict[str, Optional[OrderBook]]:
        results = await asyncio.gather(
            self.fetch_orderbook('bybit', symbol),
            return_exceptions=True
        )
        return {'bybit': (results[0] if isinstance(results[0], (OrderBook, type(None))) else None)}

    async def fetch_markets(self, exchange: str) -> List[MarketInfo]:
        try:
            return await self.exchanges[exchange].fetch_markets()
        except Exception as e:
            print(f"Error fetching markets from {exchange}: {e}")
            return []

    async def fetch_all_markets(self) -> Dict[str, List[MarketInfo]]:
        results = await asyncio.gather(
            self.fetch_markets('bybit'),
            return_exceptions=True
        )
        return {'bybit': (results[0] if isinstance(results[0], list) else [])}

    async def close(self):
        await self.bybit.close() 