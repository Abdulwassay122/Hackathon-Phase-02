# Quickstart: Fix /tasks Page Auth Handling

**Feature**: 007-fix-tasks-auth
**Date**: 2026-02-08
**Purpose**: Manual testing guide for authentication fix

## Overview

This guide provides step-by-step instructions for manually testing the /tasks page authentication fix. The fix prevents redirect loops for authenticated users after login/signup by correcting the authentication check mechanism.

---

## Prerequisites

1. **Frontend Running**: Next.js frontend must be running on `http://localhost:3000`
2. **Backend Running**: FastAPI backend must be running on `http://localhost:8000`
3. **Database**: Neon PostgreSQL database must be accessible
4. **Browser**: Use Chrome, Firefox, Safari, or Edge with DevTools available
5. **Clean State**: Clear browser localStorage before starting tests

---

## Test Suite 1: User Story 1 - Login Flow (Priority: P1)

### Test 1.1: Successful Login and Access to /tasks

**Objective**: Verify that authenticated users can access /tasks after login without redirect loop

**Steps**:
1. Open browser and navigate to `http://localhost:3000/signin`
2. Open DevTools → Application tab → Local Storage
3. Verify localStorage is empty (no `auth-token` key)
4. Enter valid credentials:
   - Email: `test@example.com`
   - Password: `Test1234`
5. Click "Sign In" button
6. Observe the page navigation

**Expected Result**:
- ✅ User redirected to `/tasks` page
- ✅ `/tasks` page loads and displays task list
- ✅ No redirect back to `/signin`
- ✅ localStorage contains `auth-token` key with JWT value
- ✅ Page shows "My Tasks" heading
- ✅ Task creation form is visible

**Verification Checklist**:
- [ ] URL is `http://localhost:3000/tasks` (no redirect)
- [ ] Page content is visible (not blank)
- [ ] localStorage has `auth-token` key
- [ ] No console errors related to authentication
- [ ] No infinite redirect loop

---

### Test 1.2: Page Refresh While Authenticated

**Objective**: Verify that authenticated users remain on /tasks after page refresh

**Prerequisites**: Complete Test 1.1 (user is logged in)

**Steps**:
1. While on `/tasks` page, press F5 or click browser refresh button
2. Observe page behavior

**Expected Result**:
- ✅ Page reloads successfully
- ✅ User remains on `/tasks` page
- ✅ Task list is displayed
- ✅ No redirect to `/signin`
- ✅ Authentication state persists

**Verification Checklist**:
- [ ] URL remains `http://localhost:3000/tasks`
- [ ] Page content reloads without redirect
- [ ] localStorage still contains `auth-token`
- [ ] No authentication errors in console

---

### Test 1.3: Manual Navigation to /tasks While Authenticated

**Objective**: Verify that authenticated users can manually navigate to /tasks via URL bar

**Prerequisites**: Complete Test 1.1 (user is logged in)

**Steps**:
1. While logged in, navigate to home page or any other page
2. Manually type `http://localhost:3000/tasks` in URL bar
3. Press Enter
4. Observe page behavior

**Expected Result**:
- ✅ `/tasks` page loads successfully
- ✅ No redirect to `/signin`
- ✅ Task list is displayed
- ✅ Authentication state is recognized

**Verification Checklist**:
- [ ] Page loads without redirect
- [ ] Task list is visible
- [ ] No authentication errors

---

## Test Suite 2: User Story 2 - Signup Flow (Priority: P1)

### Test 2.1: Successful Signup and Access to /tasks

**Objective**: Verify that new users can access /tasks after signup without redirect loop

**Steps**:
1. Clear browser localStorage (DevTools → Application → Local Storage → Clear All)
2. Navigate to `http://localhost:3000/signup`
3. Enter new user information:
   - Name: `Test User`
   - Email: `newuser@example.com` (use unique email)
   - Password: `NewPass123`
4. Click "Sign Up" button
5. Observe the page navigation

**Expected Result**:
- ✅ User redirected to `/tasks` page
- ✅ `/tasks` page loads and displays empty task list
- ✅ No redirect back to `/signin`
- ✅ localStorage contains `auth-token` key with JWT value
- ✅ Page shows "My Tasks" heading
- ✅ Welcome state for new user (no tasks)

**Verification Checklist**:
- [ ] URL is `http://localhost:3000/tasks`
- [ ] Page shows empty task list (new user)
- [ ] localStorage has `auth-token` key
- [ ] No console errors
- [ ] No redirect loop

