# Research Method

The repository demonstrates a disciplined research workflow without publishing proprietary strategy research.

## Recommended sequence

1. Define the data contract and provenance.
2. Validate missing, duplicate, and inconsistent observations.
3. Freeze a baseline and test it before parameter search.
4. Use rolling-origin or walk-forward validation rather than a single split.
5. Account for transaction costs, slippage, turnover, and capacity.
6. Measure drawdown, tail risk, stability, and exposure.
7. Treat repeated parameter searches as a multiple-testing problem.
8. Re-test on untouched data before considering production use.
9. Keep strategy answers private when they are the core asset.

## Public boundary

This repository contains the reusable research machinery, not the private research answer. The demo strategy is intentionally unrelated to production logic and exists to make the framework runnable.
