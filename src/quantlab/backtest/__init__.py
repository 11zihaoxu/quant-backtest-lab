"""Event-driven paper backtesting primitives."""

from quantlab.backtest.engine import run_backtest
from quantlab.backtest.models import BacktestResult

__all__ = ["BacktestResult", "run_backtest"]
