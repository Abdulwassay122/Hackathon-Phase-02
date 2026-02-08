# Quickstart: Fix Token Retrieval for API Requests

**Feature**: 008-fix-token-retrieval
**Date**: 2026-02-08
**Status**: Complete

## Overview

This quickstart guide provides step-by-step instructions for testing the token retrieval fix. The fix modifies `getToken()` in `frontend/src/lib/auth/session.ts` to read JWT tokens directly from localStorage, eliminating 403 Forbidden errors on API requests.

## Prerequisites

- Backend API running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- Valid user account (or ability to create one via signup)
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- Browser DevTools knowledge (Console, Network, Application tabs)

## Quick Test (2 minutes)

### Test 1: Verify Token Retrieval After Login

1. **Navigate to signin page**
   ```
   http://localhost:3000/signin
   ```

2. **Login with valid credentials**
   - Email: `test@example.com`
   - Password: `your-password`

3. **Open Browser DevTools**
   - Press F12 (Windows/Linux) or Cmd+Option+I (Mac)
   - Go to Console tab

4. **Check token in localStorage**
   ```javascript
   localStorage.getItem("auth-token")
   ```
   - **Expected**: Non-null JWT token string (e.g., `eyJhbGciOiJIUzI1NiIs...`)
   - **Failure**: `null` or `undefined` (indicates token not stored)

5. **Navigate to tasks page**
   ```
   http://localhost:3000/tasks
   ```

6. **Verify tasks load successfully**
   - **Expected**: Task list displays (may be empty for new users)
   - **Failure**: Redirect to signin or error message

### Test 2: Verify API Requests Include Token

1. **Open Browser DevTools → Network tab**
   - Press F12 and click "Network" tab
   - Check "Preserve log" option

2. **Navigate to tasks page** (if not already there)
   ```
   http://localhost:3000/tasks
   ```

3. **Find the GET /api/tasks request**
   - Look for request to `http://localhost:8000/api/tasks`
   - Click on the request to view details

4. **Check Request Headers**
   - Scroll to "Request Headers" section
   - Find `Authorization` header
   - **Expected**: `Authorization: Bearer eyJhbGciOiJIUzI1NiIs...`
   - **Failure**: No Authorization header present

5. **Check Response Status**
   - Look at the status code in the Network tab
   - **Expected**: `200 OK`
   - **Failure**: `403 Forbidden` or `401 Unauthorized`

### Test 3: Verify Token Persistence Across Refresh

1. **While on tasks page, refresh the browser**
   - Press F5 or Ctrl+R (Windows/Linux) or Cmd+R (Mac)

2. **Verify tasks still load**
   - **Expected**: Tasks display without redirect to signin
   - **Failure**: Redirect to signin page

3. **Check Network tab again**
   - Verify GET /api/tasks returns 200 OK
   - Verify Authorization header is present

## Comprehensive Test Suite

### Test Suite 1: Token Retrieval (User Story 1)

#### Test 1.1: View Tasks After Login
**Objective**: Verify authenticated user can view tasks without 403 errors

**Steps**:
1. Login with valid credentials
2. Navigate to /tasks
3. Open DevTools → Network tab
4. Observe GET /api/tasks request

**Expected Results**:
- ✅ Request includes `Authorization: Bearer <token>` header
- ✅ Response status is 200 OK
- ✅ Task list displays (empty or with tasks)
- ✅ No console errors

**Failure Indicators**:
- ❌ Response status is 403 Forbidden
- ❌ No Authorization header in request
- ❌ Console error: "Failed to retrieve auth token"

#### Test 1.2: Create Task
**Objective**: Verify POST requests include token

**Steps**:
1. On /tasks page, create a new task
2. Enter title: "Test Task"
3. Enter description: "Testing token retrieval"
4. Click "Create Task"
5. Check Network tab for POST /api/tasks request

**Expected Results**:
- ✅ Request includes Authorization header
- ✅ Response status is 201 Created
- ✅ New task appears in task list
- ✅ No console errors

#### Test 1.3: Update Task
**Objective**: Verify PUT requests include token

**Steps**:
1. Click "Edit" on an existing task
2. Modify the title or description
3. Click "Save"
4. Check Network tab for PUT /api/tasks/{id} request

**Expected Results**:
- ✅ Request includes Authorization header
- ✅ Response status is 200 OK
- ✅ Task updates in the list
- ✅ No console errors

#### Test 1.4: Delete Task
**Objective**: Verify DELETE requests include token

**Steps**:
1. Click "Delete" on an existing task
2. Confirm deletion (if prompted)
3. Check Network tab for DELETE /api/tasks/{id} request

**Expected Results**:
- ✅ Request includes Authorization header
- ✅ Response status is 204 No Content
- ✅ Task removed from list
- ✅ No console errors

### Test Suite 2: Token Persistence (User Story 2)

#### Test 2.1: Page Refresh
**Objective**: Verify token persists across page refresh

**Steps**:
1. Login and navigate to /tasks
2. Verify tasks load successfully
3. Press F5 to refresh the page
4. Observe page behavior

**Expected Results**:
- ✅ Page reloads without redirect to signin
- ✅ Tasks still display
- ✅ GET /api/tasks returns 200 OK
- ✅ Authorization header present in request

#### Test 2.2: Browser Tab Close/Reopen
**Objective**: Verify token persists across browser sessions

**Steps**:
1. Login and navigate to /tasks
2. Close the browser tab
3. Open a new tab and navigate to http://localhost:3000/tasks
4. Observe page behavior

**Expected Results**:
- ✅ Tasks load without redirect to signin
- ✅ Authorization header present in requests
- ✅ No re-authentication required

**Note**: This test assumes localStorage persists across tabs (default browser behavior).

