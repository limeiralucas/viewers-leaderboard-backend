PORT ?= 8000

setup:
	pdm install
dev:
	pdm run uvicorn src.viewers_leaderboard.main:app --port $(PORT) --reload
test:
	pdm run pytest
format:
	pdm run black ./src
	pdm run black ./tests