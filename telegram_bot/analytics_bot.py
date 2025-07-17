import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from typing import Dict, List, Optional
from loguru import logger
import base64
import io

class AnalyticsBot:
    """Enhanced Telegram bot with comprehensive analytics features"""
    
    def __init__(self, risk_manager, analytics_manager):
        self.risk_manager = risk_manager
        self.analytics_manager = analytics_manager
        self.chart_generator = analytics_manager.chart_generator
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command with analytics options"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Portfolio Analytics", callback_data="portfolio_analytics"),
                InlineKeyboardButton("📈 Performance Report", callback_data="performance_report")
            ],
            [
                InlineKeyboardButton("⚠️ Risk Analysis", callback_data="risk_analysis"),
                InlineKeyboardButton("🧪 Stress Testing", callback_data="stress_testing")
            ],
            [
                InlineKeyboardButton("💰 Cost Analysis", callback_data="cost_analysis"),
                InlineKeyboardButton("📋 Custom Report", callback_data="custom_report")
            ],
            [
                InlineKeyboardButton("🔄 Real-time Monitor", callback_data="real_time_monitor"),
                InlineKeyboardButton("📱 Dashboard", callback_data="dashboard")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 **Crypto Hedging Bot - Analytics Dashboard**\n\n"
            "Welcome to the comprehensive analytics system!\n\n"
            "**Available Features:**\n"
            "• 📊 Real-time portfolio analytics\n"
            "• 📈 Historical performance tracking\n"
            "• ⚠️ Risk analysis and stress testing\n"
            "• 💰 Cost analysis and optimization\n"
            "• 📋 Custom report generation\n"
            "• 📱 Interactive visualizations\n\n"
            "Select an option below to get started:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def portfolio_analytics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Portfolio analytics command"""
        try:
            # Get portfolio metrics
            portfolio_metrics = await self.analytics_manager.portfolio_analytics.calculate_portfolio_metrics()
            positions = await self.risk_manager.get_all_positions()
            
            # Generate portfolio dashboard chart
            chart_data = await self.chart_generator.generate_portfolio_dashboard(portfolio_metrics, positions)
            
            # Create detailed analytics message
            message = self._format_portfolio_analytics_message(portfolio_metrics, positions)
            
            # Send message with chart
            if chart_data:
                await update.message.reply_photo(
                    photo=chart_data,
                    caption=message,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error in portfolio analytics: {e}")
            await update.message.reply_text("❌ Error generating portfolio analytics. Please try again.")
    
    async def performance_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Performance report command"""
        try:
            # Get performance data
            performance_data = self.analytics_manager.performance_tracker.get_performance_summary("all")
            
            # Generate performance chart
            chart_data = await self.chart_generator.generate_performance_chart(performance_data)
            
            # Create performance message
            message = self._format_performance_message(performance_data)
            
            # Send message with chart
            if chart_data:
                await update.message.reply_photo(
                    photo=chart_data,
                    caption=message,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error in performance report: {e}")
            await update.message.reply_text("❌ Error generating performance report. Please try again.")
    
    async def risk_analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Risk analysis command"""
        try:
            # Generate risk report
            risk_report = await self.analytics_manager.risk_reporter.generate_risk_report()
            
            # Generate risk heatmap
            chart_data = await self.chart_generator.generate_risk_heatmap(risk_report.correlation_matrix)
            
            # Create risk analysis message
            message = self._format_risk_analysis_message(risk_report)
            
            # Send message with chart
            if chart_data:
                await update.message.reply_photo(
                    photo=chart_data,
                    caption=message,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error in risk analysis: {e}")
            await update.message.reply_text("❌ Error generating risk analysis. Please try again.")
    
    async def stress_testing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stress testing command"""
        try:
            # Run stress tests
            stress_results = await self.analytics_manager.stress_tester.run_stress_test()
            
            # Generate stress test chart
            chart_data = await self.chart_generator.generate_stress_test_chart(stress_results)
            
            # Create stress test message
            message = self._format_stress_test_message(stress_results)
            
            # Send message with chart
            if chart_data:
                await update.message.reply_photo(
                    photo=chart_data,
                    caption=message,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error in stress testing: {e}")
            await update.message.reply_text("❌ Error running stress tests. Please try again.")
    
    async def cost_analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cost analysis command"""
        try:
            # Get cost analysis
            cost_analysis = self.analytics_manager.performance_tracker.calculate_cost_analysis("all")
            
            # Generate cost analysis chart
            chart_data = await self.chart_generator.generate_cost_analysis_chart({
                'costs': {
                    'total_fees': cost_analysis.total_fees,
                    'total_slippage': cost_analysis.total_slippage,
                    'funding_costs': cost_analysis.funding_costs,
                    'opportunity_costs': cost_analysis.opportunity_costs
                }
            })
            
            # Create cost analysis message
            message = self._format_cost_analysis_message(cost_analysis)
            
            # Send message with chart
            if chart_data:
                await update.message.reply_photo(
                    photo=chart_data,
                    caption=message,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error in cost analysis: {e}")
            await update.message.reply_text("❌ Error generating cost analysis. Please try again.")
    
    async def custom_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Custom report command with options"""
        keyboard = [
            [
                InlineKeyboardButton("📊 P&L Attribution", callback_data="custom_pnl"),
                InlineKeyboardButton("📈 Performance Metrics", callback_data="custom_performance")
            ],
            [
                InlineKeyboardButton("⚠️ Risk Metrics", callback_data="custom_risk"),
                InlineKeyboardButton("💰 Cost Breakdown", callback_data="custom_cost")
            ],
            [
                InlineKeyboardButton("📋 Full Report", callback_data="custom_full"),
                InlineKeyboardButton("🔄 Real-time Data", callback_data="custom_realtime")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 **Custom Report Generator**\n\n"
            "Select the type of report you'd like to generate:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Interactive dashboard command"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Portfolio Overview", callback_data="dashboard_portfolio"),
                InlineKeyboardButton("📈 Performance Chart", callback_data="dashboard_performance")
            ],
            [
                InlineKeyboardButton("⚠️ Risk Dashboard", callback_data="dashboard_risk"),
                InlineKeyboardButton("💰 Cost Dashboard", callback_data="dashboard_cost")
            ],
            [
                InlineKeyboardButton("🔄 Refresh Data", callback_data="dashboard_refresh"),
                InlineKeyboardButton("📱 Full Dashboard", callback_data="dashboard_full")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📱 **Interactive Analytics Dashboard**\n\n"
            "Choose a dashboard view:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        try:
            if query.data == "portfolio_analytics":
                await self.portfolio_analytics_command(update, context)
            elif query.data == "performance_report":
                await self.performance_report_command(update, context)
            elif query.data == "risk_analysis":
                await self.risk_analysis_command(update, context)
            elif query.data == "stress_testing":
                await self.stress_testing_command(update, context)
            elif query.data == "cost_analysis":
                await self.cost_analysis_command(update, context)
            elif query.data == "custom_report":
                await self.custom_report_command(update, context)
            elif query.data == "dashboard":
                await self.dashboard_command(update, context)
            elif query.data.startswith("custom_"):
                await self._handle_custom_report(query, context)
            elif query.data.startswith("dashboard_"):
                await self._handle_dashboard(query, context)
            else:
                await query.edit_message_text("❌ Unknown command. Please try again.")
                
        except Exception as e:
            logger.error(f"Error in button callback: {e}")
            await query.edit_message_text("❌ Error processing request. Please try again.")
    
    async def _handle_custom_report(self, query, context):
        """Handle custom report generation"""
        report_type = query.data.replace("custom_", "")
        
        try:
            if report_type == "pnl":
                # Generate P&L attribution chart
                pnl_history = self.analytics_manager.portfolio_analytics.pnl_history
                chart_data = await self.chart_generator.generate_pnl_chart(pnl_history)
                message = "📊 **P&L Attribution Report**\n\nGenerated P&L attribution chart."
                
            elif report_type == "performance":
                # Generate performance metrics
                performance_data = self.analytics_manager.performance_tracker.get_performance_summary("all")
                chart_data = await self.chart_generator.generate_performance_chart(performance_data)
                message = "📈 **Performance Metrics Report**\n\nGenerated performance analysis."
                
            elif report_type == "risk":
                # Generate risk report
                risk_report = await self.analytics_manager.risk_reporter.generate_risk_report()
                message = self._format_risk_analysis_message(risk_report)
                chart_data = None
                
            elif report_type == "cost":
                # Generate cost analysis
                cost_analysis = self.analytics_manager.performance_tracker.calculate_cost_analysis("all")
                chart_data = await self.chart_generator.generate_cost_analysis_chart({
                    'costs': {
                        'total_fees': cost_analysis.total_fees,
                        'total_slippage': cost_analysis.total_slippage,
                        'funding_costs': cost_analysis.funding_costs,
                        'opportunity_costs': cost_analysis.opportunity_costs
                    }
                })
                message = self._format_cost_analysis_message(cost_analysis)
                
            elif report_type == "full":
                # Generate comprehensive report
                message = await self._generate_comprehensive_report()
                chart_data = None
                
            elif report_type == "realtime":
                # Generate real-time report
                message = await self._generate_realtime_report()
                chart_data = None
                
            else:
                await query.edit_message_text("❌ Unknown report type.")
                return
            
            # Send the report
            if chart_data:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=chart_data,
                    caption=message,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error generating custom report: {e}")
            await query.edit_message_text("❌ Error generating report. Please try again.")
    
    async def _handle_dashboard(self, query, context):
        """Handle dashboard views"""
        dashboard_type = query.data.replace("dashboard_", "")
        
        try:
            if dashboard_type == "portfolio":
                # Portfolio overview dashboard
                portfolio_metrics = await self.analytics_manager.portfolio_analytics.calculate_portfolio_metrics()
                positions = await self.risk_manager.get_all_positions()
                chart_data = await self.chart_generator.generate_portfolio_dashboard(portfolio_metrics, positions)
                message = "📊 **Portfolio Overview Dashboard**"
                
            elif dashboard_type == "performance":
                # Performance dashboard
                performance_data = self.analytics_manager.performance_tracker.get_performance_summary("all")
                chart_data = await self.chart_generator.generate_performance_chart(performance_data)
                message = "📈 **Performance Dashboard**"
                
            elif dashboard_type == "risk":
                # Risk dashboard
                risk_report = await self.analytics_manager.risk_reporter.generate_risk_report()
                chart_data = await self.chart_generator.generate_risk_heatmap(risk_report.correlation_matrix)
                message = "⚠️ **Risk Dashboard**"
                
            elif dashboard_type == "cost":
                # Cost dashboard
                cost_analysis = self.analytics_manager.performance_tracker.calculate_cost_analysis("all")
                chart_data = await self.chart_generator.generate_cost_analysis_chart({
                    'costs': {
                        'total_fees': cost_analysis.total_fees,
                        'total_slippage': cost_analysis.total_slippage,
                        'funding_costs': cost_analysis.funding_costs,
                        'opportunity_costs': cost_analysis.opportunity_costs
                    }
                })
                message = "💰 **Cost Analysis Dashboard**"
                
            elif dashboard_type == "refresh":
                # Refresh data
                await self.analytics_manager.portfolio_analytics.calculate_portfolio_metrics()
                message = "🔄 **Data Refreshed**\n\nAll analytics data has been updated."
                chart_data = None
                
            elif dashboard_type == "full":
                # Full dashboard
                portfolio_metrics = await self.analytics_manager.portfolio_analytics.calculate_portfolio_metrics()
                positions = await self.risk_manager.get_all_positions()
                chart_data = await self.chart_generator.generate_portfolio_dashboard(portfolio_metrics, positions)
                message = "📱 **Full Analytics Dashboard**"
                
            else:
                await query.edit_message_text("❌ Unknown dashboard type.")
                return
            
            # Send the dashboard
            if chart_data:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=chart_data,
                    caption=message,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            await query.edit_message_text("❌ Error generating dashboard. Please try again.")
    
    def _format_portfolio_analytics_message(self, portfolio_metrics, positions: Dict) -> str:
        """Format portfolio analytics message"""
        return (
            "📊 **Portfolio Analytics Dashboard**\n\n"
            f"💰 **Portfolio Value:** ${portfolio_metrics.total_value:,.2f}\n"
            f"📈 **Total P&L:** ${portfolio_metrics.total_pnl:,.2f} ({portfolio_metrics.pnl_percentage:.2f}%)\n"
            f"⚡ **Sharpe Ratio:** {portfolio_metrics.sharpe_ratio:.3f}\n"
            f"📉 **Max Drawdown:** {portfolio_metrics.max_drawdown:.2%}\n"
            f"📊 **Volatility:** {portfolio_metrics.volatility:.2%}\n\n"
            f"📋 **Positions:** {len(positions)}\n"
            f"⚠️ **Risk Level:** {self._get_risk_level(portfolio_metrics)}\n\n"
            "🔄 *Data updated in real-time*"
        )
    
    def _format_performance_message(self, performance_data: Dict) -> str:
        """Format performance message"""
        perf = performance_data.get('performance', {})
        costs = performance_data.get('costs', {})
        
        return (
            "📈 **Performance Report**\n\n"
            f"💰 **Total Return:** ${perf.get('total_return', 0):,.2f}\n"
            f"⚡ **Sharpe Ratio:** {perf.get('sharpe_ratio', 0):.3f}\n"
            f"📉 **Max Drawdown:** {perf.get('max_drawdown', 0):.2%}\n"
            f"📊 **Volatility:** {perf.get('volatility', 0):.2%}\n"
            f"🎯 **Win Rate:** {perf.get('win_rate', 0):.1f}%\n"
            f"📊 **Profit Factor:** {perf.get('profit_factor', 0):.2f}\n"
            f"📈 **Total Trades:** {perf.get('total_trades', 0)}\n\n"
            f"💸 **Total Costs:** ${costs.get('total_costs', 0):,.2f}\n"
            f"📊 **Cost %:** {costs.get('cost_percentage', 0):.2f}%\n\n"
            "📅 *Historical performance data*"
        )
    
    def _format_risk_analysis_message(self, risk_report) -> str:
        """Format risk analysis message"""
        return (
            "⚠️ **Risk Analysis Report**\n\n"
            f"📊 **Risk Level:** {risk_report.risk_level}\n"
            f"💰 **Portfolio Value:** ${risk_report.portfolio_value:,.2f}\n\n"
            f"📉 **VaR (95%):** {risk_report.total_risk_metrics.get('var_95', 0):.2%}\n"
            f"📉 **VaR (99%):** {risk_report.total_risk_metrics.get('var_99', 0):.2%}\n"
            f"📊 **Max Drawdown:** {risk_report.total_risk_metrics.get('max_drawdown', 0):.2%}\n"
            f"📈 **Volatility:** {risk_report.total_risk_metrics.get('volatility', 0):.2%}\n"
            f"📊 **Concentration Risk:** {risk_report.total_risk_metrics.get('concentration_risk', 0):.2%}\n\n"
            f"📋 **High-Risk Positions:** {len([p for p in risk_report.position_risks.values() if p.get('total_risk_score', 0) > 0.7])}\n"
            f"💡 **Recommendations:** {len(risk_report.recommendations)}\n\n"
            "🔄 *Risk metrics updated in real-time*"
        )
    
    def _format_stress_test_message(self, stress_results: List) -> str:
        """Format stress test message"""
        if not stress_results:
            return "❌ No stress test results available."
        
        worst_scenario = min(stress_results, key=lambda x: x.pnl_impact)
        best_scenario = max(stress_results, key=lambda x: x.pnl_impact)
        
        return (
            "🧪 **Stress Test Results**\n\n"
            f"📊 **Scenarios Tested:** {len(stress_results)}\n\n"
            f"⚠️ **Worst Scenario:** {worst_scenario.scenario_name}\n"
            f"📉 **P&L Impact:** {worst_scenario.pnl_impact:.2%}\n"
            f"📊 **VaR Impact:** {worst_scenario.var_impact:.2%}\n\n"
            f"✅ **Best Scenario:** {best_scenario.scenario_name}\n"
            f"📈 **P&L Impact:** {best_scenario.pnl_impact:.2%}\n\n"
            f"💡 **Recommendations:** {len(worst_scenario.recommendations)}\n\n"
            "🔄 *Stress testing completed*"
        )
    
    def _format_cost_analysis_message(self, cost_analysis) -> str:
        """Format cost analysis message"""
        return (
            "💰 **Cost Analysis Report**\n\n"
            f"💸 **Total Costs:** ${cost_analysis.total_costs:,.2f}\n"
            f"📊 **Cost %:** {cost_analysis.cost_percentage:.2f}%\n\n"
            f"💳 **Trading Fees:** ${cost_analysis.total_fees:,.2f}\n"
            f"📉 **Slippage:** ${cost_analysis.total_slippage:,.2f}\n"
            f"💰 **Funding Costs:** ${cost_analysis.funding_costs:,.2f}\n"
            f"⏰ **Opportunity Costs:** ${cost_analysis.opportunity_costs:,.2f}\n\n"
            f"📊 **Fee Breakdown:** {len(cost_analysis.fee_breakdown)} exchanges\n"
            f"📈 **Slippage Breakdown:** {len(cost_analysis.slippage_breakdown)} symbols\n\n"
            "🔄 *Cost analysis updated*"
        )
    
    def _get_risk_level(self, portfolio_metrics) -> str:
        """Get risk level based on metrics"""
        var_95 = abs(portfolio_metrics.risk_metrics.get('var_95', 0))
        volatility = portfolio_metrics.volatility
        
        if var_95 > 0.05 or volatility > 0.5:
            return "🔴 HIGH"
        elif var_95 > 0.03 or volatility > 0.3:
            return "🟡 MEDIUM"
        else:
            return "🟢 LOW"
    
    async def _generate_comprehensive_report(self) -> str:
        """Generate comprehensive report"""
        try:
            # Get all analytics data
            portfolio_metrics = await self.analytics_manager.portfolio_analytics.calculate_portfolio_metrics()
            performance_data = self.analytics_manager.performance_tracker.get_performance_summary("all")
            risk_report = await self.analytics_manager.risk_reporter.generate_risk_report()
            cost_analysis = self.analytics_manager.performance_tracker.calculate_cost_analysis("all")
            
            return (
                "📋 **Comprehensive Analytics Report**\n\n"
                f"💰 **Portfolio Value:** ${portfolio_metrics.total_value:,.2f}\n"
                f"📈 **Total P&L:** ${portfolio_metrics.total_pnl:,.2f}\n"
                f"⚡ **Sharpe Ratio:** {portfolio_metrics.sharpe_ratio:.3f}\n"
                f"⚠️ **Risk Level:** {risk_report.risk_level}\n"
                f"💸 **Total Costs:** ${cost_analysis.total_costs:,.2f}\n\n"
                f"📊 **Performance:** {performance_data.get('performance', {}).get('win_rate', 0):.1f}% win rate\n"
                f"📉 **Risk:** {portfolio_metrics.risk_metrics.get('var_95', 0):.2%} VaR\n"
                f"📈 **Positions:** {len(await self.risk_manager.get_all_positions())}\n\n"
                "🔄 *Comprehensive analysis completed*"
            )
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return "❌ Error generating comprehensive report."
    
    async def _generate_realtime_report(self) -> str:
        """Generate real-time report"""
        try:
            # Get real-time data
            portfolio_metrics = await self.analytics_manager.portfolio_analytics.calculate_portfolio_metrics()
            positions = await self.risk_manager.get_all_positions()
            
            return (
                "🔄 **Real-time Analytics Report**\n\n"
                f"⏰ **Timestamp:** {portfolio_metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"💰 **Portfolio Value:** ${portfolio_metrics.total_value:,.2f}\n"
                f"📈 **Total P&L:** ${portfolio_metrics.total_pnl:,.2f}\n"
                f"📊 **Positions:** {len(positions)}\n"
                f"⚠️ **Risk Level:** {self._get_risk_level(portfolio_metrics)}\n\n"
                "🔄 *Real-time data updated*"
            )
        except Exception as e:
            logger.error(f"Error generating real-time report: {e}")
            return "❌ Error generating real-time report." 