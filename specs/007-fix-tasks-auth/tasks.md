# Tasks: Fix /tasks Page Auth Handling

**Input**: Design documents from `/specs/007-fix-tasks-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification. Manual testing procedures are documented in quickstart.md (15 test cases).

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

- [x] T001 Verify existing middleware implementation in frontend/src/middleware.ts to understand current protection logic
- [x] T002 Verify existing /tasks page implementation in frontend/src/app/(dashboard)/tasks/page.tsx to confirm no auth check exists
- [x] T003 Verify AuthContext implementation in frontend/src/contexts/AuthContext.tsx to understand available authentication state

---

## Phase 2: Core Authentication Fix (Foundational)

**Purpose**: Implement the core authentication check that fixes the redirect loop for ALL user scenarios

**⚠️ CRITICAL**: This phase MUST be complete before user story validation can begin. The authentication fix affects both login and signup flows.

- [x] T004 Remove /tasks from protected paths array in frontend/src/middleware.ts (line 15)
- [x] T005 Import useAuth hook and useRouter in frontend/src/app/(dashboard)/tasks/page.tsx
- [x] T006 Add authentication state extraction using useAuth() hook in frontend/src/app/(dashboard)/tasks/page.tsx
- [x] T007 Add useEffect hook to check authentication and redirect if not authenticated in frontend/src/app/(dashboard)/tasks/page.tsx
- [x] T008 Add loading state check to show LoadingSpinner while auth initializes in frontend/src/app/(dashboard)/tasks/page.tsx
- [x] T009 Add early return (null) if not authenticated to prevent flash of content in frontend/src/app/(dashboard)/tasks/page.tsx
- [x] T010 Uncomment onAuthError callback in API client initialization in frontend/src/app/(dashboard)/tasks/page.tsx (lines 23-27)

**Checkpoint**: Core authentication fix implemented - both login and signup flows should now work without redirect loops

---

## Phase 3: User Story 1 - Login Flow Validation (Priority: P1) 🎯 MVP

**Goal**: Verify that authenticated users can access /tasks after login without redirect loop

**Independent Test**: Login with valid credentials via POST /signin, verify redirect to /tasks stays on /tasks without loop. See quickstart.md Test Suite 1 for detailed test cases.

**Acceptance Criteria**:
- User can login and access /tasks without redirect loop
- Page refresh while authenticated keeps user on /tasks
- Manual navigation to /tasks while authenticated works
- No flash of unauthenticated content

### Validation for User Story 1

- [ ] T011 [P] [US1] Manually test login flow per quickstart.md Test 1.1 (successful login and access to /tasks)
- [ ] T012 [P] [US1] Manually test page refresh while authenticated per quickstart.md Test 1.2
- [ ] T013 [P] [US1] Manually test manual navigation to /tasks while authenticated per quickstart.md Test 1.3
- [ ] T014 [US1] Verify URL remains http://localhost:3000/tasks after login (no redirect)
- [ ] T015 [US1] Verify localStorage contains auth-token key after login
- [ ] T016 [US1] Verify no console errors related to authentication after login
- [ ] T017 [US1] Verify no infinite redirect loop occurs after login

**Checkpoint**: At this point, User Story 1 should be fully functional. Users can login and access /tasks without redirect loops.

---

## Phase 4: User Story 2 - Signup Flow Validation (Priority: P1) 🎯 MVP

**Goal**: Verify that new users can access /tasks after signup without redirect loop

**Independent Test**: Create new account via POST /signup, verify redirect to /tasks stays on /tasks without loop. See quickstart.md Test Suite 2 for detailed test cases.

**Acceptance Criteria**:
- New user can signup and access /tasks without redirect loop
- Empty task list displayed for new user
- New user can immediately create tasks
- No flash of unauthenticated content

### Validation for User Story 2

- [ ] T018 [P] [US2] Manually test signup flow per quickstart.md Test 2.1 (successful signup and access to /tasks)
- [ ] T019 [P] [US2] Manually test new user can create tasks per quickstart.md Test 2.2
- [ ] T020 [US2] Verify URL remains http://localhost:3000/tasks after signup (no redirect)
- [ ] T021 [US2] Verify localStorage contains auth-token key after signup
- [ ] T022 [US2] Verify empty task list displayed for new user
- [ ] T023 [US2] Verify no console errors related to authentication after signup

**Checkpoint**: At this point, User Stories 1 AND 2 should both work. Users can login or signup and access /tasks without redirect loops.

---

## Phase 5: User Story 3 - Unauthenticated Access Validation (Priority: P2)

**Goal**: Verify that unauthenticated users are still properly redirected to /signin

**Independent Test**: Clear localStorage, navigate to /tasks, verify redirect to /signin occurs. See quickstart.md Test Suite 3 for detailed test cases.

**Acceptance Criteria**:
- Users without tokens redirected to /signin
- Users with expired tokens redirected to /signin
- Users with malformed tokens redirected to /signin
- Security maintained (protected route still protected)

### Validation for User Story 3

- [ ] T024 [P] [US3] Manually test unauthenticated access per quickstart.md Test 3.1 (no token redirect)
- [ ] T025 [P] [US3] Manually test expired token redirect per quickstart.md Test 3.2
- [ ] T026 [P] [US3] Manually test malformed token redirect per quickstart.md Test 3.3
- [ ] T027 [US3] Verify redirect to /signin occurs for unauthenticated users
- [ ] T028 [US3] Verify invalid tokens are cleared from localStorage
- [ ] T029 [US3] Verify no infinite redirect loop for unauthenticated users

**Checkpoint**: At this point, all three user stories should work. Authentication fix is complete and security is maintained.

---

## Phase 6: Edge Cases & Polish

**Purpose**: Verify edge cases and ensure production readiness

- [ ] T030 [P] Manually test localStorage unavailable scenario per quickstart.md Test 4.1
- [ ] T031 [P] Manually test race condition handling per quickstart.md Test 4.2 (rapid navigation)
- [ ] T032 [P] Manually test token expiry during active session per quickstart.md Test 4.3
- [ ] T033 [P] Manually test page load time per quickstart.md Test 5.1 (verify <2 seconds)
- [ ] T034 [P] Manually test no flash of unauthenticated content per quickstart.md Test 5.2
- [ ] T035 Verify all success criteria from spec.md are met (SC-001 through SC-006)
- [ ] T036 Run full test suite from quickstart.md (all 15 test cases) and document results
- [ ] T037 Verify no regression in existing authentication functionality (login/signup/logout)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Core Fix (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Core Fix completion - Delivers MVP for login flow
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
- T004-T010 must run sequentially (each builds on previous changes)

**User Story 1 Validation**:
- T011-T013 can run in parallel [P] if multiple testers available (independent test cases)
- T014-T017 should run sequentially after manual tests

**User Story 2 Validation**:
- T018-T019 can run in parallel [P] if multiple testers available (independent test cases)
- T020-T023 should run sequentially after manual tests

**User Story 3 Validation**:
- T024-T026 can run in parallel [P] if multiple testers available (independent test cases)
- T027-T029 should run sequentially after manual tests

**Edge Cases & Polish Phase**:
- T030-T034 can run in parallel [P] (independent test cases)
- T035-T037 should run sequentially (comprehensive validation)

### Parallel Opportunities

- **Setup Phase**: No parallel tasks (sequential understanding)
- **Core Fix Phase**: No parallel tasks (sequential implementation)
- **User Story 1**: T011-T013 can run in parallel [P] (3 tasks)
- **User Story 2**: T018-T019 can run in parallel [P] (2 tasks)
- **User Story 3**: T024-T026 can run in parallel [P] (3 tasks)
- **Edge Cases & Polish**: T030-T034 can run in parallel [P] (5 tasks)
- **Across User Stories**: Once Core Fix completes, US1, US2, and US3 validation can run in parallel if team capacity allows

**Total parallelizable tasks**: 13 out of 37 (35%)

---

## Parallel Example: User Story 1 Validation

```bash
# After Core Fix completes, launch these together:
Task T011: "Manually test login flow per quickstart.md Test 1.1"
Task T012: "Manually test page refresh while authenticated per quickstart.md Test 1.2"
Task T013: "Manually test manual navigation to /tasks while authenticated per quickstart.md Test 1.3"
```

---

## Parallel Example: All User Stories Validation

```bash
# After Core Fix completes, launch all validation in parallel (if multiple testers):
# Tester A: User Story 1 validation (T011-T017)
# Tester B: User Story 2 validation (T018-T023)
# Tester C: User Story 3 validation (T024-T029)
```

---

## Implementation Strategy

### MVP First (Core Fix + User Story 1)

1. Complete Phase 1: Setup (understand existing code)
2. Complete Phase 2: Core Fix (implement authentication check)
3. Complete Phase 3: User Story 1 (validate login flow)
4. **STOP and VALIDATE**: Test login with long passwords
5. Deploy/demo if ready - users can now login and access /tasks!

**MVP Delivers**: Login flow works without redirect loop. This unblocks the most critical user journey.

### Incremental Delivery

1. Complete Setup + Core Fix → Authentication check ready
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 → Test independently → Deploy/Demo (signup functionality)
4. Add User Story 3 → Test independently → Deploy/Demo (security validation)
5. Add Edge Cases & Polish → Test independently → Deploy/Demo (production-ready)
6. Each phase adds value without breaking previous functionality

### Parallel Team Strategy

With multiple team members:

1. Team completes Setup + Core Fix together (10 tasks, ~2-4 hours)
2. Once Core Fix is done:
   - Tester A: User Story 1 validation (7 tasks, login tests)
   - Tester B: User Story 2 validation (6 tasks, signup tests)
   - Tester C: User Story 3 validation (6 tasks, security tests)
3. Stories validate and integrate independently
4. Team validates edge cases together (Phase 6)

---

## Task Summary

**Total Tasks**: 37 tasks across 6 phases

**Task Count by Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Core Fix): 7 tasks
- Phase 3 (User Story 1): 7 tasks
- Phase 4 (User Story 2): 6 tasks
- Phase 5 (User Story 3): 6 tasks
- Phase 6 (Edge Cases & Polish): 8 tasks

**Task Count by User Story**:
- Core Fix (blocking): 7 tasks
- User Story 1 (Login): 7 tasks
- User Story 2 (Signup): 6 tasks
- User Story 3 (Unauthenticated): 6 tasks
- Edge Cases & Polish: 8 tasks

**Parallel Opportunities Identified**:
- User Story 1: 3 tasks can run in parallel (T011-T013)
- User Story 2: 2 tasks can run in parallel (T018-T019)
- User Story 3: 3 tasks can run in parallel (T024-T026)
- Edge Cases & Polish: 5 tasks can run in parallel (T030-T034)
- **Total parallelizable tasks**: 13 out of 37 (35%)

**Independent Test Criteria**:
- **User Story 1**: Login with valid credentials → stay on /tasks without redirect loop
- **User Story 2**: Signup with valid information → stay on /tasks without redirect loop
- **User Story 3**: Navigate to /tasks without token → redirect to /signin

**Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Core Fix) + Phase 3 (User Story 1) = 17 tasks
- Delivers core value: Users can login and access /tasks without redirect loops
- Unblocks the most critical user journey
- Can be completed in 4-6 hours

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
