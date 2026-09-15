# Public Release Hygiene

This document defines the public-history boundary for the repository.

## Commit messages

- Use short, generic messages such as `feat: add walk-forward splitter`.
- Do not include parameter values, experiment identifiers, performance results, account details, or private research labels.
- Do not paste internal roadmaps into commit bodies.
- Prefer a fresh public history over importing private development history.

## Branches and tags

- Use generic prefixes such as `feature/`, `fix/`, `docs/`, and `chore/`.
- Avoid branch or tag names that describe a private strategy, market, timeframe, parameter set, or research decision.

## Issues and pull requests

- Describe publicly observable behavior and generic engineering changes.
- Do not post proprietary strategy logic, private configuration, account data, credentials, or live execution evidence.
- Redact logs before attaching them.
- Keep security reports in GitHub private vulnerability reporting.

## Screenshots and charts

- Use synthetic or public data only.
- Remove broker, wallet, account, order, and API dashboard content.
- Keep the `Synthetic Demo` label visible where a return or equity chart is shown.
- Strip text metadata from generated images before committing.
- Do not imply that a demo result is production performance.

## File names and comments

- Use generic engineering names.
- Comments should describe public behavior only.
- Do not mention private systems, internal experiment names, or non-public research history.

## Release check

```bash
ruff check .
mypy src
pytest
gitleaks git --staged --redact --verbose
```

Also inspect `git status`, `git ls-files`, commit messages, branch names, issue text, pull request text, and image metadata.
