.PHONY: install lint typecheck test demo clean

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest

demo:
	python -m quantlab demo --config configs/demo.yaml --output results/demo

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
