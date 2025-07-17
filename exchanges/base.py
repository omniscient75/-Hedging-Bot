# Requires pydantic. If you see an import error for pydantic, install with: pip install pydantic
import abc
from typing import List, Dict, Any
from pydantic import BaseModel

class OrderBook(BaseModel):
    exchange: str
    symbol: str
    bids: List[List[float]]  # [[price, size], ...]
    asks: List[List[float]]  # [[price, size], ...]
    timestamp: float

class MarketInfo(BaseModel):
    exchange: str
    symbol: str
    base: str
    quote: str
    type: str  # spot, perp, future, option
    tick_size: float
    lot_size: float
    additional: Dict[str, Any] = {}

class BaseExchangeClient(abc.ABC):
    name: str

    @abc.abstractmethod
    async def fetch_orderbook(self, symbol: str) -> OrderBook:
        pass

    @abc.abstractmethod
    async def fetch_markets(self) -> List[MarketInfo]:
        pass 