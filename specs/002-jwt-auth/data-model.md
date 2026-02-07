# Data Model: JWT Authentication

## Overview

This feature does not introduce new database entities. Instead, it adds authentication and authorization layers to the existing Task entity from Phase 1 (001-todo-backend).

## Authentication Entities (Conceptual)

### Authentication Token

**Type**: Transient (not stored in database)

**Description**: A JWT (JSON Web Token) issued by Better Auth containing cryptographically signed user identity and expiration information.

**Structure**:
```json
{
  "sub": "user-uuid-123",
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1770461300,
  "exp": 1770547700
}
```

**Attributes**:
- `sub` (subject): Unique user identifier
- `exp` (expiration): Unix timestamp when token expires
- `iat` (issued at): Unix timestamp when token was created
- `email`: User's email address (optional)
- `name`: User's display name (optional)

**Lifecycle**:
- Created by Better Auth during user login
- Transmitted via HTTP Authorization header
- Verified by backend on each request
- Expires after configured duration (default: 7 days)
- Not stored server-side (stateless)

### User Identity

**Type**: Derived (extracted from JWT token)

**Description**: The authenticated user's identity extracted from a verified JWT token.

**Attributes**:
- `user_id`: Unique identifier matching the `sub` claim from JWT
- `email`: User's email address (if present in token)
- `username`: User's display name (if present in token)

**Usage**:
- Extracted during request processing
- Used to filter database queries
- Enforces data isolation
- Not persisted beyond request scope

### Protected Resource

**Type**: Existing entity with added protection

**Description**: The existing Task entity from Phase 1, now protected by authentication and authorization.

**No Schema Changes**: The Task entity schema remains unchanged:
```python
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    user_id: int  # Now verified against JWT token
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Behavioral Changes**:
- `user_id` field now verified against authenticated user from JWT
- All queries filtered by authenticated user_id
- Creation automatically sets user_id from JWT token
- Updates/deletes require ownership verification

## Authentication Flow Impact on Data

### Request Flow

1. **Token Extraction**: Extract JWT from Authorization header
2. **Token Verification**: Verify signature and expiration
3. **Identity Extraction**: Extract user_id from token's `sub` claim
4. **Ownership Verification**: Match token user_id with requested resource
5. **Query Filtering**: Filter all database queries by authenticated user_id

### Data Isolation Rules

**Rule 1: Automatic User Scoping**
- All task queries automatically filtered by authenticated user_id
- Users cannot query tasks belonging to other users

**Rule 2: Ownership Verification**
- Task creation: user_id set from JWT token (not request body)
- Task retrieval: user_id must match authenticated user
- Task update: user_id must match authenticated user
- Task deletion: user_id must match authenticated user

**Rule 3: No Cross-User Access**
- Attempting to access another user's task returns 403 Forbidden
- Database queries never return tasks from other users
- User cannot modify user_id field to access other users' data

## Validation Rules

### Token Validation

- Token must be present in Authorization header
- Token signature must be valid (verified with BETTER_AUTH_SECRET)
- Token must not be expired (exp claim checked)
- Token must contain required claims (sub, exp)
- Token user_id must match request context

### User Identity Validation

- User ID from token must be extractable
- User ID must be in valid format (integer or UUID)
- User ID must match user_id in request path (if present)

### Resource Access Validation

- Authenticated user must own the requested resource
- User cannot modify ownership of existing resources
- User cannot create resources for other users

## State Transitions

### Authentication State

```
Unauthenticated → [Valid Token Provided] → Authenticated
Authenticated → [Token Expires] → Unauthenticated
Authenticated → [Invalid Token] → Unauthenticated
```

### Resource Access State

```
Request Received → [Token Verified] → Identity Extracted
Identity Extracted → [Ownership Verified] → Access Granted
Identity Extracted → [Ownership Failed] → Access Denied (403)
Request Received → [Token Invalid] → Unauthorized (401)
```

## Configuration Data

### Environment Variables

**BETTER_AUTH_SECRET**:
- Type: String
- Required: Yes
- Description: Shared secret for JWT signature verification
- Security: Must match Better Auth configuration
- Storage: Environment variable (.env file)
- Minimum Length: 32 bytes

**JWT_ALGORITHM**:
- Type: String
- Required: No (defaults to HS256)
- Description: Algorithm used for JWT signature verification
- Allowed Values: HS256, HS384, HS512
- Default: HS256

## Migration Impact

### Database Migrations

**No database migrations required**. The existing Task table schema remains unchanged.

### API Changes

**Breaking Changes**:
- All task endpoints now require authentication
- Requests without valid JWT tokens will be rejected (401)
- User_id in URL path may be removed (derived from token instead)

**Backward Compatibility**:
- Phase 1 endpoints without authentication will no longer work
- Clients must update to include Authorization header
- No data migration needed

## Security Considerations

### Data Protection

- User data isolated by authenticated user_id
- No cross-user data leakage possible
- Ownership verified on every request
- Stateless authentication (no session storage)

### Token Security

- Tokens signed with cryptographic secret
- Signature verification prevents tampering
- Expiration prevents indefinite token validity
- Tokens transmitted over HTTPS only (production)

### Error Handling

- Authentication failures return 401 Unauthorized
- Authorization failures return 403 Forbidden
- Error messages don't expose sensitive information
- Failed attempts logged for security monitoring
