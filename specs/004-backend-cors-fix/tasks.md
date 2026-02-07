# Tasks: Backend CORS Configuration

**Input**: Design documents from `/specs/004-backend-cors-fix/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

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

## Phase 1: Foundational (CORS Configuration Infrastructure)

**Purpose**: Core CORS configuration infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

This phase creates the shared configuration infrastructure (parsing, validation, CORSConfig dataclass) that all three user stories will use. Without this foundation, none of the user stories can be implemented.

- [x] T001 Add CORSConfig dataclass to backend/src/config.py with fields for allow_origins, allow_credentials, allow_methods, allow_headers, expose_headers, and max_age
- [x] T002 [P] Add validate_origin() function to backend/src/config.py to validate single origin URL (check protocol, no trailing slash, not wildcard, not empty)
- [x] T003 Add parse_cors_origins() function to backend/src/config.py to parse comma-separated origins from environment variable and validate each origin
- [x] T004 Add get_cors_origins() function to backend/src/config.py to load CORS_ORIGINS from environment and call parse_cors_origins()
- [x] T005 Add get_cors_config() function to backend/src/config.py to create CORSConfig instance with parsed origins and hardcoded security settings
- [x] T006 [P] Add log_cors_configuration() function to backend/src/logging_config.py to log CORS configuration at startup with allowed origins, credentials, methods, and headers

**Checkpoint**: Configuration infrastructure ready - user story implementation can now begin

---

## Phase 2: User Story 1 - Frontend API Communication (Priority: P1) 🎯 MVP

**Goal**: Enable the Next.js frontend running on http://localhost:3000 to make API requests to the FastAPI backend without CORS errors. This is the foundation for frontend-backend integration.

**Independent Test**: Start frontend on http://localhost:3000, make any API call to the backend (e.g., GET /api/users/123/tasks), and verify no CORS errors appear in browser console. Verify response headers include `access-control-allow-origin: http://localhost:3000`.

**Acceptance Criteria**:
- Frontend can make GET requests without CORS errors
- Frontend can make POST requests with JSON body without CORS errors
- Frontend can make requests with Authorization header (JWT token) without CORS errors
- Backend responds to preflight OPTIONS requests with appropriate CORS headers
- PUT, PATCH, and DELETE requests work without CORS errors

### Implementation for User Story 1

- [x] T007 [US1] Import CORSMiddleware from fastapi.middleware.cors in backend/src/main.py
- [x] T008 [US1] Import get_cors_config from src.config in backend/src/main.py
- [x] T009 [US1] Call get_cors_config() after FastAPI app creation in backend/src/main.py to load CORS configuration
- [x] T010 [US1] Add CORSMiddleware to FastAPI app in backend/src/main.py using app.add_middleware() with configuration from get_cors_config() (must be BEFORE route registration)
- [x] T011 [US1] Call log_cors_configuration() in startup_event() function in backend/src/main.py to log CORS settings at application startup
- [x] T012 [US1] Set CORS_ORIGINS=http://localhost:3000 in backend/.env file for local development testing

**Checkpoint**: At this point, User Story 1 should be fully functional. Frontend on localhost:3000 can communicate with backend without CORS errors. Test independently before proceeding.

---

## Phase 3: User Story 2 - Environment-Based Configuration (Priority: P2)

**Goal**: Enable flexible, environment-specific CORS configuration by reading allowed origins from the CORS_ORIGINS environment variable. This allows different origins for development, staging, and production without code changes.

