.PHONY: build up lab verify test lint clean
build:
	docker compose build
up:
	docker compose up research
lab:
	docker compose --profile lab up lab
verify:
	docker compose --profile verify up verify
test:
	python3 -m pytest -q
lint:
	ruff check src experiments tests || true
clean:
	rm -rf benchmarks/*.csv benchmarks/*.png __pycache__ .pytest_cache
run-all:
	python3 experiments/exp01_zins_verification.py
	python3 experiments/exp02_renten_tilgung.py
	python3 experiments/exp03_optimierung_benchmark.py
	python3 experiments/exp04_hidden_patterns.py
