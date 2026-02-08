# Quickstart: Frontend Authentication Integration

**Feature**: 005-frontend-auth-integration
**Date**: 2026-02-07
**Purpose**: Manual testing guide for frontend authentication integration

## Overview

This guide provides step-by-step manual testing procedures for verifying the frontend authentication integration with the FastAPI backend. All tests should be performed in a web browser with developer tools open to monitor network requests and localStorage.

---

## Prerequisites

### Backend Setup
1. Backend server must be running on port 8000 (or configured port)
2. Backend authentication endpoints must be functional (feature 001-backend-auth-endpoints)
3. CORS must be configured to allow frontend origin (feature 004-backend-cors-fix)
4. Database must be accessible and initialized

```bash
# Start backend server
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

### Frontend Setup
1. Frontend development server must be running
2. Better Auth library must be removed from package.json
3. Authentication pages must be updated to use new implementation

```bash
# Start frontend server
cd frontend
npm run dev
```

### Browser Setup
1. Open browser developer tools (F12)
2. Navigate to Application/Storage tab to monitor localStorage
3. Navigate to Network tab to monitor API requests
4. Clear localStorage before each test for clean state

---

## Test 1: User Signup Flow (User Story 1 - P1)

### Test 1.1: Successful Signup with Valid Data

**Objective**: Verify that a new user can create an account and receive a JWT token.

**Steps**:
1. Clear localStorage in browser developer tools
2. Navigate to signup page (e.g., http://localhost:3000/signup)
3. Fill in the form:
   - Email: `testuser1@example.com`
   - Password: `SecurePass123`
   - Name: `Test User One`
4. Click "Sign Up" button
5. Observe network request in developer tools

**Expected Results**:
- ✅ POST request sent to `http://localhost:8000/api/auth/signup`
- ✅ Request body contains: `{"email":"testuser1@example.com","password":"SecurePass123","name":"Test User One"}`
- ✅ Response status: 201 Created
- ✅ Response body contains: `access_token`, `token_type: "bearer"`, `user` object
- ✅ JWT token stored in localStorage with key `auth_token`
- ✅ User redirected to main application (e.g., /tasks or /dashboard)
- ✅ User information displayed in UI (name, email)
- ✅ No error messages displayed

