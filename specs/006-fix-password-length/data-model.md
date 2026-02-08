# Data Model: Fix Password Length Error (72-Byte Limit)

**Feature**: 006-fix-password-length
**Date**: 2026-02-08
**Status**: Complete

## Overview

This fix does not introduce new data entities or modify existing database schemas. It changes the behavior of password handling logic to prevent bcrypt 72-byte limit errors. This document describes the affected entities and their modified behavior.

---

## Affected Entity: User Password Handling

### Description
The password handling process for user authentication. This is not a database entity but rather the behavior of how passwords are processed before hashing and verification.

### Storage Location
- **Database**: `users` table, `password_hash` column (unchanged)
- **Runtime**: Password processing utilities in `backend/src/auth/password_utils.py`

### Modified Behavior

**Before Fix**:
```
User Input (password) → bcrypt.hashpw() → Error if >72 bytes
User Input (password) → bcrypt.checkpw() → Error if >72 bytes
```

**After Fix**:
```
User Input (password) → Truncate to 72 bytes → bcrypt.hashpw() → Success
User Input (password) → Truncate to 72 bytes → bcrypt.checkpw() → Success
```

### Properties

| Property | Type | Description | Validation |
|----------|------|-------------|------------|
| Raw Password | string | User-provided password (any length) | Required, non-empty |
| Truncated Password | bytes | Password truncated to 72 bytes (UTF-8) | Exactly 72 bytes or less |
| Password Hash | string | Bcrypt hash of truncated password | Stored in database |

### Lifecycle

1. **User Registration**:
   - User provides password (any length)
   - System truncates to 72 bytes (UTF-8 encoding)
   - System hashes truncated password with bcrypt
   - System stores hash in database

2. **User Login**:
   - User provides password (any length)
   - System truncates to 72 bytes (UTF-8 encoding)
   - System verifies truncated password against stored hash
   - System grants access if verification succeeds

3. **Password Change** (future):
   - Same truncation logic applies
   - New hash generated from truncated password

### State Transitions

```
[User Input: Any Length Password]
    ↓
[Encode to UTF-8 bytes]
    ↓
[Truncate to 72 bytes]
    ↓
[Hash with bcrypt] OR [Verify against hash]
    ↓
[Success: No byte-length errors]
```

### Validation Rules

**Input Validation** (unchanged):
- Password must not be empty
- Password must meet complexity requirements (min 8 chars, letter + number)
- Password format validation occurs before truncation

**Truncation Rules** (new):
- Encode password to UTF-8 bytes
- Take first 72 bytes
- If truncation splits a multi-byte character, drop incomplete bytes
- Result is always ≤72 bytes

### Security Considerations

- **Truncation is transparent**: Users are not notified when passwords are truncated
- **No entropy loss for short passwords**: Passwords <72 bytes are unaffected
- **Entropy cap for long passwords**: Passwords >72 bytes have effective entropy limited to 72 bytes (bcrypt's existing behavior)
- **Backward compatible**: Existing password hashes continue to work
- **No new attack vectors**: Truncation makes existing bcrypt behavior explicit

---

## Affected Entity: Authentication Request

### Description
The authentication request process that validates user credentials. This is not a database entity but rather the flow of authentication operations.

### Modified Behavior

**Signup Flow**:
```
Before: POST /api/auth/signup → hash_password(raw) → Error if >72 bytes
After:  POST /api/auth/signup → hash_password(truncate(raw)) → Success
```

**Login Flow**:
```
Before: POST /api/auth/login → verify_password(raw, hash) → Error if >72 bytes
After:  POST /api/auth/login → verify_password(truncate(raw), hash) → Success
```

### Properties

| Property | Type | Description | Modified |
|----------|------|-------------|----------|
| Email | string | User's email address | No |
| Password | string | User's password (any length) | No (input unchanged) |
| Password Hash | string | Bcrypt hash | No (format unchanged) |
| Truncation Applied | boolean | Whether password was >72 bytes | New (internal only) |

### Validation Rules

**Request Validation** (unchanged):
- Email must be valid format
- Password must not be empty
- Name required for signup

**Password Processing** (modified):
- Password truncated to 72 bytes before hashing/verification
- Truncation is transparent (not exposed in API)
- Error handling unchanged (same HTTP status codes)

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Signup Flow                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User Input                                                   │
│  ┌──────────────────────────────────────┐                   │
│  │ email: "user@example.com"            │                   │
│  │ password: "very_long_password..." (80 chars)             │
│  │ name: "John Doe"                     │                   │
│  └──────────────┬───────────────────────┘                   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                   │
│  │ Truncate Password to 72 bytes        │ ← NEW STEP       │
│  │ "very_long_password..."[:72 bytes]   │                   │
│  └──────────────┬───────────────────────┘                   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                   │
│  │ Hash with bcrypt                     │                   │
│  │ → $2b$12$... (hash)                  │                   │
│  └──────────────┬───────────────────────┘                   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                   │
│  │ Store in Database                    │                   │
│  │ users.password_hash = hash           │                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     Login Flow                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User Input                                                   │
│  ┌──────────────────────────────────────┐                   │
│  │ email: "user@example.com"            │                   │
│  │ password: "very_long_password..." (80 chars)             │
│  └──────────────┬───────────────────────┘                   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                   │
│  │ Truncate Password to 72 bytes        │ ← NEW STEP       │
│  │ "very_long_password..."[:72 bytes]   │                   │
│  └──────────────┬───────────────────────┘                   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                   │
│  │ Retrieve hash from Database          │                   │
│  │ users.password_hash                  │                   │
│  └──────────────┬───────────────────────┘                   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                   │
│  │ Verify with bcrypt                   │                   │
│  │ checkpw(truncated, hash) → True/False│                   │
│  └──────────────┬───────────────────────┘                   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                   │
│  │ Grant/Deny Access                    │                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Notes

### No Database Changes
- **Schema**: No changes to `users` table or any other tables
- **Migrations**: No database migrations required
- **Data**: Existing password hashes remain valid and unchanged

### Backward Compatibility
- **Existing Users**: Can continue logging in with their passwords
- **Existing Hashes**: Work without modification (bcrypt already truncates internally)
- **API Contracts**: No changes to request/response formats

### Testing Considerations
- Test with passwords of various lengths (short, exactly 72 bytes, long)
- Test with multi-byte UTF-8 characters (emojis, international characters)
- Test backward compatibility with existing user accounts
- Verify no database changes occur

---

## Summary

This fix modifies the behavior of password processing without changing data models or database schemas. The key change is the addition of a truncation step before bcrypt operations, which prevents byte-length errors while maintaining full backward compatibility with existing password hashes.

**Modified Components**:
- Password hashing logic (new truncation step)
- Password verification logic (new truncation step)

**Unchanged Components**:
- Database schema
- API contracts
- User model
- JWT token handling
- Frontend code
