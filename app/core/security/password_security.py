from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_password_hash(password: str) -> str:
    """
    Function to create password hash
    Args:
        password:

    Returns:
        password_hash (str): Password hashed
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Function to verify password.
    Args:
        plain_password (str): password to be verified
        hashed_password (str): hashed password to be verified

    Returns:
        result (bool): result of verifying password
    """
    return pwd_context.verify(plain_password, hashed_password)

