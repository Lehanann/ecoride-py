
class DataIntegrityError(Exception):
    """Raised when the system is in an invalid data state."""
    def __init__(self, message: str):
        super().__init__(message)