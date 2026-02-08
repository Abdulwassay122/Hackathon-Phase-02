# Tasks: Fix Password Length Error (72-Byte Limit)

**Input**: Design documents from `/specs/006-fix-password-length/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification. Manual testing procedures are documented in quickstart.md.

**Organization**: Tasks are grouped by implementation phase. The core fix (Phase 2) is foundational and blocks both user stories. Each user story then has validation tasks to verify the fix works for that specific scenario.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with backend/frontend structure:
- Backend: `backend/src/` (changes in this feature)
- Frontend: `frontend/src/` (no changes in this feature)

---

## Phase 1: Setup & Verification

**Purpose**: Verify existing code structure and prepare for implementation

- [ ] T001 Verify existing password hashing implementation in backend/src/auth/password_utils.py (if exists) or identify where password hashing currently occurs
- [ ] T002 Verify existing authentication endpoints in backend/src/api/auth_routes.py use password hashing functions
- [ ] T003 Review existing test structure in backend/tests/ to understand testing patterns

---

## Phase 2: Core Password Truncation Fix (Foundational)

**Purpose**: Implement the core password truncation logic that fixes the 72-byte error for ALL authentication operations

**⚠️ CRITICAL**: This phase MUST be complete before user story validation can begin. The truncation logic affects both registration and login.

- [ ] T004 [P] Create or update password_utils.py in backend/src/auth/ with truncate_password() function that encodes password to UTF-8 and truncates to 72 bytes
- [ ] T005 [P] Implement hash_password() function in backend/src/auth/password_utils.py that calls truncate_password() before bcrypt hashing
- [ ] T006 [P] Implement verify_password() function in backend/src/auth/password_utils.py that calls truncate_password() before bcrypt verification
- [ ] T007 Update signup endpoint in backend/src/api/auth_routes.py to use hash_password() from password_utils
- [ ] T008 Update login endpoint in backend/src/api/auth_routes.py to use verify_password() from password_utils
- [ ] T009 Add error handling to ensure byte-length errors are caught and logged (if they still occur)
- [ ] T010 Add UTF-8 decoding with errors='ignore' to handle split multi-byte characters gracefully

**Checkpoint**: Core truncation logic implemented - both registration and login should now handle long passwords

---

## Phase 3: User Story 1 - Registration with Long Password (Priority: P1) 🎯 MVP

**Goal**: Enable users to register with passwords longer than 72 bytes without encountering errors

**Independent Test**: Register a new user with an 80-character password via POST /api/auth/signup and verify: (1) 201 Created response, (2) JWT token returned, (3) no byte-length errors. See quickstart.md Test Suite 1 for detailed test cases.

**Acceptance Criteria**:
- New user can signup with 80-character password
- New user can signup with 100-character password
- New user can signup with password containing multi-byte UTF-8 characters
- System returns 201 Created with JWT token
- No "72 bytes" error message appears

### Validation for User Story 1

- [ ] T011 [US1] Manually test registration with 80-character password per quickstart.md Test 1.1
- [ ] T012 [US1] Manually test registration with 100-character password per quickstart.md Test 1.2
- [ ] T013 [US1] Manually test registration with multi-byte UTF-8 characters per quickstart.md Test 1.3
- [ ] T014 [US1] Manually test registration with exactly 72-byte password per quickstart.md Test 1.4
- [ ] T015 [US1] Verify that registration endpoint returns 201 Created for all long password cases
- [ ] T016 [US1] Verify that JWT token is returned in response for successful registrations
- [ ] T017 [US1] Verify that no "password cannot be longer than 72 bytes" error appears in logs or responses

**Checkpoint**: At this point, User Story 1 should be fully functional. Users can register with long passwords without errors.

---

## Phase 4: User Story 2 - Login with Long Password (Priority: P1) 🎯 MVP

**Goal**: Enable users to authenticate with passwords longer than 72 bytes without encountering errors

**Independent Test**: First create user via signup with 80-character password. Then login with same password via POST /api/auth/login and verify: (1) 200 OK response, (2) JWT token returned, (3) no byte-length errors. See quickstart.md Test Suite 2 for detailed test cases.

**Acceptance Criteria**:
- Existing user can login with 80-character password
- Existing user can login with 100-character password
- Existing user can login with password containing multi-byte UTF-8 characters
- System returns 200 OK with JWT token
- Backward compatibility maintained for short passwords

### Validation for User Story 2

- [ ] T018 [US2] Manually test login with 80-character password per quickstart.md Test 2.1
- [ ] T019 [US2] Manually test login with 100-character password per quickstart.md Test 2.2
- [ ] T020 [US2] Manually test login with multi-byte UTF-8 characters per quickstart.md Test 2.3
- [ ] T021 [US2] Verify that login endpoint returns 200 OK for all long password cases
- [ ] T022 [US2] Verify that JWT token is returned in response for successful logins
- [ ] T023 [US2] Verify that no "password cannot be longer than 72 bytes" error appears in logs or responses

**Checkpoint**: At this point, User Stories 1 AND 2 should both work. Users can register and login with long passwords.

---

## Phase 5: Backward Compatibility & Edge Cases

**Purpose**: Verify that the fix doesn't break existing functionality and handles edge cases correctly

- [ ] T024 [P] Test backward compatibility: existing user with short password (<72 bytes) can still login per quickstart.md Test 3.1
- [ ] T025 [P] Test that wrong passwords are still rejected with 401 Unauthorized per quickstart.md Test 3.2
- [ ] T026 [P] Test edge case: password with only multi-byte characters per quickstart.md Test 4.1
- [ ] T027 [P] Test edge case: empty password still fails validation per quickstart.md Test 4.2
- [ ] T028 [P] Test edge case: password at truncation boundary (73 bytes) per quickstart.md Test 4.3
- [ ] T029 Verify that password truncation adds negligible overhead (<1ms) per quickstart.md Test 5.1

---

## Phase 6: Polish & Documentation

**Purpose**: Final validation and documentation updates

- [ ] T030 [P] Verify all success criteria from spec.md are met (SC-001 through SC-006)
- [ ] T031 [P] Confirm error message "password cannot be longer than 72 bytes" no longer appears in application logs
- [ ] T032 [P] Document the password truncation behavior in code comments (if not already done)
- [ ] T033 Run full test suite from quickstart.md (all 15 test cases) and document results
- [ ] T034 Verify no regression in existing authentication functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Core Fix (Phase 2)**: Depends on Setup completion - BLOCKS both user stories
- **User Story 1 (Phase 3)**: Depends on Core Fix completion - Delivers MVP for registration
- **User Story 2 (Phase 4)**: Depends on Core Fix completion - Can run in parallel with US1 validation if different testers
- **Backward Compatibility (Phase 5)**: Depends on Core Fix completion - Can run in parallel with US1/US2 validation
- **Polish (Phase 6)**: Depends on all user stories being validated

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Core Fix (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on Core Fix (Phase 2) - No dependencies on other stories (can validate in parallel with US1)

**Note**: While the user stories CAN be validated in parallel (they test different endpoints), they share the same core implementation (Phase 2).

### Within Each Phase

**Setup Phase**:
- T001-T003 should run sequentially (each builds understanding)

**Core Fix Phase**:
- T004, T005, T006 can run in parallel [P] (different functions)
- T007-T010 must run sequentially after T004-T006 (depend on utility functions)

**User Story 1 Validation**:
- T011-T017 can run in parallel [P] if multiple testers available (independent test cases)

**User Story 2 Validation**:
- T018-T023 can run in parallel [P] if multiple testers available (independent test cases)

**Backward Compatibility**:
- T024-T029 can run in parallel [P] (independent test cases)

**Polish Phase**:
- T030-T032 can run in parallel [P] (different concerns)
- T033-T034 should run sequentially (comprehensive validation)

### Parallel Opportunities

- **Setup Phase**: No parallel tasks (sequential understanding)
- **Core Fix Phase**: T004, T005, T006 can run in parallel [P] (3 tasks)
- **User Story 1**: T011-T017 can run in parallel [P] (7 tasks)
- **User Story 2**: T018-T023 can run in parallel [P] (6 tasks)
- **Backward Compatibility**: T024-T029 can run in parallel [P] (6 tasks)
- **Polish Phase**: T030-T032 can run in parallel [P] (3 tasks)
- **Across User Stories**: Once Core Fix completes, US1 and US2 validation can run in parallel if team capacity allows

**Total parallelizable tasks**: 25 out of 34 (74%)

---

## Parallel Example: Core Fix Phase

```bash
# After Setup completes, launch these together:
Task T004: "Create truncate_password() function in backend/src/auth/password_utils.py"
Task T005: "Implement hash_password() function in backend/src/auth/password_utils.py"
Task T006: "Implement verify_password() function in backend/src/auth/password_utils.py"
```

---

## Parallel Example: User Story 1 Validation

```bash
# Launch all validation tests together (if multiple testers):
Task T011: "Test registration with 80-character password"
Task T012: "Test registration with 100-character password"
Task T013: "Test registration with multi-byte UTF-8 characters"
Task T014: "Test registration with exactly 72-byte password"
Task T015: "Verify 201 Created response"
Task T016: "Verify JWT token in response"
Task T017: "Verify no byte-length errors"
```

---

## Implementation Strategy

### MVP First (Core Fix + User Story 1)

1. Complete Phase 1: Setup (understand existing code)
2. Complete Phase 2: Core Fix (implement truncation logic)
3. Complete Phase 3: User Story 1 (validate registration)
4. **STOP and VALIDATE**: Test registration with long passwords
5. Deploy/demo if ready - users can now register with long passwords!

**MVP Delivers**: Registration with long passwords works. This unblocks user signups and prevents the most critical error.

### Incremental Delivery

1. Complete Setup + Core Fix → Truncation logic ready
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 → Test independently → Deploy/Demo (login functionality)
4. Add Backward Compatibility → Test independently → Deploy/Demo (production-ready)
5. Each phase adds value without breaking previous functionality

### Parallel Team Strategy

With multiple team members:

1. Team completes Setup + Core Fix together (10 tasks, ~2-4 hours)
2. Once Core Fix is done:
   - Tester A: User Story 1 validation (7 tasks, registration tests)
   - Tester B: User Story 2 validation (6 tasks, login tests)
   - Tester C: Backward Compatibility (6 tasks, edge cases)
3. Stories validate and integrate independently
4. Team validates together (Phase 6)

---

## Task Summary

**Total Tasks**: 34 tasks across 6 phases

**Task Count by Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Core Fix): 7 tasks
- Phase 3 (User Story 1): 7 tasks
- Phase 4 (User Story 2): 6 tasks
- Phase 5 (Backward Compatibility): 6 tasks
- Phase 6 (Polish): 5 tasks

**Task Count by User Story**:
- Core Fix (blocking): 7 tasks
- User Story 1 (Registration): 7 tasks
- User Story 2 (Login): 6 tasks
- Backward Compatibility: 6 tasks
- Polish & Documentation: 5 tasks

**Parallel Opportunities Identified**:
- Core Fix: 3 tasks can run in parallel (T004, T005, T006)
- User Story 1: 7 tasks can run in parallel (T011-T017)
- User Story 2: 6 tasks can run in parallel (T018-T023)
- Backward Compatibility: 6 tasks can run in parallel (T024-T029)
- Polish: 3 tasks can run in parallel (T030-T032)
- **Total parallelizable tasks**: 25 out of 34 (74%)

**Independent Test Criteria**:
- **User Story 1**: Register with 80-character password → 201 Created with JWT token, no byte-length errors
- **User Story 2**: Login with 80-character password → 200 OK with JWT token, no byte-length errors

**Suggested MVP Scope**: Phase 1 (Setup) + Phase 2 (Core Fix) + Phase 3 (User Story 1) = 17 tasks
- Delivers core value: Users can register with long passwords without errors
- Unblocks user signups and prevents critical authentication failures
- Can be completed in 4-6 hours

---

## Notes

- [P] tasks = different files or independent test cases, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently testable after Core Fix is complete
- Tests are NOT included as they were not requested in the specification
- Manual testing procedures documented in quickstart.md (15 test cases)
- Commit after each task or logical group
- Stop at any checkpoint to validate functionality independently
- All tasks include exact file paths for clarity
