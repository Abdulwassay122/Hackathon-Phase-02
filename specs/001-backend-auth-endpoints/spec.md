# Feature Specification: Backend Authentication Endpoints

**Feature Branch**: `001-backend-auth-endpoints`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Resolve Authentication Architecture Mismatch

Objective:
Resolve the authentication disconnect by defining and implementing a single, functional auth flow between the frontend and backend.

Problem statement:
The backend can verify JWT tokens but cannot create users or issue tokens.
The frontend uses Better Auth for login, but no auth service or backend endpoints exist to support this flow.

Chosen approach:
Implement authentication directly in the FastAPI backend.

Scope:
- Add User model to backend database
- Implement /api/auth/signup endpoint
- Implement /api/auth/login endpoint
- Hash and verify passwords securely
- Generate and issue JWT tokens from backend
- Keep existing JWT verification and protected routes

Success criteria:
- Users can sign up and log in successfully
- Backend issues valid JWT tokens
- Frontend can authenticate and access protected APIs
- Existing task isolation by user_id continues to work

Constraints:
- JWT-based auth only
- Backend is the single source of truth for authentication
- No external auth services

Not building:
- OAuth providers
- Email verification
- Password reset flows"

## User Scenarios & Testing

### User Story 1 - New User Registration (Priority: P1)

A new user wants to create an account in the todo application so they can start managing their tasks. The user provides their email, password, and name to register. The system creates a new user account, securely stores their credentials, and returns a JWT token so they can immediately start using the application.

**Why this priority**: This is the foundation of the authentication system. Without user registration, no one can create accounts or use the application. This is the absolute minimum requirement for a functional authentication system and must be implemented first.

**Independent Test**: Can be fully tested by sending a POST request to the signup endpoint with valid user data (email, password, name) and verifying that a user account is created in the database and a valid JWT token is returned. Delivers the value of allowing new users to join the application.

**Acceptance Scenarios**:

1. **Given** no existing user with email "user@example.com", **When** a user submits signup with email "user@example.com", password "SecurePass123", and name "John Doe", **Then** a new user account is created and a JWT token is returned
2. **Given** a user with email "existing@example.com" already exists, **When** a new user tries to signup with the same email, **Then** the system rejects the request with an error message indicating the email is already registered
3. **Given** a user submits signup with an invalid email format, **When** the system validates the input, **Then** the request is rejected with an error message indicating invalid email format
4. **Given** a user submits signup with a weak password (less than 8 characters), **When** the system validates the input, **Then** the request is rejected with an error message indicating password requirements
5. **Given** a user submits signup with missing required fields (email, password, or name), **When** the system validates the input, **Then** the request is rejected with an error message indicating which fields are required

---

### User Story 2 - Existing User Login (Priority: P2)

An existing user wants to log in to the todo application to access their tasks. The user provides their email and password. The system verifies the credentials, and if valid, returns a JWT token that the user can use to access protected endpoints.

**Why this priority**: While critical for returning users, the application can function with just registration for initial testing. Login is essential for production use but not blocking for the MVP. This is the second most important feature after registration.

**Independent Test**: Can be fully tested by first creating a user account, then sending a POST request to the login endpoint with the correct email and password, and verifying that a valid JWT token is returned. Delivers the value of allowing existing users to authenticate and access their data.

**Acceptance Scenarios**:

1. **Given** a user with email "user@example.com" and password "SecurePass123" exists, **When** the user submits login with correct credentials, **Then** a JWT token is returned
2. **Given** a user with email "user@example.com" exists, **When** the user submits login with an incorrect password, **Then** the system rejects the request with an error message indicating invalid credentials
3. **Given** no user with email "nonexistent@example.com" exists, **When** someone tries to login with this email, **Then** the system rejects the request with an error message indicating invalid credentials
4. **Given** a user submits login with missing email or password, **When** the system validates the input, **Then** the request is rejected with an error message indicating which fields are required
5. **Given** a user successfully logs in, **When** the JWT token is decoded, **Then** it contains the user's ID and email in the payload

---

### User Story 3 - Secure Token Management (Priority: P3)

Users want their authentication tokens to be secure and properly managed. The system generates JWT tokens with appropriate expiration times, includes necessary user information in the token payload, and ensures tokens can be verified by existing protected endpoints.

**Why this priority**: While important for security and production readiness, basic token generation can work with simple defaults during development. This is an enhancement to ensure production-ready security and proper integration with existing JWT verification.

**Independent Test**: Can be fully tested by generating a token, verifying it contains the correct user information (user ID, email), checking that it has an expiration time set, and confirming that existing protected endpoints (like task routes) can successfully verify and use the token. Delivers the value of secure, production-ready authentication.

**Acceptance Scenarios**:

1. **Given** a user successfully signs up or logs in, **When** a JWT token is generated, **Then** the token includes the user's ID in the "sub" claim and email in the payload
2. **Given** a JWT token is generated, **When** the token is inspected, **Then** it has an expiration time set (default 24 hours from issuance)
3. **Given** a valid JWT token is issued, **When** the token is used to access a protected endpoint (e.g., GET /api/users/{user_id}/tasks), **Then** the existing JWT verification middleware successfully validates the token
4. **Given** a JWT token has expired, **When** the token is used to access a protected endpoint, **Then** the system rejects the request with a 401 Unauthorized error
5. **Given** a JWT token is generated with user ID 123, **When** the token is used to access /api/users/456/tasks, **Then** the system rejects the request because the user ID in the token doesn't match the requested resource

---

### Edge Cases

