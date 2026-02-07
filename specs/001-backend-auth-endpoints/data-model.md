# Data Model: Backend Authentication Endpoints

**Feature**: 001-backend-auth-endpoints
**Date**: 2026-02-07
**Status**: Complete

## Overview

This document defines the data models for user authentication, including the User entity, request/response schemas, and validation rules.

## Entities

### User (Database Model)

**Purpose**: Represents a registered user in the system with authentication credentials.

**Table Name**: `users`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique identifier for the user |
| email | String(255) | Unique, Not Null, Indexed | User's email address (used for login) |
| password_hash | String(255) | Not Null | Bcrypt hash of user's password |
| name | String(255) | Not Null | User's display name |
| created_at | DateTime | Not Null, Default: UTC now | Timestamp when user was created |
| updated_at | DateTime | Not Null, Default: UTC now | Timestamp when user was last updated |

**Indexes**:
- Primary key index on `id`
- Unique index on `email` (for fast lookup and duplicate prevention)

**Relationships**:
- One-to-Many with Task: One user owns many tasks (via Task.user_id foreign key)
- No explicit relationship definition needed in User model (one-way reference from Task)

**Validation Rules**:
- Email must be valid email format (validated by Pydantic EmailStr)
- Email must be unique across all users (enforced by database constraint)
- Password must be hashed before storage (never store plaintext)
- Name must be non-empty string after trimming whitespace
- Timestamps automatically managed by SQLModel

**SQLModel Definition**:
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

**Security Considerations**:
- Password field is `password_hash`, not `password` (emphasizes it's hashed)
- Never expose password_hash in API responses
- Email is indexed for fast lookup during login
- Unique constraint prevents duplicate registrations

---

## Request Schemas

### SignupRequest

**Purpose**: Validates user registration data submitted to POST /api/auth/signup

**Fields**:

| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| email | EmailStr | Yes | Valid email format |
| password | String | Yes | Min 8 chars, at least 1 letter, at least 1 number |
| name | String | Yes | Non-empty after trimming whitespace |

**Validation Logic**:
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
```

**Example Valid Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Example Invalid Requests**:
```json
// Invalid email format
{
  "email": "not-an-email",
  "password": "SecurePass123",
  "name": "John Doe"
}
// Error: "value is not a valid email address"

// Password too short
{
  "email": "user@example.com",
  "password": "Pass1",
  "name": "John Doe"
}
// Error: "Password must be at least 8 characters"

// Password missing number
{
  "email": "user@example.com",
  "password": "SecurePassword",
  "name": "John Doe"
}
// Error: "Password must contain at least one number"

// Empty name
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "   "
}
// Error: "Name cannot be empty"
```

---

### LoginRequest

**Purpose**: Validates user login credentials submitted to POST /api/auth/login

**Fields**:

| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| email | EmailStr | Yes | Valid email format |
| password | String | Yes | Any non-empty string (validation happens during verification) |

**Validation Logic**:
```python
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

**Example Valid Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Note**: Password validation is minimal for login (only non-empty) because the actual validation happens when comparing against the stored hash. We don't want to reject login attempts based on current password rules if the user registered under different rules.

---

## Response Schemas

### AuthResponse

**Purpose**: Standard response for successful signup or login

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| access_token | String | JWT token for authentication |
| token_type | String | Always "bearer" |
| user | UserResponse | User information (excluding password) |

**Schema Definition**:
```python
from pydantic import BaseModel

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

**Example Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzA3NDM2ODAwfQ.signature",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

### UserResponse

**Purpose**: User information returned in API responses (excludes sensitive data)

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | User's unique identifier |
| email | String | User's email address |
| name | String | User's display name |

**Schema Definition**:
```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True  # Allows creation from SQLModel instances
```

**Security Note**: This schema explicitly excludes:
- `password_hash` (never expose password hashes)
- `created_at` and `updated_at` (not needed for authentication response)

**Example**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe"
}
```

---

## Error Response Schema

### ErrorResponse

**Purpose**: Standard error response format for all authentication endpoints

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| detail | String | Human-readable error message |

**Schema Definition**:
```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
```

**Example Error Responses**:

**400 Bad Request (Validation Error)**:
```json
{
  "detail": "Password must be at least 8 characters"
}
```

**401 Unauthorized (Invalid Credentials)**:
```json
{
  "detail": "Invalid email or password"
}
```

**409 Conflict (Duplicate Email)**:
```json
{
  "detail": "Email already registered"
}
```

**422 Unprocessable Entity (Pydantic Validation)**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## JWT Token Structure

### Token Payload

**Purpose**: Claims included in JWT tokens issued by signup and login endpoints

**Claims**:

| Claim | Type | Description |
|-------|------|-------------|
| sub | String | User ID (as string) - subject of the token |
| email | String | User's email address |
| exp | Integer | Expiration timestamp (Unix epoch) |

**Example Decoded Token**:
```json
{
  "sub": "1",
  "email": "user@example.com",
  "exp": 1707436800
}
```

**Token Generation**:
```python
import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: int, email: str, secret: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token
```

