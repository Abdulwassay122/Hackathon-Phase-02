# Implementation Plan: JWT Authentication for Task API

**Branch**: `002-jwt-auth` | **Date**: 2026-02-07 | **Spec**: [specs/002-jwt-auth/spec.md](spec.md)
**Input**: Feature specification from `/specs/002-jwt-auth/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement JWT-based authentication for the FastAPI backend to secure all task API endpoints. The system will verify JWT tokens issued by Better Auth, extract authenticated user identity, and enforce strict user-level data isolation. All existing task endpoints will require valid authentication tokens, and users will only be able to access their own tasks. This implementation adds a security layer to the Phase 1 backend without modifying the database schema.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLModel, PyJWT[crypto]==2.8.0, python-dotenv
**Storage**: Neon Serverless PostgreSQL (existing from Phase 1)
**Testing**: pytest with authentication test coverage
**Target Platform**: Linux server (containerized)
**Project Type**: web (backend API)
**Performance Goals**: <50ms authentication overhead per request, support 1000 concurrent authenticated users
**Constraints**: Stateless authentication (no session storage), JWT tokens issued by Better Auth, shared secret configuration, backward incompatible with Phase 1 (all endpoints now require authentication)
**Scale/Scope**: Multi-user authentication, per-request token verification, user data isolation enforcement

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gates:

- **Correctness of Data Modeling and API Behavior**: ✅ PASS
  - No database schema changes required
  - API behavior remains deterministic with added authentication layer
  - JWT verification follows standard RFC 7519 specifications
  - Error responses match specification exactly (401, 403)

- **Clear Separation of Concerns**: ✅ PASS
  - Authentication logic centralized in dedicated auth module
  - JWT verification separated from business logic
  - FastAPI dependency injection maintains clean separation
  - No authentication logic scattered in route handlers

- **Deterministic and Reproducible Backend Behavior**: ✅ PASS
  - JWT verification produces consistent results
  - Token expiration enforced deterministically
  - User identity extraction follows standard JWT claims
  - All authentication failures return predictable error codes

- **Spec-Driven, Agentic Implementation**: ✅ PASS
  - Implementation follows specification exactly
  - All changes traceable to functional requirements
  - No manual coding outside agent-generated output
  - Research phase completed before implementation

- **Comprehensive Testability and Verification**: ✅ PASS
  - All authentication scenarios testable via HTTP requests
  - Token verification independently testable
  - User isolation verifiable through API calls
  - Contract tests validate OpenAPI specification compliance

- **RESTful API Compliance**: ✅ PASS
  - Proper HTTP status codes (401 Unauthorized, 403 Forbidden)
  - Standard Authorization header usage (Bearer scheme)
  - Error responses follow REST conventions
  - No changes to REST resource structure

- **Authentication and Security**: ✅ PASS
  - Stateless JWT-based authentication implemented
  - User isolation enforced at API level
  - JWT verification centralized and reusable
  - Proper error codes for authentication failures (401/403)
  - Token expiry respected and enforced
  - Backend never trusts user_id from URL without JWT verification
  - All authentication logic testable and auditable

## Project Structure

### Documentation (this feature)

```text
specs/002-jwt-auth/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── openapi.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── auth/                    # NEW: Authentication module
│   │   ├── __init__.py
│   │   ├── jwt_handler.py       # JWT verification logic
│   │   └── dependencies.py      # FastAPI auth dependencies
│   ├── models/
│   │   └── task_model.py        # Existing from Phase 1
│   ├── api/
│   │   └── task_routes.py       # MODIFIED: Add authentication
│   ├── services/
│   │   └── task_service.py      # Existing from Phase 1
│   ├── database/
│   │   └── database.py          # Existing from Phase 1
│   ├── config.py                # MODIFIED: Add JWT config
│   ├── logging_config.py        # Existing from Phase 1
│   └── main.py                  # Existing from Phase 1
└── tests/
    ├── unit/
    │   ├── test_models.py       # Existing from Phase 1
    │   └── test_jwt_handler.py  # NEW: JWT handler tests
    ├── integration/
    │   └── test_api_auth.py     # NEW: Authenticated API tests
    └── contract/
        └── test_contracts.py    # MODIFIED: Add auth tests
