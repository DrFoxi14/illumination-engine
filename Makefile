.PHONY: install lint test check

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest -q

check: lint test
