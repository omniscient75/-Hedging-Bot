import asyncio
import httpx
from typing import List
from .base import BaseExchangeClient, OrderBook, MarketInfo

BYBIT_BASE_URL = "https://api.bybit.com"

class BybitClient(BaseExchangeClient):
    name = "bybit"

    def __init__(self):
        self._client = httpx.AsyncClient(base_url=BYBIT_BASE_URL, timeout=10)
        self._rate_limit = asyncio.Semaphore(5)

    async def fetch_orderbook(self, symbol: str) -> OrderBook:
        async with self._rate_limit:
            try:
                # Bybit uses USDT pairs for spot and perp
                # For demo, try spot first, then perp if not found
                resp = await self._client.get("/v5/market/orderbook", params={"category": "spot", "symbol": symbol.replace("/", "")})
                data = resp.json()
                if data["retCode"] != 0:
                    # Try perp
                    resp = await self._client.get("/v5/market/orderbook", params={"category": "linear", "symbol": symbol.replace("/", "") + "USDT"})
                    data = resp.json()
                ob = data["result"]
                return OrderBook(
                    exchange=self.name,
                    symbol=symbol,
                    bids=[[float(b[0]), float(b[1])] for b in ob["b"]],
                    asks=[[float(a[0]), float(a[1])] for a in ob["a"]],
                    timestamp=float(ob["ts"]) / 1000.0
                )
            except Exception as e:
                print(f"Bybit orderbook error: {e}")
                raise

    async def fetch_markets(self) -> List[MarketInfo]:
        async with self._rate_limit:
            try:
                # Spot
                resp = await self._client.get("/v5/market/instruments-info", params={"category": "spot"})
                spot_markets = resp.json()["result"]["list"]
                # Perp
                resp = await self._client.get("/v5/market/instruments-info", params={"category": "linear"})
                perp_markets = resp.json()["result"]["list"]
                markets = []
                for m in spot_markets + perp_markets:
                    markets.append(MarketInfo(
                        exchange=self.name,
                        symbol=m["symbol"].replace("_", "/"),
                        base=m["baseCoin"],
                        quote=m["quoteCoin"],
                        type="spot" if m["category"] == "spot" else "perp",
                        tick_size=float(m["priceFilter"]["tickSize"]),
                        lot_size=float(m["lotSizeFilter"]["minOrderQty"]),
                        additional={}
                    ))
                return markets
            except Exception as e:
                print(f"Bybit markets error: {e}")
                raise

    async def close(self):
        await self._client.aclose() 