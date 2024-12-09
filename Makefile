setup:
	pdm install
dev:
	pdm run uvicorn src.viewers_leaderboard_backend.main:app --reload
test:
	pdm run pytest
format:
	pdm run black ./src