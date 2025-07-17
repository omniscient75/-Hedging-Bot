import asyncio
from typing import Dict, List, Any, Callable
from datetime import datetime, timedelta
from logger import logger

class AlertMonitor:
    def __init__(self, alert_system, risk_manager, check_interval: int = 30):
        self.alert_system = alert_system
        self.risk_manager = risk_manager
        self.check_interval = check_interval
        self.running = False
        self.alert_stats = {
            'total_alerts': 0,
            'critical_alerts': 0,
            'last_alert_time': None,
            'response_times': []
        }
        
    async def start_monitoring(self):
        """Start real-time alert monitoring."""
        self.running = True
        logger.info("Alert monitoring started")
        
        while self.running:
            try:
                await self._check_risk_thresholds()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _check_risk_thresholds(self):
        """Check risk thresholds and trigger alerts if needed."""
        try:
            # Get current risk metrics
            portfolio_risk = await self.risk_manager.calculate_real_time_risk()
            if not portfolio_risk:
                return
            
            risk_metrics = {
                'delta': portfolio_risk.total_delta,
                'gamma': portfolio_risk.total_gamma,
                'vega': portfolio_risk.total_vega,
                'var': portfolio_risk.portfolio_var,
                'drawdown': 0.0  # Calculate from portfolio history
            }
            
            # Check for threshold breaches
            breaches = self.alert_system.check_thresholds(risk_metrics)
            
            for breach in breaches:
                await self._trigger_alert(breach, risk_metrics, portfolio_risk.positions)
                
        except Exception as e:
            logger.error(f"Threshold check error: {e}")
    
    async def _trigger_alert(self, breach_type: str, risk_metrics: Dict[str, float], positions: List[Dict]):
        """Trigger alert for threshold breach."""
        try:
            # Determine severity based on breach magnitude
            threshold = self.alert_system.thresholds.get(breach_type, 0)
            current_value = abs(risk_metrics.get(breach_type, 0))
            
            if current_value > threshold * 2:
                severity = 'critical'
            elif current_value > threshold * 1.5:
                severity = 'high'
            elif current_value > threshold * 1.2:
                severity = 'medium'
            else:
                severity = 'low'
            
            # Send alert
            success = await self.alert_system.send_risk_alert(
                risk_metrics, positions, breach_type, severity
            )
            
            if success:
                self._update_alert_stats(severity)
                logger.info(f"Alert triggered: {breach_type} - {severity}")
            
        except Exception as e:
            logger.error(f"Alert triggering error: {e}")
    
    def _update_alert_stats(self, severity: str):
        """Update alert statistics."""
        self.alert_stats['total_alerts'] += 1
        if severity == 'critical':
            self.alert_stats['critical_alerts'] += 1
        self.alert_stats['last_alert_time'] = datetime.now()
    
    def get_alert_performance(self) -> Dict[str, Any]:
        """Get alert performance metrics."""
        try:
            total_alerts = self.alert_stats['total_alerts']
            critical_alerts = self.alert_stats['critical_alerts']
            
            if total_alerts == 0:
                return {
                    'total_alerts': 0,
                    'critical_alerts': 0,
                    'critical_rate': 0.0,
                    'avg_response_time': 0.0,
                    'last_alert': None
                }
            
            critical_rate = critical_alerts / total_alerts
            avg_response_time = 2.3  # Placeholder - calculate from actual response times
            
            return {
                'total_alerts': total_alerts,
                'critical_alerts': critical_alerts,
                'critical_rate': critical_rate,
                'avg_response_time': avg_response_time,
                'last_alert': self.alert_stats['last_alert_time']
            }
        except Exception as e:
            logger.error(f"Performance calculation error: {e}")
            return {}
    
    def stop_monitoring(self):
        """Stop alert monitoring."""
        self.running = False
        logger.info("Alert monitoring stopped") 