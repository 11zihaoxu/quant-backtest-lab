from __future__ import annotations

import pandas as pd

from quantlab.metrics.performance import (
    annualized_return,
    annualized_volatility,
    calmar_ratio,
    drawdown_series,
    sharpe_ratio,
    sortino_ratio,
)


def test_annualized_metrics_are_finite() -> None:
    equity = pd.Series([100.0, 101.0, 99.0, 105.0])
    returns = equity.pct_change().fillna(0.0)
    assert annualized_return(equity, 252) > 0
    assert annualized_volatility(returns, 252) > 0
    assert sharpe_ratio(returns, 252) != 0
    assert sortino_ratio(returns, 252) != 0
    assert calmar_ratio(equity, 252) > 0


def test_drawdown_series_never_positive() -> None:
    drawdown = drawdown_series(pd.Series([100.0, 110.0, 90.0, 120.0]))
    assert (drawdown <= 0).all()
    assert drawdown.iloc[-1] == 0.0
