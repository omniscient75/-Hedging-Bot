import numpy as np
from typing import List, Tuple

def calculate_beta(asset_returns: List[float], benchmark_returns: List[float]) -> float:
    """
    Calculate beta of an asset relative to a benchmark.
    asset_returns: List of asset returns
    benchmark_returns: List of benchmark returns
    Returns: beta (float)
    """
    try:
        if len(asset_returns) != len(benchmark_returns) or len(asset_returns) < 2:
            raise ValueError("Input lists must have the same length and at least 2 elements.")
        asset_arr = np.array(asset_returns)
        bench_arr = np.array(benchmark_returns)
        cov = np.cov(asset_arr, bench_arr)[0][1]
        var = np.var(bench_arr)
        if var == 0:
            raise ValueError("Benchmark variance is zero.")
        beta = cov / var
        return beta
    except Exception as e:
        return 0.0

def calculate_hedge_ratio(beta: float, correlation: float, position_size: float) -> float:
    """
    Calculate hedge ratio for a position using beta and correlation.
    beta: Beta of the asset
    correlation: Correlation coefficient between asset and hedge instrument
    position_size: Size of the position to hedge
    Returns: hedge ratio (float)
    """
    try:
        if not (-1 <= correlation <= 1):
            raise ValueError("Correlation must be between -1 and 1.")
        hedge_ratio = beta * correlation * position_size
        return hedge_ratio
    except Exception as e:
        return 0.0 