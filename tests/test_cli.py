from __future__ import annotations

import json
from pathlib import Path

from quantlab.cli import main


def test_demo_cli_writes_review_artifacts(tmp_path: Path) -> None:
    config = tmp_path / "demo.yaml"
    config.write_text(
        "\n".join(
            [
                "data:",
                "  periods: 240",
                "  seed: 42",
                "  periods_per_year: 8760",
                "strategy:",
                "  name: sma_crossover",
                "  fast_window: 5",
                "  slow_window: 15",
                "  allocation: 0.8",
                "execution:",
                "  initial_cash: 1000",
                "  fee_bps: 1",
                "  slippage_bps: 2",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "output"
    assert main(["demo", "--config", str(config), "--output", str(output)]) == 0
    for name in [
        "dataset.csv",
        "equity.csv",
        "trades.csv",
        "metrics.json",
        "equity_and_drawdown.png",
    ]:
        assert (output / name).exists()
    metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["initial_equity"] == 1000.0
