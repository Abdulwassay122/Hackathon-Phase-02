# Implementation Plan: Backend Authentication Endpoints

**Branch**: `001-backend-auth-endpoints` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-auth-endpoints/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement authentication endpoints in the FastAPI backend to enable user registration and login. The backend currently has JWT verification capabilities but cannot create users or issue tokens. This feature adds a User model to the database, implements POST /api/auth/signup and POST /api/auth/login endpoints, securely hashes passwords using bcrypt, and generates JWT tokens compatible with the existing verification middleware. This resolves the authentication architecture mismatch where the frontend uses Better Auth but has no backend endpoints to support the authentication flow.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLModel, passlib[bcrypt] (password hashing), PyJWT (JWT generation - already installed)
**Storage**: Neon Serverless PostgreSQL (already configured via DATABASE_URL)
**Testing**: pytest (existing test infrastructure in backend/tests/)
**Target Platform**: Linux server (web backend API)
**Project Type**: Web application (backend component)
**Performance Goals**: <2 seconds for signup, <1 second for login (per spec success criteria)
**Constraints**: Must use existing BETTER_AUTH_SECRET for JWT signing, must use HS256 algorithm, must be compatible with existing JWT verification middleware in auth/jwt_handler.py, User ID must be integer to match Task model's user_id foreign key
**Scale/Scope**: Small to medium scale todo application (estimated <10k users initially), 2 new endpoints (/api/auth/signup, /api/auth/login), 1 new model (User), password hashing must be bcrypt with cost factor 12

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Correctness of Data Modeling and API Behavior
✅ **PASS** - User model will be precisely defined with email (unique), password_hash, name, id, timestamps. Auth endpoints will have deterministic behavior (signup creates user + returns token, login verifies credentials + returns token).

### Principle II: Clear Separation of Concerns
✅ **PASS** - User model in `backend/src/models/user_model.py`, auth endpoints in `backend/src/api/auth_routes.py`, password hashing utility in `backend/src/auth/password.py`, JWT generation in existing `backend/src/auth/jwt_handler.py`. Clear separation between API layer (routes), business logic (password verification), and data layer (User model).

### Principle III: Deterministic and Reproducible Backend Behavior
✅ **PASS** - Auth endpoints will produce consistent results: same credentials always produce same outcome (success/failure). Password hashing uses bcrypt with fixed cost factor (12). JWT tokens have deterministic structure with user ID in "sub" claim. All behavior testable via HTTP requests.

### Principle IV: Spec-Driven, Agentic Implementation
✅ **PASS** - Following spec-driven workflow: spec.md created → plan.md (this file) → tasks.md → implementation via agents. No manual coding.

### Principle V: Comprehensive Testability and Verification
✅ **PASS** - Both endpoints testable via HTTP POST requests. Signup: POST with email/password/name → verify 201 + token returned. Login: POST with email/password → verify 200 + token returned. Token validity testable by using it with existing protected endpoints. All functionality verifiable without frontend.

### Principle VI: RESTful API Compliance
✅ **PASS** - POST /api/auth/signup (201 Created on success), POST /api/auth/login (200 OK on success). Proper HTTP status codes: 400 for validation errors, 401 for invalid credentials, 409 for duplicate email. JSON request/response bodies with Content-Type: application/json.

### Principle VII: Authentication and Security
✅ **PASS** - Core focus of this feature. Implements user creation and JWT token issuance. Passwords hashed with bcrypt (industry standard). JWT tokens compatible with existing verification middleware. User isolation enforced (user_id in token matches Task ownership). No plaintext passwords stored. Tokens include expiration (24 hours).

### Principle VIII: Frontend Integration and User Experience
⚠️ **DEFERRED** - This is a backend-only feature (Phase 2 of project). Frontend integration will happen in Phase 3. Backend provides the necessary endpoints for Better Auth integration but does not implement frontend components.

**Overall Assessment**: ✅ All applicable principles satisfied. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-auth-endpoints/
├── spec.md              # Feature specification (already exists)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── signup.yaml      # POST /api/auth/signup OpenAPI spec
│   └── login.yaml       # POST /api/auth/login OpenAPI spec
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task_model.py      # Existing
│   │   ├── user_model.py      # NEW - User SQLModel
│   │   └── __init__.py
│   ├── services/
│   │   ├── task_service.py    # Existing
│   │   └── __init__.py
│   ├── api/
│   │   ├── task_routes.py     # Existing
│   │   ├── auth_routes.py     # NEW - Signup/Login endpoints
│   │   └── __init__.py
│   ├── auth/
│   │   ├── jwt_handler.py     # Existing - JWT verification
│   │   ├── password.py        # NEW - Password hashing utilities
│   │   ├── dependencies.py    # Existing
│   │   └── __init__.py
│   ├── database/
│   │   ├── database.py        # Existing
│   │   ├── init_db.py         # Existing - may need update for User table
│   │   └── __init__.py
│   ├── config.py              # Existing - CORS config
│   ├── logging_config.py      # Existing
│   ├── main.py                # Existing - will register auth_routes
│   └── __init__.py
└── tests/
    ├── contract/              # Existing structure
    ├── integration/           # Existing structure
    └── unit/                  # Existing structure

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: Web application structure (Option 2) with backend/frontend separation. This feature modifies only the backend component. New files: `backend/src/models/user_model.py`, `backend/src/api/auth_routes.py`, `backend/src/auth/password.py`. Modified files: `backend/src/main.py` (register auth routes), potentially `backend/src/auth/jwt_handler.py` (add token generation function if not present).

