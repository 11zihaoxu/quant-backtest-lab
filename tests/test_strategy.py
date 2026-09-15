from __future__ import annotations

import numpy as np
import pandas as pd

from quantlab.data.io import validate_ohlcv
from quantlab.strategies import SMACrossoverStrategy


def _frame_from_close(close: np.ndarray) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=len(close), freq="h", tz="UTC")
    frame = pd.DataFrame(
        {
            "open": close,
            "high": close * 1.001,
            "low": close * 0.999,
            "close": close,
            "volume": 100.0,
        },
        index=index,
    )
    validate_ohlcv(frame)
    return frame


def test_crossover_strategy_has_no_warmup_signal() -> None:
    close = np.linspace(100.0, 130.0, 80)
    frame = _frame_from_close(close)
    strategy = SMACrossoverStrategy(fast_window=3, slow_window=8, allocation=0.75)
    targets = strategy.generate_target_weights(frame)
    assert (targets.iloc[:7] == 0.0).all()
    assert targets.iloc[-1] == 0.75


def test_crossover_strategy_switches_to_cash_on_downtrend() -> None:
    rising = np.linspace(100.0, 150.0, 80)
    falling = np.linspace(150.0, 80.0, 80)
    frame = _frame_from_close(np.concatenate([rising, falling]))
    strategy = SMACrossoverStrategy(fast_window=4, slow_window=12, allocation=0.8)
    targets = strategy.generate_target_weights(frame)
    assert targets.iloc[80] == 0.8
    assert targets.iloc[-1] == 0.0
