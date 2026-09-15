# Contributing

Thanks for your interest in improving the project.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Quality gates

```bash
ruff check .
mypy src
test -f .coverage || pytest
```

Use small, focused commits. Add tests for behavioral changes. Do not add proprietary strategy code, real trading data, credentials, or account identifiers.
