# Tasks: Fix Token Retrieval for API Requests

**Input**: Design documents from `/specs/008-fix-token-retrieval/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification. Manual testing procedures are documented in quickstart.md (15 test cases across 4 test suites).

**Organization**: Tasks are grouped by implementation phase. The core fix (Phase 2) is foundational and blocks all user stories. Each user story then has validation tasks to verify the fix works for that specific scenario.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with frontend-only changes:
- Frontend: `frontend/src/` (changes in this feature)
- Backend: No changes (backend authentication remains unchanged)

---

## Phase 1: Setup & Verification

**Purpose**: Verify existing code structure and understand current implementation

- [x] T001 Verify existing getToken() implementation in frontend/src/lib/auth/session.ts to understand current token retrieval logic
- [x] T002 Verify existing setSession() implementation in frontend/src/lib/auth/session.ts to confirm "auth-token" key is being written
- [x] T003 Verify APIClient usage of getToken callback in frontend/src/app/(dashboard)/tasks/page.tsx to understand integration point

---

## Phase 2: Core Token Retrieval Fix (Foundational)

**Purpose**: Implement the core fix that enables all user scenarios

**⚠️ CRITICAL**: This phase MUST be complete before user story validation can begin. The fix affects all three user stories.

- [x] T004 Modify getToken() function in frontend/src/lib/auth/session.ts to read directly from localStorage "auth-token" key
- [x] T005 Add try-catch error handling to getToken() in frontend/src/lib/auth/session.ts for localStorage access failures
- [x] T006 Add console.error logging for token retrieval failures in frontend/src/lib/auth/session.ts
- [x] T007 Remove dependency on getSession() from getToken() function in frontend/src/lib/auth/session.ts
- [x] T008 Verify getToken() returns string | null as per contract in frontend/src/lib/auth/session.ts

**Checkpoint**: Core fix implemented - all user stories should now work without 403 Forbidden errors

---

## Phase 3: User Story 1 - Authenticated User Can View Tasks (Priority: P1) 🎯 MVP

**Goal**: Verify that authenticated users can access /tasks and perform all CRUD operations without 403 Forbidden errors

**Independent Test**: Login with valid credentials, navigate to /tasks, verify GET /api/tasks returns 200 OK with Authorization header present. See quickstart.md Test Suite 1 for detailed test cases.

**Acceptance Criteria**:
- API requests include non-null Authorization header with Bearer token
- GET /api/tasks returns 200 OK (not 403 Forbidden)
- All CRUD operations (create, read, update, delete) succeed with appropriate status codes
- No console errors related to token retrieval

### Validation for User Story 1

- [ ] T009 [P] [US1] Manually test login and view tasks per quickstart.md Test 1.1 (verify 200 OK response)
- [ ] T010 [P] [US1] Manually test create task operation per quickstart.md Test 1.2 (verify 201 Created response)
- [ ] T011 [P] [US1] Manually test update task operation per quickstart.md Test 1.3 (verify 200 OK response)
- [ ] T012 [P] [US1] Manually test delete task operation per quickstart.md Test 1.4 (verify 204 No Content response)
- [ ] T013 [US1] Verify Authorization header present in all API requests using browser DevTools Network tab
- [ ] T014 [US1] Verify localStorage contains "auth-token" key with non-null JWT value after login
- [ ] T015 [US1] Verify no console errors related to "getToken" or "Failed to retrieve auth token"
- [ ] T016 [US1] Verify no 403 Forbidden errors in Network tab for any /api/tasks requests

**Checkpoint**: At this point, User Story 1 should be fully functional. Users can login and perform all task operations without 403 errors.

---

## Phase 4: User Story 2 - Token Persists Across Page Refreshes (Priority: P1)

**Goal**: Verify that authenticated users maintain their session across page refreshes and browser tab close/reopen

**Independent Test**: Login, navigate to /tasks, refresh page (F5), verify tasks still load without redirect to signin. See quickstart.md Test Suite 2 for detailed test cases.

**Acceptance Criteria**:
- Page refresh maintains authentication state
- Tasks load successfully after refresh without redirect
- Authorization header present in requests after refresh
- No re-authentication required

### Validation for User Story 2

- [ ] T017 [P] [US2] Manually test page refresh while authenticated per quickstart.md Test 2.1 (verify tasks still load)
- [ ] T018 [P] [US2] Manually test browser tab close/reopen per quickstart.md Test 2.2 (verify session persists)
- [ ] T019 [US2] Verify localStorage "auth-token" key persists across page refresh
- [ ] T020 [US2] Verify GET /api/tasks returns 200 OK after page refresh (check Network tab)
- [ ] T021 [US2] Verify Authorization header present in requests after page refresh
- [ ] T022 [US2] Verify no redirect to /signin occurs after page refresh

**Checkpoint**: At this point, User Stories 1 AND 2 should both work. Users can login, perform operations, and maintain session across refreshes.

---

## Phase 5: User Story 3 - Expired Token Handling (Priority: P2)

**Goal**: Verify that expired or invalid tokens are handled gracefully with proper error handling and redirect to signin

**Independent Test**: Login, manually delete "auth-token" from localStorage, attempt to perform task operation, verify redirect to /signin occurs. See quickstart.md Test Suite 3 for detailed test cases.

**Acceptance Criteria**:
- Missing tokens trigger redirect to /signin
- Expired tokens trigger redirect to /signin with expired=true parameter
- Malformed tokens trigger redirect to /signin
- Session cleared from localStorage on auth errors
- onAuthError callback fires correctly

### Validation for User Story 3

- [ ] T023 [P] [US3] Manually test missing token scenario per quickstart.md Test 3.1 (delete auth-token, verify redirect)
- [ ] T024 [P] [US3] Manually test expired token scenario per quickstart.md Test 3.2 (verify 401 response and redirect)
- [ ] T025 [P] [US3] Manually test malformed token scenario per quickstart.md Test 3.3 (set invalid token, verify redirect)
- [ ] T026 [US3] Verify redirect to /signin occurs when token is missing
- [ ] T027 [US3] Verify redirect to /signin?expired=true occurs when token is expired (401 response)
- [ ] T028 [US3] Verify localStorage "auth-token" key is cleared after auth error
- [ ] T029 [US3] Verify onAuthError callback fires and clears session correctly

**Checkpoint**: At this point, all three user stories should work. Authentication fix is complete and error handling is verified.

---

## Phase 6: Edge Cases & Polish

**Purpose**: Verify edge cases and ensure production readiness

- [ ] T030 [P] Manually test localStorage unavailable scenario per quickstart.md Test 4.1 (private browsing mode)
- [ ] T031 [P] Manually test concurrent tabs scenario per quickstart.md Test 4.2 (logout in one tab, verify other tab)
- [ ] T032 Verify all success criteria from spec.md are met (SC-001 through SC-006)
- [ ] T033 Run full test suite from quickstart.md (all 15 test cases) and document results
- [ ] T034 Verify no regression in existing authentication functionality (login/signup/logout)
- [x] T035 Remove debug console.log statements from frontend/src/app/(dashboard)/tasks/page.tsx (line 50)
- [x] T036 Remove debug console.log statements from frontend/src/lib/auth/session.ts (lines 11, 38) if present
- [ ] T037 Verify code follows project conventions and style guidelines

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Core Fix (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Core Fix completion - Delivers MVP
- **User Story 2 (Phase 4)**: Depends on Core Fix completion - Can run in parallel with US1 validation if different testers
- **User Story 3 (Phase 5)**: Depends on Core Fix completion - Can run in parallel with US1/US2 validation
- **Edge Cases & Polish (Phase 6)**: Depends on all user stories being validated

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Core Fix (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on Core Fix (Phase 2) - No dependencies on other stories (can validate in parallel with US1)
- **User Story 3 (P2)**: Depends on Core Fix (Phase 2) - No dependencies on other stories (can validate in parallel with US1/US2)

**Note**: All three user stories CAN be validated in parallel (they test different scenarios), but they share the same core implementation (Phase 2).

### Within Each Phase

**Setup Phase**:
- T001-T003 should run sequentially (each builds understanding)

**Core Fix Phase**:
- T004-T008 must run sequentially (each builds on previous changes)

**User Story 1 Validation**:
- T009-T012 can run in parallel [P] if multiple testers available (independent test cases)
- T013-T016 should run sequentially after manual tests

**User Story 2 Validation**:
- T017-T018 can run in parallel [P] if multiple testers available (independent test cases)
- T019-T022 should run sequentially after manual tests

**User Story 3 Validation**:
- T023-T025 can run in parallel [P] if multiple testers available (independent test cases)
- T026-T029 should run sequentially after manual tests

**Edge Cases & Polish Phase**:
- T030-T031 can run in parallel [P] (independent test cases)
- T032-T037 should run sequentially (comprehensive validation and cleanup)

### Parallel Opportunities

- **Setup Phase**: No parallel tasks (sequential understanding)
- **Core Fix Phase**: No parallel tasks (sequential implementation)
- **User Story 1**: T009-T012 can run in parallel [P] (4 tasks)
- **User Story 2**: T017-T018 can run in parallel [P] (2 tasks)
- **User Story 3**: T023-T025 can run in parallel [P] (3 tasks)
- **Edge Cases & Polish**: T030-T031 can run in parallel [P] (2 tasks)
- **Across User Stories**: Once Core Fix completes, US1, US2, and US3 validation can run in parallel if team capacity allows

**Total parallelizable tasks**: 11 out of 37 (30%)

---

## Parallel Example: User Story 1 Validation

```bash
# After Core Fix completes, launch these together:
Task T009: "Manually test login and view tasks per quickstart.md Test 1.1"
Task T010: "Manually test create task operation per quickstart.md Test 1.2"
Task T011: "Manually test update task operation per quickstart.md Test 1.3"
Task T012: "Manually test delete task operation per quickstart.md Test 1.4"
```

---

## Parallel Example: All User Stories Validation

```bash
# After Core Fix completes, launch all validation in parallel (if multiple testers):
# Tester A: User Story 1 validation (T009-T016)
# Tester B: User Story 2 validation (T017-T022)
# Tester C: User Story 3 validation (T023-T029)
```

---

## Implementation Strategy

### MVP First (Core Fix + User Story 1)

1. Complete Phase 1: Setup (understand existing code)
2. Complete Phase 2: Core Fix (implement token retrieval fix)
3. Complete Phase 3: User Story 1 (validate CRUD operations work)
4. **STOP and VALIDATE**: Test all task operations with proper authorization
5. Deploy/demo if ready - users can now access tasks without 403 errors!

**MVP Delivers**: Authenticated users can view and manage tasks without 403 Forbidden errors. This unblocks the most critical user journey.

### Incremental Delivery

1. Complete Setup + Core Fix → Token retrieval fixed
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 → Test independently → Deploy/Demo (session persistence verified)
4. Add User Story 3 → Test independently → Deploy/Demo (error handling verified)
5. Add Edge Cases & Polish → Test independently → Deploy/Demo (production-ready)
6. Each phase adds value without breaking previous functionality

### Parallel Team Strategy

With multiple team members:

1. Team completes Setup + Core Fix together (8 tasks, ~1-2 hours)
2. Once Core Fix is done:
   - Tester A: User Story 1 validation (8 tasks, CRUD operation tests)
   - Tester B: User Story 2 validation (6 tasks, persistence tests)
   - Tester C: User Story 3 validation (7 tasks, error handling tests)
3. Stories validate and integrate independently
4. Team validates edge cases together (Phase 6)

---

## Task Summary

**Total Tasks**: 37 tasks across 6 phases

**Task Count by Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Core Fix): 5 tasks
- Phase 3 (User Story 1): 8 tasks
- Phase 4 (User Story 2): 6 tasks
- Phase 5 (User Story 3): 7 tasks
- Phase 6 (Edge Cases & Polish): 8 tasks

**Task Count by User Story**:
- Core Fix (blocking): 5 tasks
- User Story 1 (CRUD operations): 8 tasks
- User Story 2 (Session persistence): 6 tasks
- User Story 3 (Error handling): 7 tasks
- Edge Cases & Polish: 8 tasks

**Parallel Opportunities Identified**:
- User Story 1: 4 tasks can run in parallel (T009-T012)
- User Story 2: 2 tasks can run in parallel (T017-T018)
- User Story 3: 3 tasks can run in parallel (T023-T025)
- Edge Cases & Polish: 2 tasks can run in parallel (T030-T031)
- **Total parallelizable tasks**: 11 out of 37 (30%)

**Independent Test Criteria**:
- **User Story 1**: Login → perform CRUD operations → verify 200/201/204 responses (not 403)
- **User Story 2**: Login → refresh page → verify tasks still load without redirect
- **User Story 3**: Delete token → attempt operation → verify redirect to /signin

**Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Core Fix) + Phase 3 (User Story 1) = 16 tasks
- Delivers core value: Users can access and manage tasks without 403 errors
- Unblocks the most critical user journey
- Can be completed in 2-3 hours

---

## Notes

- [P] tasks = independent test cases or different files, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable after Core Fix is complete
- Tests are NOT included as they were not requested in the specification
- Manual testing procedures documented in quickstart.md (15 test cases)
- Commit after each task or logical group
- Stop at any checkpoint to validate functionality independently
- All tasks include exact file paths for clarity
