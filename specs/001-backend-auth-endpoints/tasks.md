# Tasks: Backend Authentication Endpoints

**Input**: Design documents from `/specs/001-backend-auth-endpoints/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/signup.yaml, contracts/login.yaml, quickstart.md

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with backend/frontend structure:
- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/src/` (no changes in this feature)

---

## Phase 1: Setup (Dependencies)

**Purpose**: Install required dependencies for authentication implementation

- [x] T001 Add passlib[bcrypt] to backend/requirements.txt for password hashing
- [x] T002 Install dependencies by running pip install -r backend/requirements.txt

---

## Phase 2: Foundational (Core Authentication Infrastructure)

**Purpose**: Core authentication components that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

This phase creates the shared authentication infrastructure (User model, password utilities, JWT generation) that all three user stories will use. Without this foundation, none of the user stories can be implemented.

- [x] T003 Create User model in backend/src/models/user_model.py with fields: id (int, primary key), email (str, unique, indexed), password_hash (str), name (str), created_at (datetime), updated_at (datetime)
- [x] T004 [P] Create password hashing utilities in backend/src/auth/password.py with hash_password() and verify_password() functions using passlib bcrypt with cost factor 12
- [x] T005 [P] Add create_access_token() function to backend/src/auth/jwt_handler.py to generate JWT tokens with sub (user ID), email, and exp (24 hours) claims using existing BETTER_AUTH_SECRET and HS256 algorithm
- [x] T006 Update backend/src/database/init_db.py to import User model and include it in SQLModel.metadata.create_all() for automatic table creation
- [x] T007 [P] Create Pydantic request/response schemas in backend/src/api/auth_routes.py: SignupRequest (email, password, name with validators), LoginRequest (email, password), AuthResponse (access_token, token_type, user), UserResponse (id, email, name)

**Checkpoint**: Authentication infrastructure ready - user story implementation can now begin

---

## Phase 3: User Story 1 - New User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create accounts by providing email, password, and name. System creates user account, hashes password, and returns JWT token for immediate use.

**Independent Test**: Send POST request to /api/auth/signup with valid user data (email, password, name). Verify 201 Created response with JWT token and user data. Verify user record exists in database with hashed password. Verify token can be used with existing protected endpoints.

**Acceptance Criteria**:
- New user can signup with valid email, password (min 8 chars, letter + number), and name
- System returns 201 Created with JWT token and user data (id, email, name)
- Password is hashed with bcrypt before storage (never plaintext)
- Duplicate email returns 409 Conflict
- Invalid email format returns 422 Unprocessable Entity
- Weak password returns 400 Bad Request with specific error message
- Empty name returns 400 Bad Request

### Implementation for User Story 1

- [x] T008 [US1] Create POST /api/auth/signup endpoint in backend/src/api/auth_routes.py that accepts SignupRequest (email, password, name)
- [x] T009 [US1] Add email format validation using Pydantic EmailStr in SignupRequest schema
- [x] T010 [US1] Add password complexity validator to SignupRequest: minimum 8 characters, at least one letter, at least one number (use @validator decorator)
- [x] T011 [US1] Add name validation to SignupRequest: non-empty after stripping whitespace (use @validator decorator)
- [x] T012 [US1] Implement signup endpoint logic: check if email exists in database, return 409 Conflict if duplicate
- [x] T013 [US1] Hash password using hash_password() from backend/src/auth/password.py before creating User record
- [x] T014 [US1] Create User record in database with email, password_hash, name, and auto-generated timestamps
- [x] T015 [US1] Generate JWT token using create_access_token() with user ID and email
- [x] T016 [US1] Return 201 Created with AuthResponse containing access_token, token_type="bearer", and UserResponse (id, email, name)
- [x] T017 [US1] Add error handling for database constraint violations (unique email) and return 409 Conflict with message "Email already registered"
- [x] T018 [US1] Add error handling for validation errors and return 400 Bad Request with specific error messages
- [x] T019 [US1] Add logging for successful signups and failed attempts (log email but never log passwords)
- [x] T020 [US1] Register auth router in backend/src/main.py with prefix "/api/auth" and include_router()

**Checkpoint**: At this point, User Story 1 should be fully functional. Users can signup and receive JWT tokens. Test independently before proceeding.

---

## Phase 4: User Story 2 - Existing User Login (Priority: P2)

**Goal**: Enable existing users to authenticate by providing email and password. System verifies credentials and returns JWT token for accessing protected endpoints.

**Independent Test**: First create a user via signup endpoint. Then send POST request to /api/auth/login with correct email and password. Verify 200 OK response with JWT token. Verify invalid credentials return 401 Unauthorized with generic error message. Verify token can be used with existing protected endpoints.

**Acceptance Criteria**:
- Existing user can login with correct email and password
- System returns 200 OK with JWT token and user data (id, email, name)
- Invalid password returns 401 Unauthorized with generic message "Invalid email or password"
- Non-existent email returns 401 Unauthorized with same generic message (no user enumeration)
- Missing email or password returns 422 Unprocessable Entity
- Token contains user ID in "sub" claim and email in payload

