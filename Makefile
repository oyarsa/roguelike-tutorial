lint:
	poetry run black .
	poetry run isort --profile black .
	poetry run flake8 --ignore=E203,W503 --max-line-length=88 .
	poetry run mypy .
