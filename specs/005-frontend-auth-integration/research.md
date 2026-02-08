# Research: Frontend Authentication Integration

**Feature**: 005-frontend-auth-integration
**Date**: 2026-02-07
**Status**: Complete

## Overview

This document captures research findings and decisions for implementing frontend authentication integration with the FastAPI backend. The research focuses on Next.js 16+ App Router patterns, JWT token management, and secure authentication state handling.

---

## Research Question 1: Next.js 16+ App Router Authentication Patterns

### Decision
Use a hybrid approach combining:
- **Client Components** for authentication forms and interactive UI
- **React Context API** for authentication state management
- **Next.js Middleware** for route protection at the edge
- **Custom hooks** (useAuth) for accessing authentication state

### Rationale
- Next.js 16+ App Router defaults to Server Components, but authentication requires client-side interactivity (forms, state management)
- Middleware runs at the edge before page rendering, enabling efficient route protection
- Context API provides a clean way to share authentication state across components
- Custom hooks encapsulate authentication logic and provide a clean API

### Alternatives Considered
1. **Server-only authentication with cookies**
   - Rejected: Requires backend changes to support cookie-based auth (spec requires JWT in Authorization header)
   - Rejected: More complex to implement with existing backend

2. **Third-party auth libraries (NextAuth.js, Clerk)**
   - Rejected: Spec explicitly requires removing Better Auth and using direct API calls
   - Rejected: Adds unnecessary complexity for simple JWT-based auth

3. **Client-side only (no middleware)**
   - Rejected: Less secure, allows unauthorized users to see protected pages briefly
   - Rejected: Worse user experience with flash of unauthenticated content

### Implementation Pattern
```typescript
// Client Component for forms
'use client'
export function LoginForm() { ... }

// Context Provider for auth state
'use client'
export function AuthProvider({ children }) { ... }

// Middleware for route protection
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')
  if (!token && isProtectedRoute(request.nextUrl.pathname)) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}

// Custom hook for accessing auth
export function useAuth() {
  const context = useContext(AuthContext)
  return context
}
```

---

## Research Question 2: JWT Token Storage Best Practices

### Decision
Use **localStorage** for JWT token storage with XSS mitigation strategies.

### Rationale
- Spec explicitly requires localStorage (FR-004, FR-007)
- Simple to implement and works across all modern browsers
- Tokens persist across browser sessions (required for User Story 3)
- No server-side changes needed (unlike cookies)

### Security Considerations
**XSS Protection Strategies**:
1. Content Security Policy (CSP) headers to prevent script injection
2. Input sanitization on all user inputs
3. Use React's built-in XSS protection (JSX escaping)
4. Regular security audits of dependencies
5. HTTPS-only in production (tokens encrypted in transit)

**Token Handling**:
- Store only the JWT token (no sensitive user data)
- Clear token immediately on logout
- Clear token on 401 Unauthorized responses
- Never log token values

### Alternatives Considered
1. **httpOnly Cookies**
   - Rejected: Requires backend changes to set cookies
   - Rejected: Spec requires Authorization header, not cookies
   - Advantage: Immune to XSS attacks
   - Disadvantage: Vulnerable to CSRF (requires additional protection)

2. **sessionStorage**
   - Rejected: Tokens don't persist across browser sessions
   - Rejected: Spec requires 24-hour persistence (User Story 3)
   - Advantage: Cleared when browser closes
   - Disadvantage: Poor user experience (must login every session)

3. **In-memory only (React state)**
   - Rejected: Tokens lost on page refresh
   - Rejected: Spec requires persistence across sessions
   - Advantage: Most secure (no storage)
   - Disadvantage: Terrible user experience

### Implementation Pattern
```typescript
// lib/auth.ts
export const authStorage = {
  setToken: (token: string) => {
    localStorage.setItem('auth_token', token)
  },
  getToken: (): string | null => {
    return localStorage.getItem('auth_token')
  },
  clearToken: () => {
    localStorage.removeItem('auth_token')
  }
}
```

---

## Research Question 3: React Context API for Authentication State

### Decision
Implement a dedicated **AuthContext** with AuthProvider component to manage authentication state globally.

### Rationale
- Context API is built into React (no additional dependencies)
- Provides clean way to share auth state across components
- Works well with Next.js App Router (wrap root layout)
- Supports both authentication state and user information
- Enables centralized token management

### State Structure
```typescript
interface AuthState {
  isAuthenticated: boolean
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  loading: boolean
  error: string | null
}
```

