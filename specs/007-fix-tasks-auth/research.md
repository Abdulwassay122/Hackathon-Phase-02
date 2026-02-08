# Research: Fix /tasks Page Auth Handling

**Feature**: 007-fix-tasks-auth
**Date**: 2026-02-08
**Purpose**: Investigate root cause of redirect loop and determine fix approach

## Research Question 1: What is the current authentication check implementation on the /tasks page?

**Finding**: The /tasks page (`frontend/src/app/(dashboard)/tasks/page.tsx`) currently has NO authentication check logic. It relies entirely on the middleware for protection.

**Current Implementation**:
- Page is a client component (`'use client'`)
- Imports `getToken` from `@/lib/auth/session` but only uses it for API calls
- No check for authentication state before rendering
- No redirect logic if user is not authenticated

**Code Reference**: `frontend/src/app/(dashboard)/tasks/page.tsx:1-126`

---

## Research Question 2: How does the AuthContext provide authentication state?

**Finding**: AuthContext provides comprehensive authentication state management through React Context.

**Available Properties**:
- `isAuthenticated: boolean` - Whether user is currently authenticated
- `user: User | null` - Current user data (id, email, name)
- `token: string | null` - JWT token
- `loading: boolean` - Whether auth state is being initialized
- `error: string | null` - Any authentication errors

**Available Methods**:
- `login(email, password)` - Authenticate user and redirect to /tasks
- `signup(email, password, name)` - Register user and redirect to /tasks
- `logout()` - Clear session and redirect to /login

**Initialization**: On mount, AuthContext checks localStorage for existing token and decodes it to populate user state (lines 50-78).

**Code Reference**: `frontend/src/contexts/AuthContext.tsx:19-28, 50-78`

---

## Research Question 3: What is causing the redirect loop?

**ROOT CAUSE IDENTIFIED**: Mismatch between token storage location and middleware check.

**The Problem**:
1. **Token Storage**: Authentication system stores JWT token in **localStorage** (via `setToken()` in AuthContext)
2. **Middleware Check**: Middleware checks for token in **cookies** (`request.cookies.get('auth-token')`)
3. **Result**: Middleware never finds the token because it's looking in the wrong place

**Redirect Loop Sequence**:
1. User logs in successfully → token stored in localStorage
2. `router.push("/tasks")` executes
3. Middleware runs (server-side) and checks for cookie
4. Cookie doesn't exist (token is in localStorage)
5. Middleware redirects to /signin
6. User is already authenticated in AuthContext
7. If they try to access /tasks again, loop repeats

**Why Middleware Can't Access localStorage**:
- Middleware runs on the server (Next.js edge runtime)
- localStorage is a browser-only API
- Server-side code cannot access client-side storage

**Code References**:
- Token storage: `frontend/src/contexts/AuthContext.tsx:112, 175`
- Middleware check: `frontend/src/middleware.ts:12, 21-25`

---

## Research Question 4: What is the correct pattern for protecting routes in Next.js App Router?

**Decision**: Use client-side authentication check with AuthContext for client components.

**Rationale**:
- Next.js App Router supports both server and client components
- The /tasks page is already a client component (`'use client'`)
- AuthContext is available in client components via `useAuth()` hook
- This pattern is standard for client-side protected routes in Next.js

**Best Practice Pattern**:
```typescript
'use client';

export default function ProtectedPage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/signin');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return null; // Prevent flash while redirecting
  }

  return <PageContent />;
}
```

**Alternatives Considered**:
1. **Move token to cookies**: Would require rewriting entire auth system (out of scope)
2. **Server-side authentication**: Would require converting page to server component (breaks existing functionality)
3. **Keep middleware, add client check**: Redundant and still causes issues

**Code Reference**: Next.js documentation on client-side route protection

---

## Research Question 5: How should token validation be performed on the client side?

**Decision**: Use AuthContext's `isAuthenticated` flag, which already validates token on initialization.

**Rationale**:
- AuthContext already decodes JWT and validates format (lines 56-71)
- Invalid tokens are caught and cleared automatically
- No need for additional validation logic
- Keeps validation logic centralized in AuthContext

**Token Validation in AuthContext**:
```typescript
try {
  const payload = JSON.parse(atob(existingToken.split(".")[1]));
  const userData: User = {
    id: parseInt(payload.sub),
    email: payload.email,
    name: payload.name || payload.email,
  };
  setIsAuthenticated(true);
  setUser(userData);
  setTokenState(existingToken);
} catch (err) {
  // Invalid token, clear it
  clearToken();
  console.error("Failed to decode token:", err);
}
```

**What We Don't Need to Check**:
- Token expiry on client side (backend validates on API calls)
- Token signature (backend validates)
- Token format beyond basic JWT structure (already checked)

**Code Reference**: `frontend/src/contexts/AuthContext.tsx:56-71`

---

## Research Question 6: What are the edge cases that need to be handled?

**Edge Cases Identified**:

1. **Token expires while on /tasks page**:
   - Current: API calls fail with 401, onAuthError callback commented out
   - Solution: Uncomment onAuthError callback to handle gracefully

2. **Malformed tokens**:
   - Current: AuthContext catches decode errors and clears token
   - Solution: Already handled, no changes needed

3. **Race conditions in auth state updates**:
   - Current: AuthContext uses `loading` flag during initialization
   - Solution: Check `loading` flag before redirecting

4. **localStorage unavailable**:
   - Current: `getToken()` will return null if localStorage fails
   - Solution: Treat as unauthenticated, redirect to /signin

5. **Manual URL navigation while authenticated**:
   - Current: No check, page loads normally
   - Solution: Add auth check to handle this case

6. **Network errors during token validation**:
   - Current: No network calls for token validation (client-side decode only)
   - Solution: Not applicable, validation is synchronous

**Handling Strategy**: Use AuthContext's `loading` and `isAuthenticated` flags to handle all cases consistently.

---

## Summary of Findings

### Root Cause
Middleware checks for token in cookies, but authentication system stores token in localStorage. Middleware cannot access localStorage (server-side limitation), causing it to always redirect authenticated users.

### Solution
Remove middleware protection for /tasks and add client-side authentication check using AuthContext's `useAuth()` hook. This aligns with Next.js App Router best practices for client-side protected routes.

### Implementation Approach
1. Modify middleware to exclude /tasks from protected paths
2. Add authentication check to /tasks page using `useAuth()` hook
3. Show loading state while checking authentication
4. Redirect to /signin if not authenticated
5. Prevent flash of unauthenticated content by returning null during redirect

### Key Decisions
- **Token Storage**: Keep in localStorage (no changes)
- **Validation**: Use AuthContext's existing validation (no additional checks)
- **Protection Pattern**: Client-side check with useAuth hook
- **Edge Cases**: Handled by AuthContext's loading and isAuthenticated flags

### Files to Modify
1. `frontend/src/middleware.ts` - Remove /tasks from protected paths
2. `frontend/src/app/(dashboard)/tasks/page.tsx` - Add authentication check

### No Changes Needed
- AuthContext (already provides all necessary functionality)
- Token storage mechanism (localStorage is correct for client-side auth)
- Login/signup flows (already working correctly)
