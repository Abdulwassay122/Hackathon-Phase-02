# API Contract: Password Length Fix

**Feature**: 006-fix-password-length
**Date**: 2026-02-08
**Status**: No API Changes

## Overview

This fix does not modify any API contracts. The signup and login endpoints remain unchanged in terms of their request/response formats, HTTP methods, status codes, and behavior. The fix is internal to the password processing logic.

## Affected Endpoints

### POST /api/auth/signup

**Status**: No changes to contract

**Existing Behavior**:
- Accepts email, password, and name
- Returns 201 Created with JWT token on success
- Returns 400/409/422/500 on various errors

**Modified Internal Behavior**:
- Password is now truncated to 72 bytes before hashing
- This prevents the "password cannot be longer than 72 bytes" error
- All request/response formats remain identical

**Contract Reference**: See `specs/001-backend-auth-endpoints/contracts/signup.yaml` for full contract specification.

---

### POST /api/auth/login

**Status**: No changes to contract

**Existing Behavior**:
- Accepts email and password
- Returns 200 OK with JWT token on success
- Returns 401/422/500 on various errors

**Modified Internal Behavior**:
- Password is now truncated to 72 bytes before verification
- This prevents the "password cannot be longer than 72 bytes" error
- All request/response formats remain identical

**Contract Reference**: See `specs/001-backend-auth-endpoints/contracts/login.yaml` for full contract specification.

---

## Testing Contract Compliance

### Signup Endpoint Tests

**Test 1: Long Password (80 characters)**
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "ThisIsAVeryLongPasswordThatExceeds72BytesAndShouldStillWorkWithoutAnyErrors123",
  "name": "Test User"
}

Expected Response: 201 Created
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

**Test 2: Password with Multi-byte Characters**
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "test2@example.com",
  "password": "café☕🔒password" + "x" * 60,
  "name": "Test User 2"
}

Expected Response: 201 Created
(Same format as Test 1)
```

### Login Endpoint Tests

**Test 3: Login with Long Password**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "ThisIsAVeryLongPasswordThatExceeds72BytesAndShouldStillWorkWithoutAnyErrors123"
}

Expected Response: 200 OK
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

**Test 4: Backward Compatibility (Short Password)**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "existing@example.com",
  "password": "ShortPass123"
}

Expected Response: 200 OK
(Existing users with short passwords continue to work)
```

---

## Error Handling

### Before Fix
```http
POST /api/auth/signup
{
  "email": "test@example.com",
  "password": "very_long_password..." (>72 bytes),
  "name": "Test"
}

Response: 500 Internal Server Error
{
  "detail": "password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])"
}
```

### After Fix
```http
POST /api/auth/signup
{
  "email": "test@example.com",
  "password": "very_long_password..." (>72 bytes),
  "name": "Test"
}

Response: 201 Created
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {...}
}
```

---

## Contract Validation

**Validation Criteria**:
- ✅ No changes to request schemas
- ✅ No changes to response schemas
- ✅ No changes to HTTP status codes
- ✅ No changes to error message formats (except removal of byte-length error)
- ✅ Backward compatible with existing clients
- ✅ No breaking changes

**Conclusion**: This fix maintains full API contract compatibility. Existing clients will continue to work without modification. The only observable change is that long passwords now succeed instead of failing with a 500 error.
