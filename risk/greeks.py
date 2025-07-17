import math
from typing import Literal
from scipy.stats import norm

# Option type: 'call' or 'put'
def black_scholes_greeks(
    S: float, K: float, T: float, r: float, sigma: float, option_type: Literal['call', 'put']
):
    """
    Calculate Black-Scholes Greeks for European options.
    S: Spot price
    K: Strike price
    T: Time to expiry (in years)
    r: Risk-free rate (annualized, decimal)
    sigma: Volatility (annualized, decimal)
    option_type: 'call' or 'put'
    Returns: dict with delta, gamma, theta, vega
    """
    try:
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            raise ValueError("Invalid input for Black-Scholes greeks.")
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        if option_type == 'call':
            delta = norm.cdf(d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * norm.cdf(d2)) / 365
        else:
            delta = -norm.cdf(-d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) + r * K * math.exp(-r * T) * norm.cdf(-d2)) / 365
        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
        vega = S * norm.pdf(d1) * math.sqrt(T) / 100
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega
        }
    except Exception as e:
        return {
            'delta': 0.0,
            'gamma': 0.0,
            'theta': 0.0,
            'vega': 0.0,
            'error': str(e)
        } 