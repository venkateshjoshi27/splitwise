from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from models.request import UserCreate
from service import helpers
from exceptions import user_exceptions

router = APIRouter()

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate) -> dict:
    """Create User

    Args:
        body (UserCreate): User create request payload

    Raises:
        HTTPException: Raises HTTP 409 Exception if user already exists.

    Returns:
        dict: Dictionary containing the created user ID.
    """
    try:
        user = helpers.add_user_in_db(body)
        return dict(user_id=user.user_id)
    except user_exceptions.UserAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
