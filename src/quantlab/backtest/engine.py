"""Small event-driven engine with next-open execution and explicit costs.

The engine is intentionally generic. A close-generated target weight is shifted
one bar forward and executed at the following open, which keeps the public demo
honest about signal timing and helps tests detect look-ahead mistakes.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from quantlab.backtest.models import BacktestResult
from quantlab.config import ExecutionConfig
from quantlab.data.io import validate_ohlcv

_EPSILON = 1e-12


def _validate_weights(target_weights: pd.Series, index: pd.Index) -> pd.Series:
    if not target_weights.index.equals(index):
        raise ValueError("target weights must share the data index")
    result = target_weights.astype(float).copy()
    if result.isna().any():
        raise ValueError("target weights must not contain missing values")
    if ((result < 0.0) | (result > 1.0)).any():
        raise ValueError("target weights must be between 0 and 1")
    return result


def run_backtest(
    data: pd.DataFrame,
    target_weights: pd.Series,
    execution: ExecutionConfig | None = None,
) -> BacktestResult:
    """Run a long-only, fractional-share paper backtest."""

    validate_ohlcv(data)
    costs = execution or ExecutionConfig()
    costs.validate()
    targets = _validate_weights(target_weights, data.index)

    cash = float(costs.initial_cash)
    shares = 0.0
    previous_target = 0.0
    fee_rate = costs.fee_bps / 10_000.0
    slippage_rate = costs.slippage_bps / 10_000.0

    equity_values: list[float] = []
    cash_values: list[float] = []
    share_values: list[float] = []
    position_values: list[float] = []
    fee_values: list[float] = []
    turnover_values: list[float] = []
    trades: list[dict[str, Any]] = []
    open_trade: dict[str, Any] | None = None

    # Close-generated signals become executable only on the next bar open.
    executable_targets = targets.shift(1).fillna(0.0)

    for timestamp, row in data.iterrows():
        open_price = float(row["open"])
        close_price = float(row["close"])
        target = float(executable_targets.loc[timestamp])
        gross_notional = 0.0
        bar_fee = 0.0

        should_rebalance = abs(target - previous_target) > _EPSILON
        if should_rebalance:
            equity_at_open = cash + shares * open_price
            direction = target - previous_target
            price_multiplier = 1.0 + slippage_rate if direction > 0 else 1.0 - slippage_rate
            fill_price = open_price * price_multiplier
            desired_notional = equity_at_open * target
            desired_shares = desired_notional / fill_price if fill_price > 0 else 0.0
            delta_shares = desired_shares - shares

            if delta_shares > 0:
                available = max(cash, 0.0)
                affordable_shares = available / (fill_price * (1.0 + fee_rate))
                if delta_shares > affordable_shares:
                    delta_shares = affordable_shares

            trade_notional = abs(delta_shares * fill_price)
            bar_fee = trade_notional * fee_rate
            cash -= delta_shares * fill_price + bar_fee
            shares += delta_shares
            if abs(shares) < _EPSILON:
                shares = 0.0
            gross_notional = trade_notional

            if open_trade is None and shares > _EPSILON:
                open_trade = {
                    "entry_time": timestamp,
                    "entry_price": fill_price,
                    "entry_shares": shares,
                    "entry_cost": trade_notional + bar_fee,
                    "entry_fee": bar_fee,
                }
            elif open_trade is not None and shares <= _EPSILON:
                exit_value = trade_notional - bar_fee
                entry_cost = float(open_trade["entry_cost"])
                pnl = exit_value - entry_cost
                trades.append(
                    {
                        **open_trade,
                        "exit_time": timestamp,
                        "exit_price": fill_price,
                        "exit_fee": bar_fee,
                        "pnl": pnl,
                        "return_pct": pnl / entry_cost if entry_cost > 0 else 0.0,
                    }
                )
                open_trade = None
            elif open_trade is not None and delta_shares > 0:
                open_trade["entry_shares"] = float(open_trade["entry_shares"]) + delta_shares
                open_trade["entry_cost"] = (
                    float(open_trade["entry_cost"]) + trade_notional + bar_fee
                )

            previous_target = target

        equity = cash + shares * close_price
        equity_values.append(equity)
        cash_values.append(cash)
        share_values.append(shares)
        position_values.append((shares * close_price / equity) if equity > 0 else 0.0)
        fee_values.append(bar_fee)
        turnover_values.append((gross_notional / equity) if equity > 0 else 0.0)

    equity = pd.Series(equity_values, index=data.index, name="equity")
    returns = equity.pct_change().fillna(0.0).rename("returns")
    trade_columns = [
        "entry_time",
        "entry_price",
        "entry_shares",
        "entry_cost",
        "entry_fee",
        "exit_time",
        "exit_price",
        "exit_fee",
        "pnl",
        "return_pct",
    ]
    trade_frame = pd.DataFrame(trades, columns=trade_columns)
    return BacktestResult(
        equity=equity,
        returns=returns,
        cash=pd.Series(cash_values, index=data.index, name="cash"),
        shares=pd.Series(share_values, index=data.index, name="shares"),
        position_weight=pd.Series(position_values, index=data.index, name="position_weight"),
        fees=pd.Series(fee_values, index=data.index, name="fees"),
        turnover=pd.Series(turnover_values, index=data.index, name="turnover"),
        trades=trade_frame,
    )
