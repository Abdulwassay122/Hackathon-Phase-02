from passlib.context import CryptContext

# Configure password hashing context with bcrypt
# Cost factor 12 provides good balance between security and performance (~300ms per hash)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password to hash

    Returns:
        Bcrypt hash of the password (60 characters, starts with $2b$12$)

    Example:
        >>> hashed = hash_password("SecurePass123")
        >>> print(hashed)
        $2b$12$abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQR
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        plain_password: Plaintext password to verify
        hashed_password: Bcrypt hash to compare against

    Returns:
        True if password matches hash, False otherwise

    Example:
        >>> hashed = hash_password("SecurePass123")
        >>> verify_password("SecurePass123", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)
