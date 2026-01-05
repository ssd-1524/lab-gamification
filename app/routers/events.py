from fastapi import APIRouter, Depends

from app.routers.deps import get_authenticated_user

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/")
def log_event(
    data: dict,
    user: dict = Depends(get_authenticated_user),
):
    user_id = user["sub"]

    return {
        "message": "Event logged",
        "user_id": user_id,
    }
