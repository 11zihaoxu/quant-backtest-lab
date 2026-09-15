"""Backtest result and trade data models."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    """Immutable output from a completed paper backtest."""

    equity: pd.Series
    returns: pd.Series
    cash: pd.Series
    shares: pd.Series
    position_weight: pd.Series
    fees: pd.Series
    turnover: pd.Series
    trades: pd.DataFrame
