class AppException(Exception):
    pass

class UserAlreadyExistsException(AppException):
    def __init__(self, message: str = "User with this phone already exists."):
        self.message = message
        super().__init__(self.message)

class UserNotFoundException(AppException):
    def __init__(self, message: str = "User not found."):
        self.message = message
        super().__init__(self.message)

class ExternalServiceException(AppException):
    def __init__(self, message: str = "Error during external service call."):
        self.message = message
        super().__init__(self.message)

class DependencyException(AppException):
    def __init__(self, message: str = "Error initializing dependency."):
        self.message = message
        super().__init__(self.message)
