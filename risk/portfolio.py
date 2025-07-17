import numpy as np
from typing import List, Dict

def calculate_var(returns: List[float], confidence: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) using historical simulation.
    returns: List of portfolio returns
    confidence: Confidence level (e.g., 0.95)
    Returns: VaR (float, positive number)
    """
    try:
        if not returns or len(returns) < 2:
            raise ValueError("Not enough data for VaR calculation.")
        sorted_returns = np.sort(returns)
        index = int((1 - confidence) * len(sorted_returns))
        var = abs(sorted_returns[index])
        return var
    except Exception as e:
        return 0.0

def calculate_max_drawdown(values: List[float]) -> float:
    """
    Calculate maximum drawdown from a list of portfolio values.
    values: List of portfolio values (e.g., equity curve)
    Returns: max drawdown (float, as a positive number)
    """
    try:
        if not values or len(values) < 2:
            raise ValueError("Not enough data for drawdown calculation.")
        values = np.array(values)
        running_max = np.maximum.accumulate(values)
        drawdowns = (running_max - values) / running_max
        max_drawdown = np.max(drawdowns)
        return max_drawdown
    except Exception as e:
        return 0.0

def calculate_correlation_matrix(price_series: Dict[str, List[float]]) -> np.ndarray:
    """
    Calculate correlation matrix for a dict of price series.
    price_series: Dict of {symbol: [prices]}
    Returns: correlation matrix (np.ndarray)
    """
    try:
        if not price_series or len(price_series) < 2:
            raise ValueError("Need at least two assets for correlation matrix.")
        data = np.array(list(price_series.values()))
        corr_matrix = np.corrcoef(data)
        return corr_matrix
    except Exception as e:
        return np.zeros((len(price_series), len(price_series))) 