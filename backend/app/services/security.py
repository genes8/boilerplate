"""Security utilities for password hashing and verification."""

import bcrypt

# Cost factor for bcrypt (12 is recommended for production)
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        str: Hashed password string.

    Example:
        >>> hashed = hash_password("mysecretpassword")
        >>> hashed.startswith("$2b$")
        True
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to compare against.

    Returns:
        bool: True if password matches, False otherwise.

    Example:
        >>> hashed = hash_password("mysecretpassword")
        >>> verify_password("mysecretpassword", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be rehashed.

    This is useful when upgrading the hashing algorithm or cost factor.

    Args:
        hashed_password: Hashed password to check.

    Returns:
        bool: True if password needs rehashing, False otherwise.
    """
    # Check if the hash uses the current cost factor
    try:
        # Extract rounds from hash (format: $2b$XX$...)
        parts = hashed_password.split("$")
        if len(parts) >= 3:
            current_rounds = int(parts[2])
            return current_rounds < BCRYPT_ROUNDS
    except (ValueError, IndexError):
        pass
    return True
