import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from db.models import EmailQueue
from db.connection import get_session
from datetime import datetime
import threading
from typing import List

# Get SendGrid API key from environment variable
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "info@splitwise.com")

email_lock = threading.Lock()
def _send_email(recipient_email, subject, body) -> None:
    """
    Send an email using SendGrid API.

    Args:
        sender_email (str): Email address of the sender.
        recipient_email (str): Email address of the recipient.
        subject (str): Subject of the email.
        body (str): Body content of the email in HTML format.

    Returns:
        None

    Raises:
        Exception: If there is an error sending the email.

    """
    # Create message object for sending email
    email_lock.acquire()
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=recipient_email,
        subject=subject,
        html_content=body
    )
    # Create EmailQueue entry for the sent email
    email = EmailQueue(
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        sent_at=datetime.now()
    )
    try:
        # Attempt to send email using SendGrid API
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        # Update is_sent flag based on response status code
        if response.status_code == 200 or response.status_code == 201:
            email.is_sent = True
        else:
            email.is_sent = False
        
    except Exception as e:
        # Handle exception and mark email as not sent
        print(str(e))
        email.is_sent = False
    finally:
        # Commit changes to the database session
        get_session().add(email)
        get_session().commit()
        email_lock.release()


def send_expense_created_email(expense_details: dict) -> None:
    """
    Sends an email notifying the creation of an expense.

    Args:
        recipient_email (str): Email address of the recipient.
        expense_name (str): Name of the expense created.
        total_amount (float): Total amount of the expense.

    Returns:
        None
    """
    expense_name = expense_details["expense_name"]
    total_amount = expense_details["total_amount"]
    expense_payer = expense_details["expense_payer"]
    
    for shares in expense_details["user_shares"]:
        email = shares["user_email"]
        amount = shares["amount"]
        subject = f"Expense Created: {expense_name} by {expense_payer}"
        body = f"An expense named '{expense_name}' has been created with a total amount of ${total_amount} and your share: ${amount}"
        # Fire off the email sending operation asynchronously
        threading.Thread(target=_send_email, args=(email, subject, body)).start()

def send_weekly_reminder_email(reminder_data: dict) -> None:
    """
    Sends a weekly reminder email containing expense details for a single user.

    Args:
        reminder_data (dict): Dictionary containing expense details for a single user.

    Returns:
        None
    """
    recipient_email = reminder_data["email"]
    subject = "Weekly Expense Reminder"
    body = "Hello,\n\nHere's your weekly expense reminder:\n\n"
    for expense_details in reminder_data["expenses"]:
        body += f"Expense Name: {expense_details['name']}\n"
        body += f"Created At: {expense_details['created_at']}\n"
        body += f"Share Amount: {expense_details['share']}\n"
        body += f"Lender ID: {expense_details['lender_id']}\n"
        body += f"Lender Name: {expense_details['lender_name']}\n"
        body += f"Total Expense: {expense_details['total_expense']}\n\n"
    # Fire off the email sending operation asynchronously
    threading.Thread(target=_send_email, args=(recipient_email, subject, body)).start()
