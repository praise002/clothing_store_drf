class ErrorCode:
    """
    A class to represent various error codes as constants.
    """
    # Authentication & Authorization
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    TOKEN_INVALID = "token_invalid"
    TOKEN_EXPIRED = "token_expired"
    
    # Resource States
    NON_EXISTENT = "non_existent"
    ALREADY_EXISTS = "already_exists"
    ALREADY_VERIFIED = "already_verified"
    OUT_OF_STOCK = "out_of_stock"
    EMPTY = "empty"
    
    # Validation
    INVALID_INPUT = "invalid_input"
    INVALID_STATUS = "invalid_status"
    VALIDATION_ERROR = "validation_error"
    PASSWORDS_MISMATCH = "passwords_mismatch"
    
    # Payment
    PAYMENT_ERROR = "payment_error"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_CANCELLED = "payment_cancelled"
    
    # Processing
    BAD_REQUEST = "bad_request"
    SERVER_ERROR = "server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    OPERATION_FAILED = "operation_failed"
    
    # Time-based
    EXPIRED = "expired"
    TOO_LATE = "too_late"
    TOO_EARLY = "too_early"