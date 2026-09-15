"""Risk, return, and trade-level statistics."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from quantlab.backtest.models import BacktestResult


def total_return(equity: pd.Series) -> float:
    if equity.empty:
        return 0.0
    initial = float(equity.iloc[0])
    return float(equity.iloc[-1] / initial - 1.0) if initial > 0 else 0.0


def annualized_return(equity: pd.Series, periods_per_year: int) -> float:
    if equity.empty:
        return 0.0
    periods = max(len(equity) - 1, 1)
    initial = float(equity.iloc[0])
    final = float(equity.iloc[-1])
    if initial <= 0 or final <= 0:
        return 0.0
    return float((final / initial) ** (periods_per_year / periods) - 1.0)


def annualized_volatility(returns: pd.Series, periods_per_year: int) -> float:
    if len(returns) < 2:
        return 0.0
    value = float(returns.std(ddof=0) * math.sqrt(periods_per_year))
    return value if np.isfinite(value) else 0.0


def sharpe_ratio(
    returns: pd.Series,
    periods_per_year: int,
    risk_free_rate: float = 0.0,
) -> float:
    if len(returns) < 2:
        return 0.0
    excess = returns - (risk_free_rate / periods_per_year)
    deviation = float(excess.std(ddof=0))
    if deviation <= 0:
        return 0.0
    value = float(excess.mean() / deviation * math.sqrt(periods_per_year))
    return value if np.isfinite(value) else 0.0


def sortino_ratio(
    returns: pd.Series,
    periods_per_year: int,
    target: float = 0.0,
) -> float:
    if len(returns) < 2:
        return 0.0
    excess = returns - (target / periods_per_year)
    downside = excess.clip(upper=0.0)
    downside_deviation = float(np.sqrt(np.mean(np.square(downside.to_numpy(dtype=float)))))
    if downside_deviation <= 0:
        return 0.0
    value = float(excess.mean() / downside_deviation * math.sqrt(periods_per_year))
    return value if np.isfinite(value) else 0.0


def drawdown_series(equity: pd.Series) -> pd.Series:
    if equity.empty:
        return pd.Series(dtype=float, name="drawdown")
    running_max = equity.cummax()
    drawdown = equity / running_max.replace(0.0, np.nan) - 1.0
    return drawdown.fillna(0.0).rename("drawdown")


def max_drawdown(equity: pd.Series) -> float:
    drawdown = drawdown_series(equity)
    return abs(float(drawdown.min())) if not drawdown.empty else 0.0


def calmar_ratio(equity: pd.Series, periods_per_year: int) -> float:
    drawdown = max_drawdown(equity)
    if drawdown <= 0:
        return 0.0
    return annualized_return(equity, periods_per_year) / drawdown


def profit_factor(pnl: pd.Series) -> float:
    """Return gross gains divided by absolute gross losses."""

    if pnl.empty:
        return 0.0
    gains = float(pnl[pnl > 0].sum())
    losses = float(pnl[pnl < 0].sum())
    if losses < 0:
        return gains / abs(losses)
    return math.inf if gains > 0 else 0.0


def build_summary(result: BacktestResult, periods_per_year: int) -> dict[str, Any]:
    """Build a compact, JSON-serializable set of public demo metrics."""

    equity = result.equity
    trades = result.trades
    pnl = trades["pnl"].astype(float) if not trades.empty else pd.Series(dtype=float)
    gains = float(pnl[pnl > 0].sum())
    losses = float(pnl[pnl < 0].sum())
    average_trade = float(pnl.mean()) if not pnl.empty else 0.0
    median_trade = float(pnl.median()) if not pnl.empty else 0.0
    win_rate = float((pnl > 0).mean()) if not pnl.empty else 0.0
    profit_factor = gains / abs(losses) if losses < 0 else (math.inf if gains > 0 else 0.0)
    return {
        "initial_equity": float(equity.iloc[0]) if not equity.empty else 0.0,
        "final_equity": float(equity.iloc[-1]) if not equity.empty else 0.0,
        "total_return": total_return(equity),
        "annualized_return": annualized_return(equity, periods_per_year),
        "annualized_volatility": annualized_volatility(result.returns, periods_per_year),
        "sharpe_ratio": sharpe_ratio(result.returns, periods_per_year),
        "sortino_ratio": sortino_ratio(result.returns, periods_per_year),
        "max_drawdown": max_drawdown(equity),
        "calmar_ratio": calmar_ratio(equity, periods_per_year),
        "trade_count": int(len(trades)),
        "win_rate": win_rate,
        "average_trade_pnl": average_trade,
        "median_trade_pnl": median_trade,
        "profit_factor": profit_factor if np.isfinite(profit_factor) else None,
        "average_exposure": float(result.position_weight.mean()),
        "total_turnover": float(result.turnover.sum()),
        "total_fees": float(result.fees.sum()),
    }
