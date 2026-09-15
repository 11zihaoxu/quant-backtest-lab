# Publication Boundary

## Included

- generic data processing and validation
- reusable indicators
- an unrelated demonstration strategy
- paper execution and trade accounting
- performance and drawdown metrics
- charts, tests, CLI, and documentation
- deterministic synthetic data

## Excluded

- private strategy implementation and configuration
- credentials and account data
- private datasets and transaction history
- private research notebooks and archived conversations

## Release checklist

- run unit tests and linting
- run a secrets scanner
- review commit messages, branch names, issues, and pull requests for non-public detail
- inspect staged files with `git status` and `git ls-files`
- confirm that generated data and results are ignored
- confirm that `.env` files are absent
- confirm that no local absolute paths remain
- confirm that all examples use synthetic or public data only
