from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.models.models import User
from pydantic import BaseModel

router = APIRouter()

class UserResponse(BaseModel):
    email: str
    id: str
    is_admin: bool = False

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        email=current_user.email,
        id=str(current_user.id),
        is_admin=getattr(current_user, "is_admin", False)
    )
