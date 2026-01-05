from fastapi import APIRouter, Depends
from app.routers.deps import get_current_user

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/me")
def who_am_i(current_user: dict = Depends(get_current_user)):
    return current_user
