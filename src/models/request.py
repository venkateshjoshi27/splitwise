from pydantic import BaseModel, EmailStr, Field, validator
from typing import List

class UserCreate(BaseModel):
    """
    Pydantic model for creating a user.

    Attributes:
    - name (str): The name of the user.
    - email (EmailStr): The email address of the user.
    - mobile_number (str): The mobile number of the user (10 digits).
    """

    name: str = Field(..., description="The name of the user.")
    email: EmailStr = Field(..., description="The email address of the user.")
    mobile_number: str = Field(..., description="The mobile number of the user (10 digits).")

    @validator('mobile_number')
    def validate_mobile_number(cls, v):
        if not v.isdigit():
            raise ValueError('Mobile number must contain only digits')
        if len(v) != 10:
            raise ValueError('Mobile number should be 10 digits long')
        return v

    @validator('email')
    def email_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Email must not be empty')
        return v.strip()

class ExpenseParticipantBase(BaseModel):
    user_id: int
    share: float | None

class ExpenseRequest(BaseModel):
    lender_id: int
    total_amount: float = Field(..., gt=0, description="Total amount paid")
    expense_type: str = Field(..., description="Type of expense: EQUAL, EXACT, or PERCENT")
    participants: List[ExpenseParticipantBase]
    expense_name: str = Field(..., description="Name of the expense")
    notes: str = Field(..., description="Notes for the expense")