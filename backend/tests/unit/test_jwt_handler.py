"""
Unit tests for JWT Handler
Tests token verification and user ID extraction
"""
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from src.auth.jwt_handler import JWTHandler


@pytest.fixture
def jwt_handler():
    """Create a JWT handler instance with test secret"""
    return JWTHandler(secret_key="test-secret-key-minimum-32-characters-long", algorithm="HS256")


@pytest.fixture
def valid_token(jwt_handler):
    """Generate a valid JWT token for testing"""
    payload = {
        "sub": "123",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, jwt_handler.secret_key, algorithm=jwt_handler.algorithm)


@pytest.fixture
def expired_token(jwt_handler):
    """Generate an expired JWT token for testing"""
    payload = {
        "sub": "123",
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    return jwt.encode(payload, jwt_handler.secret_key, algorithm=jwt_handler.algorithm)


@pytest.fixture
def invalid_signature_token():
    """Generate a token with invalid signature"""
    payload = {
        "sub": "123",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, "wrong-secret-key", algorithm="HS256")


@pytest.fixture
def nested_user_token(jwt_handler):
    """Generate a token with nested user format"""
    payload = {
        "user": {"id": "456"},
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, jwt_handler.secret_key, algorithm=jwt_handler.algorithm)


class TestJWTHandlerVerifyToken:
    """Tests for JWTHandler.verify_token method"""

    def test_verify_valid_token(self, jwt_handler, valid_token):
        """T027: Test verify_token with valid token returns payload"""
        payload = jwt_handler.verify_token(valid_token)

        assert payload is not None
        assert "sub" in payload
        assert payload["sub"] == "123"
        assert "exp" in payload

    def test_verify_expired_token(self, jwt_handler, expired_token):
        """T028: Test verify_token with expired token raises 401"""
        with pytest.raises(HTTPException) as exc_info:
            jwt_handler.verify_token(expired_token)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_verify_invalid_signature(self, jwt_handler, invalid_signature_token):
        """T028: Test verify_token with invalid signature raises 401"""
        with pytest.raises(HTTPException) as exc_info:
            jwt_handler.verify_token(invalid_signature_token)

        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()

    def test_verify_malformed_token(self, jwt_handler):
        """T028: Test verify_token with malformed token raises 401"""
        with pytest.raises(HTTPException) as exc_info:
            jwt_handler.verify_token("not-a-valid-jwt-token")

        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()

    def test_verify_token_missing_exp(self, jwt_handler):
        """T028: Test verify_token with missing exp claim raises 401"""
        payload = {"sub": "123"}  # Missing exp
        token = jwt.encode(payload, jwt_handler.secret_key, algorithm=jwt_handler.algorithm)

        with pytest.raises(HTTPException) as exc_info:
            jwt_handler.verify_token(token)

        assert exc_info.value.status_code == 401

    def test_verify_token_missing_sub(self, jwt_handler):
        """T028: Test verify_token with missing sub claim raises 401"""
        payload = {"exp": datetime.utcnow() + timedelta(hours=1)}  # Missing sub
        token = jwt.encode(payload, jwt_handler.secret_key, algorithm=jwt_handler.algorithm)

        with pytest.raises(HTTPException) as exc_info:
            jwt_handler.verify_token(token)

        assert exc_info.value.status_code == 401


class TestJWTHandlerExtractUserId:
    """Tests for JWTHandler.extract_user_id method"""

    def test_extract_user_id_from_sub(self, jwt_handler):
        """T029: Test extract_user_id with standard 'sub' claim"""
        payload = {"sub": "123"}
        user_id = jwt_handler.extract_user_id(payload)

        assert user_id == 123
        assert isinstance(user_id, int)

    def test_extract_user_id_from_nested(self, jwt_handler):
        """T029: Test extract_user_id with nested user.id format"""
        payload = {"user": {"id": "456"}}
        user_id = jwt_handler.extract_user_id(payload)

        assert user_id == 456
        assert isinstance(user_id, int)

    def test_extract_user_id_integer_sub(self, jwt_handler):
        """T029: Test extract_user_id with integer sub claim"""
        payload = {"sub": 789}
        user_id = jwt_handler.extract_user_id(payload)

        assert user_id == 789
        assert isinstance(user_id, int)

    def test_extract_user_id_missing(self, jwt_handler):
        """T029: Test extract_user_id with missing user ID raises 401"""
        payload = {"other": "data"}

        with pytest.raises(HTTPException) as exc_info:
            jwt_handler.extract_user_id(payload)

        assert exc_info.value.status_code == 401
        assert "missing user identifier" in exc_info.value.detail.lower()

    def test_extract_user_id_invalid_format(self, jwt_handler):
        """T029: Test extract_user_id with non-numeric ID raises 401"""
        payload = {"sub": "not-a-number"}

        with pytest.raises(HTTPException) as exc_info:
            jwt_handler.extract_user_id(payload)

        assert exc_info.value.status_code == 401
        assert "invalid user identifier" in exc_info.value.detail.lower()

    def test_extract_user_id_none_value(self, jwt_handler):
        """T029: Test extract_user_id with None value raises 401"""
        payload = {"sub": None}

        with pytest.raises(HTTPException) as exc_info:
            jwt_handler.extract_user_id(payload)

        assert exc_info.value.status_code == 401
