"""Run the synthetic demo without installing the console script."""

from pathlib import Path

from quantlab.cli import main

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    raise SystemExit(main(["demo", "--config", str(ROOT / "configs" / "demo.yaml")]))
