class UserError(Exception):
    pass


class UserValidationError(UserError):
    code = "invalid_user_data"

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidUsernameError(UserValidationError):
    code = "invalid_username"


class InvalidEmailError(UserValidationError):
    code = "invalid_email"


class InvalidPasswordError(UserValidationError):
    code = "invalid_password"


class InvalidTimezoneError(UserValidationError):
    code = "invalid_timezone"


class UserConflictError(UserError):
    code = "user_conflict"


class EmailAlreadyExistsError(UserConflictError):
    code = "email_already_exists"

    def __init__(self) -> None:
        super().__init__("Email is already registered")


class UsernameAlreadyExistsError(UserConflictError):
    code = "username_already_exists"

    def __init__(self) -> None:
        super().__init__("Username is already registered")
