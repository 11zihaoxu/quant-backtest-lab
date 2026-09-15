"""End-to-end demo pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from quantlab.backtest.engine import run_backtest
from quantlab.backtest.models import BacktestResult
from quantlab.config import BacktestConfig
from quantlab.data.synthetic import generate_synthetic_ohlcv
from quantlab.metrics.performance import build_summary
from quantlab.reporting.plots import plot_equity_and_drawdown
from quantlab.strategies.sma_crossover import SMACrossoverStrategy


@dataclass(frozen=True)
class RunArtifacts:
    data_path: Path
    equity_path: Path
    trades_path: Path
    metrics_path: Path
    chart_path: Path
    metrics: dict[str, Any]


def run_frame(config: BacktestConfig, data: pd.DataFrame, output_dir: str | Path) -> RunArtifacts:
    """Run the demo strategy on a supplied frame and persist review artifacts."""

    config.validate()
    strategy = SMACrossoverStrategy.from_config(config.strategy)
    targets = strategy.generate_target_weights(data)
    result: BacktestResult = run_backtest(data, targets, config.execution)
    metrics = build_summary(result, config.data.periods_per_year)

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    data_path = destination / "dataset.csv"
    equity_path = destination / "equity.csv"
    trades_path = destination / "trades.csv"
    metrics_path = destination / "metrics.json"
    chart_path = destination / "equity_and_drawdown.png"

    serializable = data.copy()
    serializable.index.name = "timestamp"
    serializable.to_csv(data_path)
    result.equity.rename("equity").to_frame().to_csv(equity_path)
    result.trades.to_csv(trades_path, index=False)
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    plot_equity_and_drawdown(result.equity, chart_path)
    return RunArtifacts(
        data_path=data_path,
        equity_path=equity_path,
        trades_path=trades_path,
        metrics_path=metrics_path,
        chart_path=chart_path,
        metrics=metrics,
    )


def run_demo(config: BacktestConfig, output_dir: str | Path) -> RunArtifacts:
    """Generate synthetic data and run the complete public demo pipeline."""

    data = generate_synthetic_ohlcv(config.data)
    return run_frame(config, data, output_dir)
