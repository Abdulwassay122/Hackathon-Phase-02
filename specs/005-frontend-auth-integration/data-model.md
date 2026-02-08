# Data Model: Frontend Authentication Integration

**Feature**: 005-frontend-auth-integration
**Date**: 2026-02-07
**Status**: Complete

## Overview

This document defines the data structures and state management entities for frontend authentication integration. These entities exist in the browser's memory and localStorage, managing the authentication state and JWT tokens for the Next.js frontend application.

---

## Entity 1: JWT Token

### Description
Authentication credential issued by the backend upon successful signup or login. The token is a JSON Web Token (JWT) containing user identification and expiration information, used to authenticate API requests.

### Storage Location
- **Primary**: Browser localStorage (key: `auth_token`)
- **Runtime**: React Context state (for quick access)

### Structure
The JWT token is an encoded string. When decoded, it contains:

```typescript
interface JWTPayload {
  sub: string        // User ID (as string)
  email: string      // User email address
  exp: number        // Expiration timestamp (Unix epoch)
  iat?: number       // Issued at timestamp (optional)
}
```

### Properties

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| sub | string | Yes | User ID from backend | Non-empty string |
| email | string | Yes | User's email address | Valid email format |
| exp | number | Yes | Token expiration (Unix timestamp) | Future timestamp |
| iat | number | No | Token issued at (Unix timestamp) | Past timestamp |

### Lifecycle

1. **Creation**: Backend generates token on successful signup/login
2. **Storage**: Frontend stores in localStorage immediately after receiving
3. **Usage**: Attached to Authorization header for all API requests
4. **Validation**: Backend validates signature and expiration on each request
5. **Expiration**: Token expires after 24 hours (backend enforced)
6. **Removal**: Cleared on logout or 401 Unauthorized response

### State Transitions

```
[No Token]
    ↓ (signup/login success)
[Valid Token in localStorage]
    ↓ (app load)
[Token in Context State]
    ↓ (API request)
[Token in Authorization Header]
    ↓ (backend validates)
[Authenticated Request] OR [401 Unauthorized]
    ↓ (401 response)
[Token Cleared] → [No Token]
    ↓ (logout)
[Token Cleared] → [No Token]
```

### Security Considerations

- **Storage**: localStorage is vulnerable to XSS attacks
- **Mitigation**: CSP headers, input sanitization, HTTPS-only
- **Transmission**: Always sent over HTTPS in production
- **Logging**: Never log token values (security risk)
- **Exposure**: Only exposed to frontend code, never to external services

### Example

```typescript
// Encoded token (stored in localStorage)
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJleHAiOjE3MDc0MzY4MDB9.signature"

// Decoded payload (for reference only - frontend doesn't decode)
{
  "sub": "123",
  "email": "user@example.com",
  "exp": 1707436800  // 24 hours from issuance
}
```

---

## Entity 2: Authentication State

### Description
Current authentication status of the user in the frontend application. Managed by React Context API and persists across component re-renders. Represents whether a user is logged in, their user information, and any authentication errors.

### Storage Location
- **Primary**: React Context state (in-memory)
- **Persistence**: Derived from localStorage token on app load

### Structure

```typescript
interface AuthState {
  // Authentication status
  isAuthenticated: boolean

  // User information (from JWT or API)
  user: User | null

  // JWT token (for API requests)
  token: string | null

  // Loading state (during auth operations)
  loading: boolean

  // Error state (from failed auth operations)
  error: string | null

  // Authentication actions
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
}

interface User {
  id: number
  email: string
  name: string
}
```

### Properties

| Field | Type | Required | Description | Default Value |
|-------|------|----------|-------------|---------------|
| isAuthenticated | boolean | Yes | Whether user is logged in | false |
| user | User \| null | Yes | User information if authenticated | null |
| token | string \| null | Yes | JWT token if authenticated | null |
| loading | boolean | Yes | Loading state during auth operations | true (initial) |
| error | string \| null | Yes | Error message from failed operations | null |
| login | function | Yes | Login action | - |
| signup | function | Yes | Signup action | - |
| logout | function | Yes | Logout action | - |

### User Properties

| Field | Type | Required | Description | Source |
|-------|------|----------|-------------|--------|
| id | number | Yes | Unique user identifier | Backend API response |
| email | string | Yes | User's email address | Backend API response |
| name | string | Yes | User's display name | Backend API response |

### Lifecycle