## Complexity Tracking

**No violations requiring justification.**

All constitution principles are satisfied by this design:
- Clear separation of concerns (User model, auth routes, password utilities)
- RESTful API compliance (proper HTTP methods and status codes)
- Security best practices (bcrypt hashing, JWT tokens, user isolation)
- Testability (all endpoints testable via HTTP requests)
- Spec-driven implementation (following established workflow)

The design follows existing patterns in the codebase and introduces minimal complexity appropriate for the authentication requirements.

---

## Planning Summary

### Phase 0: Research (Complete)

**Output**: `research.md`

**Key Decisions**:
- Password hashing: passlib with bcrypt, cost factor 12
- JWT generation: PyJWT with HS256, 24-hour expiration
- User model: SQLModel with email (unique), password_hash, name, id (integer), timestamps
- API design: POST /api/auth/signup (201), POST /api/auth/login (200)
- Input validation: Pydantic models with custom validators
- Database migration: SQLModel.metadata.create_all() (existing pattern)
- Error handling: Generic messages for auth failures, specific for validation

**Research Areas Covered**:
1. Password hashing with bcrypt
2. JWT token generation and structure
3. User model design and relationships
4. API endpoint design and contracts
5. Input validation patterns
6. Database migration strategy
7. Error handling and security

### Phase 1: Design & Contracts (Complete)

**Outputs**:
- `data-model.md` - Complete data model specification
- `contracts/signup.yaml` - OpenAPI spec for signup endpoint
- `contracts/login.yaml` - OpenAPI spec for login endpoint
- `quickstart.md` - Testing guide with 6 test scenarios

**Data Model**:
- User entity with 6 fields (id, email, password_hash, name, created_at, updated_at)
- Request schemas: SignupRequest, LoginRequest
- Response schemas: AuthResponse, UserResponse, ErrorResponse
- JWT token structure with sub, email, exp claims

**API Contracts**:
- POST /api/auth/signup: 201 Created, 400 Validation, 409 Conflict, 422 Invalid
- POST /api/auth/login: 200 OK, 401 Unauthorized, 422 Invalid

**Testing Guide**:
- Test 1: User Signup (7 test cases)
- Test 2: User Login (4 test cases)
- Test 3: JWT Token Verification (3 test cases)
- Test 4: User Isolation (2 test cases)
- Test 5: Password Security (2 test cases)
- Test 6: Integration with Existing Features (1 test case)

### Agent Context Update (Complete)

**Updated**: `CLAUDE.md`

**Added Technologies**:
- Python 3.11 (confirmed)
- passlib[bcrypt] (new dependency for password hashing)
- PyJWT (already installed, confirmed usage)
- Neon Serverless PostgreSQL (confirmed)

### Constitution Re-check (Complete)

All principles remain satisfied after design phase:
- ✅ Principle I: Correctness of Data Modeling and API Behavior
- ✅ Principle II: Clear Separation of Concerns
- ✅ Principle III: Deterministic and Reproducible Backend Behavior
- ✅ Principle IV: Spec-Driven, Agentic Implementation
- ✅ Principle V: Comprehensive Testability and Verification
- ✅ Principle VI: RESTful API Compliance
- ✅ Principle VII: Authentication and Security
- ⚠️ Principle VIII: Frontend Integration (deferred to Phase 3)

### Next Steps

**Ready for Phase 2**: Task Breakdown

Run `/sp.tasks` to generate implementation tasks based on this plan.

**Expected Implementation Files**:
- `backend/src/models/user_model.py` (NEW)
- `backend/src/auth/password.py` (NEW)
- `backend/src/api/auth_routes.py` (NEW)
- `backend/src/auth/jwt_handler.py` (MODIFY - add token generation)
- `backend/src/main.py` (MODIFY - register auth routes)
- `backend/src/database/init_db.py` (MODIFY - include User model)

**Dependencies to Install**:
- passlib[bcrypt]

**Testing Strategy**:
- Follow quickstart.md for manual testing
- Unit tests for password hashing and JWT generation
- Integration tests for signup and login endpoints
- Contract tests to verify OpenAPI compliance