---

### Test 2.2: New User Can Create Tasks

**Objective**: Verify that newly signed up users can immediately use the application

**Prerequisites**: Complete Test 2.1 (new user signed up)

**Steps**:
1. While on `/tasks` page after signup, fill in task creation form:
   - Title: `My First Task`
   - Description: `Testing task creation`
2. Click "Create Task" button
3. Observe the result

**Expected Result**:
- ✅ Task is created successfully
- ✅ Task appears in task list
- ✅ No authentication errors
- ✅ User remains on `/tasks` page

**Verification Checklist**:
- [ ] Task appears in list
- [ ] No redirect or errors
- [ ] Task has correct title and description

---

## Test Suite 3: User Story 3 - Unauthenticated Access (Priority: P2)

### Test 3.1: Unauthenticated User Cannot Access /tasks

**Objective**: Verify that users without valid tokens are redirected to /signin

**Steps**:
1. Clear browser localStorage completely
2. Navigate directly to `http://localhost:3000/tasks`
3. Observe the page behavior

**Expected Result**:
- ✅ User redirected to `/signin` page
- ✅ `/tasks` page does not load
- ✅ No task content is visible
- ✅ URL changes to `/signin`

**Verification Checklist**:
- [ ] Redirect to `/signin` occurs
- [ ] No task content visible
- [ ] No authentication errors in console

---

### Test 3.2: Expired Token Redirects to /signin

**Objective**: Verify that users with expired tokens are redirected

**Steps**:
1. Log in successfully (Test 1.1)
2. Open DevTools → Application → Local Storage
3. Manually edit the `auth-token` value to an expired token (or wait for expiration)
4. Refresh the page or navigate to `/tasks`
5. Observe the behavior

**Expected Result**:
- ✅ User redirected to `/signin`
- ✅ localStorage cleared (invalid token removed)
- ✅ Error message may appear (optional)

**Verification Checklist**:
- [ ] Redirect to `/signin` occurs
- [ ] Invalid token cleared from localStorage
- [ ] No infinite redirect loop

---

### Test 3.3: Malformed Token Redirects to /signin

**Objective**: Verify that malformed tokens are handled gracefully

**Steps**:
1. Clear localStorage
2. Open DevTools → Application → Local Storage
3. Manually add `auth-token` key with value: `invalid.token.here`
4. Navigate to `http://localhost:3000/tasks`
5. Observe the behavior

**Expected Result**:
- ✅ User redirected to `/signin`
- ✅ Malformed token cleared from localStorage
- ✅ No JavaScript errors (handled gracefully)

**Verification Checklist**:
- [ ] Redirect to `/signin` occurs
- [ ] Malformed token cleared
- [ ] No unhandled errors in console

---

## Test Suite 4: Edge Cases

### Test 4.1: localStorage Unavailable (Private Mode)

**Objective**: Verify behavior when localStorage is disabled

**Steps**:
1. Open browser in private/incognito mode
2. Navigate to `http://localhost:3000/signin`
3. Attempt to log in with valid credentials
4. Observe the behavior

**Expected Result**:
- ⚠️ Login may fail (cannot store token)
- ✅ User sees appropriate error message
- ✅ No JavaScript errors crash the page

**Verification Checklist**:
- [ ] Error handled gracefully
- [ ] User informed of issue
- [ ] No page crash

---

### Test 4.2: Race Condition - Multiple Rapid Navigations

**Objective**: Verify no race conditions in authentication check

**Steps**:
1. Log in successfully
2. Rapidly click browser back/forward buttons multiple times
3. Rapidly navigate between `/tasks` and other pages
4. Observe the behavior

**Expected Result**:
- ✅ No redirect loop occurs
- ✅ Authentication state remains consistent
- ✅ Page loads correctly each time

**Verification Checklist**:
- [ ] No redirect loop
- [ ] No authentication errors
- [ ] Consistent behavior

---

### Test 4.3: Token Expires During Active Session

**Objective**: Verify handling of token expiration while using the app

**Prerequisites**: This test requires a short-lived token (modify backend for testing)

**Steps**:
1. Log in successfully
2. Wait for token to expire (or use short-lived token)
3. Attempt to create/update/delete a task
4. Observe the behavior

**Expected Result**:
- ✅ API call fails with 401 error
- ✅ User redirected to `/signin` with `?expired=true` parameter
- ✅ Session cleared from localStorage
- ✅ User sees "Session expired" message

