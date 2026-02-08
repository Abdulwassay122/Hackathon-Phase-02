# API Contracts: Fix /tasks Page Auth Handling

**Feature**: 007-fix-tasks-auth
**Date**: 2026-02-08
**Purpose**: Document API contract compliance

## Overview

This feature involves **NO API contract changes**. All modifications are frontend-only, affecting client-side authentication check logic on the /tasks page.

---

## Existing API Contracts (Unchanged)

### Authentication Endpoints

These endpoints remain unchanged and are not affected by this fix:

#### POST /api/auth/login
**Purpose**: Authenticate user with email and password
**Request**: `{ email: string, password: string }`
**Response**: `{ access_token: string, token_type: "bearer", user: { id: number, email: string, name: string } }`
**Status Codes**: 200 (success), 401 (invalid credentials), 422 (validation error)

#### POST /api/auth/signup
**Purpose**: Register new user account
**Request**: `{ email: string, password: string, name: string }`
**Response**: `{ access_token: string, token_type: "bearer", user: { id: number, email: string, name: string } }`
**Status Codes**: 201 (created), 400 (validation error), 409 (email exists), 422 (invalid format)

### Task Management Endpoints

These endpoints remain unchanged and are not affected by this fix:

#### GET /api/tasks
**Purpose**: List all tasks for authenticated user
**Headers**: `Authorization: Bearer <token>`
**Response**: `Task[]`
**Status Codes**: 200 (success), 401 (unauthorized)

#### POST /api/tasks
**Purpose**: Create new task
**Headers**: `Authorization: Bearer <token>`
**Request**: `{ title: string, description?: string }`
**Response**: `Task`
**Status Codes**: 201 (created), 401 (unauthorized), 422 (validation error)

#### PATCH /api/tasks/{id}
**Purpose**: Update existing task
**Headers**: `Authorization: Bearer <token>`
**Request**: `{ title?: string, description?: string, completed?: boolean }`
**Response**: `Task`
**Status Codes**: 200 (success), 401 (unauthorized), 404 (not found)

#### DELETE /api/tasks/{id}
**Purpose**: Delete task
**Headers**: `Authorization: Bearer <token>`
**Response**: `{ message: string }`
**Status Codes**: 200 (success), 401 (unauthorized), 404 (not found)

---

## Frontend-Backend Contract Compliance

### Token Transmission

**Contract**: JWT token must be included in Authorization header for all protected endpoints

**Compliance**: ✅ Maintained
- Token retrieved from localStorage via `getToken()`
- Passed to API client constructor
- API client adds `Authorization: Bearer <token>` header to all requests
- No changes to token transmission mechanism

**Code Reference**: `frontend/src/app/(dashboard)/tasks/page.tsx:20-28`

---

### Error Handling

**Contract**: Backend returns 401 for invalid/expired tokens, frontend must handle gracefully

**Compliance**: ✅ Improved
- Before: `onAuthError` callback commented out
- After: `onAuthError` callback active, clears session and redirects to /signin
- Maintains proper error handling contract

**Code Reference**: `frontend/src/app/(dashboard)/tasks/page.tsx:23-27`

---

### Authentication State

**Contract**: Frontend must verify authentication before accessing protected resources

**Compliance**: ✅ Fixed
- Before: Middleware checked cookies (wrong location), causing redirect loop
- After: Client-side check uses AuthContext (correct location)
- Properly verifies authentication before rendering protected content

---

## No Breaking Changes

This fix introduces **zero breaking changes** to API contracts:

✅ All API endpoints remain unchanged
✅ Request/response formats unchanged
✅ Authentication mechanism unchanged (JWT tokens)
✅ Token storage location unchanged (localStorage)
✅ Token transmission unchanged (Authorization header)
✅ Error handling improved (better compliance with contract)

---

## Contract Verification Tests

### Test 1: Authenticated API Calls Still Work

**Scenario**: User logs in and accesses /tasks page
**Expected**: API calls to GET /api/tasks succeed with 200 status
**Verification**: Token properly included in Authorization header

### Test 2: Unauthenticated API Calls Still Fail

**Scenario**: User without token tries to access API
**Expected**: API returns 401 Unauthorized
**Verification**: Backend still enforces authentication

### Test 3: Expired Token Handling

**Scenario**: User with expired token makes API call
**Expected**: API returns 401, frontend clears session and redirects
**Verification**: Error handling contract maintained

### Test 4: Token Format Unchanged

**Scenario**: Login/signup returns JWT token
**Expected**: Token format matches existing structure (header.payload.signature)
**Verification**: Token can be decoded and used for API calls

---

## Summary

**API Contract Status**: ✅ **NO CHANGES**

This is a frontend-only fix that corrects the authentication check mechanism without modifying any API contracts. All existing API endpoints, request/response formats, and authentication mechanisms remain unchanged. The fix improves compliance with the error handling contract by properly handling 401 responses.

**Backward Compatibility**: ✅ **FULLY MAINTAINED**

The fix is 100% backward compatible with the existing backend API. No backend changes are required, and all existing API integrations continue to work without modification.
