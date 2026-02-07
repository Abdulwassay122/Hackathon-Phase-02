# Better Auth JWT Token Research

**Date**: 2026-02-07
**Purpose**: Determine JWT token format and structure for FastAPI backend integration

## Executive Summary

Better Auth primarily uses **cookie-based session management** rather than standalone JWT bearer tokens. However, it supports JWT encoding as one of three cookie cache strategies. The project requirements assume Better Auth can issue JWT tokens for API authentication, but this pattern is not explicitly documented in Better Auth's official documentation.

## Key Findings

### 1. Better Auth Session Architecture

Better Auth uses traditional cookie-based sessions with the following structure:

**Session Table Fields:**
- `id`: Unique session identifier
- `userId`: Foreign key to user table
- `token`: Unique session token (also used as session cookie)
- `expiresAt`: Session expiration timestamp
- `ipAddress`: Client IP address (optional)
- `userAgent`: Client user agent (optional)
- `createdAt`/`updatedAt`: Timestamps

**User Table Fields:**
- `id`: Unique user identifier
- `email`: User email address
- `name`: User display name
- `emailVerified`: Email verification status
- `image`: User profile image
- Timestamps

### 2. JWT Cookie Cache Strategy

Better Auth supports three encoding strategies for cookie caching:

| Strategy | Algorithm | Security | Size | Readable | Use Case |
|----------|-----------|----------|------|----------|----------|
| `compact` | Base64url + HMAC-SHA256 | Good | Smallest | No | Default, minimal overhead |
| `jwt` | HS256 (HMAC-SHA256) | Good | Medium | Yes | External system interoperability |
| `jwe` | A256CBC-HS512 + HKDF | Best | Largest | No | Maximum security, encrypted |

**Configuration Example:**
```typescript
export const auth = betterAuth({
    session: {
        cookieCache: {
            enabled: true,
            maxAge: 5 * 60, // 5 minutes
            strategy: "jwt"
        }
    }
});
```

### 3. Session Data Payload Structure

From Better Auth source code (`packages/better-auth/src/cookies/index.ts`), the session data encoded in JWT tokens contains:

```typescript
{
  session: {
    id: string,
    userId: string,
    token: string,
    expiresAt: number,
    ipAddress?: string,
    userAgent?: string,
    // ... additional session fields
  },
  user: {
    id: string,
    email: string,
    name: string,
    emailVerified: boolean,
    image?: string,
    // ... additional user fields
  },
  updatedAt: number,  // Timestamp
  version: string     // Cache version
}
```

### 4. JWT Standard Claims

Based on JWT RFC 7519 and Better Auth implementation:

**Registered Claims (Standard):**
- `sub` (subject): User identifier - "identifies the principal that is the subject of the JWT"
- `exp` (expiration): Unix timestamp - "identifies the expiration time on or after which the JWT MUST NOT be accepted"
- `iat` (issued at): Unix timestamp - "identifies the time at which the JWT was issued"
- `iss` (issuer): Token issuer (optional)
- `aud` (audience): Token audience (optional)

**Better Auth Custom Payload:**
Better Auth appears to embed the entire session and user objects rather than using minimal standard claims.

### 5. Token Signing Algorithm

**Algorithm**: HS256 (HMAC with SHA-256)
- **Type**: Symmetric signing
- **Key Requirement**: Shared secret (minimum 32 bytes recommended)
- **Security**: Signed but not encrypted - tokens are readable but tamper-proof

**JWT Library**: Better Auth uses `jose` (v6.1.3) for JWT operations

### 6. Token Expiration Handling

**Session Expiration:**
- Default: 7 days (`expiresIn: 60 * 60 * 24 * 7`)
- Configurable via `session.expiresIn` setting

**Cookie Cache Expiration:**
- Default: 5 minutes (`maxAge: 5 * 60`)
- Separate from session expiration
- Automatic refresh at 80% of maxAge (configurable)

**Validation:**
- PyJWT automatically validates `exp` claim during `jwt.decode()`
- Raises `jwt.ExpiredSignatureError` if token is expired
- Supports `leeway` parameter for clock skew tolerance

### 7. Shared Secret Configuration

**Environment Variable**: `BETTER_AUTH_SECRET`
- Used for signing JWT tokens
- Must be shared between Better Auth (frontend/auth service) and FastAPI backend
- Minimum recommended length: 32 bytes for HS256

**Configuration:**
```typescript
// Better Auth
export const auth = betterAuth({
    secret: process.env.BETTER_AUTH_SECRET
});
```

```python
# FastAPI Backend
import os
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
```

## Critical Gap: Bearer Token Authentication

**Issue**: Better Auth documentation does not explicitly cover:
- Issuing standalone JWT tokens for API authentication
- Using JWT tokens in `Authorization: Bearer <token>` headers
- Extracting session tokens from cookies for API use
- Service-to-service authentication patterns

**Current Architecture**: Better Auth is designed for:
- Browser-based cookie authentication
- Automatic session management via cookies
- Server-side session validation

**Project Assumption**: The CLAUDE.md file states:
> "Better Auth can be configured to issue JWT (JSON Web Token) tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key."

**Reality**: This pattern is not documented in Better Auth's official documentation. The JWT strategy is only for cookie cache encoding, not standalone bearer tokens.