```

**Structure Decision**: Web application structure (Option 2) selected to maintain separation between backend and frontend (future phase). Authentication module added as new component within existing backend structure. This aligns with constitutional principle II (Clear Separation of Concerns) by isolating authentication logic in dedicated module.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. All gates passed.

## Phase 0: Research Summary

**Completed**: research.md created with comprehensive findings

**Key Decisions**:
1. **JWT Library**: PyJWT selected over python-jose and authlib for simplicity, performance, and Better Auth compatibility
2. **Authentication Pattern**: FastAPI dependency injection chosen over middleware for granular control and testability
3. **Token Verification**: Centralized JWT handler with composable dependencies

**Critical Discovery**: Better Auth is primarily designed for cookie-based authentication, not standalone JWT bearer tokens. Implementation must verify Better Auth configuration supports JWT token issuance for API authentication.

## Phase 1: Design Summary

**Completed**: data-model.md, contracts/openapi.yaml, quickstart.md created

**Data Model**:
- No new database entities required
- Authentication Token (transient, not stored)
- User Identity (derived from JWT)
- Protected Resource (existing Task entity with added protection)

**API Contracts**:
- All endpoints require Bearer authentication
- New security scheme: BearerAuth (JWT)
- Error responses: 401 Unauthorized, 403 Forbidden
- User_id automatically derived from JWT token

**Integration Scenarios**:
- Token extraction from Authorization header
- JWT signature verification
- User identity extraction from sub claim
- Ownership verification for all operations
- Automatic user scoping for queries

## Implementation Phases

### Phase 1: Authentication Infrastructure (Foundation)

**Goal**: Create JWT verification infrastructure

**Tasks**:
- Create auth module structure
- Implement JWTHandler class for token verification
- Create FastAPI authentication dependencies
- Update config.py with JWT settings
- Add PyJWT to requirements.txt

**Deliverables**:
- `backend/src/auth/jwt_handler.py`
- `backend/src/auth/dependencies.py`
- `backend/src/auth/__init__.py`
- Updated `backend/src/config.py`
- Updated `backend/requirements.txt`

### Phase 2: Endpoint Protection (Core Security)

**Goal**: Protect all task endpoints with authentication

**Tasks**:
- Update task routes to require authentication
- Remove user_id from URL paths (derive from token)
- Implement ownership verification
- Update error handling for auth failures
- Ensure user data isolation in queries

**Deliverables**:
- Updated `backend/src/api/task_routes.py`
- Updated `backend/src/services/task_service.py` (if needed)

### Phase 3: Testing and Validation (Quality Assurance)

**Goal**: Comprehensive test coverage for authentication

**Tasks**:
- Create unit tests for JWT handler
- Create integration tests for authenticated endpoints
- Update contract tests with authentication
- Test user isolation enforcement
- Performance testing for auth overhead

**Deliverables**:
- `backend/tests/unit/test_jwt_handler.py`
- `backend/tests/integration/test_api_auth.py`
- Updated `backend/tests/contract/test_contracts.py`

## Dependencies

**External Dependencies**:
- Better Auth JWT token issuance (frontend/auth service)
- Shared secret (BETTER_AUTH_SECRET) configuration
- Phase 1 backend implementation (001-todo-backend)

**Internal Dependencies**:
- Existing Task model and database schema
- Existing task service layer
- Existing database connection management

## Risks and Mitigations

**Risk 1: Better Auth JWT Token Format**
- **Impact**: High - Implementation depends on token structure
- **Mitigation**: Document expected token format, implement flexible extraction logic
- **Contingency**: Support multiple token formats (standard and nested)

**Risk 2: Shared Secret Management**
- **Impact**: High - Security vulnerability if secret compromised
- **Mitigation**: Use environment variables, document secret rotation procedure
- **Contingency**: Implement secret rotation support

**Risk 3: Performance Overhead**
- **Impact**: Medium - Token verification on every request
- **Mitigation**: Use PyJWT for fast verification, avoid database lookups
- **Contingency**: Implement caching if needed (though stateless preferred)

**Risk 4: Backward Compatibility**
- **Impact**: High - Phase 1 clients will break
- **Mitigation**: Document breaking changes, provide migration guide
- **Contingency**: Implement optional authentication mode for transition period

## Success Metrics

- All task endpoints require valid JWT tokens (100% coverage)
- Authentication overhead <50ms per request
- Zero cross-user data access incidents
- All tests passing (unit, integration, contract)
- Token verification success rate >99.9%
- No authentication logic scattered outside auth module

## Next Steps

After completing this plan:
1. Run `/sp.tasks` to generate detailed implementation tasks
2. Review tasks.md for task breakdown and dependencies
3. Execute implementation via `/sp.implement`
4. Verify all tests pass
5. Update documentation with any implementation discoveries
