# Implementation Plan: Backend CORS Configuration

**Branch**: `004-backend-cors-fix` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-backend-cors-fix/spec.md`

## Summary

Enable Cross-Origin Resource Sharing (CORS) in the FastAPI backend to allow the Next.js frontend running on http://localhost:3000 to make authenticated API requests. The implementation will use FastAPI's built-in CORSMiddleware with environment-based configuration, explicit header and method allowances, and no wildcard permissions. This unblocks frontend-backend integration while maintaining security best practices.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI 0.104.1, python-dotenv 1.0.0
**Storage**: N/A (configuration only)
**Testing**: pytest 7.4.3, manual browser testing
**Target Platform**: Linux/Windows server (development: localhost)
**Project Type**: Web application (backend component)
**Performance Goals**: No measurable impact on API response times (<5ms overhead for CORS header processing)
**Constraints**: Must not use wildcard (*) for any CORS setting; must read configuration from environment variables only; must not modify frontend code
**Scale/Scope**: Single backend instance; 5 HTTP methods; 2 custom headers; 1-3 allowed origins (development/staging/production)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Correctness of Data Modeling and API Behavior
- **Status**: PASS
- **Rationale**: CORS configuration does not modify data models or API behavior. Existing endpoints remain unchanged; only HTTP response headers are added.

### ✅ Principle II: Clear Separation of Concerns
- **Status**: PASS
- **Rationale**: CORS middleware operates at the application layer, separate from business logic. Configuration is centralized in environment variables and applied at startup.

### ✅ Principle III: Deterministic and Reproducible Backend Behavior
- **Status**: PASS
- **Rationale**: CORS configuration is loaded from environment variables at startup, ensuring consistent behavior across environments. All CORS responses are deterministic based on request origin.

### ✅ Principle IV: Spec-Driven, Agentic Implementation
- **Status**: PASS
- **Rationale**: This plan follows the spec-driven workflow: specification → plan → tasks → implementation. No manual coding will occur.

### ✅ Principle V: Comprehensive Testability and Verification
- **Status**: PASS
- **Rationale**: CORS behavior is testable via browser DevTools and HTTP requests. Preflight requests can be verified independently. Success criteria include specific observable outcomes (no CORS errors, proper headers in responses).

### ✅ Principle VI: RESTful API Compliance
- **Status**: PASS
- **Rationale**: CORS middleware adds standard HTTP headers without modifying REST semantics. All existing REST conventions are preserved.

### ✅ Principle VII: Authentication and Security
- **Status**: PASS
- **Rationale**: CORS configuration explicitly allows the Authorization header for JWT tokens. No wildcard origins are used, maintaining security boundaries. Credentials support is enabled for authenticated requests.

### ✅ Principle VIII: Frontend Integration and User Experience
- **Status**: PASS
- **Rationale**: This feature directly enables frontend-backend communication. CORS errors will be eliminated, allowing the frontend to make authenticated API requests seamlessly.

**Overall Assessment**: All constitutional principles are satisfied. No violations require justification.

## Project Structure

### Documentation (this feature)

```text
specs/004-backend-cors-fix/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output: FastAPI CORS best practices
├── data-model.md        # Phase 1 output: CORS configuration structure
├── quickstart.md        # Phase 1 output: Testing CORS configuration
├── contracts/           # Phase 1 output: N/A (no API contracts changed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                    # [MODIFY] Add CORSMiddleware configuration
│   ├── config.py                  # [MODIFY] Add CORS_ORIGINS environment variable
│   ├── api/
│   │   └── task_routes.py         # [NO CHANGE] Existing routes work with CORS
│   ├── auth/
│   │   └── jwt_handler.py         # [NO CHANGE] JWT verification unchanged
│   ├── models/
│   │   └── task.py                # [NO CHANGE] Data models unchanged
│   └── database/
│       └── database.py            # [NO CHANGE] Database layer unchanged
├── tests/
│   ├── test_cors.py               # [CREATE] CORS configuration tests
│   └── integration/
│       └── test_cors_integration.py  # [CREATE] Browser-based CORS tests
├── .env.example                   # [MODIFY] Add CORS_ORIGINS example
└── requirements.txt               # [NO CHANGE] FastAPI already includes CORS support

