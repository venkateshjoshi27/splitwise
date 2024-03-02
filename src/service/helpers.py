from db.connection import get_session
from db.models import User, Expense, ExpenseParticipant, ExpenseType
from exceptions import user_exceptions, expense_exceptions
from models.request import UserCreate, ExpenseParticipantBase, ExpenseRequest
from collections import defaultdict
from sqlalchemy import func
from typing import List
from emails import send_email

find_user_by_email = lambda email: get_session().query(User).filter(User.email == email).first()

find_user_by_id = lambda id: get_session().query(User).filter(User.user_id == id).first()

get_expense_by_id = lambda expense_id: get_session().query(Expense).filter(Expense.expense_id == expense_id).first()

find_all_expense_by_user = lambda user_id: get_session().query(ExpenseParticipant).filter(ExpenseParticipant.user_id == user_id).all()

find_expense_participants_by_expense_id = lambda expense_id: get_session().query(ExpenseParticipant).filter(ExpenseParticipant.expense_id == expense_id).all()

find_all_user_ids = lambda: get_session().query(User.user_id).first()

def add_user_in_db(user: UserCreate) -> User:
    """Add User in DB

    Args:
        user (UserCreate): User Create Request

    Raises:
        user_exceptions.UserAlreadyExists: When user already exists in DB

    Returns:
        User: Created User
    """
    
    # Check if user already exists
    if find_user_by_email(user.email):
        raise user_exceptions.UserAlreadyExists(f"{user.email}")

    # Create new user
    user_obj = User(
        name=user.name,
        email=user.email,
        mobile_number=user.mobile_number
    )

    # Add user to database
    get_session().add(user_obj)
    get_session().commit()
    return user_obj


def create_expense(expense: ExpenseRequest) -> Expense:
    
    """Create Expense in DB

    Raises:
        user_exceptions.UserDoesNotExists: When creating an expense for the user that does not exists
        expense_exceptions.ExpenseValidationException: Error in validating the expense based on the requirements

    Returns:
        Expense: DB Created Expense
    """
    
    total_users = len(expense.participants)
    
    user_expenses = []
    
    for participant in expense.participants:
        if not find_user_by_id( participant.user_id ):
            raise user_exceptions.UserDoesNotExists(participant.user_id)
        
    if expense.expense_type == ExpenseType.EQUAL.value:
        share_amount = round((expense.total_amount / total_users), 2)
        extra_amount = 0
        if(share_amount * total_users > expense.total_amount):
            extra_amount = expense.total_amount - (share_amount * total_users)
        
        for participant in expense.participants:
            user_expense = dict(share=share_amount+extra_amount, user_id=participant.user_id)
            extra_amount = 0
            user_expenses.append(user_expense)
        
            
    elif expense.expense_type == ExpenseType.EXACT.value:
        # Check if the sum of shares equals the total amount
        total_shares = sum(participant.share for participant in expense.participants)
        if total_shares != expense.total_amount:
            raise expense_exceptions.ExpenseValidationException("Total shares must equal the total amount for EXACT expense type.")
        for participant in expense.participants:
            user_expense = dict(share=participant.share, user_id=participant.user_id)
            user_expenses.append(user_expense)
            
    elif expense.expense_type == ExpenseType.PERCENT.value:
        # Check if the total percentage is 100
        total_percent = sum(participant.share for participant in expense.participants)
        if total_percent != 100:
            raise expense_exceptions.ExpenseValidationException("Total percentage shares must equal 100 for PERCENT expense type.")
        
        # Calculate share amount based on percentages
        for participant in expense.participants:
            participant.share = (participant.share / 100) * expense.total_amount
            user_expense = dict(share=participant.share, user_id=participant.user_id)
            user_expenses.append(user_expense)
            
    else:
        raise expense_exceptions.ExpenseValidationException("Invalid expense type: " + expense.expense_type)
    expense = _create_expense_participants_entry(user_expenses, expense)
    _send_email(expense)
    return expense


