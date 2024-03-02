class UserAlreadyExists(Exception):
    """Exception raised when a user already exists."""

    def __init__(self, email):
        self.email = email
        super().__init__(f"User with email {email} already exists")
        
class UserDoesNotExists(Exception):
    """Exception raised when a user does not exists."""

    def __init__(self, id):
        self.id = id
        super().__init__(f"User with id {id} does not exists")