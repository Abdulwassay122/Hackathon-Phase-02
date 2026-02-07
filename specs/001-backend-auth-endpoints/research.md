# Research: Backend Authentication Endpoints

**Feature**: 001-backend-auth-endpoints
**Date**: 2026-02-07
**Status**: Complete

## Overview

This document captures research findings and technical decisions for implementing user authentication endpoints in the FastAPI backend. The research focuses on password hashing, JWT token generation, User model design, and integration with existing authentication infrastructure.

## Research Areas

### 1. Password Hashing with bcrypt

**Decision**: Use passlib library with bcrypt algorithm and cost factor 12

**Rationale**:
- bcrypt is industry-standard for password hashing (OWASP recommended)
- Adaptive hashing algorithm that remains secure as hardware improves
- Built-in salt generation (no need to manage salts separately)
- Cost factor 12 provides good balance between security and performance (~300ms per hash)
- passlib provides clean Python API: `pwd_context.hash()` and `pwd_context.verify()`

**Implementation Pattern**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password
is_valid = pwd_context.verify(plain_password, hashed_password)
```

**Alternatives Considered**:
- argon2: More modern but requires additional C dependencies, overkill for this scale
- scrypt: Good alternative but bcrypt is more widely adopted and tested
- PBKDF2: Older standard, bcrypt is preferred for new applications

**Security Considerations**:
- Never log or expose plaintext passwords
- Hash passwords synchronously (FastAPI handles async wrapping)
- Use constant-time comparison (passlib handles this internally)
- Cost factor 12 provides ~300ms hashing time (acceptable for signup/login)

### 2. JWT Token Generation

**Decision**: Use PyJWT library with HS256 algorithm and existing BETTER_AUTH_SECRET

**Rationale**:
- PyJWT already installed and used by existing jwt_handler.py
- HS256 (HMAC-SHA256) is symmetric algorithm suitable for single-service architecture
- Must use same secret (BETTER_AUTH_SECRET) for compatibility with existing verification
- Token structure must match existing verification expectations

**Implementation Pattern**:
```python
import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),  # Subject claim (user ID as string)
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)  # Expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
```

**Token Structure**:
- `sub` claim: User ID as string (required by existing verification)
- `email` claim: User email for convenience
- `exp` claim: Expiration timestamp (24 hours from issuance)
- Algorithm: HS256 (must match JWT_ALGORITHM in config)

**Alternatives Considered**:
- RS256 (asymmetric): Overkill for single-service architecture, adds key management complexity
- Refresh tokens: Out of scope per spec, can be added later if needed
- Longer expiration: 24 hours is reasonable balance between security and UX

**Integration with Existing Verification**:
- Existing `jwt_handler.py` has `verify_token()` function
- Must ensure generated tokens pass existing verification
- User ID in "sub" claim must be extractable by existing code
- No changes to verification logic required

### 3. User Model Design

**Decision**: SQLModel with email (unique), password_hash, name, id (integer), timestamps

**Rationale**:
- SQLModel provides both Pydantic validation and SQLAlchemy ORM
- Email as unique identifier (no separate username field per spec assumptions)
- Integer ID for compatibility with Task model's user_id foreign key
- Timestamps (created_at, updated_at) for audit trail
- Password stored as hash, never plaintext

**Schema Design**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Validation Rules**:
- Email: Valid email format (Pydantic EmailStr)
- Password: Minimum 8 characters, at least one letter and one number (validated before hashing)
- Name: Required, non-empty string
- Unique constraint on email enforced at database level

**Alternatives Considered**:
- UUID for user ID: Integer is simpler and matches existing Task model
- Separate username field: Email-only is simpler and sufficient per spec
- Soft delete flag: Out of scope, can be added later if needed

**Relationship with Task Model**:
- Task model has `user_id: int` foreign key
- User model doesn't need explicit relationship definition (one-way reference)
- Task isolation by user_id continues to work unchanged

### 4. API Endpoint Design

**Decision**: POST /api/auth/signup and POST /api/auth/login with JSON request/response

**Rationale**:
- RESTful convention: POST for resource creation (signup) and authentication (login)
- JSON format for request bodies (standard for modern APIs)
- Consistent response structure: `{"access_token": "...", "token_type": "bearer"}`
- Proper HTTP status codes per REST conventions

**Signup Endpoint**:
```
POST /api/auth/signup
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}

Response (201 Created):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}

Error (409 Conflict - duplicate email):
{
  "detail": "Email already registered"
}

Error (400 Bad Request - validation):
{
  "detail": "Password must be at least 8 characters"
}
```

**Login Endpoint**:
```
POST /api/auth/login
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response (200 OK):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}

