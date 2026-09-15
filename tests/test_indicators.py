from __future__ import annotations

import math

import pandas as pd

from quantlab.indicators import relative_strength_index, rolling_zscore, simple_moving_average


def test_simple_moving_average_warmup() -> None:
    values = pd.Series([1.0, 2.0, 3.0, 4.0])
    result = simple_moving_average(values, 2)
    assert math.isnan(result.iloc[0])
    assert result.iloc[1] == 1.5
    assert result.iloc[2] == 2.5
    assert result.iloc[3] == 3.5


def test_rolling_zscore_constant_window_is_zero() -> None:
    values = pd.Series([5.0, 5.0, 5.0, 5.0])
    result = rolling_zscore(values, 3)
    assert result.iloc[-1] == 0.0


def test_rising_series_has_high_rsi() -> None:
    values = pd.Series(range(1, 40), dtype=float)
    result = relative_strength_index(values, 14)
    assert result.iloc[-1] == 100.0