def get_balance_by_user(user_id: int) -> List:
    
    """Get Balances of the user

    Args:
        user_id (int): User Id for the fetching user balances

    Raises:
        user_exceptions.UserDoesNotExists: When user does not exists in the DB

    Returns:
        List: User Expenses
    """
    if not find_user_by_id(user_id):
        raise user_exceptions.UserDoesNotExists(user_id)
    expense_participant = find_all_expense_by_user(user_id)
    return _convert_expenses_by_user_to_dict(expense_participant)


def get_by_lender_id(lender_id: int) -> dict:
    """Find all the data for a lender

    Args:
        lender_id (int): User id of the lender

    Raises:
        user_exceptions.UserDoesNotExists: When lender does not exists in the DB

    Returns:
        dict: Users to lender dictionary
    """
    if not find_user_by_id(lender_id):
        raise user_exceptions.UserDoesNotExists(lender_id)
    expense_participants = find_all_expense_by_user(lender_id)
    return _calculate_balances(expense_participants)


def _create_expense_participants_entry(user_expenses: dict, expense: ExpenseRequest) -> Expense:
    """Creating entry in Expense Participants

    Args:
        user_expenses (dict): User Expenses Dict
        expense (ExpenseRequest): Actual Expense

    Returns:
        Expense: Expense created in DB
    """
    total_shares = len(user_expenses)
    expense = Expense(
        user_id=expense.lender_id,
        name=expense.expense_name,
        amount=expense.total_amount,
        expense_type=expense.expense_type,
        total_shares=total_shares,
        notes=expense.notes
    )
    get_session().add(expense)
    get_session().commit()
    
    for user_expense in user_expenses:
        expense_participant = ExpenseParticipant(
            expense_id=expense.expense_id, 
            user_id=user_expense["user_id"],
            share_amount=user_expense["share"]
        )
        get_session().add(expense_participant)
        
    get_session().commit()
    return expense

def get_all_balances(simplify: bool) -> dict:
    """Get all the balances for all users

    Args:
        simplify (bool): If simplify is true then minimum amount between the users will be shared

    Returns:
        dict: Balances of the users
    """
    expense_participants = get_session().query(ExpenseParticipant).all()
    amount = _calculate_balances(expense_participants)
    if simplify:
        return _simplify_data(amount)
    return amount
    

def add_user_in_db(user: UserCreate) -> User:
    """Add a new user to the database.

    Args:
        user (UserCreate): The user object to be added.

    Raises:
        user_exceptions.UserAlreadyExists: Raised if the user already exists in the database.

    Returns:
        User: The created user object.
    """
    if find_user_by_email(user.email):
        raise user_exceptions.UserAlreadyExists(f"{user.email}")

    user_obj = User(
        name=user.name,
        email=user.email,
        mobile_number=user.mobile_number
    )

    get_session().add(user_obj)
    get_session().commit()
    return user_obj


def _calculate_balances(expense_participants: List[ExpenseParticipant]) -> dict:
    """Calculate balances based on expense participants.

    Args:
        expense_participants (List[ExpenseParticipant]): The list of expense participants.

    Returns:
        dict: A dictionary containing balances.
    """
    for data in expense_participants:
        data.payer = data.expense.user_id
    response = {}
    for data in expense_participants:
        user_id = data.user_id
        payer = data.payer
        share = data.share_amount
        if user_id == payer:
            continue
        response.setdefault(payer, {}).setdefault(user_id, 0.0)
        response[payer][user_id] += share
    return response


def _simplify_data(amount_owed: dict) -> dict:
    """Simplify debt data.

    Args:
        amount_owed (dict): The debt data to be simplified.

    Returns:
        dict: The simplified debt data.
    """
    amount_data = []
    for lender, borrowers_dict in amount_owed.items():
        for borrower, amount in borrowers_dict.items():
            amount_data.append([lender, borrower, amount])

    user_and_balance = {}
    for data in amount_data:
        lender = data[0]
        borrower = data[1]
        amount = data[2]
        user_and_balance[lender] = user_and_balance.get(lender, 0) - amount
        user_and_balance[borrower] = user_and_balance.get(borrower, 0) + amount

    amount = list(user_and_balance.values())
    users = list(user_and_balance.keys())
    data_to_return = _min_cash_flow(amount)
    return _convert_to_user_data(data_to_return, users)


