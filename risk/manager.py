import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from .base import RiskCalculator, Position, PortfolioRisk, RiskMetrics
from exchanges import ExchangeManager
from logger import logger

class RiskManager:
    def __init__(self, exchange_manager: ExchangeManager):
        self.exchange_manager = exchange_manager
        self.calculator = RiskCalculator()
        self.positions: Dict[str, Position] = {}
        self.last_risk_update: Optional[PortfolioRisk] = None
        
    async def update_position(self, symbol: str, exchange: str, size: float, current_price: float):
        """Update or add a position"""
        position = Position(
            symbol=symbol,
            exchange=exchange,
            size=size,
            entry_price=current_price,  # Simplified for demo
            current_price=current_price,
            pnl=0.0  # Calculate based on entry vs current
        )
        self.positions[f"{exchange}:{symbol}"] = position
        logger.info(f"Updated position: {symbol} on {exchange}")
    
    async def fetch_market_data(self, symbols: List[str]) -> Dict[str, float]:
        """Fetch current prices for symbols"""
        prices = {}
        for symbol in symbols:
            try:
                # Try to get orderbook from any exchange
                orderbooks = await self.exchange_manager.fetch_all_orderbooks(symbol)
                for exchange, ob in orderbooks.items():
                    if ob and ob.bids and ob.asks:
                        # Use mid price
                        mid_price = (ob.bids[0][0] + ob.asks[0][0]) / 2
                        prices[symbol] = mid_price
                        break
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")
        return prices
    
    async def calculate_real_time_risk(self) -> PortfolioRisk:
        """Calculate real-time portfolio risk"""
        # Update prices for all positions
        symbols = list(set(p.symbol for p in self.positions.values()))
        prices = await self.fetch_market_data(symbols)
        
        # Update position prices
        for pos_key, position in self.positions.items():
            if position.symbol in prices:
                position.current_price = prices[position.symbol]
                position.pnl = (position.current_price - position.entry_price) * position.size
                position.timestamp = datetime.now()
        
        # Calculate portfolio risk
        self.calculator.positions = list(self.positions.values())
        portfolio_risk = self.calculator.calculate_portfolio_risk()
        self.last_risk_update = portfolio_risk
        
        logger.info(f"Risk calculated: Delta={portfolio_risk.total_delta:.4f}, VaR={portfolio_risk.portfolio_var:.2f}")
        return portfolio_risk
    
    def get_formatted_risk_message(self) -> str:
        """Get formatted risk message for Telegram"""
        if not self.last_risk_update:
            return "No risk data available."
        
        risk = self.last_risk_update
        return (
            f"📊 Risk Metrics:\n"
            f"Delta: {risk.total_delta:.4f}\n"
            f"Gamma: {risk.total_gamma:.4f}\n"
            f"Vega: {risk.total_vega:.4f}\n"
            f"Theta: {risk.total_theta:.4f}\n"
            f"VaR (95%): ${risk.portfolio_var:.2f}\n"
            f"Positions: {len(risk.positions)}"
        )
    
    def get_formatted_positions_message(self) -> str:
        """Get formatted positions message for Telegram"""
        if not self.positions:
            return "No positions."
        
        msg = "📈 Positions:\n"
        for pos_key, position in self.positions.items():
            pnl_color = "🟢" if position.pnl >= 0 else "🔴"
            msg += f"{pnl_color} {position.symbol} ({position.exchange})\n"
            msg += f"   Size: {position.size:.4f}\n"
            msg += f"   PnL: ${position.pnl:.2f}\n"
        return msg
    
    async def start_monitoring(self, update_interval: int = 30):
        """Start continuous risk monitoring"""
        logger.info("Starting risk monitoring...")
        while True:
            try:
                await self.calculate_real_time_risk()
                await asyncio.sleep(update_interval)
            except Exception as e:
                logger.error(f"Risk monitoring error: {e}")
                await asyncio.sleep(5) 