### Implementation for User Story 2

- [x] T021 [US2] Create POST /api/auth/login endpoint in backend/src/api/auth_routes.py that accepts LoginRequest (email, password)
- [x] T022 [US2] Implement login endpoint logic: query database for User by email
- [x] T023 [US2] If user not found, return 401 Unauthorized with generic message "Invalid email or password" (do not reveal email doesn't exist)
- [x] T024 [US2] If user found, verify password using verify_password() from backend/src/auth/password.py comparing submitted password against stored password_hash
- [x] T025 [US2] If password verification fails, return 401 Unauthorized with generic message "Invalid email or password"
- [x] T026 [US2] If password verification succeeds, generate JWT token using create_access_token() with user ID and email
- [x] T027 [US2] Return 200 OK with AuthResponse containing access_token, token_type="bearer", and UserResponse (id, email, name)
- [x] T028 [US2] Add logging for successful logins and failed login attempts (log email but never log passwords)
- [x] T029 [US2] Add error handling for database errors and return 500 Internal Server Error with generic message

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can signup and login to receive JWT tokens.

---

## Phase 5: User Story 3 - Secure Token Management (Priority: P3)

**Goal**: Ensure JWT tokens are secure, properly structured, and compatible with existing JWT verification middleware. Tokens include correct claims, have appropriate expiration, and work seamlessly with protected endpoints.

**Independent Test**: Generate token via signup or login. Decode token and verify it contains sub (user ID as string), email, and exp (24 hours) claims. Use token to access existing protected endpoint (e.g., GET /api/users/{user_id}/tasks) and verify it's accepted by existing JWT verification middleware. Test with expired token and verify 401 Unauthorized. Test cross-user access and verify 403 Forbidden.

**Acceptance Criteria**:
- JWT tokens include user ID in "sub" claim as string
- JWT tokens include email in payload
- JWT tokens have expiration set to 24 hours from issuance
- Tokens are compatible with existing JWT verification in backend/src/auth/jwt_handler.py
- Tokens work with existing protected endpoints without middleware changes
- Expired tokens are rejected with 401 Unauthorized
- Cross-user access attempts are rejected with 403 Forbidden

### Implementation for User Story 3

- [x] T030 [US3] Verify create_access_token() in backend/src/auth/jwt_handler.py includes "sub" claim with user ID as string (str(user_id))
- [x] T031 [US3] Verify create_access_token() in backend/src/auth/jwt_handler.py includes "email" claim with user email
- [x] T032 [US3] Verify create_access_token() in backend/src/auth/jwt_handler.py sets "exp" claim to datetime.utcnow() + timedelta(hours=24)
- [x] T033 [US3] Verify create_access_token() uses BETTER_AUTH_SECRET from environment (same secret as existing verification)
- [x] T034 [US3] Verify create_access_token() uses HS256 algorithm (same as existing verification)
- [x] T035 [US3] Test token generation by creating a user via signup, decoding the returned token (without verification), and confirming claims structure
- [x] T036 [US3] Test token compatibility by using a token from signup/login to access existing protected endpoint (e.g., GET /api/users/{user_id}/tasks) and verify 200 OK response
- [x] T037 [US3] Verify existing JWT verification middleware in backend/src/auth/dependencies.py correctly extracts user ID from "sub" claim
- [x] T038 [US3] Verify user isolation: create two users, use User 2's token to access User 1's resources, confirm 403 Forbidden response

**Checkpoint**: All user stories should now be independently functional with secure, production-ready token management.

---

## Phase 6: Polish & Documentation

**Purpose**: Final validation and documentation to ensure feature is production-ready

- [x] T039 [P] Add authentication endpoints documentation to backend/README.md explaining signup and login usage with curl examples
- [x] T040 [P] Add troubleshooting section to backend/README.md for common authentication issues (duplicate email, invalid credentials, token expiration)
- [ ] T041 Manually test User Story 1: Run quickstart.md Test 1 (User Signup) - all 7 test cases
- [ ] T042 Manually test User Story 2: Run quickstart.md Test 2 (User Login) - all 4 test cases
- [ ] T043 Manually test User Story 3: Run quickstart.md Test 3 (JWT Token Verification) - all 3 test cases
- [ ] T044 Run quickstart.md Test 4 (User Isolation) and verify cross-user access is blocked
- [ ] T045 Run quickstart.md Test 5 (Password Security) and verify passwords are hashed in database
- [ ] T046 Run quickstart.md Test 6 (Integration) and verify complete user flow works end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - Delivers MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion - Can start in parallel with US1 if different developers
- **User Story 3 (Phase 5)**: Depends on Foundational completion - Can start in parallel with US1/US2 if different developers
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational phase - No dependencies on other stories
- **User Story 2 (P2)**: Depends on Foundational phase - No dependencies on other stories (can run parallel with US1)
- **User Story 3 (P3)**: Depends on Foundational phase - No dependencies on other stories (can run parallel with US1/US2)

**Note**: While the user stories CAN be implemented in parallel (they touch different endpoints), they are designed to build on each other in priority order for incremental value delivery.

### Within Each Phase

**Foundational Phase**:
- T003 (User model) must complete first
- T004 (password utilities) and T005 (JWT generation) can run in parallel [P]
- T006 (init_db update) depends on T003 (User model)
- T007 (Pydantic schemas) can run in parallel [P]

**User Story 1**:
- T008-T020 must run sequentially (each builds on previous)
- T020 (register router) must be last

**User Story 2**:
- T021-T029 must run sequentially (each builds on previous)

**User Story 3**:
- T030-T038 are verification tasks (check existing code)
- All can run in parallel [P] except T036-T038 which require running server

**Polish Phase**:
- T039-T040 can run in parallel [P] (documentation)
- T041-T046 should run sequentially (manual testing)

### Parallel Opportunities

- **Setup Phase**: T001 and T002 must run sequentially (install after adding to requirements)
- **Foundational Phase**: T004, T005, T007 can run in parallel [P]
- **User Story 1**: All tasks sequential (same file)
- **User Story 2**: All tasks sequential (same file)
- **User Story 3**: T030-T035 can run in parallel [P] (verification tasks)
- **Polish Phase**: T039-T040 can run in parallel [P]
- **Across User Stories**: Once Foundational completes, US1, US2, and US3 can all start in parallel if team capacity allows

---

## Parallel Example: Foundational Phase

```bash
# After T003 completes, launch these together:
Task T004: "Create password hashing utilities in backend/src/auth/password.py"
Task T005: "Add create_access_token() function to backend/src/auth/jwt_handler.py"
Task T007: "Create Pydantic request/response schemas in backend/src/api/auth_routes.py"
```

---

## Parallel Example: User Story 3

```bash
# All verification tasks can run together:
Task T030: "Verify create_access_token() includes sub claim"
Task T031: "Verify create_access_token() includes email claim"
Task T032: "Verify create_access_token() sets exp claim to 24 hours"
Task T033: "Verify create_access_token() uses BETTER_AUTH_SECRET"
Task T034: "Verify create_access_token() uses HS256 algorithm"
Task T035: "Test token generation by creating user and decoding token"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install passlib)
2. Complete Phase 2: Foundational (User model, password utilities, JWT generation)
3. Complete Phase 3: User Story 1 (signup endpoint)
4. **STOP and VALIDATE**: Test signup endpoint with quickstart.md Test 1
5. Deploy/demo if ready - users can now create accounts!

**MVP Delivers**: User registration works. This unblocks frontend development for signup flows.

### Incremental Delivery

1. Complete Setup + Foundational → Authentication infrastructure ready
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 → Test independently → Deploy/Demo (login functionality)
4. Add User Story 3 → Test independently → Deploy/Demo (production-ready security)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (7 tasks, ~2-3 hours)
2. Once Foundational is done:
   - Developer A: User Story 1 (13 tasks, signup endpoint)
   - Developer B: User Story 2 (9 tasks, login endpoint)
   - Developer C: User Story 3 (9 tasks, token verification)
3. Stories complete and integrate independently
4. Team validates together (Phase 6)

---

## Task Summary

**Total Tasks**: 46 tasks across 6 phases

**Task Count by Phase**:
- Phase 1 (Setup): 2 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (User Story 1 - P1): 13 tasks
- Phase 4 (User Story 2 - P2): 9 tasks
- Phase 5 (User Story 3 - P3): 9 tasks
- Phase 6 (Polish): 8 tasks

**Task Count by User Story**:
- Foundational (blocking): 5 tasks
- User Story 1 (New User Registration): 13 tasks
- User Story 2 (Existing User Login): 9 tasks
- User Story 3 (Secure Token Management): 9 tasks
- Polish & Documentation: 8 tasks

**Parallel Opportunities Identified**:
- Foundational: 3 tasks can run in parallel (T004, T005, T007)
- User Story 3: 6 tasks can run in parallel (T030-T035)
- Polish: 2 tasks can run in parallel (T039-T040)
- **Total parallelizable tasks**: 11 out of 46 (24%)

**Independent Test Criteria**:
- **User Story 1**: POST /api/auth/signup with valid data → 201 Created with token
- **User Story 2**: POST /api/auth/login with correct credentials → 200 OK with token
- **User Story 3**: Use token with protected endpoint → 200 OK (token accepted)

**Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1) = 20 tasks
- Delivers core value: Users can create accounts and receive JWT tokens
- Unblocks frontend development for signup flows
- Can be completed in 4-6 hours

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Foundational phase is CRITICAL - blocks all user stories
- Tests are NOT included as they were not requested in the specification
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks include exact file paths for clarity
- Verification tasks (T030-T038) check that code meets requirements without modifying code
