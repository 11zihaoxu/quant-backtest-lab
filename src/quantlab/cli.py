"""Command-line interface for the public demo framework."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from quantlab import __version__
from quantlab.config import ConfigError, load_config
from quantlab.data.io import load_ohlcv_csv
from quantlab.pipeline import run_demo, run_frame

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "demo.yaml"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quantlab",
        description="Run reproducible public demonstration backtests.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="Run the synthetic-data demo end to end.")
    demo.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    demo.add_argument("--output", type=Path, default=Path("results/demo"))

    backtest = subparsers.add_parser("backtest", help="Backtest the demo strategy on a CSV file.")
    backtest.add_argument("--data", type=Path, required=True)
    backtest.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    backtest.add_argument("--output", type=Path, default=Path("results/backtest"))

    return parser


def _print_metrics(metrics: dict[str, object]) -> None:
    print(json.dumps(metrics, indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            config = load_config(args.config)
            artifacts = run_demo(config, args.output)
            _print_metrics(artifacts.metrics)
            print(f"artifacts: {artifacts.metrics_path.parent}")
            return 0
        if args.command == "backtest":
            config = load_config(args.config)
            data = load_ohlcv_csv(args.data)
            artifacts = run_frame(config, data, args.output)
            _print_metrics(artifacts.metrics)
            print(f"artifacts: {artifacts.metrics_path.parent}")
            return 0
    except (ConfigError, FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))
    return 2
