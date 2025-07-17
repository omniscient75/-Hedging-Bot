from typing import List, Dict, Any

def aggregate_risk_metrics(risk_metrics_list: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Aggregate risk metrics across multiple positions/exchanges.
    risk_metrics_list: List of dicts with keys: delta, gamma, theta, vega, var, drawdown
    Returns: dict with aggregated metrics
    """
    agg = {'delta': 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0, 'var': 0.0, 'drawdown': 0.0}
    try:
        for metrics in risk_metrics_list:
            agg['delta'] += metrics.get('delta', 0.0)
            agg['gamma'] += metrics.get('gamma', 0.0)
            agg['theta'] += metrics.get('theta', 0.0)
            agg['vega'] += metrics.get('vega', 0.0)
            agg['var'] += abs(metrics.get('var', 0.0))
            agg['drawdown'] = max(agg['drawdown'], abs(metrics.get('drawdown', 0.0)))
        return agg
    except Exception as e:
        return {k: 0.0 for k in agg} 