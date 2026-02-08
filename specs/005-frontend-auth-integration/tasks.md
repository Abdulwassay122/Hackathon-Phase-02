# Tasks: Frontend Authentication Integration

**Input**: Design documents from `/specs/005-frontend-auth-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification. Manual testing procedures are documented in quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with backend/frontend structure:
- Backend: `backend/src/` (no changes in this feature)
- Frontend: `frontend/src/`

---

## Phase 1: Setup (Better Auth Removal & Dependencies)

**Purpose**: Remove Better Auth library and prepare project for custom authentication implementation

- [x] T001 Search codebase for all Better Auth imports and usage in frontend/src/ directory
- [x] T002 Remove Better Auth package from frontend/package.json dependencies
- [x] T003 Delete Better Auth configuration files if they exist in frontend/ directory
- [x] T004 Remove Better Auth provider components from frontend/src/app/layout.tsx or root layout
- [x] T005 Verify no Better Auth imports remain by running build or type check

---

## Phase 2: Foundational (Core Authentication Infrastructure)

**Purpose**: Core authentication components that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

This phase creates the shared authentication infrastructure (token storage utilities, AuthContext, useAuth hook, API client) that all three user stories will use. Without this foundation, none of the user stories can be implemented.

- [x] T006 [P] Create authentication token storage utilities in frontend/src/lib/auth.ts with setToken(), getToken(), clearToken() functions for localStorage management
- [x] T007 [P] Create API client wrapper in frontend/src/lib/api.ts with authenticatedFetch() function that automatically attaches Authorization header from localStorage token
- [x] T008 Create AuthContext in frontend/src/contexts/AuthContext.tsx with AuthState interface (isAuthenticated, user, token, loading, error, login, signup, logout methods)
- [x] T009 Implement AuthProvider component in frontend/src/contexts/AuthContext.tsx that initializes auth state from localStorage on mount
- [x] T010 Create useAuth custom hook in frontend/src/hooks/useAuth.ts that provides access to AuthContext
- [x] T011 Wrap root layout with AuthProvider in frontend/src/app/layout.tsx to make auth state available throughout the app
- [x] T012 [P] Create Next.js middleware in frontend/src/middleware.ts for route protection that checks for auth token and redirects unauthenticated users to login

**Checkpoint**: Authentication infrastructure ready - user story implementation can now begin

---

## Phase 3: User Story 1 - New User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create accounts by providing email, password, and name. System calls backend API, stores JWT token, and redirects to main application.

**Independent Test**: Navigate to signup page, enter valid credentials (email, password, name), submit form. Verify: (1) POST request to /api/auth/signup, (2) JWT token stored in localStorage, (3) redirect to main application, (4) subsequent API calls include Authorization header. See quickstart.md Test 1 for detailed test cases.

**Acceptance Criteria**:
- New user can signup with valid email, password (min 8 chars, letter + number), and name
- System returns JWT token and user data
- Token stored in localStorage
- User redirected to main application
- Duplicate email returns 409 error with message
- Invalid email format returns 422 error
- Weak password returns 400 error with specific message

### Implementation for User Story 1

- [x] T013 [P] [US1] Create SignupForm component in frontend/src/components/auth/SignupForm.tsx with email, password, name input fields
- [x] T014 [P] [US1] Add client-side form validation to SignupForm: email format (regex), password complexity (min 8 chars, letter + number), name non-empty
- [x] T015 [US1] Implement signup method in AuthContext (frontend/src/contexts/AuthContext.tsx) that calls POST /api/auth/signup endpoint
- [x] T016 [US1] Add error handling in signup method for 400 (validation), 409 (duplicate email), 422 (invalid format), 500 (server error) responses
- [x] T017 [US1] Add network error handling in signup method to display "Unable to connect to server" message
- [x] T018 [US1] Implement token storage in signup method: on 201 success, store access_token in localStorage using setToken()
- [x] T019 [US1] Update AuthContext state in signup method: set isAuthenticated=true, user object, token after successful signup
- [x] T020 [US1] Add loading state management in signup method: set loading=true before request, loading=false after response
- [x] T021 [US1] Implement form submission prevention in SignupForm while loading=true (disable submit button, disable form fields)
- [x] T022 [US1] Add error message display in SignupForm component for validation errors and API errors
- [x] T023 [US1] Create signup page in frontend/src/app/(auth)/signup/page.tsx that renders SignupForm component
- [x] T024 [US1] Implement redirect logic in signup method: on success, redirect to main application (e.g., /tasks or /dashboard) using Next.js router
- [x] T025 [US1] Add logging for successful signups and failed attempts in signup method (log email but never log passwords)

**Checkpoint**: At this point, User Story 1 should be fully functional. Users can signup and receive JWT tokens. Test independently using quickstart.md Test 1 before proceeding.

---

## Phase 4: User Story 2 - Existing User Login (Priority: P2)

**Goal**: Enable existing users to authenticate by providing email and password. System calls backend API, stores JWT token, and redirects to main application.

**Independent Test**: First create user via signup. Then navigate to login page, enter correct email and password, submit form. Verify: (1) POST request to /api/auth/login, (2) JWT token stored in localStorage, (3) redirect to main application, (4) user can access existing data. See quickstart.md Test 2 for detailed test cases.

**Acceptance Criteria**:
- Existing user can login with correct email and password
- System returns JWT token and user data
- Token stored in localStorage
- User redirected to main application
- Invalid password returns 401 with generic message "Invalid email or password"
- Non-existent email returns 401 with same generic message (no user enumeration)
- Token persists across page navigation

### Implementation for User Story 2

- [x] T026 [P] [US2] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx with email and password input fields
- [x] T027 [P] [US2] Add client-side form validation to LoginForm: email format validation, password non-empty validation
- [x] T028 [US2] Implement login method in AuthContext (frontend/src/contexts/AuthContext.tsx) that calls POST /api/auth/login endpoint
- [x] T029 [US2] Add error handling in login method for 401 (invalid credentials), 422 (missing fields), 500 (server error) responses
- [x] T030 [US2] Ensure login method displays generic error message "Invalid email or password" for both wrong password and non-existent email (security requirement)
- [x] T031 [US2] Add network error handling in login method to display "Unable to connect to server" message
- [x] T032 [US2] Implement token storage in login method: on 200 success, store access_token in localStorage using setToken()
- [x] T033 [US2] Update AuthContext state in login method: set isAuthenticated=true, user object, token after successful login
- [x] T034 [US2] Add loading state management in login method: set loading=true before request, loading=false after response
- [x] T035 [US2] Implement form submission prevention in LoginForm while loading=true (disable submit button, disable form fields)
- [x] T036 [US2] Add error message display in LoginForm component for validation errors and API errors
- [x] T037 [US2] Create login page in frontend/src/app/(auth)/login/page.tsx that renders LoginForm component
- [x] T038 [US2] Implement redirect logic in login method: on success, redirect to main application (e.g., /tasks or /dashboard) using Next.js router
- [x] T039 [US2] Add logging for successful logins and failed login attempts in login method (log email but never log passwords)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can signup and login to receive JWT tokens. Test independently using quickstart.md Tests 1 and 2.

---

## Phase 5: User Story 3 - Session Persistence and Token Management (Priority: P3)

**Goal**: Ensure JWT tokens persist across browser sessions, handle token expiration gracefully, and implement logout functionality. Users remain authenticated until token expires or they explicitly logout.

**Independent Test**: Login successfully, close browser, reopen application. Verify: (1) user remains authenticated if token valid, (2) user redirected to login if token expired, (3) logout clears token and redirects to login. See quickstart.md Test 3 for detailed test cases.

**Acceptance Criteria**:
- JWT token persists in localStorage across browser close/reopen
- User remains authenticated on app load if token valid
- Expired tokens detected and cleared automatically
- 401 Unauthorized responses trigger token clearing and redirect to login
- Logout function clears token and redirects to login page
- Protected routes redirect to login if no valid token

### Implementation for User Story 3

- [x] T040 [US3] Implement token persistence check in AuthProvider useEffect: on mount, retrieve token from localStorage using getToken()
- [x] T041 [US3] Add token validation logic in AuthProvider: if token exists, decode JWT payload to extract user info (id, email, name)
- [x] T042 [US3] Update AuthContext state on mount: if valid token found, set isAuthenticated=true, user object, token
- [x] T043 [US3] Implement logout method in AuthContext: clear token from localStorage using clearToken(), reset state to initial values
- [x] T044 [US3] Add redirect logic to logout method: after clearing state, redirect to login page using Next.js router
- [x] T045 [US3] Implement global 401 handler in authenticatedFetch() (frontend/src/lib/api.ts): on 401 response, call clearToken() and redirect to login
- [x] T046 [US3] Add token expiration detection in authenticatedFetch(): check if token expired before making request (optional optimization)
- [x] T047 [US3] Update Next.js middleware (frontend/src/middleware.ts) to check for valid token on protected routes and redirect to login if missing
- [x] T048 [US3] Add logout button or trigger in main application UI that calls logout method from useAuth hook
- [x] T049 [US3] Implement token clearing on any 401 response from any API endpoint (not just auth endpoints) in authenticatedFetch()
- [x] T050 [US3] Add error handling for localStorage unavailable (private browsing mode): detect and display error message "Browser storage unavailable"

**Checkpoint**: All user stories should now be independently functional with secure, production-ready token management. Test all scenarios using quickstart.md Tests 1-3.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and improvements that affect multiple user stories

- [x] T051 [P] Add loading indicators (spinners, skeleton screens) to signup and login forms during authentication requests
- [x] T052 [P] Ensure all error messages are user-friendly and actionable (no technical jargon, clear next steps)
- [x] T053 [P] Verify existing UI design and layout preserved for signup and login pages (minimal UI changes requirement)
- [x] T054 [P] Add proper TypeScript types for all authentication-related functions and components
- [x] T055 [P] Verify all API requests include Authorization header with Bearer token format
- [x] T056 [P] Test form validation edge cases: special characters in inputs, very long inputs, empty whitespace
- [ ] T057 Run quickstart.md Test 1 (User Signup Flow) - all 7 test cases
- [ ] T058 Run quickstart.md Test 2 (User Login Flow) - all 4 test cases
- [ ] T059 Run quickstart.md Test 3 (Session Persistence) - all 5 test cases
- [ ] T060 Run quickstart.md Test 4 (API Request Authorization) - all 3 test cases
- [ ] T061 Run quickstart.md Test 5 (Edge Cases) - all 4 test cases
- [ ] T062 Run quickstart.md Test 6 (Cross-Browser Compatibility) - Chrome, Firefox, Safari

**Note**: Tasks T057-T062 are manual testing tasks that require the backend API to be running and browser-based testing. Follow the procedures in `specs/005-frontend-auth-integration/quickstart.md` to complete these tests.

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

**Note**: While the user stories CAN be implemented in parallel (they touch different components), they are designed to build on each other in priority order for incremental value delivery.

### Within Each Phase

**Setup Phase**:
- T001-T005 should run sequentially (each builds on previous)

**Foundational Phase**:
- T006 (auth utilities) and T007 (API client) can run in parallel [P]
- T008-T011 must run sequentially (AuthContext → AuthProvider → useAuth → wrap layout)
- T012 (middleware) can run in parallel with T008-T011 [P]

**User Story 1**:
- T013 (SignupForm) and T014 (validation) can run in parallel [P]
- T015-T025 must run sequentially (each builds on previous)

**User Story 2**:
- T026 (LoginForm) and T027 (validation) can run in parallel [P]
- T028-T039 must run sequentially (each builds on previous)

**User Story 3**:
- T040-T050 must run sequentially (each builds on previous)

**Polish Phase**:
- T051-T056 can run in parallel [P] (different concerns)
- T057-T062 should run sequentially (manual testing)

### Parallel Opportunities

- **Setup Phase**: No parallel tasks (sequential removal)
- **Foundational Phase**: T006, T007, T012 can run in parallel [P] (3 tasks)
- **User Story 1**: T013, T014 can run in parallel [P] (2 tasks)
- **User Story 2**: T026, T027 can run in parallel [P] (2 tasks)
- **User Story 3**: No parallel tasks (sequential state management)
- **Polish Phase**: T051-T056 can run in parallel [P] (6 tasks)
- **Across User Stories**: Once Foundational completes, US1, US2, and US3 can all start in parallel if team capacity allows

**Total parallelizable tasks**: 13 out of 62 (21%)

---

## Parallel Example: Foundational Phase

```bash
# After Setup completes, launch these together:
Task T006: "Create authentication token storage utilities in frontend/src/lib/auth.ts"
Task T007: "Create API client wrapper in frontend/src/lib/api.ts"
Task T012: "Create Next.js middleware in frontend/src/middleware.ts"
```

---

## Parallel Example: User Story 1

```bash
# Launch form and validation together:
Task T013: "Create SignupForm component in frontend/src/components/auth/SignupForm.tsx"
Task T014: "Add client-side form validation to SignupForm"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (remove Better Auth)
2. Complete Phase 2: Foundational (authentication infrastructure)
3. Complete Phase 3: User Story 1 (signup endpoint)
4. **STOP and VALIDATE**: Test signup endpoint with quickstart.md Test 1
5. Deploy/demo if ready - users can now create accounts!

