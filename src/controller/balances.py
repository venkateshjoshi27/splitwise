from fastapi import APIRouter, HTTPException, status, Query
from service import helpers
from exceptions import user_exceptions
from typing import List

router = APIRouter()


@router.get("/balances", response_model=dict)
def get_balances(simplify=Query(default=False)) -> dict:
    """Get Balances

    Args:
        simplify (bool, optional): Flag to simplify balances. Defaults to False.

    Returns:
        dict: Dictionary containing balances.
    """
    return helpers.get_all_balances(simplify)


@router.get("/balances/{user_id}", response_model=List)
def get_balance_by_user(user_id: int) -> List:
    """Get Balance by User ID

    Args:
        user_id (int): User ID

    Raises:
        HTTPException: Raises HTTP 404 Exception if user does not exist.

    Returns:
        List: List of balances for the user.
    """
    try:
       return helpers.get_balance_by_user(user_id)
    except user_exceptions.UserDoesNotExists as e:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/balances/lender/{lender_id}", response_model=dict)
def get_by_lender_id(lender_id: int) -> dict:
    """Get Balances by Lender ID

    Args:
        lender_id (int): Lender ID

    Raises:
        HTTPException: Raises HTTP 404 Exception if lender does not exist.

    Returns:
        dict: Dictionary containing balances.
    """
    try:
       return helpers.get_by_lender_id(lender_id)
    except user_exceptions.UserDoesNotExists as e:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
