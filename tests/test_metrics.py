from __future__ import annotations

import math

import pandas as pd

from quantlab.metrics.performance import max_drawdown, profit_factor, total_return


def test_max_drawdown_uses_peak_to_trough() -> None:
    equity = pd.Series([100.0, 120.0, 90.0, 110.0])
    assert max_drawdown(equity) == 0.25


def test_total_return() -> None:
    equity = pd.Series([100.0, 125.0])
    assert total_return(equity) == 0.25


def test_profit_factor_handles_losses() -> None:
    pnl = pd.Series([10.0, -5.0, 2.0, -1.0])
    assert profit_factor(pnl) == 2.0


def test_profit_factor_without_losses_is_infinite() -> None:
    pnl = pd.Series([1.0, 2.0])
    assert math.isinf(profit_factor(pnl))