**Verification**:
```javascript
// Check localStorage in browser console
localStorage.getItem('auth_token')
// Should return: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Test 1.2: Signup with Duplicate Email

**Objective**: Verify that duplicate email registration is prevented with appropriate error message.

**Steps**:
1. Complete Test 1.1 first (create testuser1@example.com)
2. Navigate back to signup page
3. Fill in the form with the same email:
   - Email: `testuser1@example.com`
   - Password: `AnotherPass456`
   - Name: `Another User`
4. Click "Sign Up" button

**Expected Results**:
- ✅ POST request sent to backend
- ✅ Response status: 409 Conflict
- ✅ Response body contains: `{"detail":"Email already registered"}`
- ✅ Error message displayed: "Email already registered"
- ✅ User remains on signup page (no redirect)
- ✅ No token stored in localStorage
- ✅ Form fields retain entered values (except password)

---

### Test 1.3: Signup with Weak Password

**Objective**: Verify that password complexity requirements are enforced.

**Steps**:
1. Clear localStorage
2. Navigate to signup page
3. Fill in the form with weak password:
   - Email: `testuser2@example.com`
   - Password: `weak` (too short, no number)
   - Name: `Test User Two`
4. Click "Sign Up" button

**Expected Results**:
- ✅ Client-side validation error displayed before API call (if implemented)
- ✅ OR POST request sent and backend returns 400 Bad Request
- ✅ Error message displayed: "Password must be at least 8 characters and contain at least one letter and one number"
- ✅ User remains on signup page
- ✅ No token stored in localStorage

**Additional Test Cases**:
- Password: `12345678` (no letter) → Should fail
- Password: `abcdefgh` (no number) → Should fail
- Password: `Pass123` (too short) → Should fail
- Password: `Password1` (valid) → Should succeed

---

### Test 1.4: Signup with Invalid Email Format

**Objective**: Verify that email format validation works correctly.

**Steps**:
1. Clear localStorage
2. Navigate to signup page
3. Fill in the form with invalid email:
   - Email: `notanemail` (no @ symbol)
   - Password: `SecurePass123`
   - Name: `Test User`
4. Click "Sign Up" button

**Expected Results**:
- ✅ Client-side validation error displayed (if implemented)
- ✅ OR POST request sent and backend returns 422 Unprocessable Entity
- ✅ Error message displayed: "Invalid email format"
- ✅ User remains on signup page
- ✅ No token stored in localStorage

**Additional Test Cases**:
- Email: `user@` (incomplete) → Should fail
- Email: `@example.com` (no local part) → Should fail
- Email: `user @example.com` (space) → Should fail
- Email: `user@example.com` (valid) → Should succeed

---

### Test 1.5: Signup with Empty Name

**Objective**: Verify that name field validation works correctly.

**Steps**:
1. Clear localStorage
2. Navigate to signup page
3. Fill in the form with empty name:
   - Email: `testuser3@example.com`
   - Password: `SecurePass123`
   - Name: `` (empty) or `   ` (whitespace only)
4. Click "Sign Up" button

**Expected Results**:
- ✅ Client-side validation error displayed (if implemented)
- ✅ OR POST request sent and backend returns 400 Bad Request
- ✅ Error message displayed: "Name is required" or "Name cannot be empty"
- ✅ User remains on signup page
- ✅ No token stored in localStorage

---

### Test 1.6: Signup with Network Error

**Objective**: Verify that network errors are handled gracefully.

**Steps**:
1. Stop the backend server
2. Navigate to signup page
3. Fill in valid form data
4. Click "Sign Up" button

**Expected Results**:
- ✅ POST request fails (network error)
- ✅ Error message displayed: "Unable to connect to server"
- ✅ User remains on signup page
- ✅ No token stored in localStorage
- ✅ Form remains functional (can retry after backend restarts)

---

### Test 1.7: Signup Loading State

**Objective**: Verify that loading state prevents duplicate submissions.

**Steps**:
1. Ensure backend is running
2. Navigate to signup page
3. Fill in valid form data
4. Click "Sign Up" button
5. Immediately try to click "Sign Up" button again (before response)

**Expected Results**:
- ✅ Submit button disabled during request
- ✅ Loading indicator displayed (spinner, text change, etc.)
- ✅ Form fields disabled during request
- ✅ Only one POST request sent (no duplicate)
- ✅ Loading state clears after response

---

## Test 2: User Login Flow (User Story 2 - P2)

### Test 2.1: Successful Login with Valid Credentials

**Objective**: Verify that an existing user can log in and receive a JWT token.

**Prerequisites**: User account must exist (create via Test 1.1 or backend directly)

**Steps**:
1. Clear localStorage
2. Navigate to login page (e.g., http://localhost:3000/login)
3. Fill in the form:
   - Email: `testuser1@example.com`
   - Password: `SecurePass123`
4. Click "Log In" button
5. Observe network request in developer tools

**Expected Results**:
- ✅ POST request sent to `http://localhost:8000/api/auth/login`
- ✅ Request body contains: `{"email":"testuser1@example.com","password":"SecurePass123"}`
- ✅ Response status: 200 OK
- ✅ Response body contains: `access_token`, `token_type: "bearer"`, `user` object
- ✅ JWT token stored in localStorage with key `auth_token`
- ✅ User redirected to main application
- ✅ User information displayed in UI
- ✅ No error messages displayed

---

### Test 2.2: Login with Incorrect Password

**Objective**: Verify that incorrect password is rejected with generic error message.

**Steps**:
1. Clear localStorage
2. Navigate to login page
3. Fill in the form:
   - Email: `testuser1@example.com`
   - Password: `WrongPassword123`
4. Click "Log In" button

**Expected Results**:
- ✅ POST request sent to backend
- ✅ Response status: 401 Unauthorized
- ✅ Response body contains: `{"detail":"Invalid email or password"}`
- ✅ Error message displayed: "Invalid email or password"
- ✅ User remains on login page
- ✅ No token stored in localStorage
- ✅ Error message does NOT reveal that email exists (security)

---

### Test 2.3: Login with Non-Existent Email

**Objective**: Verify that non-existent email returns same error as incorrect password.

**Steps**:
1. Clear localStorage
2. Navigate to login page
3. Fill in the form:
   - Email: `nonexistent@example.com`
   - Password: `AnyPassword123`
4. Click "Log In" button

