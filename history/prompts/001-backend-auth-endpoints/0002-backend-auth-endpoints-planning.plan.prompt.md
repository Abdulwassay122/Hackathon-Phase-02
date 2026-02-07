---
id: 0002
title: backend-auth-endpoints-planning
stage: plan
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 001-backend-auth-endpoints
branch: 001-backend-auth-endpoints
user: user
command: /sp.plan
labels: ["backend", "authentication", "planning", "jwt", "password-hashing"]
links:
  spec: specs/001-backend-auth-endpoints/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-backend-auth-endpoints/plan.md
  - specs/001-backend-auth-endpoints/research.md
  - specs/001-backend-auth-endpoints/data-model.md
  - specs/001-backend-auth-endpoints/contracts/signup.yaml
  - specs/001-backend-auth-endpoints/contracts/login.yaml
  - specs/001-backend-auth-endpoints/quickstart.md
  - CLAUDE.md
tests:
  - Quickstart guide includes 19 test cases across 6 test scenarios
---

## Prompt

/sp.plan

Execute implementation planning workflow for backend authentication endpoints feature (001-backend-auth-endpoints).

## Response snapshot

**Planning Workflow Completed Successfully**

Executed complete planning workflow with Phase 0 (Research) and Phase 1 (Design & Contracts):

### Phase 0: Research (research.md)

**7 Research Areas Documented**:
1. Password Hashing with bcrypt - Decision: passlib library with bcrypt algorithm, cost factor 12
2. JWT Token Generation - Decision: PyJWT with HS256, 24-hour expiration, compatible with existing verification
3. User Model Design - Decision: SQLModel with email (unique), password_hash, name, id (integer), timestamps
4. API Endpoint Design - Decision: POST /api/auth/signup (201), POST /api/auth/login (200), JSON request/response
5. Input Validation - Decision: Pydantic models with custom validators for password complexity
6. Database Migration Strategy - Decision: SQLModel.metadata.create_all() (existing pattern)
7. Error Handling and Security - Decision: Generic messages for auth failures, specific for validation

**Key Technical Decisions**:
- passlib[bcrypt] for password hashing (industry standard, OWASP recommended)
- bcrypt cost factor 12 (~300ms per hash, good security/performance balance)
- JWT tokens with sub (user ID), email, exp (24 hours) claims
- User model with integer ID for Task model compatibility
- Generic error messages for login failures (prevent user enumeration)
- Constant-time password comparison (handled by passlib internally)

### Phase 1: Design & Contracts

**data-model.md Created** (comprehensive data model specification):
- User entity with 6 fields and validation rules
- Request schemas: SignupRequest (with password validators), LoginRequest
- Response schemas: AuthResponse, UserResponse, ErrorResponse
- JWT token structure documented
- State transitions for signup and login flows
- Data flow diagrams
- Security considerations (password storage, token security, input validation)
- Database schema (PostgreSQL DDL)

**contracts/signup.yaml Created** (OpenAPI 3.0.3 specification):
- POST /api/auth/signup endpoint
- Request schema with email, password, name
- Response schemas: 201 Created, 400 Validation, 409 Conflict, 422 Invalid
- Examples for valid and invalid requests
- Detailed error response formats

**contracts/login.yaml Created** (OpenAPI 3.0.3 specification):
- POST /api/auth/login endpoint
- Request schema with email, password
- Response schemas: 200 OK, 401 Unauthorized, 422 Invalid
- Examples for valid and invalid credentials
- Generic error messages for security

**quickstart.md Created** (comprehensive testing guide):
- 6 test scenarios with 19 total test cases
- Test 1: User Signup (7 cases - valid, duplicate, weak password, etc.)
- Test 2: User Login (4 cases - valid, invalid password, non-existent email, missing field)
- Test 3: JWT Token Verification (3 cases - decode, use with protected endpoint, expiration)
- Test 4: User Isolation (2 cases - create second user, cross-user access)
- Test 5: Password Security (2 cases - database hashing, API exposure)
- Test 6: Integration (1 case - complete user flow)
- Troubleshooting section with 4 common issues
- Success criteria checklist with 16 items

**CLAUDE.md Updated** (agent context):
- Added passlib[bcrypt] as new dependency
- Confirmed Python 3.11, FastAPI, SQLModel, PyJWT
- Confirmed Neon Serverless PostgreSQL

### Constitution Check

**All Principles Satisfied**:
- ✅ Principle I: Correctness of Data Modeling and API Behavior
- ✅ Principle II: Clear Separation of Concerns
- ✅ Principle III: Deterministic and Reproducible Backend Behavior
- ✅ Principle IV: Spec-Driven, Agentic Implementation
- ✅ Principle V: Comprehensive Testability and Verification
- ✅ Principle VI: RESTful API Compliance
- ✅ Principle VII: Authentication and Security (core focus)
- ⚠️ Principle VIII: Frontend Integration (deferred to Phase 3)

**No violations requiring justification.**

### Project Structure

**New Files to Create**:
- backend/src/models/user_model.py (User SQLModel)
- backend/src/auth/password.py (password hashing utilities)
- backend/src/api/auth_routes.py (signup/login endpoints)

**Files to Modify**:
- backend/src/auth/jwt_handler.py (add token generation function)
- backend/src/main.py (register auth routes)
- backend/src/database/init_db.py (include User model)

**New Dependency**:
- passlib[bcrypt]

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation. All technical decisions documented with rationale. Data model, API contracts, and testing guide created. Agent context updated. Ready for /sp.tasks to generate implementation task breakdown.
- 🧪 Tests: 19 test cases documented in quickstart.md covering signup, login, token verification, user isolation, password security, and integration scenarios.
- 📁 Files: 7 files created/modified - plan.md, research.md, data-model.md, signup.yaml, login.yaml, quickstart.md, CLAUDE.md
- 🔁 Next prompts: `/sp.tasks` to generate implementation task breakdown, then implement via agents (auth-agent, fastapi-backend-manager)
- 🧠 Reflection: Planning phase successfully completed with comprehensive research and design artifacts. All technical decisions justified with alternatives considered. Password hashing uses industry-standard bcrypt with appropriate cost factor. JWT tokens designed for compatibility with existing verification middleware. User model integrates seamlessly with existing Task model (integer ID foreign key). API design follows RESTful conventions with proper status codes. Security considerations addressed (generic error messages, password hashing, token expiration). Testing guide provides clear verification path with 19 test cases. No constitution violations. Ready for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow completed successfully without issues
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all applicable principles satisfied, no violations)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Proceed with /sp.tasks to generate implementation task breakdown, then use auth-agent and fastapi-backend-manager for implementation
