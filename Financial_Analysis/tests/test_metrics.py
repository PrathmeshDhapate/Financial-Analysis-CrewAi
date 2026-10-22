
import math

import pandas as pd
import pytest
from fastapi import HTTPException

from main import calculate_metrics


def test_latest_close_and_price_change():
    prices = pd.Series([100.0, 110.0, 120.0])

    result = calculate_metrics("AAPL", prices)

    assert result["latest_close"] == 120.0
    assert result["six_month_change_pct"] == 20.0
    assert result["observations"] == 3


def test_indian_stock_uses_inr():
    prices = pd.Series([100.0, 105.0, 110.0])

    result = calculate_metrics("RELIANCE.NS", prices)

    assert result["currency"] == "INR"
    assert result["currency_symbol"] == "₹"


def test_us_stock_uses_usd():
    prices = pd.Series([100.0, 105.0, 110.0])

    result = calculate_metrics("AAPL", prices)

    assert result["currency"] == "USD"
    assert result["currency_symbol"] == "$"


def test_volatility_matches_independent_calculation():
    prices = pd.Series([100.0, 110.0, 99.0, 108.9])

    daily_returns = prices.pct_change().dropna()
    expected = daily_returns.std() * math.sqrt(252) * 100

    result = calculate_metrics("AAPL", prices)

    assert result["annualized_historical_volatility_pct"] == pytest.approx(
        expected, abs=0.01
    )


def test_insufficient_prices_raise_error():
    prices = pd.Series([100.0, 110.0])

    with pytest.raises(HTTPException) as exc_info:
        calculate_metrics("AAPL", prices)

    assert exc_info.value.status_code == 400


def test_price_change_can_be_negative():
    prices = pd.Series([100.0, 90.0, 80.0])

    result = calculate_metrics("AAPL", prices)

    assert result["latest_close"] == 80.0
    assert result["six_month_change_pct"] == -20.0


def test_unchanged_prices_have_zero_change_and_volatility():
    prices = pd.Series([100.0, 100.0, 100.0])

    result = calculate_metrics("AAPL", prices)

    assert result["six_month_change_pct"] == 0.0
    assert result["annualized_historical_volatility_pct"] == 0.0


def test_observation_count_matches_supplied_prices():
    prices = pd.Series([100.0, 102.0, 101.0, 105.0, 107.0])

    result = calculate_metrics("AAPL", prices)

    assert result["observations"] == 5


def test_bombay_stock_uses_inr():
    prices = pd.Series([100.0, 105.0, 110.0])

    result = calculate_metrics("RELIANCE.BO", prices)

    assert result["currency"] == "INR"
    assert result["currency_symbol"] == "₹"



def test_small_price_change_is_rounded_to_two_decimals():
    prices = pd.Series([100.0, 100.0, 100.006])

    result = calculate_metrics("AAPL", prices)

    assert result["six_month_change_pct"] == 0.01
    assert result["latest_close"] == 100.01

