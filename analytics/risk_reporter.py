import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger

@dataclass
class RiskReport:
    """Comprehensive risk report"""
    report_id: str
    timestamp: datetime
    portfolio_value: float
    total_risk_metrics: Dict[str, float]
    position_risks: Dict[str, Dict[str, float]]
    correlation_analysis: Dict[str, float]
    stress_test_results: Dict[str, float]
    recommendations: List[str]
    risk_level: str

class RiskReporter:
    """Custom risk report generation"""
    
    def __init__(self, risk_manager, portfolio_analytics, stress_tester):
        self.risk_manager = risk_manager
        self.portfolio_analytics = portfolio_analytics
        self.stress_tester = stress_tester
        self.report_history: List[RiskReport] = []
        
    async def generate_risk_report(self, report_type: str = "comprehensive") -> RiskReport:
        """Generate custom risk report"""
        report_id = f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get current portfolio metrics
        portfolio_metrics = await self.portfolio_analytics.calculate_portfolio_metrics()
        positions = await self.risk_manager.get_all_positions()
        
        # Calculate total risk metrics
        total_risk_metrics = await self._calculate_total_risk_metrics(portfolio_metrics)
        
        # Calculate position-specific risks
        position_risks = await self._calculate_position_risks(positions)
        
        # Calculate correlation analysis
        correlation_analysis = await self._calculate_correlation_analysis(positions)
        
        # Run stress tests
        stress_test_results = await self._run_stress_tests()
        
        # Generate recommendations
        recommendations = self._generate_risk_recommendations(
            total_risk_metrics, position_risks, stress_test_results
        )
        
        # Determine overall risk level
        risk_level = self._determine_risk_level(total_risk_metrics, stress_test_results)
        
        report = RiskReport(
            report_id=report_id,
            timestamp=datetime.now(),
            portfolio_value=portfolio_metrics.total_value,
            total_risk_metrics=total_risk_metrics,
            position_risks=position_risks,
            correlation_analysis=correlation_analysis,
            stress_test_results=stress_test_results,
            recommendations=recommendations,
            risk_level=risk_level
        )
        
        self.report_history.append(report)
        return report
    
    async def _calculate_total_risk_metrics(self, portfolio_metrics) -> Dict[str, float]:
        """Calculate comprehensive risk metrics"""
        return {
            'var_95': portfolio_metrics.risk_metrics.get('var_95', 0),
            'var_99': portfolio_metrics.risk_metrics.get('var_99', 0),
            'expected_shortfall': portfolio_metrics.risk_metrics.get('expected_shortfall', 0),
            'max_drawdown': portfolio_metrics.max_drawdown,
            'volatility': portfolio_metrics.volatility,
            'sharpe_ratio': portfolio_metrics.sharpe_ratio,
            'beta': portfolio_metrics.beta,
            'skewness': portfolio_metrics.risk_metrics.get('skewness', 0),
            'kurtosis': portfolio_metrics.risk_metrics.get('kurtosis', 0),
            'concentration_risk': self._calculate_concentration_risk(portfolio_metrics.position_concentration),
            'liquidity_risk': self._calculate_liquidity_risk(portfolio_metrics),
            'leverage_risk': self._calculate_leverage_risk(portfolio_metrics)
        }
    
    async def _calculate_position_risks(self, positions: Dict) -> Dict[str, Dict[str, float]]:
        """Calculate risk metrics for each position"""
        position_risks = {}
        
        for symbol, position in positions.items():
            # Calculate position-specific risk metrics
            market_value = position.get('market_value', 0)
            unrealized_pnl = position.get('unrealized_pnl', 0)
            quantity = position.get('quantity', 0)
            current_price = position.get('current_price', 0)
            
            # Calculate various risk metrics
            price_risk = self._calculate_price_risk(position)
            liquidity_risk = self._calculate_position_liquidity_risk(position)
            concentration_risk = self._calculate_position_concentration_risk(position, positions)
            leverage_risk = self._calculate_position_leverage_risk(position)
            
            position_risks[symbol] = {
                'market_value': market_value,
                'unrealized_pnl': unrealized_pnl,
                'price_risk': price_risk,
                'liquidity_risk': liquidity_risk,
                'concentration_risk': concentration_risk,
                'leverage_risk': leverage_risk,
                'total_risk_score': (price_risk + liquidity_risk + concentration_risk + leverage_risk) / 4
            }
        
        return position_risks
    
    async def _calculate_correlation_analysis(self, positions: Dict) -> Dict[str, float]:
        """Calculate correlation analysis between positions"""
        if len(positions) < 2:
            return {}
        
        symbols = list(positions.keys())
        correlations = {}
        
        # Calculate pairwise correlations
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols[i+1:], i+1):
                pair_key = f"{symbol1}_{symbol2}"
                
                # Simplified correlation calculation
                # In a real implementation, you'd use historical price data
                correlation = self._estimate_correlation(symbol1, symbol2)
                correlations[pair_key] = correlation
        
        return correlations
    
    async def _run_stress_tests(self) -> Dict[str, float]:
        """Run stress tests and return results"""
        try:
            stress_results = await self.stress_tester.run_stress_test()
            
            # Extract key metrics from stress test results
            results = {}
            for result in stress_results:
                results[f"{result.scenario_name}_pnl_impact"] = result.pnl_impact
                results[f"{result.scenario_name}_var_impact"] = result.var_impact
                results[f"{result.scenario_name}_max_drawdown_impact"] = result.max_drawdown_impact
            
            return results
        except Exception as e:
            logger.error(f"Error running stress tests: {e}")
            return {}
    
    def _calculate_concentration_risk(self, position_concentration: Dict[str, float]) -> float:
        """Calculate concentration risk using Herfindahl index"""
        if not position_concentration:
            return 0.0
        
        # Herfindahl-Hirschman Index
        hhi = sum(weight ** 2 for weight in position_concentration.values())
        
        # Normalize to 0-1 scale
        return min(hhi, 1.0)
    
    def _calculate_liquidity_risk(self, portfolio_metrics) -> float:
        """Calculate portfolio liquidity risk"""
        # Simplified liquidity risk calculation
        # In practice, this would consider bid-ask spreads, market depth, etc.
        return 0.1  # Placeholder
    
    def _calculate_leverage_risk(self, portfolio_metrics) -> float:
        """Calculate leverage risk"""
        # Simplified leverage risk calculation
        # In practice, this would consider margin requirements, leverage ratios, etc.
        return 0.05  # Placeholder
    
    def _calculate_price_risk(self, position: Dict) -> float:
        """Calculate price risk for a position"""
        # Simplified price risk calculation
        # In practice, this would consider volatility, delta, gamma, etc.
        return 0.2  # Placeholder
    
    def _calculate_position_liquidity_risk(self, position: Dict) -> float:
        """Calculate liquidity risk for a position"""
        # Simplified liquidity risk calculation
        # In practice, this would consider trading volume, bid-ask spread, etc.
        return 0.15  # Placeholder
    
    def _calculate_position_concentration_risk(self, position: Dict, all_positions: Dict) -> float:
        """Calculate concentration risk for a position"""
        position_value = position.get('market_value', 0)
        total_value = sum(pos.get('market_value', 0) for pos in all_positions.values())
        
        if total_value == 0:
            return 0.0
        
        concentration = position_value / total_value
        return min(concentration, 1.0)
    
    def _calculate_position_leverage_risk(self, position: Dict) -> float:
        """Calculate leverage risk for a position"""
        # Simplified leverage risk calculation
        # In practice, this would consider margin requirements, leverage ratios, etc.
        return 0.1  # Placeholder
    
    def _estimate_correlation(self, symbol1: str, symbol2: str) -> float:
        """Estimate correlation between two symbols"""
        # Simplified correlation estimation
        # In practice, this would use historical price data
        
        # Common crypto pairs tend to be highly correlated
        if 'BTC' in symbol1 and 'BTC' in symbol2:
            return 0.9
        elif 'ETH' in symbol1 and 'ETH' in symbol2:
            return 0.8
        elif 'USDT' in symbol1 and 'USDT' in symbol2:
            return 0.7
        else:
            return 0.5  # Default correlation
    
    def _generate_risk_recommendations(self, total_risk_metrics: Dict, 
                                     position_risks: Dict, 
                                     stress_test_results: Dict) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        # Portfolio-level recommendations
        if total_risk_metrics.get('var_95', 0) < -0.05:
            recommendations.append("Consider reducing portfolio risk exposure")
            recommendations.append("Implement tighter stop-loss orders")
        
        if total_risk_metrics.get('concentration_risk', 0) > 0.3:
            recommendations.append("Diversify portfolio to reduce concentration risk")
            recommendations.append("Consider rebalancing positions")
        
        if total_risk_metrics.get('volatility', 0) > 0.4:
            recommendations.append("High volatility detected - consider hedging strategies")
            recommendations.append("Review position sizing")
        
        # Position-specific recommendations
        high_risk_positions = []
        for symbol, risks in position_risks.items():
            if risks.get('total_risk_score', 0) > 0.7:
                high_risk_positions.append(symbol)
        
        if high_risk_positions:
            recommendations.append(f"High-risk positions detected: {', '.join(high_risk_positions)}")
            recommendations.append("Consider reducing exposure to high-risk positions")
        
        # Stress test recommendations
        worst_stress_impact = min(stress_test_results.values()) if stress_test_results else 0
        if worst_stress_impact < -0.2:
            recommendations.append("Stress tests indicate significant downside risk")
            recommendations.append("Consider implementing protective strategies")
        
        # General recommendations
        if len(recommendations) < 3:
            recommendations.append("Monitor risk metrics regularly")
            recommendations.append("Maintain adequate liquidity reserves")
        
        return recommendations
    
    def _determine_risk_level(self, total_risk_metrics: Dict, stress_test_results: Dict) -> str:
        """Determine overall risk level"""
        risk_score = 0.0
        
        # Factor in VaR
        var_95 = abs(total_risk_metrics.get('var_95', 0))
        if var_95 > 0.05:
            risk_score += 0.3
        elif var_95 > 0.03:
            risk_score += 0.2
        
        # Factor in concentration risk
        concentration_risk = total_risk_metrics.get('concentration_risk', 0)
        if concentration_risk > 0.5:
            risk_score += 0.3
        elif concentration_risk > 0.3:
            risk_score += 0.2
        
        # Factor in volatility
        volatility = total_risk_metrics.get('volatility', 0)
        if volatility > 0.5:
            risk_score += 0.2
        elif volatility > 0.3:
            risk_score += 0.1
        
        # Factor in stress test results
        if stress_test_results:
            worst_impact = min(stress_test_results.values())
            if worst_impact < -0.3:
                risk_score += 0.2
            elif worst_impact < -0.2:
                risk_score += 0.1
        
        # Determine risk level
        if risk_score >= 0.7:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_risk_report_summary(self, report: RiskReport) -> Dict:
        """Get summary of risk report"""
        return {
            'report_id': report.report_id,
            'timestamp': report.timestamp.isoformat(),
            'portfolio_value': report.portfolio_value,
            'risk_level': report.risk_level,
            'key_risk_metrics': {
                'var_95': report.total_risk_metrics.get('var_95', 0),
                'max_drawdown': report.total_risk_metrics.get('max_drawdown', 0),
                'volatility': report.total_risk_metrics.get('volatility', 0),
                'concentration_risk': report.total_risk_metrics.get('concentration_risk', 0)
            },
            'high_risk_positions': [
                symbol for symbol, risks in report.position_risks.items()
                if risks.get('total_risk_score', 0) > 0.7
            ],
            'recommendations_count': len(report.recommendations),
            'stress_test_scenarios': len([k for k in report.stress_test_results.keys() if 'pnl_impact' in k])
        }
    
    def get_risk_report_history(self, limit: int = 10) -> List[Dict]:
        """Get history of risk reports"""
        recent_reports = sorted(self.report_history, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        return [
            {
                'report_id': report.report_id,
                'timestamp': report.timestamp.isoformat(),
                'risk_level': report.risk_level,
                'portfolio_value': report.portfolio_value,
                'key_metrics': {
                    'var_95': report.total_risk_metrics.get('var_95', 0),
                    'volatility': report.total_risk_metrics.get('volatility', 0),
                    'concentration_risk': report.total_risk_metrics.get('concentration_risk', 0)
                }
            }
            for report in recent_reports
        ] 