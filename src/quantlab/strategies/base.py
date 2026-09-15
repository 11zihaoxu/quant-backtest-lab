"""Strategy protocol used by the public backtest engine."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """Generate target portfolio weights from bars available at each close."""

    @abstractmethod
    def generate_target_weights(self, data: pd.DataFrame) -> pd.Series:
        """Return desired long exposure in the range [0, 1].

        Signals may use information available at each bar close. The backtest
        engine is responsible for shifting execution to the next bar open.
        """

        raise NotImplementedError
