class ExpenseValidationException(Exception):
    """Exception raised when a expense is invalid."""

    def __init__(self, message):
        self.message = message
        super().__init__(f"{message}")