1. **Initialization**: Context provider mounts, loading=true
2. **Token Check**: Check localStorage for existing token
3. **Token Validation**: If token exists, validate with backend (optional) or decode locally
4. **State Update**: Set isAuthenticated, user, token based on validation
5. **Ready**: loading=false, app ready for use
6. **Auth Operations**: login/signup/logout update state
7. **Error Handling**: Set error on failed operations
8. **Cleanup**: Clear state on logout or 401 response

### State Transitions

```
[Initial State: loading=true, isAuthenticated=false]
    ↓ (check localStorage)
[Token Found] OR [No Token]
    ↓ (token found)
[Validate Token]
    ↓ (valid)
[Authenticated: isAuthenticated=true, user set, loading=false]
    ↓ (no token or invalid)
[Unauthenticated: isAuthenticated=false, user=null, loading=false]
    ↓ (user calls login/signup)
[Loading: loading=true]
    ↓ (API success)
[Authenticated: isAuthenticated=true, user set, token set, loading=false]
    ↓ (API failure)
[Error: error set, loading=false]
    ↓ (user calls logout or 401 response)
[Unauthenticated: isAuthenticated=false, user=null, token=null]
```

### Validation Rules

- **isAuthenticated**: Must be true only if valid token exists
- **user**: Must be null if isAuthenticated is false
- **token**: Must be null if isAuthenticated is false
- **loading**: Must be false when no operation in progress
- **error**: Must be cleared when new operation starts

### Context Provider Pattern

```typescript
// contexts/AuthContext.tsx
const AuthContext = createContext<AuthState | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    token: null,
    loading: true,
    error: null
  })

  // Initialize on mount
  useEffect(() => {
    const token = authStorage.getToken()
    if (token) {
      // Decode token to get user info (or fetch from API)
      const user = decodeToken(token)
      setState(prev => ({
        ...prev,
        isAuthenticated: true,
        user,
        token,
        loading: false
      }))
    } else {
      setState(prev => ({ ...prev, loading: false }))
    }
  }, [])

  const login = async (email: string, password: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        throw new Error('Login failed')
      }

      const data = await response.json()
      authStorage.setToken(data.access_token)

      setState({
        isAuthenticated: true,
        user: data.user,
        token: data.access_token,
        loading: false,
        error: null
      })
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.message
      }))
    }
  }

  // Similar implementations for signup and logout

  return (
    <AuthContext.Provider value={{ ...state, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
```

---

## Entity 3: Form State (Ephemeral)

### Description
Temporary state for authentication forms (signup/login). Exists only during form interaction and is cleared after submission. Not persisted anywhere.

### Storage Location
- **Primary**: React component state (useState)
- **Persistence**: None (ephemeral)

### Structure

```typescript
interface SignupFormState {
  email: string
  password: string
  name: string
  errors: ValidationErrors
  isSubmitting: boolean
}

interface LoginFormState {
  email: string
  password: string
  errors: ValidationErrors
  isSubmitting: boolean
}

interface ValidationErrors {
  email?: string
  password?: string
  name?: string
  general?: string  // For backend errors
}
```

### Properties

| Field | Type | Required | Description | Default Value |
|-------|------|----------|-------------|---------------|
| email | string | Yes | User's email input | "" |
| password | string | Yes | User's password input | "" |
| name | string | Yes (signup only) | User's name input | "" |
| errors | ValidationErrors | Yes | Validation error messages | {} |
| isSubmitting | boolean | Yes | Form submission in progress | false |

### Lifecycle

1. **Initialization**: Form mounts, all fields empty
2. **User Input**: Fields update as user types
3. **Validation**: Client-side validation on blur or submit
4. **Submission**: isSubmitting=true, call API
5. **Success**: Clear form, redirect to app
6. **Failure**: Set errors, isSubmitting=false
7. **Cleanup**: Form unmounts, state destroyed

### Validation Rules

**Email**:
- Required: Must not be empty
- Format: Must match email regex pattern
- Example: "user@example.com"

**Password**:
- Required: Must not be empty
- Length: Minimum 8 characters
- Complexity: At least one letter AND one number
- Example: "SecurePass123"

**Name** (signup only):
- Required: Must not be empty after trimming
- Length: At least 1 character after trim
- Example: "John Doe"

### Error Messages

