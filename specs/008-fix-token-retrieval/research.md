# Research: Fix Token Retrieval for API Requests

**Feature**: 008-fix-token-retrieval
**Date**: 2026-02-08
**Status**: Complete

## Problem Analysis

### Current Implementation

The current token retrieval implementation in `frontend/src/lib/auth/session.ts` has the following flow:

```typescript
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  const session = getSession();
  console.log("session", session);
  return session?.token || null;
}

export function getSession(): UserSession | null {
  if (typeof window === "undefined") return null;

  try {
    const sessionData = localStorage.getItem("user-session");
    console.log(sessionData)
    if (!sessionData) return null;

    const session = JSON.parse(sessionData) as UserSession;

    // Check if token is expired
    const now = new Date().getTime();
    const expiresAt = new Date(session.expiresAt).getTime();

    if (now >= expiresAt) {
      clearSession();
      return null;
    }

    return session;
  } catch (error) {
    console.error("Failed to parse session data:", error);
    return null;
  }
}
```

### Root Cause

The issue is that `getToken()` depends on `getSession()`, which:
1. Reads from the "user-session" key (not "auth-token")
2. Parses JSON (potential failure point)
3. Checks expiration (potential failure point)
4. Returns null if any step fails

However, when `setSession()` is called, it stores the token in TWO places:
```typescript
localStorage.setItem("user-session", JSON.stringify(session));
localStorage.setItem("auth-token", session.token);  // Direct token storage
```

The "auth-token" key contains the raw JWT token string, which is exactly what the API client needs. By reading from "user-session" and parsing JSON, we introduce unnecessary complexity and potential failure points.

### Evidence of Failure

From the tasks/page.tsx file (line 50), there's a console.log showing the issue:
```typescript
console.log("getToken", getToken());
```

This suggests developers were debugging token retrieval issues. The 403 Forbidden errors on `/api/tasks` indicate that the Authorization header is either missing or contains a null/invalid token.

## Solution Approach

### Decision: Direct localStorage Access

**Chosen Approach**: Modify `getToken()` to read directly from the "auth-token" key in localStorage, bypassing `getSession()` entirely.

**Rationale**:
1. **Simplicity**: Single localStorage read operation, no JSON parsing
2. **Reliability**: Fewer failure points (no JSON parse errors, no expiration check failures)
3. **Performance**: Faster execution (no JSON parsing overhead)
4. **Alignment with Storage**: Uses the same key that `setSession()` writes to
5. **Separation of Concerns**: Token retrieval is independent of session validation

**Implementation**:
```typescript
export function getToken(): string | null {
  if (typeof window === "undefined") return null;

  try {
    return localStorage.getItem("auth-token");
  } catch (error) {
    console.error("Failed to retrieve auth token:", error);
    return null;
  }
}
```

### Alternatives Considered

#### Alternative 1: Fix getSession() JSON Parsing
**Approach**: Debug and fix the JSON parsing in `getSession()` to ensure it always works correctly.

**Rejected Because**:
- Doesn't address the fundamental issue: unnecessary complexity
- Still has multiple failure points (JSON parse, expiration check)
- Slower performance due to JSON parsing
- Doesn't leverage the "auth-token" key that's already being stored

#### Alternative 2: Store Token in Both Places with Fallback
**Approach**: Try reading from "auth-token" first, fall back to "user-session" if not found.

**Rejected Because**:
- Adds complexity instead of reducing it
- Maintains the problematic code path
- No clear benefit over direct access
- Harder to debug and maintain

#### Alternative 3: Remove "auth-token" Storage, Use Only "user-session"
**Approach**: Remove the `localStorage.setItem("auth-token", session.token)` line and always parse from "user-session".

**Rejected Because**:
- Doesn't solve the 403 error issue
- Maintains the complex JSON parsing path
- Goes against the principle of simplicity
- The "auth-token" key is already being used by middleware (see middleware.ts line 12)

## Best Practices

### Token Storage in Browser

**Industry Standard**: Store JWT tokens in localStorage or sessionStorage with a simple key-value pair.