def _convert_to_user_data(data_to_return: dict, users: List[str]) -> dict:
    """Change index number to user_id.

    Args:
        data_to_return (dict): The data to be converted.
        users (List[str]): The list of user IDs.

    Returns:
        dict: The converted data.
    """
    new_dict = {}
    for key, value in data_to_return.items():
        if isinstance(value, dict):
            new_dict[users[key]] = _convert_to_user_data(value, users)
        else:
            new_dict[users[key]] = value
    return new_dict


def _get_min(arr: List[float]) -> int:
    """Get the index of the minimum value in an array.

    Args:
        arr (List[float]): The list of floats.

    Returns:
        int: The index of the minimum value.
    """
    min_index = 0
    for i in range(1, len(arr)):
        if arr[i] < arr[min_index]:
            min_index = i
    return min_index


def _get_max(arr: List[float]) -> int:
    """Get the index of the maximum value in an array.

    Args:
        arr (List[float]): The list of floats.

    Returns:
        int: The index of the maximum value.
    """
    max_index = 0
    for i in range(1, len(arr)):
        if arr[i] > arr[max_index]:
            max_index = i
    return max_index


def _min_cash_flow(amount_list: List[float], data_to_return: dict = {}) -> dict:
    """Perform minimum cash flow algorithm to simplify debt.

    Args:
        amount_list (List[float]): The list of amounts.
        data_to_return (dict, optional): The data to be returned. Defaults to {}.

    Returns:
        dict: The simplified data.
    """
    receiver = _get_min(amount_list)
    giver = _get_max(amount_list)

    if amount_list[receiver] == 0 and amount_list[giver] == 0:
        return 0

    min_amount = min(-amount_list[receiver], amount_list[giver])
    amount_list[receiver] += min_amount
    amount_list[giver] -= min_amount

    if receiver not in data_to_return:
        data_to_return[receiver] = {}

    data_to_return[receiver][giver] = min_amount
    _min_cash_flow(amount_list, data_to_return)

    return data_to_return


def _convert_expenses_by_user_to_dict(expense_participants: ExpenseParticipant) -> dict:
    """Convert expenses by user to dictionary.

    Args:
        expense_participants (ExpenseParticipant): The expense participants.

    Returns:
        dict: The converted dictionary.
    """
    response = []
    for expense_participant in expense_participants:
        response.append(
            dict(name=expense_participant.expense.name, 
                 created_at=expense_participant.expense.created_at,
                 share=expense_participant.share_amount,
                 lender_id=expense_participant.expense.user_id,
                 lender_name=expense_participant.expense.user.name,
                 total_expense=expense_participant.expense.amount,
                 email=expense_participant.expense.user.email)
        )
    return response

def _send_email(expense: Expense) -> None:
    """
    Send email notification about the created expense.

    Args:
        expense (Expense): The expense object representing the created expense.

    Returns:
        None
    """
    # Prepare email data
    request = {}
    request["expense_name"] = expense.name
    request["total_amount"] = expense.amount
    request["expense_payer"] = expense.user.name
    request["user_shares"] = []

    # Retrieve expense participants
    expense_participants = find_expense_participants_by_expense_id(expense.expense_id)

    # Populate user shares data
    for expense_participant in expense_participants:
        request["user_shares"].append(
            dict(user_email=expense_participant.user.email, amount=expense_participant.share_amount)
        )

    # Send the expense created email
    send_email.send_expense_created_email(request)


def weekly_report():
    print("Weekly report")
    user_ids = find_all_user_ids()
    for user in user_ids:
        user_data = get_balance_by_user(user)
        send_email.send_weekly_reminder_email(user_data)
    