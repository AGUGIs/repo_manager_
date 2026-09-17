.PHONY: format lint typecheck test check

format:
	python3 -m autopep8 --in-place --recursive --max-line-length 79 \
		--exclude .venv,.git,.idea,__pycache__,.pytest_cache .

lint:
	python3 -m flake8

typecheck:
	python3 -m mypy main.py projects.py repositories.py members.py \
		users.py storage.py utils.py

test:
	python3 -m pytest

check: format lint typecheck test
