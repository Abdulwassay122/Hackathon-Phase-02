# Implementation Tasks: JWT Authentication for Task API

## Summary

This document breaks down the implementation of JWT authentication into testable, incremental tasks organized by user story. Each task follows the checklist format for easy tracking.

## Implementation Strategy

**Approach**: Implement features incrementally with user story priorities in mind. Start with foundational authentication infrastructure, then add endpoint protection (P1), user isolation (P2), and token expiry enforcement (P3).

**MVP Scope**: Complete User Story 1 (P1) which provides core authentication enforcement, making the API secure.

**Testing**: Each user story is independently testable via API calls with different authentication scenarios.

## Phase 1: Project Setup

- [ ] T001 Add PyJWT[crypto]==2.8.0 to backend/requirements.txt
- [ ] T002 Create backend/src/auth/ directory structure with __init__.py
- [ ] T003 Update .env.example with BETTER_AUTH_SECRET and JWT_ALGORITHM configuration
- [ ] T004 Create backend/tests/unit/test_jwt_handler.py file structure
- [ ] T005 Create backend/tests/integration/test_api_auth.py file structure

## Phase 2: Foundational Components

- [ ] T006 [P] Create JWTHandler class in backend/src/auth/jwt_handler.py with token verification logic
- [ ] T007 [P] Implement verify_token method in JWTHandler to decode and validate JWT signatures
- [ ] T008 [P] Implement extract_user_id method in JWTHandler to extract user identity from token payload
- [ ] T009 [P] Add error handling for expired tokens (ExpiredSignatureError) in JWTHandler
- [ ] T010 [P] Add error handling for invalid tokens (InvalidTokenError) in JWTHandler
- [ ] T011 Create HTTPBearer security scheme in backend/src/auth/dependencies.py
- [ ] T012 Implement get_current_user dependency in backend/src/auth/dependencies.py to extract authenticated user
- [ ] T013 Update backend/src/config.py to load BETTER_AUTH_SECRET and JWT_ALGORITHM from environment
- [ ] T014 Add JWT configuration validation in backend/src/config.py to ensure secret is set

## Phase 3: User Story 1 - Protected API Access (P1)

### Story Goal
Require authentication for all task API endpoints. Users must provide valid JWT tokens to access any task management functionality.

### Independent Test Criteria
- API calls without tokens receive 401 Unauthorized
- API calls with invalid tokens receive 401 Unauthorized
- API calls with valid tokens succeed and return user's tasks

### Tasks

#### Endpoint Protection
- [ ] T015 [P] [US1] Update GET /api/tasks endpoint in backend/src/api/task_routes.py to require authentication
- [ ] T016 [P] [US1] Update POST /api/tasks endpoint in backend/src/api/task_routes.py to require authentication
- [ ] T017 [P] [US1] Update GET /api/tasks/{task_id} endpoint in backend/src/api/task_routes.py to require authentication
- [ ] T018 [P] [US1] Update PUT /api/tasks/{task_id} endpoint in backend/src/api/task_routes.py to require authentication
- [ ] T019 [P] [US1] Update DELETE /api/tasks/{task_id} endpoint in backend/src/api/task_routes.py to require authentication
- [ ] T020 [P] [US1] Update PATCH /api/tasks/{task_id}/complete endpoint in backend/src/api/task_routes.py to require authentication

#### User Identity Integration
- [ ] T021 [US1] Modify POST /api/tasks to automatically set user_id from authenticated user in backend/src/api/task_routes.py
- [ ] T022 [US1] Remove user_id from request body validation in POST /api/tasks endpoint
- [ ] T023 [US1] Update task creation service to accept user_id from authentication in backend/src/services/task_service.py

#### Error Handling
- [ ] T024 [US1] Implement 401 Unauthorized response for missing authentication tokens
- [ ] T025 [US1] Implement 401 Unauthorized response for invalid authentication tokens
- [ ] T026 [US1] Ensure error messages don't expose sensitive information

