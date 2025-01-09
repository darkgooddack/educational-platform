class AppException(Exception):
    pass

# User exceptions
class UserAlreadyExistsException(AppException):
    def __init__(self, message: str = "User with this phone already exists."):
        self.message = message
        super().__init__(self.message)

class UserNotFoundException(AppException):
    def __init__(self, message: str = "User not found."):
        self.message = message
        super().__init__(self.message)

class ExternalServiceException(AppException):
    def __init__(self, service_name: str, message: str = "External service error."):
        self.service_name = service_name
        self.message = f"{service_name}: {message}"
        super().__init__(self.message)

class UserFetchFailedException(ExternalServiceException):
    def __init__(self, message: str = "Failed to fetch user data from the registration service."):
        super().__init__("RegistrationService", message)

class UserAuthenticationException(AppException):
    def __init__(self, message: str = "Invalid email or password."):
        self.message = message
        super().__init__(self.message)


# Token exceptions
class TokenGenerationException(AppException):
    def __init__(self, message: str = "Error generating tokens.") -> None:
        super().__init__(message)

class InvalidTokenException(AppException):
    def __init__(self, message: str = "Invalid token.") -> None:
        super().__init__(message)

class TokenExpiredException(AppException):
    def __init__(self, message: str = "Token has expired.") -> None:
        super().__init__(message)


# Database exceptions
class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed."):
        self.message = message
        super().__init__(self.message)


# Other
class DependencyException(AppException):
    def __init__(self, message: str = "Error initializing dependency."):
        self.message = message
        super().__init__(self.message)


