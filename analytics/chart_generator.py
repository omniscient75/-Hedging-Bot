import asyncio
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import io
import base64
from loguru import logger

class ChartGenerator:
    """Interactive charts and visualizations for Telegram"""
    
    def __init__(self):
        self.chart_style = {
            'background_color': '#1e1e1e',
            'text_color': '#ffffff',
            'grid_color': '#333333',
            'accent_color': '#00ff88'
        }
        
    async def generate_portfolio_dashboard(self, portfolio_metrics, positions: Dict) -> str:
        """Generate comprehensive portfolio dashboard chart"""
        try:
            # Create subplots
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=('Portfolio Value', 'P&L Attribution', 'Risk Metrics', 'Position Allocation', 'Performance', 'Risk Distribution'),
                specs=[[{"type": "indicator"}, {"type": "pie"}],
                       [{"type": "bar"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "histogram"}]]
            )
            
            # Portfolio Value Indicator
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=portfolio_metrics.total_value,
                    title={'text': "Portfolio Value ($)"},
                    delta={'reference': portfolio_metrics.total_value * 0.9},
                    gauge={
                        'axis': {'range': [None, portfolio_metrics.total_value * 1.2]},
                        'bar': {'color': self.chart_style['accent_color']},
                        'steps': [
                            {'range': [0, portfolio_metrics.total_value * 0.5], 'color': "lightgray"},
                            {'range': [portfolio_metrics.total_value * 0.5, portfolio_metrics.total_value], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': portfolio_metrics.total_value
                        }
                    }
                ),
                row=1, col=1
            )
            
            # P&L Attribution Pie Chart
            pnl_attribution = {
                'Spot P&L': portfolio_metrics.total_pnl * 0.6,
                'Hedge P&L': portfolio_metrics.total_pnl * 0.3,
                'Funding P&L': portfolio_metrics.total_pnl * 0.1
            }
            
            fig.add_trace(
                go.Pie(
                    labels=list(pnl_attribution.keys()),
                    values=list(pnl_attribution.values()),
                    hole=0.4,
                    marker_colors=['#00ff88', '#ff8800', '#0088ff']
                ),
                row=1, col=2
            )
            
            # Risk Metrics Bar Chart
            risk_metrics = {
                'VaR (95%)': abs(portfolio_metrics.risk_metrics.get('var_95', 0)),
                'Max Drawdown': abs(portfolio_metrics.max_drawdown),
                'Volatility': portfolio_metrics.volatility,
                'Sharpe Ratio': portfolio_metrics.sharpe_ratio
            }
            
            fig.add_trace(
                go.Bar(
                    x=list(risk_metrics.keys()),
                    y=list(risk_metrics.values()),
                    marker_color=self.chart_style['accent_color']
                ),
                row=2, col=1
            )
            
            # Position Allocation Bar Chart
            position_values = [pos.get('market_value', 0) for pos in positions.values()]
            position_symbols = list(positions.keys())
            
            fig.add_trace(
                go.Bar(
                    x=position_symbols,
                    y=position_values,
                    marker_color='#ff8800'
                ),
                row=2, col=2
            )
            
            # Performance Scatter (simulated data)
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            performance_data = np.cumsum(np.random.randn(len(dates)) * 0.02)
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=performance_data,
                    mode='lines+markers',
                    name='Portfolio Performance',
                    line=dict(color=self.chart_style['accent_color'])
                ),
                row=3, col=1
            )
            
            # Risk Distribution Histogram
            risk_scores = [pos.get('total_risk_score', 0) for pos in positions.values() if 'total_risk_score' in pos]
            if not risk_scores:
                risk_scores = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
            
            fig.add_trace(
                go.Histogram(
                    x=risk_scores,
                    nbinsx=10,
                    marker_color='#0088ff'
                ),
                row=3, col=2
            )
            
            # Update layout
            fig.update_layout(
                title="Portfolio Analytics Dashboard",
                height=800,
                showlegend=False,
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color'])
            )
            
            # Convert to image
            img_bytes = fig.to_image(format="png", width=800, height=600)
            return self._encode_image(img_bytes)
            
        except Exception as e:
            logger.error(f"Error generating portfolio dashboard: {e}")
            return self._generate_error_chart("Portfolio Dashboard Error")
    
    async def generate_pnl_chart(self, pnl_history: List) -> str:
        """Generate P&L over time chart"""
        try:
            if not pnl_history:
                return self._generate_error_chart("No P&L data available")
            
            # Extract data
            timestamps = [pnl.timestamp for pnl in pnl_history]
            total_pnl = [pnl.total_pnl for pnl in pnl_history]
            spot_pnl = [pnl.spot_pnl for pnl in pnl_history]
            hedge_pnl = [pnl.hedge_pnl for pnl in pnl_history]
            
            fig = go.Figure()
            
            # Add traces
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=total_pnl,
                mode='lines+markers',
                name='Total P&L',
                line=dict(color=self.chart_style['accent_color'], width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=spot_pnl,
                mode='lines',
                name='Spot P&L',
                line=dict(color='#ff8800', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=hedge_pnl,
                mode='lines',
                name='Hedge P&L',
                line=dict(color='#0088ff', width=2)
            ))
            
            # Update layout
            fig.update_layout(
                title="P&L Attribution Over Time",
                xaxis_title="Time",
                yaxis_title="P&L ($)",
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color']),
                legend=dict(
                    bgcolor=self.chart_style['background_color'],
                    bordercolor=self.chart_style['grid_color']
                )
            )
            
            img_bytes = fig.to_image(format="png", width=800, height=400)
            return self._encode_image(img_bytes)
            
        except Exception as e:
            logger.error(f"Error generating P&L chart: {e}")
            return self._generate_error_chart("P&L Chart Error")
    
    async def generate_risk_heatmap(self, correlation_matrix: pd.DataFrame) -> str:
        """Generate correlation heatmap"""
        try:
            if correlation_matrix.empty:
                return self._generate_error_chart("No correlation data available")
            
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                colorscale='RdBu',
                zmid=0
            ))
            
            fig.update_layout(
                title="Position Correlation Heatmap",
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color'])
            )
            
            img_bytes = fig.to_image(format="png", width=600, height=400)
            return self._encode_image(img_bytes)
            
        except Exception as e:
            logger.error(f"Error generating risk heatmap: {e}")
            return self._generate_error_chart("Risk Heatmap Error")
    
    async def generate_stress_test_chart(self, stress_results: List) -> str:
        """Generate stress test results chart"""
        try:
            if not stress_results:
                return self._generate_error_chart("No stress test data available")
            
            scenarios = [result.scenario_name for result in stress_results]
            pnl_impacts = [result.pnl_impact for result in stress_results]
            var_impacts = [result.var_impact for result in stress_results]
            
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('P&L Impact by Scenario', 'VaR Impact by Scenario'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            # P&L Impact
            fig.add_trace(
                go.Bar(
                    x=scenarios,
                    y=pnl_impacts,
                    name='P&L Impact',
                    marker_color=['red' if x < 0 else 'green' for x in pnl_impacts]
                ),
                row=1, col=1
            )
            
            # VaR Impact
            fig.add_trace(
                go.Bar(
                    x=scenarios,
                    y=var_impacts,
                    name='VaR Impact',
                    marker_color=['red' if x < 0 else 'green' for x in var_impacts]
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                title="Stress Test Results",
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color']),
                height=400
            )
            
            img_bytes = fig.to_image(format="png", width=800, height=400)
            return self._encode_image(img_bytes)
            
        except Exception as e:
            logger.error(f"Error generating stress test chart: {e}")
            return self._generate_error_chart("Stress Test Chart Error")
    
    async def generate_performance_chart(self, performance_data: Dict) -> str:
        """Generate performance metrics chart"""
        try:
            metrics = performance_data.get('performance', {})
            
            # Create radar chart for key metrics
            categories = ['Sharpe Ratio', 'Win Rate', 'Profit Factor', 'Max Drawdown', 'Volatility']
            values = [
                metrics.get('sharpe_ratio', 0),
                metrics.get('win_rate', 0) / 100,  # Normalize to 0-1
                min(metrics.get('profit_factor', 0) / 3, 1),  # Normalize
                abs(metrics.get('max_drawdown', 0)),
                min(metrics.get('volatility', 0) / 0.5, 1)  # Normalize
            ]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Performance Metrics',
                line_color=self.chart_style['accent_color']
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=False,
                title="Performance Metrics Radar",
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color'])
            )
            
            img_bytes = fig.to_image(format="png", width=600, height=400)
            return self._encode_image(img_bytes)
            
        except Exception as e:
            logger.error(f"Error generating performance chart: {e}")
            return self._generate_error_chart("Performance Chart Error")
    
    async def generate_cost_analysis_chart(self, cost_data: Dict) -> str:
        """Generate cost analysis chart"""
        try:
            costs = cost_data.get('costs', {})
            
            # Create pie chart for cost breakdown
            cost_breakdown = {
                'Trading Fees': costs.get('total_fees', 0),
                'Slippage': costs.get('total_slippage', 0),
                'Funding Costs': costs.get('funding_costs', 0),
                'Opportunity Costs': costs.get('opportunity_costs', 0)
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=list(cost_breakdown.keys()),
                values=list(cost_breakdown.values()),
                hole=0.3,
                marker_colors=['#ff8800', '#0088ff', '#00ff88', '#ff0088']
            )])
            
            fig.update_layout(
                title="Trading Cost Breakdown",
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color'])
            )
            
            img_bytes = fig.to_image(format="png", width=600, height=400)
            return self._encode_image(img_bytes)
            
        except Exception as e:
            logger.error(f"Error generating cost analysis chart: {e}")
            return self._generate_error_chart("Cost Analysis Chart Error")
    
    def _encode_image(self, img_bytes: bytes) -> str:
        """Encode image bytes to base64 string"""
        try:
            encoded = base64.b64encode(img_bytes).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            return ""
    
    def _generate_error_chart(self, error_message: str) -> str:
        """Generate a simple error chart"""
        try:
            fig = go.Figure()
            fig.add_annotation(
                text=error_message,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=20, color="red")
            )
            fig.update_layout(
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            
            img_bytes = fig.to_image(format="png", width=400, height=300)
            return self._encode_image(img_bytes)
        except Exception as e:
            logger.error(f"Error generating error chart: {e}")
            return ""
    
    async def generate_simple_chart(self, data: Dict, chart_type: str = "bar") -> str:
        """Generate a simple chart based on data"""
        try:
            fig = go.Figure()
            
            if chart_type == "bar":
                fig.add_trace(go.Bar(
                    x=list(data.keys()),
                    y=list(data.values()),
                    marker_color=self.chart_style['accent_color']
                ))
            elif chart_type == "line":
                fig.add_trace(go.Scatter(
                    x=list(data.keys()),
                    y=list(data.values()),
                    mode='lines+markers',
                    line=dict(color=self.chart_style['accent_color'])
                ))
            elif chart_type == "pie":
                fig.add_trace(go.Pie(
                    labels=list(data.keys()),
                    values=list(data.values())
                ))
            
            fig.update_layout(
                plot_bgcolor=self.chart_style['background_color'],
                paper_bgcolor=self.chart_style['background_color'],
                font=dict(color=self.chart_style['text_color'])
            )
            
            img_bytes = fig.to_image(format="png", width=600, height=400)
            return self._encode_image(img_bytes)
            
        except Exception as e:
            logger.error(f"Error generating simple chart: {e}")
            return self._generate_error_chart("Chart Generation Error") 