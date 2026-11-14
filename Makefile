.PHONY: run ingest test lint format

run:
	uv run uvicorn app.main:app --reload

ingest:
	uv run python -m app.rag.ingest

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .
