class DevflowError(Exception):
    # Base for every domain error, so the routers can catch a single type
    # instead of enumerating them one by one.
    pass


class UserAlreadyExistsError(DevflowError):
    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f'user with this {field} already exists')
