# API Contracts: Fix Token Retrieval for API Requests

**Feature**: 008-fix-token-retrieval
**Date**: 2026-02-08
**Status**: Complete

## Overview

This feature is a frontend bug fix that does not modify any API endpoints. This document describes the existing contracts that the fix must maintain compatibility with.

## Frontend Contracts

### 1. Token Retrieval Contract

**Function**: `getToken()`
**Location**: `frontend/src/lib/auth/session.ts`

**Contract**:
```typescript
function getToken(): string | null
```

**Behavior**:
- **Returns**: JWT token string if available, `null` if not available
- **Side Effects**: None (read-only operation)
- **Error Handling**: Returns `null` on any error (localStorage unavailable, etc.)
- **Performance**: Must complete in <1ms (synchronous operation)

**Before Fix**:
```typescript
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  const session = getSession();  // Parses JSON from "user-session"
  return session?.token || null;
}
```

**After Fix**:
```typescript
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem("auth-token");  // Direct read
  } catch (error) {
    console.error("Failed to retrieve auth token:", error);
    return null;
  }
}
```

**Contract Maintained**: ✅ Yes
- Return type unchanged: `string | null`
- Behavior unchanged: Returns token or null
- No breaking changes to consumers

### 2. localStorage Contract

**Storage Keys**:

#### Key: "auth-token"
**Type**: String (JWT token)
**Format**: Standard JWT format `header.payload.signature`
**Example**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

**Lifecycle**:
- **Written by**: `setSession()` in `frontend/src/lib/auth/session.ts`
- **Read by**: `getToken()` in `frontend/src/lib/auth/session.ts` (AFTER FIX)
- **Deleted by**: `clearSession()` in `frontend/src/lib/auth/session.ts`

**Contract**:
```typescript
// Write
localStorage.setItem("auth-token", token: string)

// Read
localStorage.getItem("auth-token") => string | null

// Delete
localStorage.removeItem("auth-token")
```

#### Key: "user-session"
**Type**: JSON string
**Format**: Serialized UserSession object
**Example**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "expiresAt": "2026-02-08T12:00:00.000Z"
}
```

**Lifecycle**:
- **Written by**: `setSession()` in `frontend/src/lib/auth/session.ts`
- **Read by**: `getSession()` in `frontend/src/lib/auth/session.ts`
- **Deleted by**: `clearSession()` in `frontend/src/lib/auth/session.ts`

**Contract**: Unchanged by this fix

### 3. APIClient Contract

**Interface**: `APIClientConfig`
**Location**: `frontend/src/lib/api/client.ts`

**Contract**:
```typescript
export interface APIClientConfig {
  baseURL: string;
  getToken: () => string | null;  // Token retrieval callback
  onAuthError: () => void;         // Auth error handler
}
```

**Usage**:
```typescript
const apiClient = new APIClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  getToken,  // References the fixed getToken() function
  onAuthError: () => {
    clearSession();
    router.push("/signin?expired=true");
  },
});
```

**Contract Maintained**: ✅ Yes
- `getToken` callback signature unchanged
- APIClient expects `() => string | null`, which the fixed `getToken()` provides
- No changes to APIClient implementation required

## Backend API Contracts (Unchanged)

### Authorization Header Format

**Header Name**: `Authorization`
**Format**: `Bearer <token>`
**Example**: `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**Contract**:
```http
GET /api/tasks HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Backend Validation**:
1. Extract token from `Authorization` header
2. Verify token signature using `BETTER_AUTH_SECRET`
3. Check token expiration
4. Extract user ID from `sub` claim
5. Return 401 if validation fails

**Contract Maintained**: ✅ Yes
- Frontend continues to send `Authorization: Bearer <token>` header
- No changes to header format or backend validation

### API Endpoints (Unchanged)

All endpoints remain unchanged. The fix only ensures tokens are properly retrieved and attached to requests.

#### GET /api/tasks
**Request**:
```http
GET /api/tasks HTTP/1.1
Authorization: Bearer <token>
```

**Response** (Success):
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "id": 1,
    "title": "Task 1",
    "description": "Description",
    "completed": false,
    "user_id": 1,
    "created_at": "2026-02-08T10:00:00Z",
    "updated_at": "2026-02-08T10:00:00Z"
  }
]
```

**Response** (Auth Error):
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Invalid or expired token"
}
```

#### POST /api/tasks
**Request**:
```http
POST /api/tasks HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "New Task",
  "description": "Task description",
  "completed": false
}
```

**Response** (Success):
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 2,
  "title": "New Task",
  "description": "Task description",
  "completed": false,
  "user_id": 1,
  "created_at": "2026-02-08T11:00:00Z",
  "updated_at": "2026-02-08T11:00:00Z"
}
```

#### PUT /api/tasks/{id}
**Request**:
```http
PUT /api/tasks/1 HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Task",
  "description": "Updated description",
  "completed": true
}
```

**Response** (Success):
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1,
  "title": "Updated Task",
  "description": "Updated description",
  "completed": true,
  "user_id": 1,
  "created_at": "2026-02-08T10:00:00Z",
  "updated_at": "2026-02-08T11:30:00Z"
}
```

#### DELETE /api/tasks/{id}
**Request**:
```http
DELETE /api/tasks/1 HTTP/1.1
Authorization: Bearer <token>
```

**Response** (Success):
```http
HTTP/1.1 204 No Content
```

## Contract Verification

### Pre-Fix Contract Violations

**Issue**: `getToken()` returns `null` despite token existing in localStorage
- **Symptom**: 403 Forbidden errors on API requests
- **Root Cause**: JSON parsing failure in `getSession()`
- **Contract Violation**: `getToken()` should return token when it exists

### Post-Fix Contract Compliance

**Verification**:
- ✅ `getToken()` returns `string | null` (contract maintained)
- ✅ `getToken()` reads from "auth-token" key (correct storage location)
- ✅ APIClient receives non-null token when user is authenticated
- ✅ Authorization header includes `Bearer <token>` format
- ✅ Backend receives valid JWT token in requests
- ✅ API endpoints return 200 OK instead of 403 Forbidden

## Backward Compatibility

**Breaking Changes**: None

**Compatibility Matrix**:
| Component | Before Fix | After Fix | Compatible? |
|-----------|-----------|-----------|-------------|
| getToken() signature | `() => string \| null` | `() => string \| null` | ✅ Yes |
| localStorage keys | "auth-token", "user-session" | "auth-token", "user-session" | ✅ Yes |
| APIClient config | `getToken: () => string \| null` | `getToken: () => string \| null` | ✅ Yes |
| Authorization header | `Bearer <token>` | `Bearer <token>` | ✅ Yes |
| Backend API | No changes | No changes | ✅ Yes |

**Migration Required**: No
**Data Migration**: No
**API Version Bump**: No

## Summary

This fix maintains full backward compatibility with all existing contracts:
- Frontend function signatures unchanged
- localStorage keys unchanged
- API request format unchanged
- Backend API unchanged

The only change is the internal implementation of `getToken()`, which now reads directly from the "auth-token" localStorage key instead of parsing the "user-session" JSON object. This eliminates the 403 Forbidden errors while maintaining all existing contracts.