frontend/
└── [NO CHANGES] Frontend code remains unchanged
```

**Structure Decision**: This is a backend-only change affecting the FastAPI application initialization. The primary modification is in `backend/src/main.py` where CORSMiddleware will be added. Configuration will be read from `backend/src/config.py` which loads environment variables. No frontend changes are required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. This section is not applicable.

## Phase 0: Research

**Objective**: Understand FastAPI CORS middleware capabilities, best practices, and security considerations.

**Deliverable**: `research.md` containing:
- FastAPI CORSMiddleware API documentation summary
- Environment variable parsing patterns for comma-separated origins
- Security implications of CORS settings (wildcards, credentials, headers)
- Preflight request handling in FastAPI
- Common CORS misconfigurations and how to avoid them
- Testing strategies for CORS (browser DevTools, curl, pytest)

**Research Questions**:
1. What are the exact parameters for FastAPI's `CORSMiddleware`?
2. How should multiple origins be parsed from a single environment variable?
3. What headers and methods should be explicitly allowed for JWT authentication?
4. How does FastAPI handle preflight OPTIONS requests automatically?
5. What are the security risks of using wildcards in CORS configuration?
6. How can CORS configuration be tested without a running frontend?

## Phase 1: Design

**Objective**: Design the CORS configuration structure, environment variable schema, and integration points.

**Deliverables**:
1. **`data-model.md`**: CORS configuration data structure
   - Environment variable schema (CORS_ORIGINS format)
   - CORSMiddleware parameters mapping
   - Default values and fallback behavior
   - Validation rules for origin URLs

2. **`quickstart.md`**: Testing guide for CORS configuration
   - How to set CORS_ORIGINS environment variable
   - How to verify CORS headers in browser DevTools
   - How to test preflight requests with curl
   - How to test with frontend running on localhost:3000
   - How to test origin blocking (requests from disallowed origins)

3. **`contracts/`**: N/A - No API contracts are modified. CORS only adds HTTP headers to existing responses.

**Design Decisions**:
- **Environment Variable Format**: Comma-separated list of origins (e.g., `http://localhost:3000,http://localhost:3001`)
- **Middleware Placement**: CORSMiddleware added immediately after FastAPI app creation in `main.py`
- **Allowed Headers**: `["Authorization", "Content-Type"]` (explicit list, no wildcards)
- **Allowed Methods**: `["GET", "POST", "PUT", "PATCH", "DELETE"]` (explicit list, no wildcards)
- **Credentials Support**: `allow_credentials=True` (required for JWT tokens)
- **Default Behavior**: If CORS_ORIGINS is not set, log warning and use empty list (no origins allowed)

## Phase 2: Implementation Tasks

**Objective**: Break down the implementation into atomic, testable tasks.

**Deliverable**: `tasks.md` (generated by `/sp.tasks` command, NOT by this plan)

**Expected Task Categories**:
1. **Configuration Tasks**: Add CORS_ORIGINS to config.py, update .env.example
2. **Middleware Tasks**: Add CORSMiddleware to main.py with explicit parameters
3. **Validation Tasks**: Add origin URL validation and logging
4. **Testing Tasks**: Create pytest tests for CORS configuration, manual browser tests
5. **Documentation Tasks**: Update README with CORS setup instructions

## Implementation Strategy

### Approach

This is a **configuration-focused** implementation with minimal code changes. The strategy is:

1. **Leverage FastAPI Built-ins**: Use `fastapi.middleware.cors.CORSMiddleware` without custom implementations
2. **Environment-Driven**: All configuration comes from environment variables, no hardcoded values
3. **Explicit Over Implicit**: Explicitly list allowed headers and methods rather than using wildcards
4. **Fail-Safe Defaults**: If configuration is missing, default to secure behavior (no origins allowed) with clear logging

