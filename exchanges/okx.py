import asyncio
import httpx
from typing import List
from .base import BaseExchangeClient, OrderBook, MarketInfo
from logger import logger

OKX_BASE_URL = "https://www.okx.com"

class OKXClient(BaseExchangeClient):
    name = "okx"

    def __init__(self):
        self._client = httpx.AsyncClient(base_url=OKX_BASE_URL, timeout=10)
        self._rate_limit = asyncio.Semaphore(5)  # 5 concurrent requests

    async def fetch_orderbook(self, symbol: str) -> OrderBook:
        resp = None
        async with self._rate_limit:
            try:
                # Ensure symbol is in OKX format (BTC-USDT)
                inst_id = symbol.replace("/", "-")
                resp = await self._client.get(f"/api/v5/market/books", params={"instId": inst_id, "sz": 20})
                resp.raise_for_status()
                data = resp.json()["data"][0]
                return OrderBook(
                    exchange=self.name,
                    symbol=symbol,
                    bids=[[float(b[0]), float(b[1])] for b in data["bids"]],
                    asks=[[float(a[0]), float(a[1])] for a in data["asks"]],
                    timestamp=float(data["ts"]) / 1000.0
                )
            except Exception as e:
                status = resp.status_code if resp is not None else 'No response'
                content = resp.text if resp is not None else 'No response'
                logger.error(f"OKX orderbook error for symbol {symbol}: {e}\nStatus: {status}\nResponse: {content}")
                raise

    async def fetch_markets(self) -> List[MarketInfo]:
        async with self._rate_limit:
            try:
                resp = await self._client.get("/api/v5/public/instruments", params={"instType": "SPOT"})
                resp.raise_for_status()
                spot_markets = resp.json()["data"]
                resp = await self._client.get("/api/v5/public/instruments", params={"instType": "SWAP"})
                resp.raise_for_status()
                perp_markets = resp.json()["data"]
                markets = []
                for m in spot_markets + perp_markets:
                    markets.append(MarketInfo(
                        exchange=self.name,
                        symbol=m["instId"].replace("-", "/"),
                        base=m["baseCcy"],
                        quote=m["quoteCcy"],
                        type="spot" if m["instType"] == "SPOT" else "perp",
                        tick_size=float(m["tickSz"]),
                        lot_size=float(m["minSz"]),
                        additional={"ctVal": m.get("ctVal"), "ctMult": m.get("ctMult")}
                    ))
                return markets
            except Exception as e:
                logger.error(f"OKX markets error: {e}")
                raise

    async def close(self):
        await self._client.aclose() 