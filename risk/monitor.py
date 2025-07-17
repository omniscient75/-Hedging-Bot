import asyncio
from typing import Callable, Dict, Any
from logger import logger

class RiskMonitor:
    def __init__(self, get_risk_metrics: Callable[[], Dict[str, Any]], thresholds: Dict[str, float], alert_callback: Callable[[str, float, float], None]):
        """
        get_risk_metrics: function returning dict of risk metrics
        thresholds: dict of {metric: threshold}
        alert_callback: function(metric, value, threshold) to call on breach
        """
        self.get_risk_metrics = get_risk_metrics
        self.thresholds = thresholds
        self.alert_callback = alert_callback
        self.running = False

    async def start(self, interval: int = 30):
        self.running = True
        while self.running:
            try:
                metrics = self.get_risk_metrics()
                for metric, threshold in self.thresholds.items():
                    value = metrics.get(metric)
                    if value is not None and abs(value) > threshold:
                        logger.warning(f"Risk threshold breached: {metric}={value} (threshold={threshold})")
                        self.alert_callback(metric, value, threshold)
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"RiskMonitor error: {e}")
                await asyncio.sleep(5)

    def stop(self):
        self.running = False 