### Key Integration Points

1. **`backend/src/config.py`**: Add `CORS_ORIGINS` environment variable loading with validation
2. **`backend/src/main.py`**: Add CORSMiddleware after FastAPI app creation, before route registration
3. **`backend/.env.example`**: Document CORS_ORIGINS format for developers

### Testing Strategy

1. **Unit Tests** (`tests/test_cors.py`):
   - Test origin parsing from environment variable
   - Test validation of malformed URLs
   - Test default behavior when CORS_ORIGINS is not set

2. **Integration Tests** (`tests/integration/test_cors_integration.py`):
   - Test preflight OPTIONS requests return correct headers
   - Test actual requests include Access-Control-Allow-Origin header
   - Test requests from disallowed origins are blocked by browser

3. **Manual Browser Tests** (documented in `quickstart.md`):
   - Start backend with CORS_ORIGINS=http://localhost:3000
   - Start frontend on localhost:3000
   - Verify no CORS errors in browser console
   - Verify API calls succeed with Authorization header
   - Test with frontend on different port (should fail)

### Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Wildcard (*) accidentally used | High - Security vulnerability | Explicit validation in config.py; code review checklist |
| CORS_ORIGINS not set in production | High - Frontend cannot connect | Fail-safe default with clear error logging; deployment checklist |
| Multiple origins parsed incorrectly | Medium - Some environments fail | Unit tests for comma-separated parsing; validation logging |
| Preflight requests fail | Medium - Complex requests blocked | Integration tests for OPTIONS requests; browser DevTools verification |
| CORS headers missing on errors | Low - Error responses blocked | Test error responses include CORS headers |

## Success Criteria Mapping

| Success Criterion | Verification Method | Phase |
|-------------------|---------------------|-------|
| SC-001: No CORS errors in browser console | Manual browser test with frontend | Phase 2 (Implementation) |
| SC-002: All HTTP methods work | Integration tests + browser test | Phase 2 (Implementation) |
| SC-003: Authorization header accepted | Integration test with JWT token | Phase 2 (Implementation) |
| SC-004: Configuration via environment variable | Unit test + manual verification | Phase 2 (Implementation) |
| SC-005: Backend starts successfully | Startup test + manual verification | Phase 2 (Implementation) |
| SC-006: Proper CORS headers in responses | Browser DevTools + integration test | Phase 2 (Implementation) |
| SC-007: No wildcard values used | Code review + unit test validation | Phase 2 (Implementation) |
| SC-008: Disallowed origins blocked | Manual browser test from different origin | Phase 2 (Implementation) |

## Dependencies and Prerequisites

### External Dependencies
- FastAPI 0.104.1 (already installed) - includes CORSMiddleware
- python-dotenv 1.0.0 (already installed) - for environment variable loading
- Frontend application from Phase 3 (already implemented) - for integration testing

### Internal Dependencies
- Phase 2 backend with JWT authentication (already implemented)
- Existing API endpoints (already implemented)
- Environment variable infrastructure (already implemented)

### Assumptions
- Backend runs on default port 8000
- Frontend runs on port 3000 during development
- HTTPS will be used in production (HTTP acceptable for localhost development)
- Better Auth provides JWT tokens in standard format

## Next Steps

1. **Run `/sp.tasks`**: Generate detailed task breakdown from this plan
2. **Review Tasks**: Ensure all tasks are atomic and testable
3. **Run `/sp.implement`**: Execute tasks in dependency order
4. **Manual Verification**: Test with browser after implementation
5. **Create PR**: Document CORS configuration in PR description

## Notes

- This is a **backend-only** change. No frontend modifications are required.
- CORS configuration is **environment-specific**. Development uses localhost:3000, production will use actual domain.
- The implementation is **non-breaking**. Existing API functionality remains unchanged.
- CORS middleware adds **minimal overhead** (<5ms per request for header processing).
- This feature **unblocks Phase 3 frontend integration** by eliminating CORS errors.
