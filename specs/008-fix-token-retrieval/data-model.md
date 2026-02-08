# Data Model: Fix Token Retrieval for API Requests

**Feature**: 008-fix-token-retrieval
**Date**: 2026-02-08
**Status**: Complete

## Overview

This feature is a bug fix that modifies token retrieval logic in the frontend. It does not introduce new data models, modify existing data structures, or change database schemas.

## Existing Data Structures

### JWT Token (String)

**Storage Location**: Browser localStorage
**Key**: "auth-token"
**Type**: String (JWT token)
**Format**: Standard JWT format: `header.payload.signature`

**Example**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Validation**: None at retrieval time (backend validates on each request)
**Lifecycle**:
- Created: During login/signup via `setSession()`
- Read: On every API request via `getToken()`
- Deleted: During logout via `clearSession()` or on token expiration

### UserSession (Existing, Unchanged)

**Storage Location**: Browser localStorage
**Key**: "user-session"
**Type**: JSON object
**Structure**:
```typescript
interface UserSession {
  token: string;        // JWT token
  user: {
    id: number;
    email: string;
    name: string;
  };
  expiresAt: string;    // ISO 8601 date string
}
```

**Note**: This structure remains unchanged. The fix only changes how `getToken()` retrieves the token (from "auth-token" key instead of parsing "user-session").

## State Transitions

### Token Lifecycle (Unchanged)

```
[No Token]
    ↓ (User logs in/signs up)
[Token Stored in localStorage]
    ↓ (User makes API request)
[Token Retrieved and Sent to Backend]
    ↓ (Backend validates token)
[Request Succeeds (200) or Fails (401/403)]
    ↓ (On 401: Token expired or invalid)
[Token Cleared, User Redirected to Signin]
```

**Change**: The "Token Retrieved" step now reads directly from "auth-token" key instead of parsing "user-session" JSON.

## Data Relationships

No data relationships involved. This is a simple key-value storage pattern in browser localStorage.

## Validation Rules

### Client-Side (Minimal)
- Token must be a non-empty string
- No format validation (backend handles this)
- No expiration check (backend handles this)

### Backend-Side (Unchanged)
- Token must be valid JWT format
- Token must be signed with correct secret
- Token must not be expired
- Token must contain valid user ID in `sub` claim

## Migration Strategy

**Migration Required**: No

**Reason**: This is a code-only change. No data migration needed. Existing tokens in localStorage remain valid and will work with the new retrieval logic.

**Backward Compatibility**: Full backward compatibility. The fix only changes the retrieval method, not the storage format or location.

## Summary

This feature does not introduce new data models or modify existing data structures. It only changes the implementation of the `getToken()` function to read from a different localStorage key. All data structures, validation rules, and state transitions remain unchanged.
