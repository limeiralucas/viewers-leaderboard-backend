import asyncio
from fastapi import APIRouter
from pymongo import DESCENDING
from src.viewers_leaderboard.ranking.models import Score
from src.viewers_leaderboard.twitch.user import get_user, UserNotFoundException

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

    scores = await Score.aggregate(pipeline).to_list()

    async def get_profile_image(username: str):
        try:
            user = await get_user(username)
            return user.profile_image if user else None
        except UserNotFoundException:
            return None

    profile_pictures = asyncio.gather(
        *[get_profile_image(score["username"]) for score in scores]
    )

    for score, profile_picture in zip(scores, await profile_pictures):
        score["profile_picture"] = profile_picture

    return scores
