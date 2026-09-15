"""Typed configuration loading for the public demo framework."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TypeVar

import yaml


class ConfigError(ValueError):
    """Raised when a configuration file is missing or invalid."""


@dataclass(frozen=True)
class DataConfig:
    periods: int = 3000
    seed: int = 20260915
    periods_per_year: int = 8760
    start_price: float = 100.0
    annual_drift: float = 0.05
    annual_volatility: float = 0.35

    def validate(self) -> None:
        if self.periods < 100:
            raise ConfigError("data.periods must be at least 100")
        if self.periods_per_year <= 0:
            raise ConfigError("data.periods_per_year must be positive")
        if self.start_price <= 0:
            raise ConfigError("data.start_price must be positive")
        if self.annual_volatility <= 0:
            raise ConfigError("data.annual_volatility must be positive")


@dataclass(frozen=True)
class StrategyConfig:
    name: str = "sma_crossover"
    fast_window: int = 10
    slow_window: int = 40
    allocation: float = 0.90

    def validate(self) -> None:
        if self.name != "sma_crossover":
            raise ConfigError(f"unsupported demo strategy: {self.name!r}")
        if self.fast_window < 2:
            raise ConfigError("strategy.fast_window must be at least 2")
        if self.slow_window <= self.fast_window:
            raise ConfigError("strategy.slow_window must be greater than fast_window")
        if not 0.0 < self.allocation <= 1.0:
            raise ConfigError("strategy.allocation must be in (0, 1]")


@dataclass(frozen=True)
class ExecutionConfig:
    initial_cash: float = 10_000.0
    fee_bps: float = 2.0
    slippage_bps: float = 5.0

    def validate(self) -> None:
        if self.initial_cash <= 0:
            raise ConfigError("execution.initial_cash must be positive")
        if self.fee_bps < 0 or self.slippage_bps < 0:
            raise ConfigError("execution fee and slippage cannot be negative")


@dataclass(frozen=True)
class BacktestConfig:
    data: DataConfig
    strategy: StrategyConfig
    execution: ExecutionConfig

    def validate(self) -> None:
        self.data.validate()
        self.strategy.validate()
        self.execution.validate()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


T = TypeVar("T")


def _mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ConfigError(f"{field} must be a mapping")
    return value


def _build_dataclass(cls: Callable[..., T], raw: Mapping[str, object], field: str) -> T:
    allowed = set(getattr(cls, "__dataclass_fields__", {}))
    unknown = set(raw) - allowed
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise ConfigError(f"unknown {field} keys: {joined}")
    try:
        return cls(**raw)
    except TypeError as exc:
        raise ConfigError(f"invalid {field} configuration: {exc}") from exc


def load_config(path: str | Path) -> BacktestConfig:
    """Load and validate a YAML configuration file."""

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"configuration file not found: {config_path}")
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML: {exc}") from exc
    root = _mapping(raw, "configuration")
    allowed = {"data", "strategy", "execution"}
    unknown = set(root) - allowed
    if unknown:
        joined = ", ".join(sorted(unknown))
        raise ConfigError(f"unknown configuration sections: {joined}")
    config = BacktestConfig(
        data=_build_dataclass(DataConfig, _mapping(root.get("data", {}), "data"), "data"),
        strategy=_build_dataclass(
            StrategyConfig, _mapping(root.get("strategy", {}), "strategy"), "strategy"
        ),
        execution=_build_dataclass(
            ExecutionConfig, _mapping(root.get("execution", {}), "execution"), "execution"
        ),
    )
    config.validate()
    return config


def save_config(config: BacktestConfig, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(config.to_dict(), sort_keys=False), encoding="utf-8")
    return output
