---
id: 0001
title: JWT authentication specification
stage: spec
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 002-jwt-auth
branch: 002-jwt-auth
user: user
command: /sp.specify
labels: ["authentication", "jwt", "security", "better-auth", "phase-2", "stateless"]
links:
  spec: specs/002-jwt-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-jwt-auth/spec.md
  - specs/002-jwt-auth/checklists/requirements.md
tests:
  - N/A (specification stage)
---

## Prompt

Todo Full-Stack Web Application – Phase 2

Objective:
Secure the FastAPI backend by integrating JWT-based authentication issued by Better Auth and enforce strict user-level data access.

Target audience:
Evaluators assessing authentication architecture and cross-service security design.

Scope:
- Configure Better Auth to issue JWT tokens
- Define shared secret via BETTER_AUTH_SECRET
- Implement FastAPI middleware for JWT verification
- Extract authenticated user identity from token
- Enforce task ownership across all API routes

Authentication Flow:
1. User logs in via frontend using Better Auth
2. Better Auth issues JWT
3. Frontend attaches JWT in Authorization header
4. Backend verifies JWT signature and expiry
5. Backend matches token user with requested user_id
6. Backend filters queries by authenticated user

Behavior changes:
- All API endpoints require Authorization: Bearer <token>
- Requests without valid JWT return 401 Unauthorized
- user_id in URL must match authenticated user

Success criteria:
- JWT verification works consistently
- User cannot access or modify another user's tasks
- Token expiry invalidates access automatically
- Backend remains stateless

Not building:
- OAuth providers
- Role-based access control
- Refresh token rotation logic
- Frontend UI changes

## Response snapshot

Successfully created comprehensive JWT authentication specification for Phase 2.

**Feature**: 002-jwt-auth (JWT Authentication for Task API)

**User Stories Created** (3 prioritized stories):
1. **P1 - Protected API Access**: Foundation security layer requiring valid tokens for all endpoints
2. **P2 - User Data Isolation**: Enforce ownership verification to prevent IDOR vulnerabilities
3. **P3 - Token Expiry Enforcement**: Respect token expiration for security hardening

**Functional Requirements**: 12 requirements covering:
- Token validation and signature verification
- User identity extraction and matching
- Data isolation through query filtering
- Proper error codes (401/403)
- Stateless authentication
- Security logging

**Success Criteria**: 7 measurable, technology-agnostic outcomes including:
- 100% rejection of unauthenticated requests
- 0% cross-user data access
- <50ms authentication overhead
- Consistent token verification across endpoints

**Key Entities**: Authentication Token, User Identity, Protected Resource

**Assumptions Documented**: JWT token format, shared secret management, user identity mapping

**Dependencies Identified**: Phase 1 backend, Better Auth configuration, JWT library

**Out of Scope**: OAuth, RBAC, refresh tokens, frontend changes, user management

**Validation**: All checklist items passed - specification is complete and ready for planning

## Outcome

- ✅ Impact: Created production-ready specification for JWT authentication layer aligned with constitutional security principles
- 🧪 Tests: N/A (specification stage - tests will be defined in planning/tasks)
- 📁 Files: Created spec.md and requirements checklist
- 🔁 Next prompts: Run /sp.plan to create implementation plan for JWT authentication
- 🧠 Reflection: Specification is comprehensive with clear security boundaries, measurable outcomes, and proper prioritization. No clarifications needed as all requirements are testable and unambiguous. Successfully avoided implementation details while maintaining clarity.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Specification quality checklist PASS (all 14 items passed)
- Prompt variant (if applicable): Standard /sp.specify workflow with security focus
- Next experiment (smallest change to try): Consider whether token refresh/renewal should be added to scope in future iterations
