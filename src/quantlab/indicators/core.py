"""Indicator implementations used by examples and tests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _validate_window(window: int) -> None:
    if window < 1:
        raise ValueError("window must be at least 1")


def simple_moving_average(series: pd.Series, window: int) -> pd.Series:
    """Return a simple moving average with no partial values before warm-up."""

    _validate_window(window)
    return series.astype(float).rolling(window=window, min_periods=window).mean()


def exponential_moving_average(series: pd.Series, span: int) -> pd.Series:
    """Return an exponential moving average."""

    _validate_window(span)
    return series.astype(float).ewm(span=span, adjust=False, min_periods=span).mean()


def average_true_range(frame: pd.DataFrame, window: int = 14) -> pd.Series:
    """Return a Wilder-style average true range."""

    _validate_window(window)
    if not {"high", "low", "close"}.issubset(frame.columns):
        raise ValueError("frame must contain high, low, and close columns")
    previous_close = frame["close"].shift(1)
    true_range = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - previous_close).abs(),
            (frame["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()


def relative_strength_index(series: pd.Series, window: int = 14) -> pd.Series:
    """Return the classic RSI using Wilder smoothing."""

    _validate_window(window)
    delta = series.astype(float).diff()
    gains = delta.clip(lower=0.0)
    losses = -delta.clip(upper=0.0)
    average_gain = gains.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()
    average_loss = losses.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()
    relative_strength = average_gain / average_loss.replace(0.0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + relative_strength))
    return rsi.where(average_loss != 0.0, 100.0)


def rolling_zscore(series: pd.Series, window: int) -> pd.Series:
    """Return a rolling z-score with zero-dispersion windows set to zero."""

    _validate_window(window)
    values = series.astype(float)
    mean = values.rolling(window=window, min_periods=window).mean()
    standard_deviation = values.rolling(window=window, min_periods=window).std(ddof=0)
    score = (values - mean) / standard_deviation.replace(0.0, np.nan)
    return score.mask(standard_deviation == 0.0, 0.0)
