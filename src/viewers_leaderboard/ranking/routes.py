from fastapi import APIRouter
from pymongo import DESCENDING
from src.viewers_leaderboard.ranking.models import Score

router = APIRouter()


@router.get("/ranking/{channel_id}")
async def ranking(channel_id: str):
    pipeline = [
        {"$match": {"broadcaster_user_id": channel_id}},
        {
            "$group": {
                "_id": "$viewer_username",
                "total_score": {"$sum": "$value"},
            }
        },
        {"$sort": {"total_score": DESCENDING}},
        {"$project": {"_id": 0, "username": "$_id", "score": "$total_score"}},
    ]

    result = await Score.aggregate(pipeline).to_list()

    return result
