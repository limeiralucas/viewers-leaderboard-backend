from fastapi import APIRouter

router = APIRouter()


@router.get("/ranking")
def list_ranking():
    return [{"user": "lucasalveslm", "score": 27}, {"user": "gaules", "score": 25}]
