from .connection import Base
from sqlalchemy import Column, String, ForeignKey, Float, DateTime, Integer, Boolean, Text
from sqlalchemy.orm import relationship
import enum
from sqlalchemy import Enum
from datetime import datetime

class User(Base):
    """
    Users DB Table
    """
    
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    mobile_number = Column(String(10), nullable=False)  # Assuming mobile number is a 10-digit string

class ExpenseType(enum.Enum):
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENT = "PERCENT"

class Expense(Base):
    """
    Expense DB Table
    """
    
    __tablename__ = 'expenses'

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    amount = Column(Float, nullable=False)
    expense_type = Column(Enum(ExpenseType), nullable=False)
    total_shares = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    notes = Column(Text)

    user = relationship("User")


class ExpenseParticipant(Base):
    """
    ExpenseParticipant DB Table
    """
    
    __tablename__ = 'expense_participants'

    participant_id = Column(Integer, primary_key=True, autoincrement=True)
    expense_id = Column(Integer, ForeignKey('expenses.expense_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    share_amount = Column(Float, nullable=False)

    expense = relationship("Expense")
    user = relationship("User")

class EmailQueue(Base):
    """
    EmailQueue DB Table
    """
    
    __tablename__ = 'email_queue'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(String(1000), nullable=False)
    sent_at = Column(DateTime)
    is_sent = Column(Boolean, default=False)
