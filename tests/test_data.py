from __future__ import annotations

import pandas as pd
import pytest

from quantlab.config import DataConfig
from quantlab.data.io import DataValidationError, load_ohlcv_csv, save_ohlcv_csv, validate_ohlcv
from quantlab.data.synthetic import generate_synthetic_ohlcv
from quantlab.data.transform import resample_ohlcv


def test_synthetic_data_is_deterministic_and_valid() -> None:
    config = DataConfig(periods=240, seed=7)
    first = generate_synthetic_ohlcv(config)
    second = generate_synthetic_ohlcv(config)
    pd.testing.assert_frame_equal(first, second)
    validate_ohlcv(first)
    assert str(first.index.tz) == "UTC"


def test_validation_rejects_impossible_high() -> None:
    index = pd.date_range("2024-01-01", periods=2, freq="h", tz="UTC")
    frame = pd.DataFrame(
        {
            "open": [100.0, 101.0],
            "high": [101.0, 100.5],
            "low": [99.0, 99.5],
            "close": [100.5, 100.0],
            "volume": [10.0, 12.0],
        },
        index=index,
    )
    with pytest.raises(DataValidationError):
        validate_ohlcv(frame)


def test_csv_round_trip(tmp_path: object) -> None:
    config = DataConfig(periods=120, seed=11)
    frame = generate_synthetic_ohlcv(config)
    path = save_ohlcv_csv(frame, tmp_path / "sample.csv")  # type: ignore[operator]
    restored = load_ohlcv_csv(path)
    pd.testing.assert_frame_equal(frame, restored, check_freq=False)


def test_resample_returns_valid_ohlcv() -> None:
    config = DataConfig(periods=120, seed=12)
    hourly = generate_synthetic_ohlcv(config)
    daily = resample_ohlcv(hourly, "4h")
    validate_ohlcv(daily)
    assert len(daily) == 30
    assert daily["volume"].sum() == pytest.approx(hourly["volume"].sum())
