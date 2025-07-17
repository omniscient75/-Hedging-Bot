import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from .portfolio_analytics import PortfolioAnalytics
from .stress_testing import StressTester
from .performance_tracker import PerformanceTracker
from .risk_reporter import RiskReporter
from .chart_generator import ChartGenerator

class AnalyticsManager:
    """Manager for all analytics components"""
    
    def __init__(self, risk_manager):
        self.risk_manager = risk_manager
        
        # Initialize analytics components
        self.portfolio_analytics = PortfolioAnalytics(risk_manager)
        self.stress_tester = StressTester(risk_manager, self.portfolio_analytics)
        self.performance_tracker = PerformanceTracker()
        self.risk_reporter = RiskReporter(risk_manager, self.portfolio_analytics, self.stress_tester)
        self.chart_generator = ChartGenerator()
        
        # Analytics state
        self.analytics_enabled = True
        self.update_interval = 60  # seconds
        
    async def start_analytics(self):
        """Start all analytics services"""
        logger.info("Starting analytics manager...")
        
        if self.analytics_enabled:
            # Start real-time analytics
            asyncio.create_task(self._run_real_time_analytics())
            logger.info("Analytics manager started successfully")
    
    async def _run_real_time_analytics(self):
        """Run real-time analytics updates"""
        while self.analytics_enabled:
            try:
                # Update portfolio analytics
                await self.portfolio_analytics.calculate_portfolio_metrics()
                
                # Update performance tracking
                self.performance_tracker.calculate_performance_metrics("all")
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in real-time analytics: {e}")
                await asyncio.sleep(10)
    
    async def get_comprehensive_analytics(self) -> Dict:
        """Get comprehensive analytics summary"""
        try:
            # Get all analytics data
            portfolio_metrics = await self.portfolio_analytics.calculate_portfolio_metrics()
            performance_summary = self.performance_tracker.get_performance_summary("all")
            risk_report = await self.risk_reporter.generate_risk_report()
            cost_analysis = self.performance_tracker.calculate_cost_analysis("all")
            
            return {
                'portfolio': {
                    'total_value': portfolio_metrics.total_value,
                    'total_pnl': portfolio_metrics.total_pnl,
                    'pnl_percentage': portfolio_metrics.pnl_percentage,
                    'sharpe_ratio': portfolio_metrics.sharpe_ratio,
                    'max_drawdown': portfolio_metrics.max_drawdown,
                    'volatility': portfolio_metrics.volatility,
                    'risk_metrics': portfolio_metrics.risk_metrics
                },
                'performance': performance_summary,
                'risk': {
                    'risk_level': risk_report.risk_level,
                    'key_metrics': risk_report.total_risk_metrics,
                    'recommendations': risk_report.recommendations
                },
                'costs': {
                    'total_costs': cost_analysis.total_costs,
                    'cost_percentage': cost_analysis.cost_percentage,
                    'fee_breakdown': cost_analysis.fee_breakdown
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive analytics: {e}")
            return {'error': str(e)}
    
    async def generate_analytics_report(self, report_type: str = "comprehensive") -> Dict:
        """Generate analytics report based on type"""
        try:
            if report_type == "portfolio":
                portfolio_metrics = await self.portfolio_analytics.calculate_portfolio_metrics()
                return {
                    'type': 'portfolio',
                    'data': await self.portfolio_analytics.get_analytics_summary(),
                    'timestamp': datetime.now().isoformat()
                }
                
            elif report_type == "performance":
                performance_summary = self.performance_tracker.get_performance_summary("all")
                return {
                    'type': 'performance',
                    'data': performance_summary,
                    'timestamp': performance_summary.get('timestamp', '')
                }
                
            elif report_type == "risk":
                risk_report = await self.risk_reporter.generate_risk_report()
                return {
                    'type': 'risk',
                    'data': self.risk_reporter.get_risk_report_summary(risk_report),
                    'timestamp': risk_report.timestamp.isoformat()
                }
                
            elif report_type == "stress_test":
                stress_results = await self.stress_tester.run_stress_test()
                stress_summary = await self.stress_tester.get_stress_test_summary(stress_results)
                return {
                    'type': 'stress_test',
                    'data': stress_summary,
                    'timestamp': stress_results[0].timestamp.isoformat() if stress_results else ''
                }
                
            elif report_type == "cost":
                cost_analysis = self.performance_tracker.calculate_cost_analysis("all")
                return {
                    'type': 'cost',
                    'data': {
                        'total_costs': cost_analysis.total_costs,
                        'cost_percentage': cost_analysis.cost_percentage,
                        'fee_breakdown': cost_analysis.fee_breakdown,
                        'slippage_breakdown': cost_analysis.slippage_breakdown
                    },
                    'timestamp': cost_analysis.timestamp.isoformat() if hasattr(cost_analysis, 'timestamp') else ''
                }
                
            else:  # comprehensive
                return await self.get_comprehensive_analytics()
                
        except Exception as e:
            logger.error(f"Error generating {report_type} report: {e}")
            return {'error': f"Error generating {report_type} report: {str(e)}"}
    
    async def get_chart(self, chart_type: str, data: Dict = None) -> str:
        """Generate chart based on type"""
        try:
            if chart_type == "portfolio_dashboard":
                portfolio_metrics = await self.portfolio_analytics.calculate_portfolio_metrics()
                positions = await self.risk_manager.get_all_positions()
                return await self.chart_generator.generate_portfolio_dashboard(portfolio_metrics, positions)
                
            elif chart_type == "pnl_chart":
                return await self.chart_generator.generate_pnl_chart(self.portfolio_analytics.pnl_history)
                
            elif chart_type == "risk_heatmap":
                portfolio_metrics = await self.portfolio_analytics.calculate_portfolio_metrics()
                return await self.chart_generator.generate_risk_heatmap(portfolio_metrics.correlation_matrix)
                
            elif chart_type == "stress_test":
                stress_results = await self.stress_tester.run_stress_test()
                return await self.chart_generator.generate_stress_test_chart(stress_results)
                
            elif chart_type == "performance":
                performance_data = self.performance_tracker.get_performance_summary("all")
                return await self.chart_generator.generate_performance_chart(performance_data)
                
            elif chart_type == "cost_analysis":
                cost_analysis = self.performance_tracker.calculate_cost_analysis("all")
                return await self.chart_generator.generate_cost_analysis_chart({
                    'costs': {
                        'total_fees': cost_analysis.total_fees,
                        'total_slippage': cost_analysis.total_slippage,
                        'funding_costs': cost_analysis.funding_costs,
                        'opportunity_costs': cost_analysis.opportunity_costs
                    }
                })
                
            elif chart_type == "simple" and data:
                return await self.chart_generator.generate_simple_chart(data)
                
            else:
                logger.error(f"Unknown chart type: {chart_type}")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating {chart_type} chart: {e}")
            return ""
    
    async def add_trade_record(self, trade_data: Dict):
        """Add a trade record to performance tracking"""
        try:
            from .performance_tracker import TradeRecord
            from datetime import datetime
            
            trade = TradeRecord(
                symbol=trade_data.get('symbol', ''),
                side=trade_data.get('side', ''),
                quantity=trade_data.get('quantity', 0),
                price=trade_data.get('price', 0),
                timestamp=trade_data.get('timestamp', datetime.now()),
                fees=trade_data.get('fees', 0),
                slippage=trade_data.get('slippage', 0),
                exchange=trade_data.get('exchange', ''),
                order_type=trade_data.get('order_type', ''),
                trade_id=trade_data.get('trade_id', '')
            )
            
            self.performance_tracker.add_trade(trade)
            logger.info(f"Added trade record: {trade.symbol} {trade.side} {trade.quantity}")
            
        except Exception as e:
            logger.error(f"Error adding trade record: {e}")
    
    def get_analytics_status(self) -> Dict:
        """Get analytics system status"""
        return {
            'enabled': self.analytics_enabled,
            'update_interval': self.update_interval,
            'components': {
                'portfolio_analytics': True,
                'stress_tester': True,
                'performance_tracker': True,
                'risk_reporter': True,
                'chart_generator': True
            },
            'data_points': {
                'portfolio_history': len(self.portfolio_analytics.portfolio_history),
                'pnl_history': len(self.portfolio_analytics.pnl_history),
                'trades': len(self.performance_tracker.trades),
                'risk_reports': len(self.risk_reporter.report_history)
            }
        }
    
    async def stop_analytics(self):
        """Stop analytics services"""
        logger.info("Stopping analytics manager...")
        self.analytics_enabled = False
        logger.info("Analytics manager stopped") 