"""CSV I/O and OHLCV contract validation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]


class DataValidationError(ValueError):
    """Raised when an OHLCV frame violates the public data contract."""


def validate_ohlcv(frame: pd.DataFrame) -> None:
    """Validate a time-indexed OHLCV frame in place without modifying it."""

    if not isinstance(frame, pd.DataFrame):
        raise DataValidationError("data must be a pandas DataFrame")
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise DataValidationError("data index must be a DatetimeIndex")
    missing = [column for column in OHLCV_COLUMNS if column not in frame.columns]
    if missing:
        raise DataValidationError(f"missing OHLCV columns: {', '.join(missing)}")
    if frame.empty:
        raise DataValidationError("data is empty")
    if frame.index.has_duplicates:
        raise DataValidationError("data index contains duplicate timestamps")
    if not frame.index.is_monotonic_increasing:
        raise DataValidationError("data index must be sorted ascending")
    if frame.index.tz is None:
        raise DataValidationError("data index must be timezone-aware")

    numeric = frame[OHLCV_COLUMNS].apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any():
        raise DataValidationError("OHLCV values must be numeric and non-null")
    if not np.isfinite(numeric.to_numpy()).all():
        raise DataValidationError("OHLCV values must be finite")
    if (numeric[["open", "high", "low", "close"]] <= 0).any().any():
        raise DataValidationError("prices must be positive")
    if (numeric["volume"] < 0).any():
        raise DataValidationError("volume cannot be negative")
    if (numeric["high"] < numeric[["open", "close", "low"]].max(axis=1)).any():
        raise DataValidationError("high must be greater than or equal to open, close, and low")
    if (numeric["low"] > numeric[["open", "close", "high"]].min(axis=1)).any():
        raise DataValidationError("low must be less than or equal to open, close, and high")


def load_ohlcv_csv(path: str | Path) -> pd.DataFrame:
    """Load an OHLCV CSV and validate its public data contract."""

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"OHLCV file not found: {source}")
    frame = pd.read_csv(source)
    if "timestamp" not in frame.columns:
        raise DataValidationError("CSV must contain a timestamp column")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.set_index("timestamp").sort_index()
    validate_ohlcv(frame)
    return frame


def save_ohlcv_csv(frame: pd.DataFrame, path: str | Path) -> Path:
    """Validate and save an OHLCV frame as CSV."""

    validate_ohlcv(frame)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    serializable = frame.copy()
    serializable.index.name = "timestamp"
    serializable.to_csv(output, index=True)
    return output
