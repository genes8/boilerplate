"""Unit tests for security service (password hashing)."""

import pytest

from app.services.security import hash_password, needs_rehash, verify_password


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_returns_string(self) -> None:
        """Test that hash_password returns a string."""
        password = "mysecretpassword123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)

    def test_hash_password_returns_bcrypt_hash(self) -> None:
        """Test that hash_password returns a bcrypt hash."""
        password = "mysecretpassword123"
        hashed = hash_password(password)
        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")

    def test_hash_password_different_for_same_input(self) -> None:
        """Test that hashing same password twice gives different hashes (salt)."""
        password = "mysecretpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct(self) -> None:
        """Test that verify_password returns True for correct password."""
        password = "mysecretpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self) -> None:
        """Test that verify_password returns False for incorrect password."""
        password = "mysecretpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self) -> None:
        """Test verify_password with empty password."""
        password = "mysecretpassword123"
        hashed = hash_password(password)
        assert verify_password("", hashed) is False

    def test_hash_password_empty_string(self) -> None:
        """Test that empty string can be hashed."""
        hashed = hash_password("")
        assert isinstance(hashed, str)
        assert verify_password("", hashed) is True

    def test_hash_password_unicode(self) -> None:
        """Test that unicode passwords work correctly."""
        password = "пароль123🔐"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_hash_password_long_password(self) -> None:
        """Test that long passwords work correctly."""
        password = "a" * 1000
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_needs_rehash_current_hash(self) -> None:
        """Test that current hashes don't need rehashing."""
        password = "mysecretpassword123"
        hashed = hash_password(password)
        assert needs_rehash(hashed) is False
