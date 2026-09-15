"""Matplotlib-based reporting helpers."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

from quantlab.metrics.performance import drawdown_series  # noqa: E402


def plot_equity_and_drawdown(
    equity: pd.Series,
    output_path: str | Path,
    title: str = "Synthetic Demo - Not Production Performance",
) -> Path:
    """Save a two-panel equity and drawdown chart."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    drawdown = drawdown_series(equity)
    figure, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, constrained_layout=True)
    axes[0].plot(equity.index, equity.values, color="#1f4e79", linewidth=1.6)
    axes[0].set_title(title)
    axes[0].set_ylabel("Equity")
    axes[0].grid(alpha=0.2)
    axes[1].fill_between(drawdown.index, drawdown.values, 0.0, color="#c0504d", alpha=0.75)
    axes[1].set_ylabel("Drawdown")
    axes[1].set_xlabel("Time (UTC)")
    axes[1].grid(alpha=0.2)
    figure.savefig(output, dpi=160, bbox_inches="tight")
    plt.close(figure)
    # Re-save without optional text metadata such as the plotting library version.
    with Image.open(output) as image:
        image.save(output, format="PNG", optimize=True)
    return output
