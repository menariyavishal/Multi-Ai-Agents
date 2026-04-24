"""Custom exceptions for the application."""

from typing import Optional


class ApplicationError(Exception):
    """Base exception for application errors."""
    pass


class RateLimitExceeded(ApplicationError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        """Initialize RateLimitExceeded exception.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        super().__init__(message)
        self.retry_after = retry_after


class ValidationError(ApplicationError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Validation failed", field: Optional[str] = None):
        """Initialize ValidationError exception.
        
        Args:
            message: Error message
            field: Optional field name that failed validation
        """
        super().__init__(message)
        self.field = field


class WorkflowError(ApplicationError):
    """Raised when workflow processing fails."""
    
    def __init__(self, message: str = "Workflow processing failed", step: Optional[str] = None):
        """Initialize WorkflowError exception.
        
        Args:
            message: Error message
            step: Optional workflow step that failed
        """
        super().__init__(message)
        self.step = step


class DatabaseError(ApplicationError):
    """Raised when database operation fails."""
    
    def __init__(self, message: str = "Database operation failed", operation: Optional[str] = None):
        """Initialize DatabaseError exception.
        
        Args:
            message: Error message
            operation: Optional database operation that failed
        """
        super().__init__(message)
        self.operation = operation


class AuthenticationError(ApplicationError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        """Initialize AuthenticationError exception.
        
        Args:
            message: Error message
        """
        super().__init__(message)


class AuthorizationError(ApplicationError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Authorization failed"):
        """Initialize AuthorizationError exception.
        
        Args:
            message: Error message
        """
        super().__init__(message)


class NotFoundError(ApplicationError):
    """Raised when requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found", resource_type: Optional[str] = None):
        """Initialize NotFoundError exception.
        
        Args:
            message: Error message
            resource_type: Type of resource not found
        """
        super().__init__(message)
        self.resource_type = resource_type


class TimeoutError(ApplicationError):
    """Raised when operation times out."""
    
    def __init__(self, message: str = "Operation timed out", timeout_seconds: Optional[float] = None):
        """Initialize TimeoutError exception.
        
        Args:
            message: Error message
            timeout_seconds: Timeout duration in seconds
        """
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


class ConfigurationError(ApplicationError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str = "Configuration error", key: Optional[str] = None):
        """Initialize ConfigurationError exception.
        
        Args:
            message: Error message
            key: Optional configuration key that is invalid
        """
        super().__init__(message)
        self.key = key