**Independent Test**: Change CORS_ORIGINS environment variable to a different origin (e.g., http://localhost:3001), restart backend, verify new origin is allowed while http://localhost:3000 is now blocked. Test with multiple comma-separated origins.

**Acceptance Criteria**:
- Backend reads CORS_ORIGINS from environment variable at startup
- Single origin configuration works (e.g., CORS_ORIGINS=http://localhost:3000)
- Multiple comma-separated origins work (e.g., CORS_ORIGINS=http://localhost:3000,http://localhost:3001)
- Backend logs warning if CORS_ORIGINS is not set or empty
- Backend uses secure default (empty list) if CORS_ORIGINS is not set
- Invalid origins are skipped with warning logs

### Implementation for User Story 2

- [x] T013 [US2] Add CORS_ORIGINS example to backend/.env.example with documentation explaining format (single origin: http://localhost:3000, multiple origins: http://localhost:3000,http://localhost:3001)
- [x] T014 [US2] Add comment in backend/.env.example explaining that CORS_ORIGINS is required for frontend-backend communication and should be set to frontend URL
- [x] T015 [US2] Add comment in backend/.env.example warning against using wildcard (*) origins and explaining security implications
- [x] T016 [US2] Verify parse_cors_origins() in backend/src/config.py handles empty CORS_ORIGINS by returning empty list and logging warning
- [x] T017 [US2] Verify parse_cors_origins() in backend/src/config.py handles multiple comma-separated origins by splitting on comma and stripping whitespace

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. CORS configuration is now environment-driven and flexible.

---

## Phase 4: User Story 3 - Secure CORS Headers (Priority: P3)

**Goal**: Ensure CORS configuration follows security best practices by using explicit lists for headers and methods (no wildcards), validating origin URLs, and enabling credentials for JWT authentication.

**Independent Test**: Inspect response headers in browser DevTools Network tab and verify Access-Control-Allow-Headers includes "Authorization" and "Content-Type" but NOT "*". Verify Access-Control-Allow-Methods includes specific methods but NOT "*". Verify Access-Control-Allow-Origin contains specific origin, not "*".

**Acceptance Criteria**:
- Access-Control-Allow-Headers includes "Authorization" and "Content-Type" but not "*"
- Access-Control-Allow-Methods includes "GET", "POST", "PUT", "PATCH", "DELETE" but not "*"
- Access-Control-Allow-Origin contains specific requesting origin, not "*"
- Access-Control-Allow-Credentials is set to "true"
- Wildcard (*) origins are rejected by validation with error log
- Origins with trailing slashes are rejected by validation with error log
- Origins without protocol (http:// or https://) are rejected by validation with error log

### Implementation for User Story 3

- [x] T018 [US3] Verify validate_origin() in backend/src/config.py rejects wildcard "*" with error message "Wildcard origin (*) not allowed per security policy"
- [x] T019 [US3] Verify validate_origin() in backend/src/config.py rejects origins with trailing slash with error message explaining trailing slash not allowed
- [x] T020 [US3] Verify validate_origin() in backend/src/config.py rejects origins without protocol (http:// or https://) with error message explaining protocol required
- [x] T021 [US3] Verify validate_origin() in backend/src/config.py rejects empty or whitespace-only origins with error message
- [x] T022 [US3] Verify get_cors_config() in backend/src/config.py sets allow_credentials=True (hardcoded, required for JWT authentication)
- [x] T023 [US3] Verify get_cors_config() in backend/src/config.py sets allow_methods to explicit list ["GET", "POST", "PUT", "PATCH", "DELETE"] (hardcoded, no wildcards)
- [x] T024 [US3] Verify get_cors_config() in backend/src/config.py sets allow_headers to explicit list ["Authorization", "Content-Type"] (hardcoded, no wildcards)
- [x] T025 [US3] Verify log_cors_configuration() in backend/src/logging_config.py logs warning if no origins are configured (empty list)

**Checkpoint**: All user stories should now be independently functional with security best practices enforced.

---

## Phase 5: Validation & Documentation

**Purpose**: Final validation and documentation to ensure feature is production-ready

- [x] T026 [P] Add section to backend/README.md explaining CORS configuration setup (how to set CORS_ORIGINS, what values are valid, security considerations)
- [x] T027 [P] Add troubleshooting section to backend/README.md for common CORS issues (missing CORS_ORIGINS, trailing slashes, protocol missing, wildcard errors)
- [ ] T028 Manually test User Story 1: Start frontend on localhost:3000, make API calls, verify no CORS errors in browser console
- [ ] T029 Manually test User Story 2: Change CORS_ORIGINS to different origin, restart backend, verify new origin works and old origin is blocked
- [ ] T030 Manually test User Story 3: Inspect response headers in browser DevTools, verify explicit headers/methods (no wildcards), verify credentials enabled
- [ ] T031 Run quickstart.md Test 1 (Verify CORS headers in browser DevTools) and document results
- [ ] T032 Run quickstart.md Test 2 (Verify preflight OPTIONS requests) and document results
- [ ] T033 Run quickstart.md Test 4 (Test origin blocking - negative test) and document results
- [ ] T034 Run quickstart.md Test 5 (Test all HTTP methods) and document results
- [ ] T035 Run quickstart.md Test 6 (Test Authorization header with JWT) and document results

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: No dependencies - can start immediately
  - BLOCKS all user stories - must complete before any user story work begins
- **User Story 1 (Phase 2)**: Depends on Foundational completion
  - Delivers MVP - frontend can communicate with backend
- **User Story 2 (Phase 3)**: Depends on Foundational completion
  - Can start in parallel with US1 if different developers
  - Enhances US1 with environment-based configuration
- **User Story 3 (Phase 4)**: Depends on Foundational completion
  - Can start in parallel with US1/US2 if different developers
  - Adds security validation to configuration
- **Validation (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational phase - No dependencies on other stories
- **User Story 2 (P2)**: Depends on Foundational phase - No dependencies on other stories (can run parallel with US1)
- **User Story 3 (P3)**: Depends on Foundational phase - No dependencies on other stories (can run parallel with US1/US2)

**Note**: While the user stories CAN be implemented in parallel (they touch different aspects of the configuration), they are designed to build on each other in priority order for incremental value delivery.

### Within Each Phase

**Foundational Phase**:
- T001 (CORSConfig dataclass) must complete first
- T002 (validate_origin) and T006 (log_cors_configuration) can run in parallel [P]
- T003 (parse_cors_origins) depends on T002 (validate_origin)
- T004 (get_cors_origins) depends on T003 (parse_cors_origins)
- T005 (get_cors_config) depends on T001 (CORSConfig) and T004 (get_cors_origins)

**User Story 1**:
- T007-T011 must run sequentially (each modifies main.py)
- T012 can run in parallel with T007-T011 (different file)

**User Story 2**:
- T013-T015 can run in parallel [P] (all modify .env.example)
- T016-T017 are verification tasks (check existing code)

**User Story 3**:
- T018-T025 are all verification tasks (check existing code)
- All can run in parallel [P]

**Validation Phase**:
- T026-T027 can run in parallel [P] (documentation)
- T028-T035 should run sequentially (manual testing)

### Parallel Opportunities

- **Foundational Phase**: T002 and T006 can run in parallel
- **User Story 1**: T012 can run in parallel with T007-T011
- **User Story 2**: T013-T015 can all run in parallel
- **User Story 3**: T018-T025 can all run in parallel
- **Validation Phase**: T026-T027 can run in parallel
- **Across User Stories**: Once Foundational completes, US1, US2, and US3 can all start in parallel if team capacity allows

---

## Parallel Example: Foundational Phase

```bash
# After T001 completes, launch these together:
Task T002: "Add validate_origin() function to backend/src/config.py"
Task T006: "Add log_cors_configuration() function to backend/src/logging_config.py"

# After T002 completes:
Task T003: "Add parse_cors_origins() function to backend/src/config.py"

# After T003 completes:
Task T004: "Add get_cors_origins() function to backend/src/config.py"

# After T001 and T004 complete:
Task T005: "Add get_cors_config() function to backend/src/config.py"
```

---

## Parallel Example: User Story 3

```bash
# All verification tasks can run together:
Task T018: "Verify validate_origin() rejects wildcard"
Task T019: "Verify validate_origin() rejects trailing slash"
Task T020: "Verify validate_origin() rejects missing protocol"
Task T021: "Verify validate_origin() rejects empty origins"
Task T022: "Verify get_cors_config() sets allow_credentials=True"
Task T023: "Verify get_cors_config() sets explicit allow_methods"
Task T024: "Verify get_cors_config() sets explicit allow_headers"
Task T025: "Verify log_cors_configuration() warns on empty origins"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Foundational (configuration infrastructure)
2. Complete Phase 2: User Story 1 (enable CORS for localhost:3000)
3. **STOP and VALIDATE**: Test with frontend, verify no CORS errors
4. Deploy/demo if ready - frontend can now communicate with backend!

**MVP Delivers**: Frontend-backend communication works. This unblocks all frontend development.

### Incremental Delivery

1. Complete Foundational → Configuration infrastructure ready
2. Add User Story 1 → Test independently → **Deploy/Demo (MVP!)**
3. Add User Story 2 → Test independently → Deploy/Demo (environment flexibility)
4. Add User Story 3 → Test independently → Deploy/Demo (production-ready security)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Foundational together (6 tasks, ~1-2 hours)
2. Once Foundational is done:
   - Developer A: User Story 1 (6 tasks, core functionality)
   - Developer B: User Story 2 (5 tasks, documentation)
   - Developer C: User Story 3 (8 tasks, verification)
3. Stories complete and integrate independently
4. Team validates together (Phase 5)

---

## Task Summary

**Total Tasks**: 35 tasks across 5 phases

**Task Count by Phase**:
- Phase 1 (Foundational): 6 tasks
- Phase 2 (User Story 1 - P1): 6 tasks
- Phase 3 (User Story 2 - P2): 5 tasks
- Phase 4 (User Story 3 - P3): 8 tasks
- Phase 5 (Validation): 10 tasks

**Task Count by User Story**:
- Foundational (blocking): 6 tasks
- User Story 1 (Frontend API Communication): 6 tasks
- User Story 2 (Environment-Based Configuration): 5 tasks
- User Story 3 (Secure CORS Headers): 8 tasks
- Validation & Documentation: 10 tasks

**Parallel Opportunities Identified**:
- Foundational: 2 tasks can run in parallel (T002, T006)
- User Story 1: 1 task can run in parallel (T012)
- User Story 2: 3 tasks can run in parallel (T013-T015)
- User Story 3: 8 tasks can run in parallel (T018-T025)
- Validation: 2 tasks can run in parallel (T026-T027)
- **Total parallelizable tasks**: 16 out of 35 (46%)

**Independent Test Criteria**:
- **User Story 1**: Start frontend, make API call, verify no CORS errors in console
- **User Story 2**: Change CORS_ORIGINS, restart backend, verify new origin works
- **User Story 3**: Inspect response headers, verify explicit lists (no wildcards)

**Suggested MVP Scope**: Phase 1 (Foundational) + Phase 2 (User Story 1) = 12 tasks
- Delivers core value: Frontend can communicate with backend
- Unblocks all frontend development
- Can be completed in 2-4 hours

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
- Verification tasks (T016-T025) check that code meets requirements without modifying code
