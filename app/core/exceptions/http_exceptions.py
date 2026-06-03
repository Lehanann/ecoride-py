from fastapi import HTTPException, status


"""
Helper functions to standardize HTTP exceptions across the application.
"""

def bad_request(detail: str = "Bad request") -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=detail)

def unauthorized(detail: str = "Unauthorized") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=detail)

def not_found(detail: str = "Resource not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=detail)

def conflict(detail: str = "Conflict") -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT,detail=detail)

def forbidden(detail: str = "Forbidden") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=detail)