### Test Suite 3: Error Handling (User Story 3)

#### Test 3.1: Missing Token
**Objective**: Verify proper handling when token is missing

**Steps**:
1. Open DevTools → Application → Local Storage
2. Delete the "auth-token" key
3. Navigate to /tasks (or refresh if already there)
4. Observe page behavior

**Expected Results**:
- ✅ Redirect to /signin occurs
- ✅ No console errors (or graceful error message)
- ✅ No 403 errors in Network tab (no requests made)

#### Test 3.2: Expired Token
**Objective**: Verify proper handling of expired tokens

**Steps**:
1. Login and navigate to /tasks
2. Wait for token to expire (or manually set expired token)
3. Perform any task operation (create/update/delete)
4. Observe response and behavior

**Expected Results**:
- ✅ API returns 401 Unauthorized
- ✅ onAuthError callback fires
- ✅ Session cleared from localStorage
- ✅ Redirect to /signin?expired=true occurs

#### Test 3.3: Malformed Token
**Objective**: Verify proper handling of invalid tokens

**Steps**:
1. Open DevTools → Application → Local Storage
2. Manually set "auth-token" to invalid value (e.g., "invalid-token")
3. Navigate to /tasks
4. Observe response and behavior

**Expected Results**:
- ✅ API returns 401 Unauthorized
- ✅ onAuthError callback fires
- ✅ Redirect to /signin occurs

### Test Suite 4: Edge Cases

#### Test 4.1: localStorage Unavailable
**Objective**: Verify graceful handling when localStorage is unavailable

**Steps**:
1. Open browser in private/incognito mode (some browsers restrict localStorage)
2. Navigate to /signin
3. Attempt to login
4. Observe behavior

**Expected Results**:
- ✅ Login may fail gracefully with error message
- ✅ No JavaScript errors crash the page
- ✅ User informed of issue (if applicable)

**Note**: Most modern browsers support localStorage in private mode, so this test may not trigger the edge case.

#### Test 4.2: Concurrent Tabs
**Objective**: Verify token retrieval works across multiple tabs

**Steps**:
1. Login in Tab 1 and navigate to /tasks
2. Open Tab 2 and navigate to /tasks
3. Verify both tabs show tasks
4. Logout in Tab 1
5. Refresh Tab 2

**Expected Results**:
- ✅ Both tabs initially show tasks
- ✅ After logout in Tab 1, Tab 2 redirects to signin on refresh
- ✅ localStorage cleared in both tabs

## Debugging Guide

### Issue: Token is null

**Symptoms**:
- `localStorage.getItem("auth-token")` returns `null`
- 403 Forbidden errors on API requests
- Redirect to signin after login

**Possible Causes**:
1. `setSession()` not called after login/signup
2. localStorage blocked by browser settings
3. Token cleared prematurely

**Debug Steps**:
1. Check if login/signup API call succeeds
2. Check if `setSession()` is called in AuthContext
3. Check browser console for localStorage errors
4. Verify "auth-token" key exists in Application → Local Storage

### Issue: Authorization header missing

**Symptoms**:
- Network tab shows no Authorization header
- 403 Forbidden errors
- Token exists in localStorage

**Possible Causes**:
1. `getToken()` not called by APIClient
2. `getToken()` returning null despite token existing
3. APIClient not initialized with correct config

**Debug Steps**:
1. Add console.log in `getToken()` to verify it's called
2. Check if APIClient config includes `getToken` callback
3. Verify `getToken()` returns non-null value

### Issue: 401 Unauthorized despite valid token

**Symptoms**:
- Authorization header present in request
- Backend returns 401 Unauthorized
- Token appears valid (not expired)

**Possible Causes**:
1. Backend JWT secret mismatch
2. Token format incorrect
3. Backend JWT verification failing

**Debug Steps**:
1. Check backend logs for JWT verification errors
2. Verify BETTER_AUTH_SECRET matches between frontend and backend
3. Decode JWT token at jwt.io to inspect claims

## Success Criteria Checklist

After completing all tests, verify the following success criteria:

- [ ] **SC-001**: 100% of API requests include non-null Authorization header
  - Verified in Network tab for all CRUD operations

- [ ] **SC-002**: GET /api/tasks returns 200 OK (not 403 Forbidden)
  - Verified in Network tab after login

- [ ] **SC-003**: All CRUD operations succeed with appropriate status codes
  - Create: 201 Created
  - Read: 200 OK
  - Update: 200 OK
  - Delete: 204 No Content

- [ ] **SC-004**: Token retrieval succeeds when token exists
  - Verified via `localStorage.getItem("auth-token")`

- [ ] **SC-005**: Expired/invalid tokens trigger proper error handling
  - Verified via Test 3.2 and Test 3.3

- [ ] **SC-006**: No console errors related to getToken/getSession
  - Verified in Console tab during all operations

## Rollback Plan

If the fix causes issues:

1. **Revert the change to session.ts**
   ```bash
   git checkout HEAD~1 frontend/src/lib/auth/session.ts
   ```

2. **Verify rollback**
   - Restart frontend dev server
   - Test login and task access
   - Confirm previous behavior restored

3. **Report issue**
   - Document the failure scenario
   - Capture console errors and network logs
   - Create bug report with reproduction steps

## Next Steps

After successful testing:

1. **Commit the changes**
   ```bash
   git add frontend/src/lib/auth/session.ts
   git commit -m "fix(auth): read JWT token directly from localStorage

   - Modified getToken() to read from 'auth-token' key directly
   - Eliminates JSON parsing and expiration check failures
   - Fixes 403 Forbidden errors on /api/tasks endpoints

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```

2. **Create pull request** (if applicable)

3. **Deploy to staging** (if applicable)

4. **Monitor for issues** in production