#### Testing
- [ ] T027 [P] [US1] Create unit test for JWTHandler.verify_token with valid token in backend/tests/unit/test_jwt_handler.py
- [ ] T028 [P] [US1] Create unit test for JWTHandler.verify_token with invalid token in backend/tests/unit/test_jwt_handler.py
- [ ] T029 [P] [US1] Create unit test for JWTHandler.extract_user_id in backend/tests/unit/test_jwt_handler.py
- [ ] T030 [P] [US1] Create integration test for GET /api/tasks without token in backend/tests/integration/test_api_auth.py
- [ ] T031 [P] [US1] Create integration test for GET /api/tasks with valid token in backend/tests/integration/test_api_auth.py
- [ ] T032 [P] [US1] Create integration test for POST /api/tasks with valid token in backend/tests/integration/test_api_auth.py

## Phase 4: User Story 2 - User Data Isolation (P2)

### Story Goal
Enforce ownership verification to prevent users from accessing or manipulating other users' data. Implement strict data isolation at the API level.

### Independent Test Criteria
- User A cannot view User B's tasks (403 Forbidden)
- User A cannot modify User B's tasks (403 Forbidden)
- User A cannot delete User B's tasks (403 Forbidden)
- Users only see their own tasks in list operations

### Tasks

#### Ownership Verification
- [ ] T033 [US2] Implement ownership verification in GET /api/tasks/{task_id} endpoint in backend/src/api/task_routes.py
- [ ] T034 [US2] Implement ownership verification in PUT /api/tasks/{task_id} endpoint in backend/src/api/task_routes.py
- [ ] T035 [US2] Implement ownership verification in DELETE /api/tasks/{task_id} endpoint in backend/src/api/task_routes.py
- [ ] T036 [US2] Implement ownership verification in PATCH /api/tasks/{task_id}/complete endpoint in backend/src/api/task_routes.py

#### Query Filtering
- [ ] T037 [US2] Ensure GET /api/tasks filters results by authenticated user_id in backend/src/services/task_service.py
- [ ] T038 [US2] Ensure get_task_by_id_and_user verifies ownership in backend/src/services/task_service.py
- [ ] T039 [US2] Prevent user_id modification in PUT /api/tasks/{task_id} endpoint

#### Error Handling
- [ ] T040 [US2] Implement 403 Forbidden response when user attempts to access another user's task
- [ ] T041 [US2] Implement 403 Forbidden response when user attempts to modify another user's task
- [ ] T042 [US2] Add security logging for unauthorized access attempts

#### Testing
- [ ] T043 [P] [US2] Create integration test for cross-user task access attempt in backend/tests/integration/test_api_auth.py
- [ ] T044 [P] [US2] Create integration test for cross-user task modification attempt in backend/tests/integration/test_api_auth.py
- [ ] T045 [P] [US2] Create integration test for cross-user task deletion attempt in backend/tests/integration/test_api_auth.py
- [ ] T046 [P] [US2] Create integration test verifying user only sees own tasks in backend/tests/integration/test_api_auth.py

## Phase 5: User Story 3 - Token Expiry Enforcement (P3)

### Story Goal
Respect token expiration times and automatically reject expired tokens. Ensure stolen or leaked tokens have limited validity.

### Independent Test Criteria
- Expired tokens receive 401 Unauthorized
- Valid non-expired tokens continue to work
- Token expiration is checked on every request

### Tasks

#### Expiry Enforcement
- [ ] T047 [US3] Verify JWT expiry checking is enabled in JWTHandler.verify_token in backend/src/auth/jwt_handler.py
- [ ] T048 [US3] Implement proper error handling for ExpiredSignatureError with clear error message
- [ ] T049 [US3] Add clock skew tolerance (leeway parameter) to JWT verification for time synchronization issues

#### Testing
- [ ] T050 [P] [US3] Create unit test for expired token rejection in backend/tests/unit/test_jwt_handler.py
- [ ] T051 [P] [US3] Create integration test for API call with expired token in backend/tests/integration/test_api_auth.py
- [ ] T052 [P] [US3] Create integration test verifying token expiry is checked on all endpoints in backend/tests/integration/test_api_auth.py

## Phase 6: Contract Testing and Validation

### Tasks