## Recommended JWT Token Structure for FastAPI Backend

Based on standard JWT practices and Better Auth's session structure, the expected token format should be:

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload (Minimal Claims)
```json
{
  "sub": "user-uuid-abc123",           // User ID from Better Auth
  "email": "user@example.com",         // User email
  "name": "John Doe",                  // User display name (optional)
  "iat": 1770461300,                   // Issued at (Unix timestamp)
  "exp": 1770547700                    // Expiration (Unix timestamp)
}
```

### Payload (Full Session Data - Better Auth Style)
```json
{
  "session": {
    "id": "session-uuid",
    "userId": "user-uuid-abc123",
    "token": "session-token-string",
    "expiresAt": 1770547700
  },
  "user": {
    "id": "user-uuid-abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": true
  },
  "updatedAt": 1770461300,
  "version": "1.0"
}
```

### Signature
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  BETTER_AUTH_SECRET
)
```

## PyJWT Verification Example

```python
import jwt
import os
from typing import Dict, Any

JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = "HS256"

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and extract user identity.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")

def extract_user_id(payload: Dict[str, Any]) -> str:
    """
    Extract user ID from token payload.

    Supports both standard JWT format (sub claim) and
    Better Auth format (nested user.id).
    """
    # Standard JWT format
    if "sub" in payload:
        return payload["sub"]

    # Better Auth format
    if "user" in payload and "id" in payload["user"]:
        return payload["user"]["id"]

    # Fallback to session.userId
    if "session" in payload and "userId" in payload["session"]:
        return payload["session"]["userId"]

    raise ValueError("No user identifier found in token")
```

## Token Verification Requirements

### FastAPI Backend Must:

1. **Extract Token from Header**
   ```python
   from fastapi import Header, HTTPException

   async def get_token(authorization: str = Header(None)) -> str:
       if not authorization:
           raise HTTPException(status_code=401, detail="Missing authorization header")

       scheme, token = authorization.split()
       if scheme.lower() != "bearer":
           raise HTTPException(status_code=401, detail="Invalid authentication scheme")

       return token
   ```

2. **Verify Signature**
   - Use shared secret from `BETTER_AUTH_SECRET`
   - Validate HMAC-SHA256 signature
   - Reject tokens with invalid signatures

3. **Validate Claims**
   - Check `exp` (expiration) - reject expired tokens
   - Verify `iat` (issued at) is not in the future
   - Extract `sub` (subject) for user identification

4. **Match User Identity**
   - Extract user ID from token payload
   - Compare with `user_id` in request URL/body
   - Reject requests where authenticated user ≠ requested user

5. **Filter Database Queries**
   - Add `WHERE user_id = <authenticated_user_id>` to all queries
   - Prevent cross-user data access

## Security Considerations

1. **Secret Key Management**
   - Store `BETTER_AUTH_SECRET` in environment variables
   - Never commit secrets to version control
   - Use minimum 32-byte random string for HS256

2. **Token Expiration**
   - Set reasonable expiration times (e.g., 1 hour to 24 hours)
   - Implement token refresh mechanism if needed
   - Reject expired tokens immediately

3. **HTTPS Required**
   - Always use HTTPS in production
   - Tokens in Authorization headers are vulnerable over HTTP

4. **Error Messages**
   - Return generic "Unauthorized" messages
   - Don't expose token validation details to clients
   - Log authentication failures for security monitoring

## Open Questions

1. **How does Better Auth issue standalone JWT tokens?**
   - Not documented in official Better Auth documentation
   - May require custom implementation or plugin
   - Cookie extraction might be necessary

2. **What is the exact claim structure?**
   - Standard JWT claims (`sub`, `exp`, `iat`) or nested objects?
   - Need to test with actual Better Auth implementation

3. **How to configure Better Auth for bearer token authentication?**
   - Documentation focuses on cookie-based sessions
   - May need to extract session token from cookies manually
   - Consider using Better Auth's stateless session mode

## Recommendations

1. **Verify Better Auth Configuration**
   - Confirm Better Auth can issue JWT tokens for API use
   - Test token format with actual Better Auth instance
   - Document any custom configuration required

2. **Use Standard JWT Claims**
   - Prefer minimal payload with standard claims (`sub`, `exp`, `iat`)
   - Avoid embedding large session objects in tokens
   - Keep tokens compact for performance

3. **Implement Robust Verification**
   - Use PyJWT library for token verification
   - Validate all required claims
   - Handle expiration and invalid tokens gracefully

4. **Plan for Token Refresh**
   - Consider implementing refresh token mechanism
   - Handle token expiration in frontend
   - Provide clear error messages for expired tokens

## References

- Better Auth Documentation: https://www.better-auth.com/docs
- Better Auth Session Management: https://www.better-auth.com/docs/concepts/session-management
- JWT RFC 7519: https://tools.ietf.org/html/rfc7519
- JWT.io Introduction: https://jwt.io/introduction
- PyJWT Documentation: https://pyjwt.readthedocs.io/
- jose Library (used by Better Auth): https://github.com/panva/jose

## Next Steps

1. Test Better Auth JWT token issuance with actual implementation
2. Verify token payload structure matches expectations
3. Implement FastAPI middleware for JWT verification
4. Create integration tests for authentication flow
5. Document any custom Better Auth configuration required
