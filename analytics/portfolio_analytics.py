import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

@dataclass
class PnLAttribution:
    """P&L attribution breakdown"""
    total_pnl: float
    spot_pnl: float
    hedge_pnl: float
    funding_pnl: float
    trading_fees: float
    slippage: float
    unrealized_pnl: float
    realized_pnl: float
    timestamp: datetime

@dataclass
class PortfolioMetrics:
    """Comprehensive portfolio metrics"""
    total_value: float
    total_pnl: float
    pnl_percentage: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    beta: float
    correlation_matrix: pd.DataFrame
    position_concentration: Dict[str, float]
    risk_metrics: Dict[str, float]

class PortfolioAnalytics:
    """Real-time portfolio analytics and P&L attribution"""
    
    def __init__(self, risk_manager):
        self.risk_manager = risk_manager
        self.pnl_history: List[PnLAttribution] = []
        self.portfolio_history: List[PortfolioMetrics] = []
        self.update_interval = 60  # seconds
        
    async def calculate_pnl_attribution(self, positions: Dict) -> PnLAttribution:
        """Calculate detailed P&L attribution"""
        total_pnl = 0.0
        spot_pnl = 0.0
        hedge_pnl = 0.0
        funding_pnl = 0.0
        trading_fees = 0.0
        slippage = 0.0
        unrealized_pnl = 0.0
        realized_pnl = 0.0
        
        for symbol, position in positions.items():
            # Calculate spot P&L
            if position.get('type') == 'spot':
                current_price = await self._get_current_price(symbol)
                entry_price = position.get('entry_price', 0)
                quantity = position.get('quantity', 0)
                
                if entry_price > 0:
                    spot_pnl += (current_price - entry_price) * quantity
                    unrealized_pnl += (current_price - entry_price) * quantity
            
            # Calculate hedge P&L
            elif position.get('type') == 'hedge':
                hedge_pnl += position.get('unrealized_pnl', 0)
                unrealized_pnl += position.get('unrealized_pnl', 0)
            
            # Calculate fees and slippage
            trading_fees += position.get('fees', 0)
            slippage += position.get('slippage', 0)
            
            # Calculate funding (for perpetual positions)
            if position.get('instrument_type') == 'perpetual':
                funding_pnl += position.get('funding_pnl', 0)
        
        total_pnl = spot_pnl + hedge_pnl + funding_pnl - trading_fees - slippage
        
        attribution = PnLAttribution(
            total_pnl=total_pnl,
            spot_pnl=spot_pnl,
            hedge_pnl=hedge_pnl,
            funding_pnl=funding_pnl,
            trading_fees=trading_fees,
            slippage=slippage,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=realized_pnl,
            timestamp=datetime.now()
        )
        
        self.pnl_history.append(attribution)
        return attribution
    
    async def calculate_portfolio_metrics(self) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        positions = await self.risk_manager.get_all_positions()
        
        # Calculate total portfolio value
        total_value = sum(pos.get('market_value', 0) for pos in positions.values())
        
        # Calculate P&L attribution
        pnl_attribution = await self.calculate_pnl_attribution(positions)
        
        # Calculate performance metrics
        returns = self._calculate_returns()
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        max_drawdown = self._calculate_max_drawdown(returns)
        volatility = self._calculate_volatility(returns)
        beta = self._calculate_beta(returns)
        
        # Calculate position concentration
        position_concentration = {}
        for symbol, position in positions.items():
            market_value = position.get('market_value', 0)
            if total_value > 0:
                position_concentration[symbol] = market_value / total_value
        
        # Calculate correlation matrix
        correlation_matrix = await self._calculate_correlation_matrix(positions)
        
        # Risk metrics
        risk_metrics = {
            'var_95': self._calculate_var(returns, 0.95),
            'var_99': self._calculate_var(returns, 0.99),
            'expected_shortfall': self._calculate_expected_shortfall(returns),
            'skewness': self._calculate_skewness(returns),
            'kurtosis': self._calculate_kurtosis(returns)
        }
        
        metrics = PortfolioMetrics(
            total_value=total_value,
            total_pnl=pnl_attribution.total_pnl,
            pnl_percentage=(pnl_attribution.total_pnl / total_value * 100) if total_value > 0 else 0,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            volatility=volatility,
            beta=beta,
            correlation_matrix=correlation_matrix,
            position_concentration=position_concentration,
            risk_metrics=risk_metrics
        )
        
        self.portfolio_history.append(metrics)
        return metrics
    
    def _calculate_returns(self) -> List[float]:
        """Calculate historical returns"""
        if len(self.pnl_history) < 2:
            return []
        
        returns = []
        for i in range(1, len(self.pnl_history)):
            prev_pnl = self.pnl_history[i-1].total_pnl
            curr_pnl = self.pnl_history[i].total_pnl
            
            if prev_pnl != 0:
                returns.append((curr_pnl - prev_pnl) / abs(prev_pnl))
        
        return returns
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        if len(returns_array) == 0:
            return 0.0
        
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        if std_return == 0:
            return 0.0
        
        # Assuming risk-free rate of 0 for crypto
        return mean_return / std_return * np.sqrt(252)  # Annualized
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0.0
        
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        return float(np.min(drawdown))
    
    def _calculate_volatility(self, returns: List[float]) -> float:
        """Calculate portfolio volatility"""
        if not returns:
            return 0.0
        
        return float(np.std(returns) * np.sqrt(252))  # Annualized
    
    def _calculate_beta(self, returns: List[float]) -> float:
        """Calculate portfolio beta (simplified)"""
        # For crypto, we'll use BTC as market proxy
        # This is a simplified implementation
        return 1.0  # Placeholder
    
    def _calculate_var(self, returns: List[float], confidence: float) -> float:
        """Calculate Value at Risk"""
        if not returns:
            return 0.0
        
        return float(np.percentile(returns, (1 - confidence) * 100))
    
    def _calculate_expected_shortfall(self, returns: List[float]) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        if not returns:
            return 0.0
        
        var_95 = self._calculate_var(returns, 0.95)
        tail_returns = [r for r in returns if r <= var_95]
        
        if not tail_returns:
            return 0.0
        
        return float(np.mean(tail_returns))
    
    def _calculate_skewness(self, returns: List[float]) -> float:
        """Calculate return skewness"""
        if not returns:
            return 0.0
        
        return float(pd.Series(returns).skew())
    
    def _calculate_kurtosis(self, returns: List[float]) -> float:
        """Calculate return kurtosis"""
        if not returns:
            return 0.0
        
        return float(pd.Series(returns).kurtosis())
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            market_data = await self.risk_manager.exchange_manager.get_market_data(symbol)
            return market_data.get('last_price', 0.0)
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return 0.0
    
    async def _calculate_correlation_matrix(self, positions: Dict) -> pd.DataFrame:
        """Calculate correlation matrix for portfolio assets"""
        symbols = list(positions.keys())
        if len(symbols) < 2:
            return pd.DataFrame()
        
        # Get historical prices for correlation calculation
        prices_data = {}
        for symbol in symbols:
            try:
                # Simplified: use recent price changes as proxy
                prices_data[symbol] = [positions[symbol].get('unrealized_pnl', 0)]
            except Exception as e:
                logger.error(f"Error getting price data for {symbol}: {e}")
                prices_data[symbol] = [0]
        
        df = pd.DataFrame(prices_data)
        return df.corr()
    
    async def get_analytics_summary(self) -> Dict:
        """Get comprehensive analytics summary"""
        metrics = await self.calculate_portfolio_metrics()
        
        return {
            'portfolio_value': metrics.total_value,
            'total_pnl': metrics.total_pnl,
            'pnl_percentage': metrics.pnl_percentage,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'volatility': metrics.volatility,
            'position_concentration': metrics.position_concentration,
            'risk_metrics': metrics.risk_metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    async def start_real_time_analytics(self):
        """Start real-time analytics monitoring"""
        logger.info("Starting real-time portfolio analytics...")
        
        while True:
            try:
                await self.calculate_portfolio_metrics()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in real-time analytics: {e}")
                await asyncio.sleep(10) 