- [ ] T053 [P] Update contract test for GET /api/tasks with authentication in backend/tests/contract/test_contracts.py
- [ ] T054 [P] Update contract test for POST /api/tasks with authentication in backend/tests/contract/test_contracts.py
- [ ] T055 [P] Update contract test for GET /api/tasks/{task_id} with authentication in backend/tests/contract/test_contracts.py
- [ ] T056 [P] Update contract test for PUT /api/tasks/{task_id} with authentication in backend/tests/contract/test_contracts.py
- [ ] T057 [P] Update contract test for DELETE /api/tasks/{task_id} with authentication in backend/tests/contract/test_contracts.py
- [ ] T058 [P] Update contract test for PATCH /api/tasks/{task_id}/complete with authentication in backend/tests/contract/test_contracts.py
- [ ] T059 [P] Add contract test for 401 Unauthorized response format in backend/tests/contract/test_contracts.py
- [ ] T060 [P] Add contract test for 403 Forbidden response format in backend/tests/contract/test_contracts.py
- [ ] T061 Run all contract tests to verify OpenAPI specification compliance

## Phase 7: Polish & Cross-Cutting Concerns

### Tasks

- [ ] T062 Update Swagger UI documentation to show Bearer authentication requirement
- [ ] T063 Add authentication examples to backend/README.md
- [ ] T064 Update quickstart.md with token generation examples for testing
- [ ] T065 Verify authentication overhead is <50ms per request through performance testing
- [ ] T066 Run security audit to verify no authentication bypass vulnerabilities
- [ ] T067 Verify all authentication failures are logged with sufficient detail
- [ ] T068 Test concurrent requests with same token to verify stateless operation
- [ ] T069 Verify JWT secret is not exposed in error messages or logs
- [ ] T070 Run full test suite to verify all tests pass
- [ ] T071 Update CLAUDE.md with authentication implementation notes

## Dependencies

### User Story Completion Order
1. User Story 1 (P1) - Protected API Access must be completed first (foundation)
2. User Story 2 (P2) - User Data Isolation depends on User Story 1 being functional
3. User Story 3 (P3) - Token Expiry Enforcement depends on User Story 1 being functional

### Blocking Relationships
- T006-T014 (Foundational) must complete before any user story tasks
- T015-T026 (US1 endpoint protection) must complete before US2 and US3 tasks
- T027-T032 (US1 tests) can run in parallel with US1 implementation
- T033-T042 (US2) can start after T015-T026 complete
- T047-T049 (US3) can start after T006-T014 complete (independent of US2)
- T053-T061 (Contract tests) should run after all user stories complete
- T062-T071 (Polish) should run after all user stories and tests complete

## Parallel Execution Examples

### Within Foundational Phase
- T006-T010 (JWT handler methods) can run in parallel (same file, different methods)
- T011-T012 (dependencies) can run in parallel with T006-T010 (different files)

### Within User Story 1
- T015-T020 (endpoint updates) can run in parallel (same file, different endpoints)
- T027-T032 (tests) can run in parallel (different test files and test cases)

### Within User Story 2
- T033-T036 (ownership verification) can run in parallel (same file, different endpoints)
- T043-T046 (tests) can run in parallel (different test cases)

### Within User Story 3
- T050-T052 (tests) can run in parallel (different test files)

### Contract Testing Phase
- T053-T060 (contract tests) can run in parallel (different test cases)

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T014) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T015-T032)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Verify all endpoints require authentication
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - authentication required!)
3. Add User Story 2 → Test independently → Deploy/Demo (data isolation enforced)
4. Add User Story 3 → Test independently → Deploy/Demo (expiry enforcement)
5. Add Contract Tests → Validate OpenAPI compliance
6. Add Polish → Production ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T014)
2. Once Foundational is done:
   - Developer A: User Story 1 (T015-T032)
   - Developer B: User Story 3 (T047-T052) - can start early, independent
3. After US1 completes:
   - Developer A: User Story 2 (T033-T046)
   - Developer B: Contract Tests (T053-T061)
4. Team: Polish together (T062-T071)

## Notes

- [P] tasks = different files or independent test cases, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Foundational phase (T006-T014) is CRITICAL and blocks all user stories
- User Story 1 is the MVP - authentication enforcement
- User Story 2 adds data isolation (prevents IDOR)
- User Story 3 adds expiry enforcement (security hardening)
- Contract tests validate OpenAPI specification compliance
- Polish phase ensures production readiness
- Avoid: vague tasks, same file conflicts without [P], cross-story dependencies that break independence
