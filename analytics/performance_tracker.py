import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger
import json
import os

@dataclass
class TradeRecord:
    """Individual trade record"""
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    timestamp: datetime
    fees: float
    slippage: float
    exchange: str
    order_type: str
    trade_id: str

@dataclass
class PerformanceMetrics:
    """Performance metrics for a period"""
    period: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: float
    total_fees: float
    total_slippage: float
    timestamp: datetime

@dataclass
class CostAnalysis:
    """Trading cost analysis"""
    total_fees: float
    total_slippage: float
    funding_costs: float
    opportunity_costs: float
    total_costs: float
    cost_percentage: float
    fee_breakdown: Dict[str, float]
    slippage_breakdown: Dict[str, float]

class PerformanceTracker:
    """Historical performance tracking and cost analysis"""
    
    def __init__(self, data_file: str = "performance_data.json"):
        self.data_file = data_file
        self.trades: List[TradeRecord] = []
        self.performance_history: List[PerformanceMetrics] = []
        self.cost_history: List[CostAnalysis] = []
        self.load_data()
        
    def load_data(self):
        """Load historical data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.trades = [TradeRecord(**trade) for trade in data.get('trades', [])]
                    self.performance_history = [PerformanceMetrics(**perf) for perf in data.get('performance', [])]
                    self.cost_history = [CostAnalysis(**cost) for cost in data.get('costs', [])]
                logger.info(f"Loaded {len(self.trades)} trades from {self.data_file}")
        except Exception as e:
            logger.error(f"Error loading performance data: {e}")
    
    def save_data(self):
        """Save data to file"""
        try:
            data = {
                'trades': [trade.__dict__ for trade in self.trades],
                'performance': [perf.__dict__ for perf in self.performance_history],
                'costs': [cost.__dict__ for cost in self.cost_history]
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")
    
    def add_trade(self, trade: TradeRecord):
        """Add a new trade record"""
        self.trades.append(trade)
        self.save_data()
    
    def get_trades_by_period(self, start_date: datetime, end_date: datetime) -> List[TradeRecord]:
        """Get trades within a specific period"""
        return [trade for trade in self.trades 
                if start_date <= trade.timestamp <= end_date]
    
    def calculate_performance_metrics(self, period: str = "all") -> PerformanceMetrics:
        """Calculate performance metrics for a period"""
        if period == "all":
            trades = self.trades
        else:
            # Calculate period based on period string (e.g., "1d", "1w", "1m")
            end_date = datetime.now()
            if period.endswith('d'):
                days = int(period[:-1])
                start_date = end_date - timedelta(days=days)
            elif period.endswith('w'):
                weeks = int(period[:-1])
                start_date = end_date - timedelta(weeks=weeks)
            elif period.endswith('m'):
                months = int(period[:-1])
                start_date = end_date - timedelta(days=months*30)
            else:
                start_date = end_date - timedelta(days=1)
            
            trades = self.get_trades_by_period(start_date, end_date)
        
        if not trades:
            return PerformanceMetrics(
                period=period,
                total_return=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                volatility=0.0,
                win_rate=0.0,
                profit_factor=0.0,
                total_trades=0,
                avg_trade_duration=0.0,
                total_fees=0.0,
                total_slippage=0.0,
                timestamp=datetime.now()
            )
        
        # Calculate returns
        returns = self._calculate_returns(trades)
        total_return = sum(returns) if returns else 0.0
        
        # Calculate metrics
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        max_drawdown = self._calculate_max_drawdown(returns)
        volatility = self._calculate_volatility(returns)
        win_rate = self._calculate_win_rate(trades)
        profit_factor = self._calculate_profit_factor(trades)
        total_trades = len(trades)
        avg_trade_duration = self._calculate_avg_trade_duration(trades)
        total_fees = sum(trade.fees for trade in trades)
        total_slippage = sum(trade.slippage for trade in trades)
        
        metrics = PerformanceMetrics(
            period=period,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            volatility=volatility,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            avg_trade_duration=avg_trade_duration,
            total_fees=total_fees,
            total_slippage=total_slippage,
            timestamp=datetime.now()
        )
        
        self.performance_history.append(metrics)
        self.save_data()
        return metrics
    
    def calculate_cost_analysis(self, period: str = "all") -> CostAnalysis:
        """Calculate detailed cost analysis"""
        if period == "all":
            trades = self.trades
        else:
            end_date = datetime.now()
            if period.endswith('d'):
                days = int(period[:-1])
                start_date = end_date - timedelta(days=days)
            elif period.endswith('w'):
                weeks = int(period[:-1])
                start_date = end_date - timedelta(weeks=weeks)
            elif period.endswith('m'):
                months = int(period[:-1])
                start_date = end_date - timedelta(days=months*30)
            else:
                start_date = end_date - timedelta(days=1)
            
            trades = self.get_trades_by_period(start_date, end_date)
        
        if not trades:
            return CostAnalysis(
                total_fees=0.0,
                total_slippage=0.0,
                funding_costs=0.0,
                opportunity_costs=0.0,
                total_costs=0.0,
                cost_percentage=0.0,
                fee_breakdown={},
                slippage_breakdown={}
            )
        
        # Calculate fee breakdown by exchange
        fee_breakdown = {}
        for trade in trades:
            exchange = trade.exchange
            fee_breakdown[exchange] = fee_breakdown.get(exchange, 0) + trade.fees
        
        # Calculate slippage breakdown by symbol
        slippage_breakdown = {}
        for trade in trades:
            symbol = trade.symbol
            slippage_breakdown[symbol] = slippage_breakdown.get(symbol, 0) + trade.slippage
        
        total_fees = sum(trade.fees for trade in trades)
        total_slippage = sum(trade.slippage for trade in trades)
        
        # Estimate funding costs (for perpetual positions)
        funding_costs = self._estimate_funding_costs(trades)
        
        # Estimate opportunity costs
        opportunity_costs = self._estimate_opportunity_costs(trades)
        
        total_costs = total_fees + total_slippage + funding_costs + opportunity_costs
        
        # Calculate cost percentage
        total_volume = sum(trade.quantity * trade.price for trade in trades)
        cost_percentage = (total_costs / total_volume * 100) if total_volume > 0 else 0
        
        analysis = CostAnalysis(
            total_fees=total_fees,
            total_slippage=total_slippage,
            funding_costs=funding_costs,
            opportunity_costs=opportunity_costs,
            total_costs=total_costs,
            cost_percentage=cost_percentage,
            fee_breakdown=fee_breakdown,
            slippage_breakdown=slippage_breakdown
        )
        
        self.cost_history.append(analysis)
        self.save_data()
        return analysis
    
    def _calculate_returns(self, trades: List[TradeRecord]) -> List[float]:
        """Calculate returns from trades"""
        if not trades:
            return []
        
        # Group trades by symbol to calculate P&L
        symbol_trades = {}
        for trade in trades:
            if trade.symbol not in symbol_trades:
                symbol_trades[trade.symbol] = []
            symbol_trades[trade.symbol].append(trade)
        
        returns = []
        for symbol, symbol_trade_list in symbol_trades.items():
            # Calculate P&L for this symbol
            pnl = 0.0
            for trade in symbol_trade_list:
                if trade.side == 'buy':
                    pnl -= trade.quantity * trade.price
                else:  # sell
                    pnl += trade.quantity * trade.price
                pnl -= trade.fees + trade.slippage
            
            if pnl != 0:
                returns.append(pnl)
        
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
        """Calculate volatility"""
        if not returns:
            return 0.0
        
        return float(np.std(returns) * np.sqrt(252))  # Annualized
    
    def _calculate_win_rate(self, trades: List[TradeRecord]) -> float:
        """Calculate win rate"""
        if not trades:
            return 0.0
        
        # Group trades by symbol to determine wins/losses
        symbol_pnl = {}
        for trade in trades:
            if trade.symbol not in symbol_pnl:
                symbol_pnl[trade.symbol] = 0.0
            
            if trade.side == 'buy':
                symbol_pnl[trade.symbol] -= trade.quantity * trade.price
            else:  # sell
                symbol_pnl[trade.symbol] += trade.quantity * trade.price
            
            symbol_pnl[trade.symbol] -= trade.fees + trade.slippage
        
        wins = sum(1 for pnl in symbol_pnl.values() if pnl > 0)
        total_positions = len(symbol_pnl)
        
        return (wins / total_positions * 100) if total_positions > 0 else 0.0
    
    def _calculate_profit_factor(self, trades: List[TradeRecord]) -> float:
        """Calculate profit factor"""
        if not trades:
            return 0.0
        
        # Group trades by symbol
        symbol_pnl = {}
        for trade in trades:
            if trade.symbol not in symbol_pnl:
                symbol_pnl[trade.symbol] = 0.0
            
            if trade.side == 'buy':
                symbol_pnl[trade.symbol] -= trade.quantity * trade.price
            else:  # sell
                symbol_pnl[trade.symbol] += trade.quantity * trade.price
            
            symbol_pnl[trade.symbol] -= trade.fees + trade.slippage
        
        gross_profit = sum(pnl for pnl in symbol_pnl.values() if pnl > 0)
        gross_loss = abs(sum(pnl for pnl in symbol_pnl.values() if pnl < 0))
        
        return gross_profit / gross_loss if gross_loss > 0 else 0.0
    
    def _calculate_avg_trade_duration(self, trades: List[TradeRecord]) -> float:
        """Calculate average trade duration"""
        if len(trades) < 2:
            return 0.0
        
        # Simplified: calculate time between first and last trade
        timestamps = [trade.timestamp for trade in trades]
        duration = max(timestamps) - min(timestamps)
        
        return duration.total_seconds() / 3600  # Return in hours
    
    def _estimate_funding_costs(self, trades: List[TradeRecord]) -> float:
        """Estimate funding costs for perpetual positions"""
        # Simplified estimation
        total_volume = sum(trade.quantity * trade.price for trade in trades)
        return total_volume * 0.0001  # 0.01% funding rate
    
    def _estimate_opportunity_costs(self, trades: List[TradeRecord]) -> float:
        """Estimate opportunity costs"""
        # Simplified estimation based on holding time
        total_volume = sum(trade.quantity * trade.price for trade in trades)
        return total_volume * 0.0005  # 0.05% opportunity cost
    
    def get_performance_summary(self, period: str = "all") -> Dict:
        """Get comprehensive performance summary"""
        metrics = self.calculate_performance_metrics(period)
        cost_analysis = self.calculate_cost_analysis(period)
        
        return {
            'period': period,
            'performance': {
                'total_return': metrics.total_return,
                'sharpe_ratio': metrics.sharpe_ratio,
                'max_drawdown': metrics.max_drawdown,
                'volatility': metrics.volatility,
                'win_rate': metrics.win_rate,
                'profit_factor': metrics.profit_factor,
                'total_trades': metrics.total_trades
            },
            'costs': {
                'total_costs': cost_analysis.total_costs,
                'cost_percentage': cost_analysis.cost_percentage,
                'fee_breakdown': cost_analysis.fee_breakdown,
                'slippage_breakdown': cost_analysis.slippage_breakdown
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_top_performers(self, period: str = "all", limit: int = 5) -> List[Dict]:
        """Get top performing symbols"""
        if period == "all":
            trades = self.trades
        else:
            end_date = datetime.now()
            if period.endswith('d'):
                days = int(period[:-1])
                start_date = end_date - timedelta(days=days)
            elif period.endswith('w'):
                weeks = int(period[:-1])
                start_date = end_date - timedelta(weeks=weeks)
            elif period.endswith('m'):
                months = int(period[:-1])
                start_date = end_date - timedelta(days=months*30)
            else:
                start_date = end_date - timedelta(days=1)
            
            trades = self.get_trades_by_period(start_date, end_date)
        
        # Calculate P&L by symbol
        symbol_pnl = {}
        for trade in trades:
            if trade.symbol not in symbol_pnl:
                symbol_pnl[trade.symbol] = 0.0
            
            if trade.side == 'buy':
                symbol_pnl[trade.symbol] -= trade.quantity * trade.price
            else:  # sell
                symbol_pnl[trade.symbol] += trade.quantity * trade.price
            
            symbol_pnl[trade.symbol] -= trade.fees + trade.slippage
        
        # Sort by P&L and return top performers
        sorted_symbols = sorted(symbol_pnl.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'symbol': symbol,
                'pnl': pnl,
                'trades': len([t for t in trades if t.symbol == symbol])
            }
            for symbol, pnl in sorted_symbols[:limit]
        ] 