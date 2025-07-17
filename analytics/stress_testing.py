import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger

@dataclass
class StressScenario:
    """Stress test scenario definition"""
    name: str
    description: str
    price_shock: float  # Percentage change
    volatility_multiplier: float
    correlation_change: float
    funding_rate_change: float
    liquidity_reduction: float

@dataclass
class StressTestResult:
    """Stress test result"""
    scenario_name: str
    original_pnl: float
    stressed_pnl: float
    pnl_impact: float
    var_impact: float
    max_drawdown_impact: float
    position_impacts: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime

class StressTester:
    """Stress testing for various market conditions"""
    
    def __init__(self, risk_manager, portfolio_analytics):
        self.risk_manager = risk_manager
        self.portfolio_analytics = portfolio_analytics
        self.scenarios = self._define_scenarios()
        
    def _define_scenarios(self) -> List[StressScenario]:
        """Define stress test scenarios"""
        return [
            StressScenario(
                name="Flash Crash",
                description="Sudden 30% market crash with high volatility",
                price_shock=-0.30,
                volatility_multiplier=3.0,
                correlation_change=0.5,
                funding_rate_change=0.001,
                liquidity_reduction=0.7
            ),
            StressScenario(
                name="Crypto Winter",
                description="Prolonged bear market with 50% decline",
                price_shock=-0.50,
                volatility_multiplier=2.0,
                correlation_change=0.8,
                funding_rate_change=0.002,
                liquidity_reduction=0.5
            ),
            StressScenario(
                name="Regulatory Shock",
                description="Regulatory crackdown scenario",
                price_shock=-0.25,
                volatility_multiplier=2.5,
                correlation_change=0.6,
                funding_rate_change=0.003,
                liquidity_reduction=0.8
            ),
            StressScenario(
                name="Liquidity Crisis",
                description="Market liquidity drying up",
                price_shock=-0.15,
                volatility_multiplier=1.5,
                correlation_change=0.3,
                funding_rate_change=0.005,
                liquidity_reduction=0.9
            ),
            StressScenario(
                name="Mega Rally",
                description="Extreme bullish scenario",
                price_shock=0.50,
                volatility_multiplier=2.0,
                correlation_change=0.4,
                funding_rate_change=-0.002,
                liquidity_reduction=0.3
            ),
            StressScenario(
                name="Black Swan",
                description="Extreme tail risk event",
                price_shock=-0.70,
                volatility_multiplier=5.0,
                correlation_change=0.9,
                funding_rate_change=0.01,
                liquidity_reduction=0.95
            )
        ]
    
    async def run_stress_test(self, scenario_name: str = None) -> List[StressTestResult]:
        """Run stress tests for specified or all scenarios"""
        results = []
        
        scenarios_to_test = [s for s in self.scenarios if scenario_name is None or s.name == scenario_name]
        
        for scenario in scenarios_to_test:
            try:
                result = await self._run_single_stress_test(scenario)
                results.append(result)
            except Exception as e:
                logger.error(f"Error running stress test {scenario.name}: {e}")
        
        return results
    
    async def _run_single_stress_test(self, scenario: StressScenario) -> StressTestResult:
        """Run a single stress test scenario"""
        # Get current portfolio state
        original_metrics = await self.portfolio_analytics.calculate_portfolio_metrics()
        original_positions = await self.risk_manager.get_all_positions()
        
        # Apply stress scenario
        stressed_positions = await self._apply_stress_scenario(original_positions, scenario)
        
        # Calculate stressed portfolio metrics
        stressed_metrics = await self._calculate_stressed_metrics(stressed_positions, scenario)
        
        # Calculate impacts
        pnl_impact = stressed_metrics.total_pnl - original_metrics.total_pnl
        var_impact = stressed_metrics.risk_metrics.get('var_95', 0) - original_metrics.risk_metrics.get('var_95', 0)
        max_drawdown_impact = stressed_metrics.max_drawdown - original_metrics.max_drawdown
        
        # Calculate position-specific impacts
        position_impacts = {}
        for symbol in original_positions:
            original_pnl = original_positions[symbol].get('unrealized_pnl', 0)
            stressed_pnl = stressed_positions.get(symbol, {}).get('unrealized_pnl', 0)
            position_impacts[symbol] = stressed_pnl - original_pnl
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scenario, pnl_impact, var_impact)
        
        return StressTestResult(
            scenario_name=scenario.name,
            original_pnl=original_metrics.total_pnl,
            stressed_pnl=stressed_metrics.total_pnl,
            pnl_impact=pnl_impact,
            var_impact=var_impact,
            max_drawdown_impact=max_drawdown_impact,
            position_impacts=position_impacts,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    async def _apply_stress_scenario(self, positions: Dict, scenario: StressScenario) -> Dict:
        """Apply stress scenario to positions"""
        stressed_positions = {}
        
        for symbol, position in positions.items():
            stressed_position = position.copy()
            
            # Apply price shock
            current_price = position.get('current_price', 0)
            if current_price > 0:
                new_price = current_price * (1 + scenario.price_shock)
                stressed_position['current_price'] = new_price
                
                # Recalculate P&L
                entry_price = position.get('entry_price', 0)
                quantity = position.get('quantity', 0)
                if entry_price > 0:
                    stressed_position['unrealized_pnl'] = (new_price - entry_price) * quantity
            
            # Apply volatility impact (affects option positions)
            if position.get('instrument_type') == 'option':
                # Simplified: reduce option value due to increased volatility
                stressed_position['unrealized_pnl'] *= (1 - scenario.volatility_multiplier * 0.1)
            
            # Apply funding rate impact (for perpetual positions)
            if position.get('instrument_type') == 'perpetual':
                funding_pnl = position.get('funding_pnl', 0)
                stressed_position['funding_pnl'] = funding_pnl * (1 + scenario.funding_rate_change)
            
            # Apply liquidity impact (slippage)
            original_slippage = position.get('slippage', 0)
            stressed_position['slippage'] = original_slippage / (1 - scenario.liquidity_reduction)
            
            stressed_positions[symbol] = stressed_position
        
        return stressed_positions
    
    async def _calculate_stressed_metrics(self, stressed_positions: Dict, scenario: StressScenario) -> 'PortfolioMetrics':
        """Calculate portfolio metrics under stress scenario"""
        # Create a temporary analytics instance for stress calculation
        temp_analytics = PortfolioAnalytics(self.risk_manager)
        
        # Calculate stressed P&L attribution
        total_pnl = 0.0
        for position in stressed_positions.values():
            total_pnl += position.get('unrealized_pnl', 0)
            total_pnl -= position.get('slippage', 0)
        
        # Calculate stressed risk metrics
        # Simplified: increase VaR and volatility under stress
        risk_metrics = {
            'var_95': -0.05 * (1 + scenario.volatility_multiplier),
            'var_99': -0.08 * (1 + scenario.volatility_multiplier),
            'expected_shortfall': -0.06 * (1 + scenario.volatility_multiplier),
            'skewness': -0.5,
            'kurtosis': 5.0
        }
        
        # Create stressed metrics object
        from .portfolio_analytics import PortfolioMetrics
        return PortfolioMetrics(
            total_value=sum(pos.get('market_value', 0) for pos in stressed_positions.values()),
            total_pnl=total_pnl,
            pnl_percentage=(total_pnl / sum(pos.get('market_value', 0) for pos in stressed_positions.values()) * 100) if any(pos.get('market_value', 0) for pos in stressed_positions.values()) else 0,
            sharpe_ratio=-1.0,  # Negative under stress
            max_drawdown=-0.3,  # Significant drawdown
            volatility=0.5 * scenario.volatility_multiplier,
            beta=1.2,  # Higher beta under stress
            correlation_matrix=pd.DataFrame(),  # Simplified
            position_concentration={},
            risk_metrics=risk_metrics
        )
    
    def _generate_recommendations(self, scenario: StressScenario, pnl_impact: float, var_impact: float) -> List[str]:
        """Generate recommendations based on stress test results"""
        recommendations = []
        
        if pnl_impact < -0.1:  # More than 10% loss
            recommendations.append("Consider reducing position sizes")
            recommendations.append("Implement tighter stop-loss orders")
        
        if var_impact < -0.05:  # VaR increased significantly
            recommendations.append("Increase hedge ratios")
            recommendations.append("Consider options-based protection")
        
        if scenario.name == "Flash Crash":
            recommendations.append("Set up circuit breakers")
            recommendations.append("Maintain higher cash reserves")
        
        elif scenario.name == "Crypto Winter":
            recommendations.append("Diversify into stablecoins")
            recommendations.append("Consider short-term hedging")
        
        elif scenario.name == "Regulatory Shock":
            recommendations.append("Monitor regulatory developments")
            recommendations.append("Prepare compliance procedures")
        
        elif scenario.name == "Liquidity Crisis":
            recommendations.append("Increase bid-ask spread tolerance")
            recommendations.append("Consider OTC trading")
        
        elif scenario.name == "Black Swan":
            recommendations.append("Implement extreme risk controls")
            recommendations.append("Consider portfolio insurance")
        
        if abs(pnl_impact) > 0.2:  # More than 20% impact
            recommendations.append("Review portfolio allocation")
            recommendations.append("Consider rebalancing strategy")
        
        return recommendations
    
    async def get_stress_test_summary(self, results: List[StressTestResult]) -> Dict:
        """Generate stress test summary"""
        if not results:
            return {"error": "No stress test results available"}
        
        worst_scenario = min(results, key=lambda x: x.pnl_impact)
        best_scenario = max(results, key=lambda x: x.pnl_impact)
        
        avg_pnl_impact = sum(r.pnl_impact for r in results) / len(results)
        avg_var_impact = sum(r.var_impact for r in results) / len(results)
        
        return {
            'total_scenarios': len(results),
            'worst_scenario': {
                'name': worst_scenario.scenario_name,
                'pnl_impact': worst_scenario.pnl_impact,
                'var_impact': worst_scenario.var_impact
            },
            'best_scenario': {
                'name': best_scenario.scenario_name,
                'pnl_impact': best_scenario.pnl_impact,
                'var_impact': best_scenario.var_impact
            },
            'average_impacts': {
                'pnl_impact': avg_pnl_impact,
                'var_impact': avg_var_impact
            },
            'risk_level': self._assess_risk_level(avg_pnl_impact, avg_var_impact),
            'timestamp': datetime.now().isoformat()
        }
    
    def _assess_risk_level(self, avg_pnl_impact: float, avg_var_impact: float) -> str:
        """Assess overall risk level based on stress test results"""
        if avg_pnl_impact < -0.15 or avg_var_impact < -0.08:
            return "HIGH"
        elif avg_pnl_impact < -0.08 or avg_var_impact < -0.05:
            return "MEDIUM"
        else:
            return "LOW" 