**Expected Results**:
- ✅ POST request sent to backend
- ✅ Response status: 401 Unauthorized
- ✅ Response body contains: `{"detail":"Invalid email or password"}`
- ✅ Error message displayed: "Invalid email or password"
- ✅ Same error message as Test 2.2 (prevents user enumeration)
- ✅ User remains on login page
- ✅ No token stored in localStorage

---

### Test 2.4: Login Loading State

**Objective**: Verify that loading state prevents duplicate submissions.

**Steps**:
1. Navigate to login page
2. Fill in valid credentials
3. Click "Log In" button
4. Immediately try to click "Log In" button again

**Expected Results**:
- ✅ Submit button disabled during request
- ✅ Loading indicator displayed
- ✅ Form fields disabled during request
- ✅ Only one POST request sent
- ✅ Loading state clears after response

---

## Test 3: Session Persistence (User Story 3 - P3)

### Test 3.1: Token Persistence Across Browser Sessions

**Objective**: Verify that JWT token persists after browser close/reopen.

**Steps**:
1. Complete Test 2.1 (login successfully)
2. Verify token in localStorage
3. Close browser completely
4. Reopen browser
5. Navigate to main application (e.g., http://localhost:3000/tasks)

**Expected Results**:
- ✅ Token still present in localStorage
- ✅ User remains authenticated (no redirect to login)
- ✅ User information displayed in UI
- ✅ Protected routes accessible
- ✅ API requests include Authorization header with token

**Verification**:
```javascript
// Check localStorage after browser reopen
localStorage.getItem('auth_token')
// Should still return the token
```

---

### Test 3.2: Token Persistence Across Page Navigation

**Objective**: Verify that authentication state persists during navigation.

**Steps**:
1. Login successfully (Test 2.1)
2. Navigate to different pages in the application
3. Refresh the page (F5)
4. Navigate back and forward using browser buttons

**Expected Results**:
- ✅ User remains authenticated across all navigation
- ✅ Token persists in localStorage
- ✅ User information displayed on all pages
- ✅ No login prompts during navigation
- ✅ All API requests include Authorization header

---

### Test 3.3: Logout Functionality

**Objective**: Verify that logout clears token and redirects to login.

**Steps**:
1. Login successfully (Test 2.1)
2. Verify token in localStorage
3. Click "Logout" button (or trigger logout action)
4. Observe localStorage and page behavior

**Expected Results**:
- ✅ Token removed from localStorage
- ✅ Authentication state cleared (user = null, isAuthenticated = false)
- ✅ User redirected to login page
- ✅ Attempting to access protected routes redirects to login
- ✅ No Authorization header in subsequent requests

**Verification**:
```javascript
// Check localStorage after logout
localStorage.getItem('auth_token')
// Should return: null
```

---

### Test 3.4: Token Expiration Handling

**Objective**: Verify that expired tokens are detected and handled correctly.

**Note**: This test requires either waiting 24 hours or manually manipulating the token expiration.

**Steps (Manual Token Manipulation)**:
1. Login successfully
2. Get token from localStorage
3. Decode token and note expiration time
4. Manually set token to an expired one (or wait 24 hours)
5. Try to access a protected route or make an API request

**Expected Results**:
- ✅ API request returns 401 Unauthorized
- ✅ Frontend detects 401 response
- ✅ Token cleared from localStorage
- ✅ User redirected to login page
- ✅ Error message displayed (optional): "Session expired. Please log in again."

---

### Test 3.5: Unauthorized Access to Protected Routes

**Objective**: Verify that unauthenticated users cannot access protected routes.

**Steps**:
1. Clear localStorage (ensure no token)
2. Directly navigate to a protected route (e.g., http://localhost:3000/tasks)

**Expected Results**:
- ✅ User immediately redirected to login page
- ✅ No protected content displayed (even briefly)
- ✅ URL changes to login page
- ✅ After login, user can access the protected route

---

## Test 4: API Request Authorization (Integration)

### Test 4.1: Authenticated API Request

**Objective**: Verify that JWT token is attached to API requests.

**Steps**:
1. Login successfully (Test 2.1)
2. Navigate to a page that makes API requests (e.g., tasks list)
3. Observe network requests in developer tools

**Expected Results**:
- ✅ All API requests include Authorization header
- ✅ Header format: `Authorization: Bearer <token>`
- ✅ Token matches the one in localStorage
- ✅ Backend accepts the token (200 OK responses)
- ✅ User-specific data returned (only user's tasks, not others')

**Verification**:
```javascript
// Check request headers in Network tab
// Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Test 4.2: API Request Without Token

**Objective**: Verify that requests without token are rejected.

**Steps**:
1. Clear localStorage (no token)
2. Manually make an API request to a protected endpoint using fetch in console

```javascript
fetch('http://localhost:8000/api/users/1/tasks', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
})
```

**Expected Results**:
- ✅ Response status: 401 Unauthorized
- ✅ Response body contains error message
- ✅ No user data returned

---

### Test 4.3: API Request with Invalid Token

**Objective**: Verify that invalid tokens are rejected.

**Steps**:
1. Set invalid token in localStorage: `localStorage.setItem('auth_token', 'invalid.token.here')`
2. Make an API request to a protected endpoint

**Expected Results**:
- ✅ Response status: 401 Unauthorized
- ✅ Frontend detects 401 and clears token
- ✅ User redirected to login page

---

## Test 5: Edge Cases and Error Scenarios

### Test 5.1: Rapid Form Submissions

**Objective**: Verify that rapid clicking doesn't cause issues.

**Steps**:
1. Navigate to signup or login page
2. Fill in valid data
3. Rapidly click submit button multiple times

**Expected Results**:
- ✅ Only one API request sent
- ✅ Button disabled after first click
- ✅ No duplicate user accounts created
- ✅ No errors in console

---

### Test 5.2: Browser Storage Unavailable

**Objective**: Verify behavior when localStorage is unavailable (private browsing).

**Steps**:
1. Open browser in private/incognito mode with localStorage disabled
2. Attempt to login

**Expected Results**:
- ✅ Error message displayed: "Browser storage unavailable. Please enable cookies and try again."
- ✅ OR fallback to sessionStorage (if implemented)
- ✅ Application doesn't crash

---

### Test 5.3: Special Characters in Input

**Objective**: Verify that special characters are handled correctly.

**Steps**:
1. Signup with special characters:
   - Email: `user+test@example.com`
   - Password: `P@ssw0rd!#$`
   - Name: `O'Brien-Smith`

**Expected Results**:
- ✅ Signup succeeds
- ✅ Special characters preserved correctly
- ✅ Login works with same credentials
- ✅ No XSS vulnerabilities (name displayed safely)

---

### Test 5.4: Very Long Inputs

**Objective**: Verify that input length limits are enforced.

**Steps**:
1. Attempt signup with very long inputs:
   - Email: 300 character email
   - Password: 300 character password
   - Name: 300 character name

**Expected Results**:
- ✅ Client-side validation limits input length (if implemented)
- ✅ OR backend returns 400 Bad Request
- ✅ Error message displayed
- ✅ No server crash

---

## Test 6: Cross-Browser Compatibility

### Test 6.1: Chrome/Edge

**Steps**: Run all tests above in Chrome or Edge

**Expected Results**: All tests pass

---

### Test 6.2: Firefox

**Steps**: Run all tests above in Firefox

**Expected Results**: All tests pass

---

### Test 6.3: Safari

**Steps**: Run all tests above in Safari

**Expected Results**: All tests pass

---

## Success Criteria Summary

All tests must pass for the feature to be considered complete:

- ✅ User Story 1 (Signup): Tests 1.1-1.7 pass
- ✅ User Story 2 (Login): Tests 2.1-2.4 pass
- ✅ User Story 3 (Session): Tests 3.1-3.5 pass
- ✅ Integration: Tests 4.1-4.3 pass
- ✅ Edge Cases: Tests 5.1-5.4 pass
- ✅ Cross-Browser: Tests 6.1-6.3 pass

**Total Test Cases**: 24 manual tests

---

## Troubleshooting

### Issue: Token not stored in localStorage
- Check browser console for errors
- Verify localStorage is enabled
- Check that API response includes access_token

### Issue: CORS errors in console
- Verify backend CORS configuration (feature 004)
- Check that frontend origin is allowed
- Ensure credentials are included in requests

### Issue: 401 Unauthorized on all requests
- Verify token format in Authorization header
- Check that backend JWT verification is working
- Ensure BETTER_AUTH_SECRET matches between frontend and backend

### Issue: Redirect not working after login
- Check that redirect logic is implemented
- Verify routing configuration
- Check for JavaScript errors in console

---

## Next Steps After Testing

1. Document any failed tests with screenshots and error messages
2. Create bug reports for any issues found
3. Retest after fixes are applied
4. Proceed to automated testing (if required)
5. Deploy to staging environment for further testing
