from typing import Dict, List, Any, Literal
from enum import Enum
import numpy as np
from logger import logger

class HedgingStrategy(Enum):
    DELTA_NEUTRAL = "delta_neutral"
    PROTECTIVE_PUT = "protective_put"
    COVERED_CALL = "covered_call"
    COLLAR = "collar"
    DYNAMIC = "dynamic"

class HedgingStrategy:
    def __init__(self, strategy_type: HedgingStrategy):
        self.strategy_type = strategy_type
        self.performance_history = []
        self.last_rebalance = None
        
    def delta_neutral_hedge(self, portfolio_delta: float, futures_price: float, futures_delta: float = 1.0) -> Dict[str, Any]:
        """
        Delta-neutral hedging using perpetual futures.
        portfolio_delta: Current portfolio delta
        futures_price: Current futures price
        futures_delta: Delta of futures contract (usually 1.0)
        Returns: dict with hedge size and cost
        """
        try:
            hedge_size = -portfolio_delta / futures_delta
            hedge_cost = abs(hedge_size) * futures_price
            return {
                'hedge_size': hedge_size,
                'hedge_cost': hedge_cost,
                'strategy': 'delta_neutral'
            }
        except Exception as e:
            logger.error(f"Delta neutral hedge error: {e}")
            return {'hedge_size': 0, 'hedge_cost': 0, 'strategy': 'delta_neutral'}

    def protective_put_hedge(self, portfolio_value: float, put_strike: float, put_premium: float) -> Dict[str, Any]:
        """
        Protective put strategy.
        portfolio_value: Current portfolio value
        put_strike: Strike price of put option
        put_premium: Cost of put option
        Returns: dict with hedge details
        """
        try:
            protection_cost = put_premium
            max_loss = portfolio_value - put_strike + put_premium
            return {
                'protection_cost': protection_cost,
                'max_loss': max_loss,
                'strategy': 'protective_put'
            }
        except Exception as e:
            logger.error(f"Protective put hedge error: {e}")
            return {'protection_cost': 0, 'max_loss': portfolio_value, 'strategy': 'protective_put'}

    def covered_call_hedge(self, portfolio_value: float, call_strike: float, call_premium: float) -> Dict[str, Any]:
        """
        Covered call strategy.
        portfolio_value: Current portfolio value
        call_strike: Strike price of call option
        call_premium: Premium received from call
        Returns: dict with hedge details
        """
        try:
            income = call_premium
            max_gain = call_strike - portfolio_value + call_premium
            return {
                'income': income,
                'max_gain': max_gain,
                'strategy': 'covered_call'
            }
        except Exception as e:
            logger.error(f"Covered call hedge error: {e}")
            return {'income': 0, 'max_gain': 0, 'strategy': 'covered_call'}

    def collar_hedge(self, portfolio_value: float, put_strike: float, call_strike: float, put_premium: float, call_premium: float) -> Dict[str, Any]:
        """
        Collar strategy (protective put + covered call).
        Returns: dict with hedge details
        """
        try:
            net_cost = put_premium - call_premium
            max_loss = portfolio_value - put_strike + net_cost
            max_gain = call_strike - portfolio_value + net_cost
            return {
                'net_cost': net_cost,
                'max_loss': max_loss,
                'max_gain': max_gain,
                'strategy': 'collar'
            }
        except Exception as e:
            logger.error(f"Collar hedge error: {e}")
            return {'net_cost': 0, 'max_loss': portfolio_value, 'max_gain': 0, 'strategy': 'collar'}

    def dynamic_hedge(self, current_metrics: Dict[str, float], target_metrics: Dict[str, float], rebalance_threshold: float = 0.1) -> Dict[str, Any]:
        """
        Dynamic hedging with rebalancing logic.
        current_metrics: Current portfolio metrics
        target_metrics: Target portfolio metrics
        rebalance_threshold: Threshold for rebalancing
        Returns: dict with rebalancing actions
        """
        try:
            actions = {}
            for metric in ['delta', 'gamma', 'vega']:
                current = current_metrics.get(metric, 0)
                target = target_metrics.get(metric, 0)
                if abs(current - target) > rebalance_threshold:
                    actions[metric] = target - current
            return {
                'actions': actions,
                'rebalance_needed': len(actions) > 0,
                'strategy': 'dynamic'
            }
        except Exception as e:
            logger.error(f"Dynamic hedge error: {e}")
            return {'actions': {}, 'rebalance_needed': False, 'strategy': 'dynamic'}

    def select_strategy(self, portfolio_metrics: Dict[str, float], market_conditions: Dict[str, Any]) -> HedgingStrategy:
        """
        Strategy selection logic based on portfolio metrics and market conditions.
        """
        try:
            delta = abs(portfolio_metrics.get('delta', 0))
            volatility = market_conditions.get('volatility', 0)
            
            if delta > 0.5:
                return HedgingStrategy.DELTA_NEUTRAL
            elif volatility > 0.3:
                return HedgingStrategy.PROTECTIVE_PUT
            elif delta < 0.1 and volatility < 0.2:
                return HedgingStrategy.COVERED_CALL
            elif delta > 0.3 and volatility > 0.25:
                return HedgingStrategy.COLLAR
            else:
                return HedgingStrategy.DYNAMIC
        except Exception as e:
            logger.error(f"Strategy selection error: {e}")
            return HedgingStrategy.DELTA_NEUTRAL

    def track_performance(self, strategy_result: Dict[str, Any], actual_pnl: float):
        """
        Track strategy performance.
        """
        try:
            performance = {
                'strategy': strategy_result.get('strategy', 'unknown'),
                'expected_cost': strategy_result.get('hedge_cost', 0) + strategy_result.get('protection_cost', 0),
                'actual_pnl': actual_pnl,
                'timestamp': None  # Add timestamp when implementing
            }
            self.performance_history.append(performance)
            logger.info(f"Strategy performance tracked: {performance}")
        except Exception as e:
            logger.error(f"Performance tracking error: {e}") 