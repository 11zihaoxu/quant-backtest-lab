# Backtest Assumptions

## Execution timing

A strategy returns a target weight using information available through bar close. The engine shifts that target by one bar and executes at the next bar open. This prevents a close-derived signal from receiving the same bar's close execution.

## Paper fills

- fractional shares are allowed
- the demo account is long-only
- buy fills include positive slippage
- sell fills include negative slippage
- fees are charged on traded notional
- insufficient cash reduces the buy quantity

## Not modeled

- order-book depth
- latency distributions
- partial fills
- exchange outages
- borrow, funding, staking, or financing costs
- taxes
- live reconciliation and settlement

## Interpretation

The public engine is a deterministic teaching tool. It is not a production execution simulator and does not establish that any strategy is tradable or profitable.
