dev:
	pdm run uvicorn src.viewers_leaderboard_backend.main:app --reload
format:
	pdm run black ./src