"""A deliberately unrelated demo strategy for the public framework."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quantlab.config import StrategyConfig
from quantlab.data.io import validate_ohlcv
from quantlab.indicators import simple_moving_average
from quantlab.strategies.base import Strategy


@dataclass(frozen=True)
class SMACrossoverStrategy(Strategy):
    """Long-only moving-average crossover used only as a teaching example.

    The parameters are demonstration defaults and are not production settings.
    This class is intentionally isolated from private systems.
    """

    fast_window: int = 10
    slow_window: int = 40
    allocation: float = 0.90

    def __post_init__(self) -> None:
        if self.fast_window < 2:
            raise ValueError("fast_window must be at least 2")
        if self.slow_window <= self.fast_window:
            raise ValueError("slow_window must be greater than fast_window")
        if not 0.0 < self.allocation <= 1.0:
            raise ValueError("allocation must be in (0, 1]")

    @classmethod
    def from_config(cls, config: StrategyConfig) -> SMACrossoverStrategy:
        config.validate()
        return cls(
            fast_window=config.fast_window,
            slow_window=config.slow_window,
            allocation=config.allocation,
        )

    def generate_target_weights(self, data: pd.DataFrame) -> pd.Series:
        validate_ohlcv(data)
        fast = simple_moving_average(data["close"], self.fast_window)
        slow = simple_moving_average(data["close"], self.slow_window)
        warm = fast.notna() & slow.notna()
        target = pd.Series(0.0, index=data.index, name="target_weight")
        target.loc[warm] = (fast.loc[warm] > slow.loc[warm]).astype(float) * self.allocation
        return target