| Validation | Error Message |
|------------|---------------|
| Email empty | "Email is required" |
| Email invalid | "Invalid email format" |
| Password empty | "Password is required" |
| Password too short | "Password must be at least 8 characters" |
| Password weak | "Password must contain at least one letter and one number" |
| Name empty | "Name is required" |
| Backend 401 | "Invalid email or password" |
| Backend 409 | "Email already registered" |
| Backend 500 | "An error occurred. Please try again." |
| Network error | "Unable to connect to server" |

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser Environment                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │ localStorage │◄────────┤  JWT Token   │                  │
│  │ (persistent) │         │  (string)    │                  │
│  └──────┬───────┘         └──────▲───────┘                  │
│         │                        │                           │
│         │ load on mount          │ store on login/signup    │
│         │                        │                           │
│         ▼                        │                           │
│  ┌──────────────────────────────┴───────┐                   │
│  │      AuthContext (React State)       │                   │
│  │  ┌────────────────────────────────┐  │                   │
│  │  │ isAuthenticated: boolean       │  │                   │
│  │  │ user: User | null              │  │                   │
│  │  │ token: string | null           │  │                   │
│  │  │ loading: boolean               │  │                   │
│  │  │ error: string | null           │  │                   │
│  │  └────────────────────────────────┘  │                   │
│  └──────────────┬───────────────────────┘                   │
│                 │                                            │
│                 │ provides state to                         │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────┐                   │
│  │     Components (useAuth hook)        │                   │
│  │  ┌────────────────────────────────┐  │                   │
│  │  │ LoginForm                      │  │                   │
│  │  │ SignupForm                     │  │                   │
│  │  │ ProtectedRoute                 │  │                   │
│  │  │ Navbar (user display)          │  │                   │
│  │  └────────────────────────────────┘  │                   │
│  └──────────────┬───────────────────────┘                   │
│                 │                                            │
│                 │ API calls with token                      │
│                 │                                            │
└─────────────────┼────────────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  Backend API       │
         │  (FastAPI)         │
         │                    │
         │  POST /api/auth/   │
         │    signup          │
         │    login           │
         │                    │
         │  Protected routes  │
         │  (require JWT)     │
         └────────────────────┘
```

---

## Relationships

### JWT Token ↔ Authentication State
- **Relationship**: One-to-one
- **Direction**: Token stored in localStorage → loaded into AuthState on mount
- **Lifecycle**: Token persists across sessions, AuthState is recreated on mount
- **Synchronization**: AuthState.token always reflects localStorage token

### Authentication State ↔ Form State
- **Relationship**: One-to-many (one AuthState, multiple forms)
- **Direction**: Forms call AuthState methods (login, signup)
- **Lifecycle**: Forms are ephemeral, AuthState persists
- **Data Flow**: Form → AuthState.login/signup → API → AuthState update

### JWT Token ↔ API Requests
- **Relationship**: One-to-many (one token, many requests)
- **Direction**: Token attached to Authorization header for each request
- **Lifecycle**: Token used until expiration or logout
- **Format**: `Authorization: Bearer <token>`

---

## Implementation Notes

### Token Decoding (Optional)
The frontend MAY decode the JWT token to extract user information without making an API call. This is safe because:
- Token signature is verified by backend on each API request
- Frontend only uses decoded data for display purposes
- Backend is the source of truth for authorization

```typescript
// Optional: Decode JWT to get user info
function decodeToken(token: string): User | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return {
      id: parseInt(payload.sub),
      email: payload.email,
      name: payload.name || payload.email  // Fallback if name not in token
    }
  } catch {
    return null
  }
}
```

### State Persistence Strategy
- **JWT Token**: Persisted in localStorage (survives browser close)
- **Authentication State**: Recreated on app load from localStorage token
- **Form State**: Never persisted (security best practice)
- **User Data**: Derived from token or fetched from API

### Error Recovery
- **Invalid Token**: Clear from localStorage, set isAuthenticated=false
- **Expired Token**: Detected by backend 401, clear and redirect to login
- **Network Error**: Show error message, keep current state
- **Validation Error**: Show inline errors, keep form data

---

## Summary

This data model defines three key entities for frontend authentication:

1. **JWT Token**: Persistent authentication credential stored in localStorage
2. **Authentication State**: Runtime state managed by React Context
3. **Form State**: Ephemeral state for user input during authentication

The model ensures clear separation between persistent storage (localStorage), runtime state (React Context), and temporary form data (component state), following React and Next.js best practices.
