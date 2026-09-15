"""Deterministic synthetic OHLCV generation for demonstrations and tests."""

from __future__ import annotations

import numpy as np
import pandas as pd

from quantlab.config import DataConfig
from quantlab.data.io import validate_ohlcv


def generate_synthetic_ohlcv(config: DataConfig) -> pd.DataFrame:
    """Generate a reproducible, non-market OHLCV fixture.

    The series uses a geometric random walk, a slow volatility regime, and
    occasional mean-reverting shocks. It is deliberately synthetic and must
    never be presented as historical performance data.
    """

    config.validate()
    rng = np.random.default_rng(config.seed)
    periods = config.periods
    dt = 1.0 / config.periods_per_year
    base_vol = config.annual_volatility * np.sqrt(dt)

    regime = 0.75 + 0.55 * np.sin(np.linspace(0, 9 * np.pi, periods))
    jumps = rng.normal(0.0, base_vol * 1.8, periods) * (rng.random(periods) < 0.015)
    shock_shape = np.sign(np.sin(np.linspace(0, 14 * np.pi, periods)))
    shocks = -0.08 * shock_shape * (rng.random(periods) < 0.006)
    returns = (
        (config.annual_drift * dt)
        + base_vol * regime * rng.normal(size=periods)
        + jumps
        + shocks
    )
    close = config.start_price * np.exp(np.cumsum(returns))
    open_price = np.empty(periods)
    open_price[0] = config.start_price
    open_price[1:] = close[:-1] * (1.0 + rng.normal(0.0, base_vol * 0.075, periods - 1))

    intrabar = np.abs(rng.normal(base_vol * 0.65, base_vol * 0.25, periods))
    high = np.maximum(open_price, close) * (1.0 + intrabar)
    low = np.minimum(open_price, close) * np.maximum(0.01, 1.0 - intrabar)
    volume = rng.lognormal(mean=10.0, sigma=0.35, size=periods)

    index = pd.date_range("2020-01-01", periods=periods, freq="h", tz="UTC")
    frame = pd.DataFrame(
        {"open": open_price, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )
    frame.index.name = "timestamp"
    validate_ohlcv(frame)
    return frame
