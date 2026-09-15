"""Generic time-series transformations for OHLCV data."""

from __future__ import annotations

import pandas as pd

from quantlab.data.io import validate_ohlcv

_AGGREGATION = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
}


def resample_ohlcv(frame: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample a validated OHLCV frame and drop empty periods."""

    validate_ohlcv(frame)
    result = frame.resample(rule, label="left", closed="left").agg(_AGGREGATION).dropna()
    if result.empty:
        raise ValueError(f"resampling rule produced no rows: {rule}")
    validate_ohlcv(result)
    return result
