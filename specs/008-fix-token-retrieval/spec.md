# Feature Specification: Fix Token Retrieval for API Requests

**Feature Branch**: `008-fix-token-retrieval`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Fix Token Retrieval for API Requests - Objective: Fix auth token retrieval by replacing getSession/getToken with direct JWT access. Scope: Stop using getSession() and getToken(), Read JWT from storage (localStorage or cookie), Attach Authorization: Bearer <token> to all task requests. Success criteria: Token is non-null on every request, /api/tasks returns 200 instead of 403"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticated User Can View Tasks (Priority: P1)

An authenticated user who has successfully logged in should be able to view their task list without encountering 403 Forbidden errors.

**Why this priority**: This is the core functionality - without proper token retrieval, authenticated users cannot access their data, making the application unusable.

**Independent Test**: Login with valid credentials, navigate to /tasks page, verify that the task list loads successfully with HTTP 200 response (not 403).

**Acceptance Scenarios**:

1. **Given** user has logged in and has valid JWT token in localStorage, **When** user navigates to /tasks page, **Then** API request to GET /api/tasks includes Authorization header with Bearer token and returns 200 OK
2. **Given** user is on /tasks page with valid token, **When** user creates a new task, **Then** API request to POST /api/tasks includes Authorization header with Bearer token and returns 201 Created
3. **Given** user is on /tasks page with valid token, **When** user updates an existing task, **Then** API request to PUT /api/tasks/{id} includes Authorization header with Bearer token and returns 200 OK
4. **Given** user is on /tasks page with valid token, **When** user deletes a task, **Then** API request to DELETE /api/tasks/{id} includes Authorization header with Bearer token and returns 204 No Content

---

### User Story 2 - Token Persists Across Page Refreshes (Priority: P1)

An authenticated user should maintain their session and continue to access tasks after refreshing the page, without needing to re-login.

**Why this priority**: Session persistence is critical for user experience - users expect to remain logged in across page refreshes.

**Independent Test**: Login, navigate to /tasks, refresh the page, verify that tasks still load successfully without redirect to signin.

**Acceptance Scenarios**:

1. **Given** user has logged in and is viewing tasks, **When** user refreshes the page (F5), **Then** JWT token is retrieved from localStorage and all API requests succeed with 200 OK
2. **Given** user has logged in and is viewing tasks, **When** user closes and reopens the browser tab, **Then** JWT token is retrieved from localStorage and all API requests succeed with 200 OK

---

### User Story 3 - Expired Token Handling (Priority: P2)

When a user's JWT token expires, the system should gracefully handle the expiration by clearing the session and redirecting to signin.

**Why this priority**: Proper error handling prevents confusing user experiences and security issues with expired tokens.

**Independent Test**: Login, manually expire the token (or wait for expiration), attempt to access /tasks, verify redirect to signin with expired=true parameter.

**Acceptance Scenarios**:

1. **Given** user has expired JWT token in localStorage, **When** user attempts to access /tasks, **Then** API returns 401 Unauthorized, onAuthError callback fires, session is cleared, and user is redirected to /signin?expired=true
2. **Given** user is viewing tasks and token expires during session, **When** user performs any task operation (create/update/delete), **Then** API returns 401 Unauthorized, onAuthError callback fires, session is cleared, and user is redirected to /signin?expired=true

---

### Edge Cases

- What happens when localStorage is unavailable (private browsing mode)?
- What happens when token is malformed or corrupted in localStorage?
- What happens when user manually deletes token from localStorage while on /tasks page?
- How does system handle race conditions between token retrieval and API requests?
- What happens when multiple tabs are open and token expires in one tab?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST read JWT token directly from localStorage using key "auth-token"
- **FR-002**: System MUST attach JWT token as "Authorization: Bearer <token>" header to all API requests
- **FR-003**: System MUST NOT use getSession() or getToken() functions for API authentication
- **FR-004**: System MUST ensure token is non-null before making API requests
- **FR-005**: System MUST handle 401 Unauthorized responses by clearing session and redirecting to signin
- **FR-006**: System MUST handle missing or malformed tokens by redirecting to signin
- **FR-007**: System MUST log token retrieval failures for debugging purposes

### Key Entities *(include if feature involves data)*

- **JWT Token**: String stored in localStorage with key "auth-token", contains user authentication credentials
- **API Client**: HTTP client responsible for making authenticated requests to backend API
- **Authorization Header**: HTTP header in format "Authorization: Bearer <token>" attached to all API requests

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of API requests to /api/tasks/* endpoints include non-null Authorization header with Bearer token
- **SC-002**: GET /api/tasks returns HTTP 200 OK (not 403 Forbidden) for authenticated users
- **SC-003**: All task operations (create, read, update, delete) succeed with appropriate HTTP status codes (200, 201, 204)
- **SC-004**: Token retrieval from localStorage succeeds in 100% of cases when token exists
- **SC-005**: Expired or invalid tokens trigger proper error handling (401 → clear session → redirect to signin) in 100% of cases
- **SC-006**: No console errors related to "getToken" or "getSession" functions after implementation