### Performance Considerations
- Context updates trigger re-renders in all consuming components
- Mitigation: Split context if needed (auth state vs user data)
- For this feature: Single context is sufficient (limited consumers)
- Use React.memo() for expensive child components if needed

### Alternatives Considered
1. **Redux/Zustand state management**
   - Rejected: Overkill for simple authentication state
   - Rejected: Adds unnecessary dependencies
   - Advantage: Better performance for complex state
   - Disadvantage: More boilerplate, steeper learning curve

2. **Props drilling**
   - Rejected: Unmaintainable for deeply nested components
   - Rejected: Violates DRY principle
   - Advantage: Explicit data flow
   - Disadvantage: Verbose, hard to refactor

3. **Server-side session management**
   - Rejected: Requires backend changes
   - Rejected: Spec requires client-side JWT storage
   - Advantage: More secure
   - Disadvantage: Doesn't meet requirements

### Implementation Pattern
```typescript
// contexts/AuthContext.tsx
'use client'
const AuthContext = createContext<AuthState | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    loading: true,
    error: null
  })

  useEffect(() => {
    // Check for existing token on mount
    const token = authStorage.getToken()
    if (token) {
      // Validate token and set user
      validateAndSetUser(token)
    }
  }, [])

  return (
    <AuthContext.Provider value={state}>
      {children}
    </AuthContext.Provider>
  )
}
```

---

## Research Question 4: HTTP Client Configuration

### Decision
Use native **fetch API** with a custom wrapper function that automatically attaches Authorization headers.

### Rationale
- fetch API is built into modern browsers (no dependencies)
- Next.js 16+ extends fetch with caching and revalidation features
- Simple to implement interceptor pattern with wrapper function
- Meets all requirements (FR-005, FR-010, FR-014)

### Interceptor Pattern
```typescript
// lib/api.ts
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = authStorage.getToken()

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers
  }

  const response = await fetch(url, {
    ...options,
    headers
  })

  // Handle 401 Unauthorized globally
  if (response.status === 401) {
    authStorage.clearToken()
    window.location.href = '/login'
  }

  return response
}
```

### Error Handling Strategy
- **401 Unauthorized**: Clear token, redirect to login (FR-010, FR-014)
- **403 Forbidden**: Show error message, don't clear token
- **400 Bad Request**: Display validation errors from backend
- **409 Conflict**: Display specific error (e.g., "Email already registered")
- **500 Internal Server Error**: Display generic error message (FR-016)
- **Network errors**: Display "Unable to connect to server" (FR-016)

### Alternatives Considered
1. **axios library**
   - Rejected: Adds dependency (fetch is sufficient)
   - Advantage: Built-in interceptors, better error handling
   - Disadvantage: Extra bundle size, not needed for simple use case

2. **SWR or React Query**
   - Rejected: Overkill for this feature
   - Advantage: Caching, revalidation, optimistic updates
   - Disadvantage: Adds complexity, not required by spec

3. **Next.js Server Actions**
   - Rejected: Requires server-side token handling
   - Rejected: Spec requires client-side localStorage
   - Advantage: Type-safe, server-side validation
   - Disadvantage: Doesn't meet requirements

---

## Research Question 5: Form Validation Patterns

### Decision
Implement **dual validation**: client-side for UX, backend for security.

### Rationale
- Client-side validation provides immediate feedback (better UX)
- Backend validation is the source of truth (security requirement)
- Spec explicitly states client-side validation is UX enhancement only (FR-011)
- Constitution Principle VIII: Frontend validation never relied upon for security

### Client-Side Validation Rules
**Email**:
- Format validation using regex or HTML5 email input
- Required field validation

**Password**:
- Minimum 8 characters (FR-011)
- At least one letter and one number (matches backend validation)
- Required field validation

**Name**:
- Non-empty after trimming whitespace
- Required field validation

### Implementation Pattern
```typescript
// components/auth/SignupForm.tsx
function validateForm(data: SignupData): ValidationErrors {
  const errors: ValidationErrors = {}

  if (!data.email || !isValidEmail(data.email)) {
    errors.email = 'Invalid email format'
  }

  if (!data.password || data.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
  } else if (!/[a-zA-Z]/.test(data.password) || !/[0-9]/.test(data.password)) {
    errors.password = 'Password must contain at least one letter and one number'
  }

  if (!data.name || data.name.trim().length === 0) {
    errors.name = 'Name is required'
  }

  return errors
}
```

### Error Display Strategy
- Show validation errors inline below each field
- Show backend errors in the same format for consistency
- Clear errors when user starts typing
- Prevent form submission while validation errors exist (FR-012)
- Display loading state during submission (FR-012)

