# Research Summary: JWT Authentication Implementation

## Decision: JWT Library Selection

**Chosen**: PyJWT (v2.8.0+)

**Rationale**: PyJWT is the industry-standard Python library for JWT operations, offering the best balance of simplicity, performance, and security for our use case. It provides all necessary features for Better Auth JWT token verification without unnecessary complexity.

**Alternatives Considered**:
1. **python-jose**: More comprehensive JOSE implementation but slower performance, less active maintenance, and unnecessary complexity for simple JWT verification
2. **authlib**: Excellent comprehensive auth solution with OAuth/OIDC support, but overkill for our current JWT-only requirements

**Key Advantages**:
- Lightweight and fast (10,000-50,000 tokens/sec)
- Minimal dependencies
- Excellent community support (5.3k+ GitHub stars)
- Simple, focused API
- Active maintenance
- Perfect compatibility with Better Auth standard JWT format

## Decision: Authentication Pattern

**Chosen**: FastAPI Dependency Injection

**Rationale**: Dependency injection provides granular per-route control, excellent testability, automatic Swagger integration, and clean separation of concerns. This aligns with constitutional principle II (Clear Separation of Concerns).

**Alternatives Considered**:
1. **Middleware approach**: Global application to all routes, harder to test, no automatic Swagger integration, runs on every request including health checks

**Implementation Pattern**:
- HTTPBearer security scheme for token extraction
- Composable dependencies for token verification and user extraction
- Reusable across all protected endpoints
- Easy to mock for testing

## Decision: Token Verification Strategy

**Chosen**: Centralized JWT handler with dependency injection

**Rationale**: Centralizing JWT verification logic ensures consistent security enforcement across all endpoints, prevents code duplication, and makes security updates easier to apply.

**Key Components**:
1. **JWTHandler class**: Encapsulates token verification logic
2. **get_current_user dependency**: Extracts authenticated user identity
3. **verify_user_access dependency**: Enforces ownership verification

## Critical Discovery: Better Auth Architecture

**Finding**: Better Auth is primarily designed for cookie-based browser authentication, not standalone JWT bearer tokens for API services.

**What Better Auth Provides**:
- Cookie-based session management (primary method)
- JWT as cookie cache encoding strategy
- Browser-focused authentication flows

**What Our Project Assumes**:
- Better Auth issues standalone JWT tokens
- Tokens sent via Authorization: Bearer header
- Backend verifies tokens independently

**Resolution Strategy**:
1. Verify Better Auth can be configured for JWT bearer token issuance
2. Document any custom configuration required
3. Implement flexible token extraction (support both cookie and header)
4. Plan for potential custom token issuance if needed

## Better Auth JWT Token Format

**Algorithm**: HS256 (HMAC with SHA-256)
**Signing**: Symmetric using shared secret (BETTER_AUTH_SECRET)

**Standard Claims**:
- `sub` (subject): User identifier
- `exp` (expiration): Unix timestamp
- `iat` (issued at): Unix timestamp
- `iss` (issuer): Optional
- `aud` (audience): Optional

**Expected Payload Structure**:
```json
{
  "sub": "user-uuid-abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1770461300,
  "exp": 1770547700
}
```

**Alternative Nested Format**:
```json
{
  "user": {
    "id": "user-uuid-123",
    "email": "user@example.com"
  },
  "session": {
    "id": "session-uuid",
    "expiresAt": 1770547700
  }
}
```

## Security Considerations

**Shared Secret Management**:
- Store in BETTER_AUTH_SECRET environment variable
- Minimum 32 bytes for HS256
- Never commit to version control
- Must match secret used by Better Auth

**Token Validation Requirements**:
- Verify signature using shared secret
- Check expiration (exp claim)
- Validate required claims (sub, exp)
- Extract user identity from sub claim
- Handle clock skew with leeway parameter

**Error Handling**:
- Return 401 for missing/invalid/expired tokens
- Return 403 for insufficient permissions
- Don't expose sensitive details in error messages
- Log authentication failures for security monitoring

## Performance Considerations

**Token Verification Overhead**:
- PyJWT verification: <1ms per token
- Target: <50ms total authentication overhead
- No database lookups required (stateless)
- Caching not needed due to fast verification

**Optimization Strategies**:
- Verify tokens only on protected endpoints
- Use dependency injection to avoid global middleware
- Leverage PyJWT's C extensions for performance
- Implement efficient user identity extraction

## Testing Strategy

**Unit Tests**:
- JWT handler token verification
- User identity extraction
- Error handling for invalid tokens
- Expiration enforcement

**Integration Tests**:
- Protected endpoint access with valid tokens
- Rejection of invalid/expired tokens
- User data isolation enforcement
- Cross-user access prevention

**Contract Tests**:
- API responses match OpenAPI specification
- Proper HTTP status codes (401, 403)
- Error response format consistency

## Dependencies

**New Dependencies**:
- PyJWT[crypto]==2.8.0 (JWT encoding/decoding with cryptography support)

**Existing Dependencies**:
- FastAPI (HTTP framework)
- SQLModel (ORM)
- python-dotenv (environment configuration)

## Implementation Phases

**Phase 1**: JWT verification infrastructure
- Create auth module with JWT handler
- Implement authentication dependencies
- Add environment configuration

**Phase 2**: Endpoint protection
- Update task routes with authentication
- Enforce user data isolation
- Remove user_id from URL paths (use token instead)

**Phase 3**: Testing and validation
- Add comprehensive test coverage
- Verify security requirements
- Performance testing

## Open Questions

1. **Better Auth Configuration**: How to configure Better Auth to issue JWT bearer tokens (not just cookies)?
2. **User ID Format**: Does Better Auth use integer IDs or UUIDs in the sub claim?
3. **Token Expiration**: What is the actual token expiration time configured in Better Auth?
4. **Custom Claims**: Does Better Auth include any custom claims beyond standard JWT claims?

These questions should be resolved during implementation through Better Auth documentation review and testing.