**Verification Checklist**:
- [ ] API error handled gracefully
- [ ] Redirect to `/signin` occurs
- [ ] Session cleared
- [ ] User informed of expiration

---

## Test Suite 5: Performance Verification

### Test 5.1: Page Load Time

**Objective**: Verify that authentication check adds negligible overhead

**Steps**:
1. Log in successfully
2. Open DevTools → Network tab
3. Clear network log
4. Navigate to `/tasks` page
5. Measure page load time in Network tab

**Expected Result**:
- ✅ Page loads in under 2 seconds
- ✅ Authentication check adds <50ms overhead
- ✅ No noticeable delay for users

**Verification Checklist**:
- [ ] Total load time < 2 seconds
- [ ] No performance degradation
- [ ] Smooth user experience

---

### Test 5.2: No Flash of Unauthenticated Content

**Objective**: Verify that unauthenticated content doesn't flash before redirect

**Steps**:
1. Clear localStorage
2. Navigate to `/tasks` page
3. Watch carefully for any content flash before redirect
4. Observe the behavior

**Expected Result**:
- ✅ Loading spinner shows immediately
- ✅ No task content visible before redirect
- ✅ Smooth transition to `/signin`
- ✅ No "flash" of unauthenticated content

**Verification Checklist**:
- [ ] No content flash
- [ ] Loading state shows first
- [ ] Clean redirect experience

---

## Success Criteria Verification

After completing all tests, verify the following success criteria from spec.md:

- [ ] **SC-001**: 100% of users with valid authentication tokens can access the /tasks page after login without being redirected to /signin (Tests 1.1, 1.2, 1.3)
- [ ] **SC-002**: 100% of users with valid authentication tokens can access the /tasks page after signup without being redirected to /signin (Tests 2.1, 2.2)
- [ ] **SC-003**: 0% of authenticated users experience redirect loops between /tasks and /signin (All tests in Suites 1 and 2)
- [ ] **SC-004**: 100% of users without valid authentication tokens are redirected from /tasks to /signin (Tests 3.1, 3.2, 3.3)
- [ ] **SC-005**: Page load time for /tasks remains under 2 seconds for authenticated users (Test 5.1)
- [ ] **SC-006**: 0% of authenticated users see a flash of unauthenticated content before /tasks loads (Test 5.2)

---

## Troubleshooting

### Issue: Redirect loop still occurs

**Diagnosis**: Authentication check not working correctly
**Solution**:
1. Verify middleware changes applied (check `frontend/src/middleware.ts`)
2. Verify /tasks page has authentication check (check `page.tsx`)
3. Clear browser cache and localStorage
4. Restart frontend development server

---

### Issue: localStorage not accessible

**Diagnosis**: Browser privacy settings or private mode
**Solution**:
1. Use normal browser mode (not private/incognito)
2. Check browser settings for localStorage permissions
3. Try different browser

---

### Issue: Token not persisting after login

**Diagnosis**: localStorage write failing
**Solution**:
1. Check browser console for errors
2. Verify `setToken()` function is called
3. Check localStorage quota (may be full)

---

## Test Summary Template

```
Test Suite 1: Login Flow
  Test 1.1: Successful login         [ PASS / FAIL ]
  Test 1.2: Page refresh             [ PASS / FAIL ]
  Test 1.3: Manual navigation        [ PASS / FAIL ]

Test Suite 2: Signup Flow
  Test 2.1: Successful signup        [ PASS / FAIL ]
  Test 2.2: New user creates task    [ PASS / FAIL ]

Test Suite 3: Unauthenticated Access
  Test 3.1: No token redirect        [ PASS / FAIL ]
  Test 3.2: Expired token redirect   [ PASS / FAIL ]
  Test 3.3: Malformed token redirect [ PASS / FAIL ]

Test Suite 4: Edge Cases
  Test 4.1: localStorage unavailable [ PASS / FAIL ]
  Test 4.2: Race conditions          [ PASS / FAIL ]
  Test 4.3: Token expiry during use  [ PASS / FAIL ]

Test Suite 5: Performance
  Test 5.1: Page load time           [ PASS / FAIL ]
  Test 5.2: No content flash         [ PASS / FAIL ]

Overall Result: [ PASS / FAIL ]
```

---

## Next Steps

After all tests pass:
1. Document any issues found
2. Verify fix in staging environment (if applicable)
3. Deploy to production
4. Monitor for any authentication errors
5. Confirm no redirect loop reports from users