- What happens when a user tries to register with an email that already exists?
- How does the system handle SQL injection attempts in email or password fields?
- What happens when a user submits a password that is too short or doesn't meet security requirements?
- How does the system handle missing or malformed request bodies?
- What happens when a user tries to login with an email that doesn't exist?
- How does the system handle concurrent registration attempts with the same email?
- What happens when the database is unavailable during signup or login?
- How does the system handle special characters in passwords?
- What happens when a user submits an extremely long email or password?
- How does the system prevent timing attacks during password verification?

## Requirements

### Functional Requirements

- **FR-001**: System MUST create a User table/model in the database with fields for id, email, password (hashed), name, created_at, and updated_at
- **FR-002**: System MUST provide a POST /api/auth/signup endpoint that accepts email, password, and name
- **FR-003**: System MUST validate that email addresses are in a valid format before creating accounts
- **FR-004**: System MUST enforce password requirements: minimum 8 characters, at least one letter and one number
- **FR-005**: System MUST hash passwords using a secure algorithm (bcrypt, argon2, or similar) before storing in the database
- **FR-006**: System MUST prevent duplicate email registrations by enforcing email uniqueness
- **FR-007**: System MUST provide a POST /api/auth/login endpoint that accepts email and password
- **FR-008**: System MUST verify passwords by comparing the submitted password against the stored hash
- **FR-009**: System MUST generate JWT tokens upon successful signup or login
- **FR-010**: System MUST include user ID in the JWT token's "sub" claim for compatibility with existing JWT verification
- **FR-011**: System MUST include user email in the JWT token payload
- **FR-012**: System MUST set JWT token expiration time to 24 hours from issuance
- **FR-013**: System MUST return appropriate HTTP status codes: 201 for successful signup, 200 for successful login, 400 for validation errors, 401 for invalid credentials, 409 for duplicate email
- **FR-014**: System MUST return error messages that are informative but don't reveal sensitive information (e.g., don't distinguish between "email not found" vs "wrong password")
- **FR-015**: System MUST sanitize all user inputs to prevent SQL injection and XSS attacks
- **FR-016**: System MUST integrate with existing JWT verification middleware without requiring changes to protected endpoints

### Key Entities

- **User**: Represents a registered user in the system. Contains email (unique identifier), hashed password (for authentication), name (display name), id (primary key for relationships with tasks), and timestamps (created_at, updated_at for audit trail). Users have a one-to-many relationship with tasks (one user owns many tasks).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can successfully create a new account by providing email, password, and name, receiving a valid JWT token in under 2 seconds
- **SC-002**: Users can successfully log in with correct credentials, receiving a valid JWT token in under 1 second
- **SC-003**: Invalid login attempts (wrong password or non-existent email) are rejected with appropriate error messages within 1 second
- **SC-004**: Duplicate email registration attempts are prevented and return clear error messages
- **SC-005**: Generated JWT tokens are successfully validated by existing protected endpoints (task routes) without modification
- **SC-006**: Users can access their tasks immediately after signup or login using the returned JWT token
- **SC-007**: Password security meets industry standards with secure hashing and minimum complexity requirements
- **SC-008**: System handles 100 concurrent signup/login requests without errors or performance degradation
- **SC-009**: All authentication endpoints return appropriate HTTP status codes and error messages for different failure scenarios
- **SC-010**: Existing task isolation by user_id continues to work correctly with the new authentication system

## Assumptions

- Email addresses are used as the unique identifier for users (no username field)
- Passwords are hashed using bcrypt with a cost factor of 12 (industry standard)
- JWT tokens expire after 24 hours (reasonable default for web applications)
- The existing JWT verification middleware expects user ID in the "sub" claim
- Password requirements are: minimum 8 characters, at least one letter and one number
- The database supports unique constraints on the email field
- The backend uses the same JWT secret (BETTER_AUTH_SECRET) for both token generation and verification
- The frontend will store JWT tokens in localStorage or sessionStorage
- HTTPS will be used in production to protect credentials in transit
- The existing database connection and ORM (SQLModel) will be used for the User model
- User accounts are created immediately without email verification (email verification is out of scope)
- Password reset functionality is not included in this feature (out of scope)

## Out of Scope

The following are explicitly excluded from this feature:

- OAuth providers (Google, GitHub, etc.)
- Social login integration
- Email verification during signup
- Password reset/forgot password functionality
- Two-factor authentication (2FA)
- Account deletion or deactivation
- User profile updates (changing email, password, name)
- Session management beyond JWT tokens
- Refresh tokens or token rotation
- Rate limiting on authentication endpoints
- CAPTCHA or bot protection
- Account lockout after failed login attempts
- Password history tracking
- Multi-device session management
- User roles or permissions (beyond basic user authentication)
- Admin user creation or management
- Audit logging of authentication events
- Integration with external identity providers

## Dependencies

- **Existing JWT Verification**: Requires the existing JWT verification middleware (jwt_handler.py) to remain compatible
- **Database**: Requires PostgreSQL database (Neon) to be accessible for User table creation
- **SQLModel ORM**: Requires SQLModel for database operations
- **Password Hashing Library**: Requires bcrypt or passlib library for secure password hashing
- **PyJWT Library**: Requires PyJWT library for JWT token generation (already installed)
- **Existing Task Model**: User model must integrate with existing Task model's user_id foreign key relationship

## Technical Constraints

- Must use the existing BETTER_AUTH_SECRET environment variable for JWT signing
- Must use the existing JWT_ALGORITHM (HS256) for token generation
- Must generate JWT tokens compatible with existing JWT verification middleware
- Must use SQLModel for database models (consistent with existing codebase)
- Must follow existing FastAPI routing patterns (prefix /api/auth)
- Must return JSON responses in a format compatible with frontend expectations
- Must not break existing protected endpoints or JWT verification logic
- Password hashing must be performed synchronously (FastAPI will handle async wrapping)
- User ID must be an integer to match existing Task model's user_id field type
