class DevflowError(Exception):
    # Base for every domain error, so the routers can catch a single type
    # instead of enumerating them one by one.
    pass


class UserAlreadyExistsError(DevflowError):
    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f'user with this {field} already exists')


class UserNotFoundError(DevflowError):
    def __init__(self, message: str = 'user not found') -> None:
        super().__init__(message)


class InvalidCredentialsError(DevflowError):
    # Raised for a missing email and for a wrong password alike: telling them
    # apart would let anyone check which emails are registered.
    def __init__(self, message: str = 'incorrect credentials') -> None:
        super().__init__(message)
