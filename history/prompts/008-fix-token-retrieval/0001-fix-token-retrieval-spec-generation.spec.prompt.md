---
id: 0001
title: fix-token-retrieval-spec-generation
stage: spec
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 008-fix-token-retrieval
branch: 008-fix-token-retrieval
user: system
command: /sp.specify
labels: ["authentication", "frontend", "bug-fix", "jwt", "api-client", "token-retrieval"]
links:
  spec: specs/008-fix-token-retrieval/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-fix-token-retrieval/spec.md
tests:
  - No automated tests (specification phase)
---

## Prompt

Fix Token Retrieval for API Requests - Objective: Fix auth token retrieval by replacing getSession/getToken with direct JWT access. Scope: Stop using getSession() and getToken(), Read JWT from storage (localStorage or cookie), Attach Authorization: Bearer <token> to all task requests. Success criteria: Token is non-null on every request, /api/tasks returns 200 instead of 403

## Response snapshot

Created comprehensive specification for fixing token retrieval in API requests. The spec addresses the issue where getSession/getToken functions are not properly retrieving JWT tokens for API authentication, causing 403 Forbidden errors.

**Key User Stories:**
1. **User Story 1 (P1)**: Authenticated user can view tasks - API requests include proper Authorization header with Bearer token, returning 200 OK instead of 403
2. **User Story 2 (P1)**: Token persists across page refreshes - JWT retrieved from localStorage maintains session without re-login
3. **User Story 3 (P2)**: Expired token handling - System gracefully handles token expiration with proper error handling and redirect

**Functional Requirements:**
- FR-001: Read JWT token directly from localStorage using key "auth-token"
- FR-002: Attach JWT as "Authorization: Bearer <token>" header to all API requests
- FR-003: Stop using getSession() and getToken() functions
- FR-004: Ensure token is non-null before making API requests
- FR-005-007: Handle 401 responses, missing/malformed tokens, and log failures

**Success Criteria:**
- SC-001: 100% of API requests include non-null Authorization header
- SC-002: GET /api/tasks returns 200 OK (not 403 Forbidden)
- SC-003: All CRUD operations succeed with appropriate status codes
- SC-004-006: Token retrieval succeeds, error handling works, no console errors

## Outcome

- ✅ Impact: Complete specification ready for planning phase, clearly defines the token retrieval fix with 3 user stories and 7 functional requirements
- 🧪 Tests: No automated tests (specification phase only)
- 📁 Files: 1 file created (spec.md)
- 🔁 Next prompts: /sp.plan to generate implementation plan
- 🧠 Reflection: Specification addresses root cause (getSession/getToken not working) and provides clear path to fix by reading JWT directly from localStorage

## Evaluation notes (flywheel)

- Failure modes observed: None - specification completed successfully
- Graders run and results (PASS/FAIL): Format validation: PASS (all mandatory sections present), Completeness: PASS (3 user stories with priorities, 7 FRs, 6 SCs)
- Prompt variant (if applicable): Standard /sp.specify workflow
- Next experiment (smallest change to try): Proceed with /sp.plan to design implementation approach
