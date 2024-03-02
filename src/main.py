from fastapi import FastAPI
from db import models
from db.connection import engine
from controller import users, expense, balances
from schedulers import weekly_scheduler

# Create database tables based on the models
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI()

# Include routers for different endpoints
app.include_router(users.router)  # Endpoint for user-related operations
app.include_router(expense.router)  # Endpoint for expense-related operations
app.include_router(balances.router)  # Endpoint for balance-related operations

if __name__ == "__main__":
    # Schedule the task when the script starts
    weekly_scheduler.Scheduler.schedule_task()
    # Run the scheduler
    weekly_scheduler.Scheduler.run_scheduler()