**Security Considerations**:
- ✅ localStorage is appropriate for JWT tokens in SPAs (Single Page Applications)
- ✅ Tokens should be transmitted only over HTTPS (prevents interception)
- ✅ Tokens should have expiration times (handled by backend JWT verification)
- ⚠️ XSS vulnerabilities can access localStorage (mitigated by React's XSS protection)
- ⚠️ CSRF attacks are prevented by using Authorization headers (not cookies)

**Performance Considerations**:
- localStorage.getItem() is synchronous and fast (<1ms)
- No JSON parsing needed for simple string retrieval
- Minimal memory footprint

### Token Retrieval Patterns

**Pattern 1: Direct Access (Chosen)**
```typescript
const token = localStorage.getItem("auth-token");
```
- Pros: Simple, fast, reliable
- Cons: No validation, no expiration check
- Use when: Backend handles all validation

**Pattern 2: Session-Based Access (Current, Problematic)**
```typescript
const session = JSON.parse(localStorage.getItem("user-session"));
const token = session?.token;
```
- Pros: Can check expiration client-side
- Cons: Complex, multiple failure points, slower
- Use when: Client needs to validate before sending

**Pattern 3: Hybrid Approach**
```typescript
const token = localStorage.getItem("auth-token");
const session = JSON.parse(localStorage.getItem("user-session"));
if (session && isExpired(session)) return null;
return token;
```
- Pros: Validation with fallback
- Cons: Still complex, redundant checks
- Use when: Client and server both need validation

**Recommendation**: Use Pattern 1 (Direct Access) because:
- Backend already validates token expiration (see backend JWT verification)
- Client-side expiration checks are redundant and error-prone
- Simpler code is more maintainable and reliable

## Integration Points

### APIClient Integration

The `APIClient` class in `frontend/src/lib/api/client.ts` expects a `getToken` callback:

```typescript
export interface APIClientConfig {
  baseURL: string;
  getToken: () => string | null;  // Must return token or null
  onAuthError: () => void;
}
```

The client uses this callback at line 65:
```typescript
const token = this.config.getToken();
```

And attaches it to the Authorization header at lines 72-74:
```typescript
if (token) {
  requestHeaders['Authorization'] = `Bearer ${token}`;
}
```

**Impact of Fix**: The fixed `getToken()` will return the token directly from localStorage, ensuring the Authorization header is always populated when a token exists.

### AuthContext Integration

The `AuthContext` manages authentication state and calls `setSession()` after successful login/signup. The context stores the token in the state:

```typescript
const [token, setToken] = useState<string | null>(null);
```

**Impact of Fix**: No changes needed to AuthContext. The fix only affects how `getToken()` retrieves the token, not how it's stored.

### Middleware Integration

The middleware in `frontend/src/middleware.ts` checks for tokens in cookies (line 12):
```typescript
const token = request.cookies.get('auth-token');
```

**Impact of Fix**: No impact. Middleware runs server-side and cannot access localStorage. The middleware check is separate from the client-side token retrieval.

## Testing Strategy

### Manual Testing Approach

1. **Test Token Retrieval After Login**
   - Login with valid credentials
   - Open browser DevTools → Console
   - Run: `localStorage.getItem("auth-token")`
   - Verify: Non-null JWT token string returned

2. **Test API Requests Include Token**
   - Login and navigate to /tasks
   - Open browser DevTools → Network tab
   - Filter for `/api/tasks` requests
   - Verify: Request headers include `Authorization: Bearer <token>`
   - Verify: Response status is 200 OK (not 403 Forbidden)

3. **Test Token Persistence Across Refresh**
   - Login and navigate to /tasks
   - Refresh the page (F5)
   - Verify: Tasks still load without redirect to signin
   - Verify: Network tab shows 200 OK responses

4. **Test Expired Token Handling**
   - Login and navigate to /tasks
   - Open DevTools → Application → Local Storage
   - Manually delete "auth-token" key
   - Perform any task operation (create/update/delete)
   - Verify: Redirect to /signin occurs

### Success Criteria Verification

- **SC-001**: 100% of API requests include non-null Authorization header
  - Verify: Check Network tab for all `/api/tasks/*` requests

- **SC-002**: GET /api/tasks returns 200 OK (not 403 Forbidden)
  - Verify: Check Network tab response status

- **SC-003**: All CRUD operations succeed
  - Verify: Create, read, update, delete tasks all return appropriate status codes

- **SC-004**: Token retrieval succeeds when token exists
  - Verify: `localStorage.getItem("auth-token")` returns non-null value

- **SC-005**: Expired/invalid tokens trigger proper error handling
  - Verify: 401 responses trigger redirect to signin

- **SC-006**: No console errors related to getToken/getSession
  - Verify: Console shows no errors after fix

## Risks and Mitigations

### Risk 1: Breaking Existing Functionality
**Likelihood**: Low
**Impact**: High
**Mitigation**: The fix only changes `getToken()` implementation. All other functions (`getSession()`, `setSession()`, `clearSession()`) remain unchanged. The API client already expects `getToken()` to return `string | null`, which the fix maintains.

### Risk 2: Token Not Found in localStorage
**Likelihood**: Low (only if setSession() wasn't called)
**Impact**: Medium (user redirected to signin)
**Mitigation**: This is the correct behavior. If no token exists, user should be redirected to signin. The `onAuthError` callback handles this gracefully.

### Risk 3: localStorage Unavailable (Private Browsing)
**Likelihood**: Low
**Impact**: Medium
**Mitigation**: The try-catch block in `getToken()` handles localStorage errors. Function returns null, triggering redirect to signin.

### Risk 4: Race Condition Between setSession and getToken
**Likelihood**: Very Low
**Impact**: Low
**Mitigation**: localStorage operations are synchronous. Once `setSession()` completes, `getToken()` will immediately see the new value.

## Conclusion

The fix is straightforward: modify `getToken()` to read directly from the "auth-token" key in localStorage. This eliminates unnecessary complexity, improves reliability, and aligns with industry best practices for JWT token storage in browser-based applications. The fix has minimal risk and can be verified through manual browser testing.
