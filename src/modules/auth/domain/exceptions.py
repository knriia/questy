class AuthError(Exception):
    pass


class CredentialsValidationError(AuthError):
    code = "invalid_credentials"

    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message)


class InvalidPasswordError(CredentialsValidationError):
    code = "invalid_password"


class InvalidSessionExpirationError(AuthError):
    pass


class InvalidTokenExpirationError(AuthError):
    pass
