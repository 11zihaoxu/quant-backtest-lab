from __future__ import annotations

import pandas as pd

from quantlab.backtest import run_backtest
from quantlab.config import ExecutionConfig


def _bars() -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=5, freq="h", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100.0, 101.0, 103.0, 104.0, 103.0],
            "high": [101.0, 104.0, 105.0, 105.0, 104.0],
            "low": [99.0, 100.0, 102.0, 102.0, 101.0],
            "close": [100.0, 103.0, 104.0, 103.0, 102.0],
            "volume": [1000.0] * 5,
        },
        index=index,
    )


def test_execution_uses_next_open_and_closes_position() -> None:
    target = pd.Series([1.0, 1.0, 0.0, 0.0, 0.0], index=_bars().index)
    result = run_backtest(_bars(), target, ExecutionConfig(fee_bps=0.0, slippage_bps=0.0))
    assert result.shares.iloc[0] == 0.0
    assert result.shares.iloc[1] > 0.0
    assert result.shares.iloc[2] > 0.0
    assert result.shares.iloc[3] == 0.0
    assert len(result.trades) == 1
    assert result.trades.iloc[0]["entry_time"] == _bars().index[1]
    assert result.trades.iloc[0]["exit_time"] == _bars().index[3]


def test_costs_reduce_equity() -> None:
    target = pd.Series([1.0, 1.0, 0.0, 0.0, 0.0], index=_bars().index)
    free = run_backtest(_bars(), target, ExecutionConfig(fee_bps=0.0, slippage_bps=0.0))
    costly = run_backtest(_bars(), target, ExecutionConfig(fee_bps=20.0, slippage_bps=20.0))
    assert costly.equity.iloc[-1] < free.equity.iloc[-1]
    assert costly.fees.sum() > 0.0
