---
id: 0001
title: Add authentication security principle
stage: constitution
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 001-todo-backend
user: user
command: /sp.constitution
labels: ["constitution", "security", "authentication", "jwt", "phase-2", "better-auth"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution updates do not require tests)
---

## Prompt

Project: Todo Full-Stack Web Application – Phase 2 (Authentication & Security)

Core principles:
- Strong user isolation and data protection
- Stateless authentication using JWT
- Explicit trust boundaries between frontend and backend
- Security rules enforced at API level, not UI

Key standards:
- Every protected request must require a valid JWT
- Backend must never trust user_id from URL without verification
- JWT verification logic must be centralized and reusable
- Authentication failures must return proper HTTP errors

Constraints:
- Authentication handled via Better Auth on frontend
- Backend must verify JWT using shared secret
- JWT-based auth only (no sessions, no cookies)
- No manual coding outside agent-generated output

Success criteria:
- Unauthorized requests receive 401 responses
- Users can only access their own tasks
- JWT claims are validated against request context
- Token expiry is respected by backend

## Response snapshot

Successfully updated the project constitution from version 1.0.0 to 1.1.0 (MINOR version bump).

**Added Principle VII: Authentication and Security**
- Establishes strong user isolation and data protection requirements
- Mandates stateless JWT-based authentication
- Defines explicit trust boundaries between frontend and backend
- Requires centralized JWT verification logic
- Specifies proper HTTP error codes for authentication failures (401/403)
- Ensures token expiry enforcement
- Prevents IDOR vulnerabilities by requiring JWT claim verification

**Updated Technology Stack Requirements**
- Changed Better Auth from "for subsequent phases" to active usage
- Clarified: Better Auth (frontend) with JWT verification (backend)

**Updated Development Workflow**
- Added Phase 2: Authentication and security layer (JWT verification, user isolation)
- Clarified phase progression: Phase 1 (backend) → Phase 2 (auth) → Phase 3 (frontend)

**Rationale Provided**
Security cannot be an afterthought. By establishing authentication as a core principle, we ensure that user data isolation, token verification, and trust boundaries are consistently applied across all features. This prevents common security vulnerabilities such as insecure direct object references (IDOR).

**Template Validation**
- ✅ plan-template.md: Constitution Check section will automatically reflect new principle
- ✅ spec-template.md: No changes needed (technology-agnostic)
- ✅ tasks-template.md: No changes needed (already supports security tasks)

## Outcome

- ✅ Impact: Added comprehensive authentication and security principle to constitution, establishing foundation for Phase 2 implementation
- 🧪 Tests: N/A (constitution is governance document)
- 📁 Files: Updated .specify/memory/constitution.md (version 1.0.0 → 1.1.0)
- 🔁 Next prompts: Run /sp.specify to create Phase 2 authentication feature specification based on new constitutional principles
- 🧠 Reflection: MINOR version bump appropriate as this adds a new principle without removing or redefining existing ones. The new principle is declarative, testable, and provides clear rationale for security-first approach.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution validation PASS (no unresolved placeholders, proper version increment, all templates validated)
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): Consider whether authentication principle should be split into separate principles for "Authentication" and "Authorization" in future amendments
