# Data Model: Fix /tasks Page Auth Handling

**Feature**: 007-fix-tasks-auth
**Date**: 2026-02-08
**Purpose**: Document authentication flow and state management changes

## Overview

This feature modifies the authentication check behavior on the /tasks page. There are **no database schema changes** and **no new data entities**. This document describes the modified authentication flow and state management.

---

## Modified Behavior: Protected Route Authentication

### Entity: Protected Route (/tasks page)

**What Changed**: Authentication check mechanism for the /tasks page

**Before**:
- Middleware (server-side) checks for token in cookies
- Token stored in localStorage (client-side)
- Mismatch causes redirect loop for authenticated users

**After**:
- Client-side authentication check using AuthContext
- Checks `isAuthenticated` flag from AuthContext
- Properly detects token in localStorage
- No redirect loop for authenticated users

**State Flow**:
```
Page Load → Check AuthContext.loading
  ↓
If loading = true → Show loading spinner
  ↓
If loading = false → Check AuthContext.isAuthenticated
  ↓
If isAuthenticated = false → Redirect to /signin
  ↓
If isAuthenticated = true → Render page content
```

---

## Existing Entities (No Changes)

### Entity: Authentication Token

**Storage**: Browser localStorage (key: `auth-token`)
**Format**: JWT token string
**Structure**: Standard JWT with three parts (header.payload.signature)
**Payload Claims**:
- `sub`: User ID (string)
- `email`: User email (string)
- `name`: User name (string)
- `exp`: Expiration timestamp (number)

**Lifecycle**:
- Created: During login/signup (backend generates)
- Stored: In localStorage via `setToken()` function
- Retrieved: Via `getToken()` function
- Validated: On AuthContext initialization (client-side decode)
- Cleared: On logout or invalid token detection

**No Changes**: Token structure, storage mechanism, and lifecycle remain unchanged.

---

### Entity: User Session

**Representation**: React state in AuthContext
**Properties**:
- `isAuthenticated: boolean` - Authentication status
- `user: User | null` - User data (id, email, name)
- `token: string | null` - JWT token
- `loading: boolean` - Initialization status
- `error: string | null` - Authentication errors

**Initialization**:
1. AuthContext mounts
2. Checks localStorage for existing token
3. If token exists, decodes JWT payload
4. Extracts user data from payload
5. Sets `isAuthenticated = true` and populates `user`
6. If token invalid, clears it and sets `isAuthenticated = false`
7. Sets `loading = false` when complete

**State Transitions**:
```
Initial State (loading=true, isAuthenticated=false)
  ↓
Token Found & Valid → Authenticated (loading=false, isAuthenticated=true)
  ↓
Token Not Found/Invalid → Unauthenticated (loading=false, isAuthenticated=false)
  ↓
Login/Signup Success → Authenticated (loading=false, isAuthenticated=true)
  ↓
Logout → Unauthenticated (loading=false, isAuthenticated=false)
```

**No Changes**: User session structure and state management remain unchanged.

---

## Authentication Flow Changes

### Before (Broken Flow)

```
User logs in
  ↓
Token stored in localStorage
  ↓
router.push("/tasks")
  ↓
Middleware runs (server-side)
  ↓
Middleware checks cookies for token
  ↓
Token not found in cookies (it's in localStorage)
  ↓
Middleware redirects to /signin
  ↓
REDIRECT LOOP
```

### After (Fixed Flow)

```
User logs in
  ↓
Token stored in localStorage
  ↓
AuthContext updates: isAuthenticated = true
  ↓
router.push("/tasks")
  ↓
Middleware skips /tasks (removed from protected paths)
  ↓
/tasks page loads
  ↓
Page checks AuthContext.loading
  ↓
If loading, show spinner
  ↓
If not loading, check AuthContext.isAuthenticated
  ↓
If authenticated, render page
  ↓
If not authenticated, redirect to /signin
  ↓
SUCCESS - No redirect loop
```

---

## Edge Case Handling

### Case 1: Token Expires During Session

**Scenario**: User is on /tasks page, token expires, API call fails with 401

**Current Behavior**: API error handler is commented out
**Fixed Behavior**:
- API client's `onAuthError` callback triggers
- Clears session via `clearSession()`
- Redirects to /signin with `?expired=true` parameter
- User sees "Session expired" message

**Data Flow**: API 401 → onAuthError → clearSession → localStorage cleared → redirect

---

### Case 2: Malformed Token in localStorage

**Scenario**: Token exists but is corrupted/malformed

**Behavior** (Already Handled):
- AuthContext tries to decode token
- Decode fails (try/catch)
- `clearToken()` called automatically
- `isAuthenticated` remains false
- User redirected to /signin

**Data Flow**: getToken → decode fails → clearToken → isAuthenticated=false → redirect

---

### Case 3: localStorage Unavailable

**Scenario**: Browser has localStorage disabled or in private mode

**Behavior**:
- `getToken()` returns null (fails silently)
- AuthContext sets `isAuthenticated = false`
- User redirected to /signin
- Login will fail (cannot store token)

**Data Flow**: getToken → null → isAuthenticated=false → redirect

---

## Validation Rules

### Client-Side Token Validation (AuthContext)

**Checks Performed**:
1. Token exists in localStorage
2. Token has valid JWT structure (3 parts separated by dots)
3. Payload can be base64 decoded
4. Payload contains required claims (sub, email)

**Checks NOT Performed** (Backend Responsibility):
- Token signature verification
- Token expiration validation
- Token revocation check

**Rationale**: Client-side validation is for UX only. Backend always validates tokens on API calls for security.

---

## No Database Changes

This feature involves **zero database changes**:
- No new tables
- No schema modifications
- No migrations required
- No data seeding needed

All changes are frontend-only, modifying authentication check logic in the /tasks page component.

---

## Summary

**Modified Components**:
1. Middleware: Remove /tasks from protected paths
2. /tasks Page: Add client-side authentication check

**Unchanged Components**:
1. AuthContext: No changes to authentication state management
2. Token Storage: Still uses localStorage
3. Login/Signup Flows: No changes to authentication endpoints
4. Backend API: No changes to token generation or validation

**Key Insight**: The fix aligns the authentication check mechanism with the token storage location (both client-side), eliminating the server-side/client-side mismatch that caused the redirect loop.
