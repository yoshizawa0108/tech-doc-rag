.PHONY: freeze run ingest

freeze:
	pip-chill > requirements.txt

run:
	uvicorn app.main:app --reload

ingest:
	python -m app.rag.ingest