**MVP Delivers**: User registration works. This unblocks frontend development for signup flows and allows new users to join the application.

### Incremental Delivery

1. Complete Setup + Foundational → Authentication infrastructure ready
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 → Test independently → Deploy/Demo (login functionality)
4. Add User Story 3 → Test independently → Deploy/Demo (production-ready session management)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (12 tasks, ~4-6 hours)
2. Once Foundational is done:
   - Developer A: User Story 1 (13 tasks, signup endpoint)
   - Developer B: User Story 2 (14 tasks, login endpoint)
   - Developer C: User Story 3 (11 tasks, session management)
3. Stories complete and integrate independently
4. Team validates together (Phase 6)

---

## Task Summary

**Total Tasks**: 62 tasks across 6 phases

**Task Count by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (User Story 1 - P1): 13 tasks
- Phase 4 (User Story 2 - P2): 14 tasks
- Phase 5 (User Story 3 - P3): 11 tasks
- Phase 6 (Polish): 12 tasks

**Task Count by User Story**:
- Foundational (blocking): 7 tasks
- User Story 1 (New User Registration): 13 tasks
- User Story 2 (Existing User Login): 14 tasks
- User Story 3 (Session Persistence): 11 tasks
- Polish & Documentation: 12 tasks

**Parallel Opportunities Identified**:
- Foundational: 3 tasks can run in parallel (T006, T007, T012)
- User Story 1: 2 tasks can run in parallel (T013, T014)
- User Story 2: 2 tasks can run in parallel (T026, T027)
- Polish: 6 tasks can run in parallel (T051-T056)
- **Total parallelizable tasks**: 13 out of 62 (21%)

**Independent Test Criteria**:
- **User Story 1**: Navigate to signup page, submit valid data → 201 Created with token stored in localStorage
- **User Story 2**: Navigate to login page, submit correct credentials → 200 OK with token stored in localStorage
- **User Story 3**: Login, close browser, reopen → User remains authenticated if token valid

**Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1) = 25 tasks
- Delivers core value: Users can create accounts and receive JWT tokens
- Unblocks frontend development for signup flows
- Can be completed in 8-12 hours

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included as they were not requested in the specification
- Manual testing procedures documented in quickstart.md (24 test cases)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks include exact file paths for clarity
