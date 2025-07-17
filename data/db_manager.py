import aiosqlite
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from loguru import logger

DB_PATH = os.getenv('DB_PATH', 'hedgingbot.db')

class DatabaseManager:
    """Manages SQLite persistence for positions, trades, and risk metrics."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        self._conn = await aiosqlite.connect(self.db_path)
        await self._conn.execute('PRAGMA journal_mode=WAL;')
        await self._conn.execute('PRAGMA synchronous=NORMAL;')
        await self._conn.execute('PRAGMA foreign_keys=ON;')
        await self._conn.commit()
        await self._migrate()
        logger.info(f"Connected to SQLite DB at {self.db_path}")

    async def close(self):
        if self._conn:
            await self._conn.close()
            logger.info("Closed SQLite DB connection")

    async def _migrate(self):
        """Create tables if not exist (idempotent)."""
        await self._conn.executescript('''
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            exchange TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            position_type TEXT NOT NULL,
            delta REAL,
            gamma REAL,
            theta REAL,
            vega REAL,
            market_value REAL,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_positions_symbol_exchange ON positions(symbol, exchange);

        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            fees REAL,
            slippage REAL,
            exchange TEXT NOT NULL,
            order_type TEXT,
            trade_id TEXT UNIQUE
        );
        CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
        CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);

        CREATE TABLE IF NOT EXISTS risk_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            portfolio_value REAL,
            total_pnl REAL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            volatility REAL,
            var_95 REAL,
            var_99 REAL,
            expected_shortfall REAL,
            skewness REAL,
            kurtosis REAL,
            risk_json TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_risk_metrics_timestamp ON risk_metrics(timestamp);
        ''')
        await self._conn.commit()
        logger.info("Database schema migrated.")

    # --- POSITIONS ---
    async def upsert_position(self, position: Dict[str, Any]):
        """Insert or update a position."""
        await self._conn.execute('''
            INSERT INTO positions (symbol, exchange, quantity, entry_price, position_type, delta, gamma, theta, vega, market_value, last_update)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, exchange) DO UPDATE SET
                quantity=excluded.quantity,
                entry_price=excluded.entry_price,
                position_type=excluded.position_type,
                delta=excluded.delta,
                gamma=excluded.gamma,
                theta=excluded.theta,
                vega=excluded.vega,
                market_value=excluded.market_value,
                last_update=excluded.last_update
        ''', (
            position['symbol'], position['exchange'], position['quantity'], position['entry_price'],
            position['position_type'], position.get('delta'), position.get('gamma'), position.get('theta'),
            position.get('vega'), position.get('market_value'), datetime.now()
        ))
        await self._conn.commit()

    async def get_position(self, symbol: str, exchange: str) -> Optional[Dict[str, Any]]:
        cur = await self._conn.execute('SELECT * FROM positions WHERE symbol=? AND exchange=?', (symbol, exchange))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def get_all_positions(self) -> List[Dict[str, Any]]:
        cur = await self._conn.execute('SELECT * FROM positions')
        rows = await cur.fetchall()
        return [dict(row) for row in rows]

    # --- TRADES ---
    async def insert_trade(self, trade: Dict[str, Any]):
        await self._conn.execute('''
            INSERT OR IGNORE INTO trades (symbol, side, quantity, price, timestamp, fees, slippage, exchange, order_type, trade_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade['symbol'], trade['side'], trade['quantity'], trade['price'], trade['timestamp'],
            trade.get('fees'), trade.get('slippage'), trade['exchange'], trade.get('order_type'), trade.get('trade_id')
        ))
        await self._conn.commit()

    async def get_trades(self, symbol: Optional[str] = None, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Dict[str, Any]]:
        query = 'SELECT * FROM trades WHERE 1=1'
        params = []
        if symbol:
            query += ' AND symbol=?'
            params.append(symbol)
        if start:
            query += ' AND timestamp>=?'
            params.append(start)
        if end:
            query += ' AND timestamp<=?'
            params.append(end)
        cur = await self._conn.execute(query, params)
        rows = await cur.fetchall()
        return [dict(row) for row in rows]

    # --- RISK METRICS ---
    async def insert_risk_metrics(self, metrics: Dict[str, Any]):
        await self._conn.execute('''
            INSERT INTO risk_metrics (timestamp, portfolio_value, total_pnl, sharpe_ratio, max_drawdown, volatility, var_95, var_99, expected_shortfall, skewness, kurtosis, risk_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics['timestamp'], metrics.get('portfolio_value'), metrics.get('total_pnl'), metrics.get('sharpe_ratio'),
            metrics.get('max_drawdown'), metrics.get('volatility'), metrics.get('var_95'), metrics.get('var_99'),
            metrics.get('expected_shortfall'), metrics.get('skewness'), metrics.get('kurtosis'), metrics.get('risk_json')
        ))
        await self._conn.commit()

    async def get_risk_metrics(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Dict[str, Any]]:
        query = 'SELECT * FROM risk_metrics WHERE 1=1'
        params = []
        if start:
            query += ' AND timestamp>=?'
            params.append(start)
        if end:
            query += ' AND timestamp<=?'
            params.append(end)
        cur = await self._conn.execute(query, params)
        rows = await cur.fetchall()
        return [dict(row) for row in rows]

    # --- ARCHIVING & BACKUP ---
    async def archive_old_trades(self, before: datetime):
        await self._conn.execute('DELETE FROM trades WHERE timestamp<?', (before,))
        await self._conn.commit()
        logger.info(f"Archived trades before {before}")

    async def backup(self, backup_path: str = None):
        backup_path = backup_path or (self.db_path + '.bak')
        async with aiosqlite.connect(backup_path) as backup_conn:
            await self._conn.backup(backup_conn)
        logger.info(f"Database backup created at {backup_path}")

    # --- DATA INTEGRITY & VALIDATION ---
    async def validate_integrity(self) -> bool:
        cur = await self._conn.execute('PRAGMA integrity_check;')
        result = await cur.fetchone()
        if result and result[0] == 'ok':
            logger.info("Database integrity check passed.")
            return True
        logger.error(f"Database integrity check failed: {result}")
        return False 