### Alternatives Considered
1. **Form libraries (React Hook Form, Formik)**
   - Rejected: Adds dependencies for simple forms
   - Advantage: Built-in validation, better performance
   - Disadvantage: Overkill for 2-3 field forms

2. **Backend-only validation**
   - Rejected: Poor user experience (round-trip for every error)
   - Advantage: Single source of truth
   - Disadvantage: Slow feedback, bad UX

3. **Client-only validation**
   - Rejected: Security risk (can be bypassed)
   - Rejected: Violates constitution principles
   - Advantage: Fast, simple
   - Disadvantage: Insecure, unreliable

---

## Research Question 6: Better Auth Removal Strategy

### Decision
**Complete removal** of Better Auth library with systematic replacement of all authentication calls.

### Rationale
- Spec explicitly requires no Better Auth usage (FR-001, Constraints)
- Backend authentication is already implemented (feature 001)
- Simpler architecture with direct API calls
- Reduces dependencies and bundle size

### Removal Checklist
1. **Identify Better Auth usage**:
   - Search codebase for Better Auth imports
   - Find all authentication-related components
   - Locate session management code
   - Check for Better Auth configuration files

2. **Replace authentication calls**:
   - Signup: Replace with POST /api/auth/signup
   - Login: Replace with POST /api/auth/login
   - Session check: Replace with token validation
   - Logout: Replace with token clearing

3. **Remove dependencies**:
   - Uninstall Better Auth package from package.json
   - Remove Better Auth configuration
   - Delete unused Better Auth components

4. **Update imports**:
   - Replace Better Auth hooks with custom useAuth hook
   - Update component imports
   - Remove Better Auth provider

### Migration Path
```typescript
// BEFORE (Better Auth)
import { useSession, signIn, signOut } from 'better-auth'

function LoginPage() {
  const { session } = useSession()
  const handleLogin = () => signIn('credentials', { email, password })
}

// AFTER (Custom implementation)
import { useAuth } from '@/hooks/useAuth'

function LoginPage() {
  const { user, login } = useAuth()
  const handleLogin = () => login(email, password)
}
```

### Testing Strategy
1. Test signup flow end-to-end
2. Test login flow end-to-end
3. Test logout functionality
4. Test protected route access
5. Test token expiration handling
6. Verify no Better Auth code remains

### Alternatives Considered
1. **Keep Better Auth for session management**
   - Rejected: Spec explicitly prohibits Better Auth usage
   - Rejected: Adds unnecessary complexity
   - Advantage: Proven library
   - Disadvantage: Doesn't meet requirements

2. **Gradual migration (keep both)**
   - Rejected: Increases complexity
   - Rejected: Confusing to maintain two auth systems
   - Advantage: Lower risk
   - Disadvantage: Technical debt, confusion

3. **Migrate to different auth library**
   - Rejected: Spec requires direct API calls only
   - Rejected: Adds dependencies
   - Advantage: Feature-rich
   - Disadvantage: Doesn't meet requirements

---

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| **Architecture** | Client Components + Context API + Middleware | Balances security, UX, and Next.js 16+ best practices |
| **Token Storage** | localStorage with XSS mitigation | Meets spec requirements, simple implementation |
| **State Management** | React Context API | Built-in, sufficient for auth state |
| **HTTP Client** | fetch API with wrapper | No dependencies, meets all requirements |
| **Validation** | Dual (client + backend) | UX enhancement + security enforcement |
| **Better Auth** | Complete removal | Spec requirement, simpler architecture |

---

## Implementation Risks

1. **XSS Vulnerabilities**
   - Risk: localStorage tokens vulnerable to XSS attacks
   - Mitigation: CSP headers, input sanitization, HTTPS-only
   - Severity: Medium (standard web app risk)

2. **Token Expiration Edge Cases**
   - Risk: User makes request with expired token
   - Mitigation: Global 401 handler, automatic redirect
   - Severity: Low (handled by backend)

3. **Browser Compatibility**
   - Risk: localStorage not available (private browsing)
   - Mitigation: Detect and show error message
   - Severity: Low (edge case documented in spec)

4. **State Synchronization**
   - Risk: Auth state out of sync with backend
   - Mitigation: Validate token on app load, handle 401 globally
   - Severity: Low (standard pattern)

---

## Next Steps

1. Create data-model.md (authentication state entities)
2. Create contracts/ (API endpoint specifications)
3. Create quickstart.md (manual testing procedures)
4. Generate tasks.md (implementation breakdown)
5. Execute implementation via /sp.implement
