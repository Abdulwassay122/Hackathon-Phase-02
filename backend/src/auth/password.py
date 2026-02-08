from passlib.context import CryptContext
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Configure password hashing context with bcrypt
# Cost factor 12 provides good balance between security and performance (~300ms per hash)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def truncate_password(password: str) -> str:
    """
    Truncate password to 72 bytes to comply with bcrypt's byte limit.

    Bcrypt has a hard limit of 72 bytes. This function ensures passwords
    are truncated before hashing or verification to prevent errors.

    The truncation process:
    1. Encode password to UTF-8 bytes
    2. Truncate to first 72 bytes
    3. Decode back to string, ignoring incomplete multi-byte characters

    Args:
        password: Plaintext password (any length)

    Returns:
        Password truncated to 72 bytes (UTF-8 encoded)

    Example:
        >>> short = truncate_password("ShortPass123")
        >>> short == "ShortPass123"
        True
        >>> long = truncate_password("A" * 100)
        >>> len(long.encode('utf-8')) <= 72
        True
        >>> emoji = truncate_password("😀" * 30)  # Each emoji is 4 bytes
        >>> len(emoji.encode('utf-8')) <= 72
        True
    """
    try:
        # Encode to UTF-8 and truncate to 72 bytes
        password_bytes = password.encode('utf-8')[:72]

        # Decode back to string, ignoring incomplete multi-byte characters at boundary
        # errors='ignore' drops any incomplete UTF-8 sequences at the 72-byte boundary
        truncated = password_bytes.decode('utf-8', errors='ignore')

        return truncated

    except Exception as e:
        # Log error but don't expose password in logs
        logger.error(f"Password truncation error: {type(e).__name__}")
        raise ValueError("Failed to process password") from e


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Automatically truncates password to 72 bytes before hashing to prevent
    bcrypt byte-length errors.

    Args:
        password: Plaintext password to hash (any length)

    Returns:
        Bcrypt hash of the password (60 characters, starts with $2b$12$)

    Example:
        >>> hashed = hash_password("SecurePass123")
        >>> print(hashed)
        $2b$12$abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQR
        >>> long_hashed = hash_password("A" * 100)  # Works without error
        >>> len(long_hashed) == 60
        True
    """
    # Truncate password to 72 bytes before hashing
    truncated = truncate_password(password)
    return pwd_context.hash(truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Automatically truncates password to 72 bytes before verification to ensure
    consistency with hash_password() behavior.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        plain_password: Plaintext password to verify (any length)
        hashed_password: Bcrypt hash to compare against

    Returns:
        True if password matches hash, False otherwise

    Example:
        >>> hashed = hash_password("SecurePass123")
        >>> verify_password("SecurePass123", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
        >>> long_pass = "A" * 100
        >>> long_hashed = hash_password(long_pass)
        >>> verify_password(long_pass, long_hashed)  # Works without error
        True
    """
    # Truncate password to 72 bytes before verification
    truncated = truncate_password(plain_password)
    return pwd_context.verify(truncated, hashed_password)
