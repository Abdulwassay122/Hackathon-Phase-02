# Feature Specification: Fix Password Length Error (72-Byte Limit)

**Feature Branch**: `006-fix-password-length`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Resolve Password Length Error (72-Byte Limit) - Fix backend authentication failure caused by password byte-length limitations"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration with Long Password (Priority: P1) 🎯 MVP

A user attempts to create a new account using a password that exceeds 72 bytes in length. The system accepts the password, successfully creates the account, and allows the user to authenticate with that password in the future.

**Why this priority**: This is the most critical scenario because it directly addresses the reported error. Users cannot create accounts when this fails, blocking all access to the system.

**Independent Test**: Can be fully tested by attempting to register a new user with a password longer than 72 bytes (e.g., 80-character password) and verifying that: (1) registration succeeds without errors, (2) user receives confirmation, (3) user can immediately log in with the same long password.

**Acceptance Scenarios**:

1. **Given** a new user on the registration page, **When** they enter a valid email, name, and a password that is 80 characters long, **Then** the account is created successfully and they receive confirmation
2. **Given** a new user on the registration page, **When** they enter a valid email, name, and a password that is exactly 72 bytes, **Then** the account is created successfully
3. **Given** a new user on the registration page, **When** they enter a valid email, name, and a password that is 100 characters long with special characters, **Then** the account is created successfully without any byte-length errors

---

### User Story 2 - User Login with Long Password (Priority: P1) 🎯 MVP

A user who previously registered with a long password (>72 bytes) attempts to log in. The system correctly verifies their password and grants access without errors.

**Why this priority**: This is equally critical to registration because existing users with long passwords must be able to authenticate. Without this, users would be locked out of their accounts.

**Independent Test**: Can be fully tested by: (1) creating a user account with a password longer than 72 bytes, (2) logging out, (3) attempting to log in with the same long password, and verifying that authentication succeeds without errors.

**Acceptance Scenarios**:

1. **Given** a user with an existing account created with an 80-character password, **When** they enter their correct email and 80-character password on the login page, **Then** they are authenticated successfully and redirected to the application
2. **Given** a user with an existing account created with a 100-character password, **When** they enter their correct email and 100-character password, **Then** authentication succeeds without byte-length errors
3. **Given** a user with an existing account created with a 72-byte password, **When** they enter their correct email and password, **Then** authentication continues to work as before (no regression)

---

### Edge Cases

- What happens when a password is exactly 72 bytes?
- What happens when a password is 73 bytes (just over the limit)?
- What happens when a password contains multi-byte UTF-8 characters that push the byte count over 72 even though character count is lower?
- How does the system handle passwords that are 200+ characters long?
- What happens when a user tries to log in with a truncated version of their long password?
- What happens when a user changes their password from a short one to a long one (>72 bytes)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept passwords of any length during user registration without throwing byte-length errors
- **FR-002**: System MUST accept passwords of any length during user login without throwing byte-length errors
- **FR-003**: System MUST handle password byte-length limitations transparently without exposing technical error messages to users
- **FR-004**: System MUST consistently handle password length across both registration and login flows
- **FR-005**: System MUST correctly verify passwords regardless of their byte length
- **FR-006**: System MUST handle multi-byte UTF-8 characters in passwords correctly when calculating byte length
- **FR-007**: System MUST NOT reject valid authentication attempts due to password byte-length issues

### Key Entities

This fix does not introduce new entities. It modifies the behavior of existing password handling for:

- **User Account**: Existing entity that stores hashed passwords
- **Authentication Request**: Existing process that verifies user credentials

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully register with passwords up to 200 characters long without encountering errors
- **SC-002**: Users can successfully authenticate with passwords up to 200 characters long without encountering errors
- **SC-003**: The specific error message "password cannot be longer than 72 bytes, truncate manually if necessary" no longer appears in any user-facing or logged errors
- **SC-004**: 100% of registration attempts with long passwords (>72 bytes) succeed when all other validation passes
- **SC-005**: 100% of login attempts with correct long passwords (>72 bytes) succeed without runtime exceptions
- **SC-006**: System maintains backward compatibility - users with existing short passwords (<72 bytes) can still authenticate successfully

## Scope *(mandatory)*

### In Scope

- Detecting passwords that exceed 72 bytes before password hashing operations
- Truncating passwords to 72 bytes prior to hashing during registration
- Truncating passwords to 72 bytes prior to verification during login
- Ensuring consistent truncation behavior across signup and login flows
- Preventing the 72-byte error from reaching API responses or user-facing errors

### Out of Scope

- Changing the password hashing algorithm
- Adding password length validation or policy enforcement
- Modifying frontend validation or error messaging
- Implementing password strength requirements
- Adding user notifications about password truncation
- Changing how passwords are stored or transmitted

## Constraints *(mandatory)*

- **Backend-only change**: No modifications to frontend code or user interface
- **Algorithm preservation**: Must continue using the existing password hashing algorithm without changes
- **No breaking changes**: Existing users with short passwords must continue to authenticate successfully
- **Transparent handling**: Password truncation must be invisible to users (no warnings or notifications)

## Assumptions *(mandatory)*

- The current system uses bcrypt for password hashing, which has a 72-byte input limit
- Users are not currently aware of the 72-byte limit and may attempt to use longer passwords
- The error is occurring in production and blocking user registrations/logins
- Truncating passwords to 72 bytes is an acceptable security trade-off (bcrypt only uses first 72 bytes anyway)
- The system currently has no password length validation on the backend
- Frontend may or may not have password length limits (out of scope for this fix)

## Dependencies *(mandatory)*

- Existing password hashing module/library must support pre-truncation of input
- No external service dependencies
- No database schema changes required

## Risks

- **Security consideration**: Users who create passwords longer than 72 bytes will have their passwords effectively truncated, meaning they could authenticate with just the first 72 bytes. However, this is the existing behavior of bcrypt and does not introduce new security risks.
- **User confusion**: Users may not realize their very long passwords are being truncated, but this is acceptable as bcrypt only uses the first 72 bytes regardless.
- **Backward compatibility**: Must ensure existing password hashes continue to work after the fix is deployed.

## Non-Functional Requirements

- **Performance**: Password truncation must add negligible overhead (<1ms) to authentication operations
- **Reliability**: Fix must work consistently across all authentication attempts
- **Maintainability**: Solution should be simple and easy to understand for future developers