Error (401 Unauthorized):
{
  "detail": "Invalid email or password"
}
```

**Security Considerations**:
- Generic error message for login failures (don't reveal if email exists)
- Rate limiting not implemented (out of scope, can be added later)
- No CAPTCHA (out of scope)
- HTTPS required in production (handled by deployment, not application code)

**Alternatives Considered**:
- OAuth2 password flow: More complex, not needed for this simple use case
- Separate token endpoint: Simpler to return token directly from signup/login
- Cookie-based auth: JWT in Authorization header is more flexible for API

### 5. Input Validation

**Decision**: Pydantic models for request validation with custom validators

**Rationale**:
- FastAPI automatically validates request bodies using Pydantic
- Custom validators for password complexity and email format
- Clear error messages for validation failures
- Validation happens before business logic

**Validation Models**:
```python
from pydantic import BaseModel, EmailStr, validator
import re

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
```

**Validation Rules**:
- Email: Valid format (handled by EmailStr)
- Password: Min 8 chars, at least one letter, at least one number
- Name: Non-empty after stripping whitespace
- All fields required (no optional fields)

**Error Handling**:
- Pydantic validation errors return 422 Unprocessable Entity
- Business logic errors (duplicate email, invalid credentials) return appropriate status codes
- All errors include descriptive messages

### 6. Database Migration Strategy

**Decision**: SQLModel.metadata.create_all() for table creation (existing pattern)

**Rationale**:
- Existing codebase uses SQLModel.metadata.create_all() in init_db.py
- Simple approach suitable for development and small-scale deployment
- User table will be created automatically on first startup
- No migration tool needed for this phase

**Implementation**:
- Add User model import to init_db.py
- SQLModel will detect new table and create it
- Unique constraint on email enforced at database level
- No data migration needed (new table, no existing data)

**Alternatives Considered**:
- Alembic migrations: More robust but adds complexity, not needed for this scale
- Manual SQL scripts: Less maintainable than SQLModel approach
- Separate migration command: Existing pattern is automatic on startup

**Future Considerations**:
- For production, consider Alembic for schema versioning
- For this phase, automatic table creation is sufficient

### 7. Error Handling and Security

**Decision**: Generic error messages for authentication failures, specific messages for validation

**Rationale**:
- Don't reveal whether email exists (prevents user enumeration)
- Provide helpful validation errors for user experience
- Log authentication failures for security monitoring
- Return appropriate HTTP status codes

**Error Response Patterns**:
- 400 Bad Request: Validation errors (specific messages)
- 401 Unauthorized: Invalid credentials (generic message)
- 409 Conflict: Duplicate email (specific message acceptable)
- 422 Unprocessable Entity: Pydantic validation errors

**Security Logging**:
- Log failed login attempts with email (for monitoring)
- Log successful signups and logins
- Don't log passwords (plaintext or hashed)
- Use existing logging_config.py infrastructure

**Timing Attack Prevention**:
- passlib.verify() uses constant-time comparison
- No need for additional timing attack mitigation
- Password hashing time dominates response time (~300ms)

## Implementation Checklist

- [ ] Install passlib[bcrypt] dependency
- [ ] Create User model in backend/src/models/user_model.py
- [ ] Create password utilities in backend/src/auth/password.py
- [ ] Add token generation function to backend/src/auth/jwt_handler.py
- [ ] Create auth routes in backend/src/api/auth_routes.py
- [ ] Register auth routes in backend/src/main.py
- [ ] Update init_db.py to include User model
- [ ] Create Pydantic request/response models
- [ ] Add input validation for password complexity
- [ ] Implement error handling with appropriate status codes
- [ ] Add security logging for auth events
- [ ] Test signup endpoint (create user, return token)
- [ ] Test login endpoint (verify credentials, return token)
- [ ] Test token compatibility with existing verification
- [ ] Test duplicate email rejection
- [ ] Test password validation rules

## Dependencies

**New Dependencies**:
- passlib[bcrypt]: Password hashing library

**Existing Dependencies** (already installed):
- FastAPI: Web framework
- SQLModel: ORM and validation
- PyJWT: JWT token handling
- psycopg2-binary: PostgreSQL driver
- pydantic: Data validation

## Risk Assessment

**Low Risk**:
- Password hashing: Well-established library (passlib) with proven security
- JWT generation: Using existing PyJWT library, compatible with existing verification
- User model: Simple schema with standard fields

**Medium Risk**:
- Database unique constraint: Must handle duplicate email gracefully (409 response)
- Token compatibility: Must ensure generated tokens work with existing verification (mitigated by using same secret and algorithm)

**Mitigation Strategies**:
- Test token generation/verification integration early
- Handle database constraint violations explicitly
- Use existing logging infrastructure for security monitoring
- Follow existing code patterns for consistency

## Next Steps

1. Proceed to Phase 1: Design (data-model.md, contracts/, quickstart.md)
2. Generate detailed data model specification
3. Create OpenAPI contracts for signup and login endpoints
4. Create quickstart guide for testing authentication endpoints
5. Update agent context with new dependencies
6. Proceed to Phase 2: Tasks (tasks.md generation via /sp.tasks)
