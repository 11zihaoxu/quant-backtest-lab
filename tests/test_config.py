from __future__ import annotations

from pathlib import Path

import pytest

from quantlab.config import (
    BacktestConfig,
    ConfigError,
    DataConfig,
    ExecutionConfig,
    StrategyConfig,
    load_config,
    save_config,
)


def test_load_default_config() -> None:
    config = load_config(Path(__file__).resolve().parents[1] / "configs" / "demo.yaml")
    assert config.strategy.name == "sma_crossover"
    assert config.execution.initial_cash == 10000.0


def test_config_rejects_invalid_windows() -> None:
    config = BacktestConfig(
        data=DataConfig(),
        strategy=StrategyConfig(fast_window=40, slow_window=10),
        execution=ExecutionConfig(),
    )
    with pytest.raises(ConfigError):
        config.validate()


def test_config_rejects_unknown_section(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("data: {}\nstrategy: {}\nexecution: {}\nunknown: {}\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    config = BacktestConfig(
        data=DataConfig(periods=200, seed=3),
        strategy=StrategyConfig(fast_window=4, slow_window=12, allocation=0.7),
        execution=ExecutionConfig(initial_cash=5000.0, fee_bps=1.0, slippage_bps=2.0),
    )
    path = save_config(config, tmp_path / "config.yaml")
    restored = load_config(path)
    assert restored == config
