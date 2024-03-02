from fastapi import APIRouter, HTTPException, status
from models.request import ExpenseRequest
from service import helpers
from exceptions import expense_exceptions, user_exceptions

router = APIRouter()


@router.post("/expenses", status_code=status.HTTP_201_CREATED, response_model=dict)
def create_expense(expense: ExpenseRequest) -> dict:
    """Create Expense

    Args:
        expense (ExpenseRequest): Expense request payload

    Raises:
        HTTPException: Raises HTTP 400 Exception if maximum amount or number of participants exceeded.
        HTTPException: Raises HTTP 400 Exception if there's an issue with expense validation or user does not exist.

    Returns:
        dict: Dictionary containing the created expense ID.
    """
    if expense.total_amount > 100000000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum amount exceeded.")
    if len(expense.participants) > 1000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum number of participants exceeded.")
    try:
        expense = helpers.create_expense(expense)
        return dict(expense_id=expense.expense_id)
    except expense_exceptions.ExpenseValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except user_exceptions.UserDoesNotExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))