**Compatibility Notes**:
- `sub` claim contains user ID as string (required by existing JWT verification)
- `exp` claim is Unix timestamp (standard JWT expiration)
- Algorithm is HS256 (matches existing verification)
- Secret is BETTER_AUTH_SECRET from environment (matches existing verification)

---

## State Transitions

### User Registration Flow

```
[No User]
    ↓ POST /api/auth/signup with valid data
[User Created in Database]
    ↓ Password hashed with bcrypt
[Password Hash Stored]
    ↓ JWT token generated
[Token Returned to Client]
```

**States**:
1. **No User**: Email does not exist in database
2. **User Created**: User record inserted with hashed password
3. **Authenticated**: Client receives JWT token

**Transitions**:
- Valid signup data → User created + Token issued
- Duplicate email → 409 Conflict (no state change)
- Invalid data → 400/422 Error (no state change)

### User Login Flow

```
[User Exists]
    ↓ POST /api/auth/login with credentials
[Credentials Verified]
    ↓ Password hash comparison
[Authentication Successful]
    ↓ JWT token generated
[Token Returned to Client]
```

**States**:
1. **User Exists**: User record present in database
2. **Credentials Verified**: Password matches stored hash
3. **Authenticated**: Client receives JWT token

**Transitions**:
- Valid credentials → Token issued
- Invalid credentials → 401 Unauthorized (no state change)
- Email not found  401 Unauthorized (no state change, generic message)

---

## Data Flow Diagrams

### Signup Data Flow

```
Client                    API                     Database
  |                        |                          |
  |-- POST /api/auth/signup with email/password/name ->|
  |                        |                          |
  |                   Validate input                  |
  |                        |                          |
  |                   Hash password                   |
  |                        |                          |
  |                        |-- INSERT User ---------->|
  |                        |                          |
  |                        |<-- User ID returned -----|
  |                        |                          |
  |                   Generate JWT                    |
  |                        |                          |
  |<-- 201 Created with token and user data ----------|
```

### Login Data Flow

```
Client                    API                     Database
  |                        |                          |
  |-- POST /api/auth/login with email/password ------>|
  |                        |                          |
  |                   Validate input                  |
  |                        |                          |
  |                        |-- SELECT User by email ->|
  |                        |                          |
  |                        |<-- User record ----------|
  |                        |                          |
  |                   Verify password                 |
  |                        |                          |
  |                   Generate JWT                    |
  |                        |                          |
  |<-- 200 OK with token and user data ---------------|
```

---

## Validation Summary

### Field-Level Validation

| Field | Validation | Error Message |
|-------|------------|---------------|
| email | Valid email format | "value is not a valid email address" |
| email | Unique in database | "Email already registered" |
| password (signup) | Min 8 characters | "Password must be at least 8 characters" |
| password (signup) | Contains letter | "Password must contain at least one letter" |
| password (signup) | Contains number | "Password must contain at least one number" |
| name | Non-empty after trim | "Name cannot be empty" |

### Business Logic Validation

| Scenario | Validation | HTTP Status | Error Message |
|----------|------------|-------------|---------------|
| Duplicate email | Check database | 409 Conflict | "Email already registered" |
| Invalid login | Verify password hash | 401 Unauthorized | "Invalid email or password" |
| Email not found | Check database | 401 Unauthorized | "Invalid email or password" |

---

## Security Considerations

### Password Storage
- Passwords are hashed using bcrypt with cost factor 12
- Plaintext passwords never stored in database
- Password hashes never exposed in API responses
- Hashing is one-way (cannot recover original password)

### Token Security
- Tokens expire after 24 hours
- Tokens signed with BETTER_AUTH_SECRET (minimum 32 characters)
- Tokens use HS256 algorithm (HMAC-SHA256)
- Tokens include user ID for authorization checks

### Input Validation
- All inputs validated before processing
- Email format validated by Pydantic
- Password complexity enforced at signup
- SQL injection prevented by SQLModel parameterization
- XSS prevented by JSON serialization

### Error Messages
- Generic message for login failures (don't reveal if email exists)
- Specific messages for validation errors (help user fix input)
- No sensitive information in error responses
- All authentication failures logged for monitoring

---

## Database Schema

### SQL Schema (PostgreSQL)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### Constraints
- Primary key on `id` (auto-incrementing)
- Unique constraint on `email` (prevents duplicates)
- Not null constraints on all fields
- Index on `email` for fast lookup

### Relationships
- Referenced by `tasks.user_id` (foreign key from Task model)
- No foreign keys in User table (no dependencies)

---

## Testing Considerations

### Unit Tests
- Test password hashing and verification
- Test JWT token generation and structure
- Test Pydantic validation rules
- Test User model creation

### Integration Tests
- Test signup with valid data (201 Created)
- Test signup with duplicate email (409 Conflict)
- Test signup with invalid data (400/422 Error)
- Test login with valid credentials (200 OK)
- Test login with invalid credentials (401 Unauthorized)
- Test login with non-existent email (401 Unauthorized)
- Test token compatibility with existing verification

### Contract Tests
- Verify request/response schemas match OpenAPI spec
- Verify HTTP status codes match specification
- Verify error response formats
- Verify token structure matches JWT standard
