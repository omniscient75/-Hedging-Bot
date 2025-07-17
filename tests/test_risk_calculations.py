import pytest
import numpy as np
from risk.greeks import calculate_delta, calculate_gamma, calculate_theta, calculate_vega
from risk.portfolio import PortfolioRiskCalculator

@pytest.mark.parametrize("option_type, S, K, T, r, sigma, expected", [
    ("call", 100, 100, 1, 0.01, 0.2, 0.6368),
    ("put", 100, 100, 1, 0.01, 0.2, -0.3632),
])
def test_calculate_delta(option_type, S, K, T, r, sigma, expected):
    delta = calculate_delta(option_type, S, K, T, r, sigma)
    assert np.isclose(delta, expected, atol=0.01)

def test_calculate_gamma():
    gamma = calculate_gamma(100, 100, 1, 0.01, 0.2)
    assert gamma > 0

def test_calculate_theta():
    theta = calculate_theta("call", 100, 100, 1, 0.01, 0.2)
    assert isinstance(theta, float)

def test_calculate_vega():
    vega = calculate_vega(100, 100, 1, 0.01, 0.2)
    assert vega > 0

def test_portfolio_risk_metrics():
    positions = [
        {"symbol": "BTC/USDT", "quantity": 1, "entry_price": 10000, "market_value": 10000},
        {"symbol": "ETH/USDT", "quantity": 2, "entry_price": 2000, "market_value": 4000},
    ]
    calc = PortfolioRiskCalculator()
    metrics = calc.calculate_metrics(positions)
    assert "total_value" in metrics
    assert metrics["total_value"] == 14000

def test_edge_case_zero_volatility():
    delta = calculate_delta("call", 100, 100, 1, 0.01, 0)
    assert isinstance(delta, float)

def test_error_handling_invalid_option_type():
    with pytest.raises(ValueError):
        calculate_delta("invalid", 100, 100, 1, 0.01, 0.2) 