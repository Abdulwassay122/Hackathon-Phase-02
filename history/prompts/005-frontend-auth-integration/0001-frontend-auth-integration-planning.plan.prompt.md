---
id: 0001
title: frontend-auth-integration-planning
stage: plan
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 005-frontend-auth-integration
branch: 005-frontend-auth-integration
user: user
command: /sp.plan
labels: ["frontend", "authentication", "planning", "nextjs", "jwt", "react", "localStorage"]
links:
  spec: specs/005-frontend-auth-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-frontend-auth-integration/plan.md
  - specs/005-frontend-auth-integration/research.md
  - specs/005-frontend-auth-integration/data-model.md
  - specs/005-frontend-auth-integration/contracts/signup.yaml
  - specs/005-frontend-auth-integration/contracts/login.yaml
  - specs/005-frontend-auth-integration/quickstart.md
  - CLAUDE.md
tests:
  - Manual testing procedures in quickstart.md (24 test cases across 6 categories)
---

## Prompt

/sp.plan

Execute implementation planning workflow for frontend authentication integration feature (005-frontend-auth-integration) following the plan template structure.

## Response snapshot

**Planning Completed Successfully - All Design Artifacts Created**

Completed comprehensive implementation planning for frontend authentication integration with FastAPI backend.

### Phase 0: Research (Complete)

Created research.md with 6 research questions answered:

1. **Next.js 16+ App Router Authentication Patterns**
   - Decision: Hybrid approach with Client Components, React Context, Next.js Middleware, and custom hooks
   - Rationale: Balances security, UX, and Next.js 16+ best practices

2. **JWT Token Storage Best Practices**
   - Decision: localStorage with XSS mitigation strategies
   - Rationale: Meets spec requirements, simple implementation, persists across sessions

3. **React Context API for Authentication State**
   - Decision: Dedicated AuthContext with AuthProvider component
   - Rationale: Built-in, clean API, works well with App Router

4. **HTTP Client Configuration**
   - Decision: Native fetch API with custom wrapper function
   - Rationale: No dependencies, automatic Authorization header attachment, global 401 handling

5. **Form Validation Patterns**
   - Decision: Dual validation (client-side for UX, backend for security)
   - Rationale: Immediate feedback + security enforcement

6. **Better Auth Removal Strategy**
   - Decision: Complete removal with systematic replacement
   - Rationale: Spec requirement, simpler architecture, reduces dependencies

### Phase 1: Design & Contracts (Complete)

Created comprehensive design artifacts:

1. **data-model.md**: 3 key entities defined
   - JWT Token (localStorage persistence, 24-hour expiration)
   - Authentication State (React Context with isAuthenticated, user, token, loading, error)
   - Form State (ephemeral component state for signup/login forms)

2. **contracts/signup.yaml**: OpenAPI specification for POST /api/auth/signup
   - Request schema: email, password, name with validation rules
   - Response: 201 Created with access_token, token_type, user
   - Error scenarios: 400 (validation), 409 (duplicate email), 422 (invalid format), 500 (server error)
   - Frontend implementation notes for each requirement

3. **contracts/login.yaml**: OpenAPI specification for POST /api/auth/login
   - Request schema: email, password
   - Response: 200 OK with access_token, token_type, user
   - Error scenarios: 401 (invalid credentials), 422 (missing fields), 500 (server error)
   - Security considerations (generic error messages prevent user enumeration)

4. **quickstart.md**: Manual testing guide with 24 test cases
   - Test 1: User Signup Flow (7 test cases)
   - Test 2: User Login Flow (4 test cases)
   - Test 3: Session Persistence (5 test cases)
   - Test 4: API Request Authorization (3 test cases)
   - Test 5: Edge Cases and Error Scenarios (4 test cases)
   - Test 6: Cross-Browser Compatibility (3 test cases)

5. **CLAUDE.md**: Updated agent context
   - Added JavaScript/TypeScript with Next.js 16+ (App Router)
   - Added React 18+, fetch API
   - Added Browser localStorage for JWT token persistence

### Constitution Check: All Requirements Met

**Pre-Design Evaluation**: ✅ PASS
- Spec-driven methodology followed
- Authentication and security principles satisfied
- Frontend integration principles satisfied
- Technology stack compliance verified

**Post-Design Re-evaluation**: ✅ PASS
- All design artifacts follow constitutional principles
- JWT token storage strategy includes XSS mitigation
- Authorization header pattern documented
- Generic error messages prevent user enumeration
- Client-side validation explicitly marked as UX-only
- Better Auth removal strategy documented
- REST-only communication (no WebSockets)

### Project Structure

Frontend structure defined:
```
frontend/src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Authentication route group
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   └── (protected)/       # Protected routes
├── components/auth/       # Auth components
├── contexts/AuthContext.tsx
├── hooks/useAuth.ts
├── lib/
│   ├── api.ts            # API client with Authorization header
│   └── auth.ts           # Token storage utilities
└── middleware.ts         # Route protection
```

### Key Technical Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Architecture | Client Components + Context API + Middleware | Security + UX + Next.js best practices |
| Token Storage | localStorage with XSS mitigation | Spec requirement, simple, persistent |
| State Management | React Context API | Built-in, sufficient for auth state |
| HTTP Client | fetch API with wrapper | No dependencies, meets requirements |
| Validation | Dual (client + backend) | UX enhancement + security |
| Better Auth | Complete removal | Spec requirement, simpler |

### Implementation Risks Identified

1. XSS Vulnerabilities (Medium) - Mitigated with CSP headers, input sanitization, HTTPS
2. Token Expiration Edge Cases (Low) - Mitigated with global 401 handler
3. Browser Compatibility (Low) - Mitigated with localStorage detection
4. State Synchronization (Low) - Mitigated with token validation on load

## Outcome

- ✅ Impact: Complete implementation plan created with all design artifacts. Research findings documented for 6 key areas. Data model defined with 3 entities. API contracts specified for signup and login endpoints. Manual testing guide created with 24 test cases. Agent context updated with new technologies. All constitutional requirements verified and satisfied.
- 🧪 Tests: Manual testing procedures defined in quickstart.md - 24 test cases covering signup flow (7 tests), login flow (4 tests), session persistence (5 tests), API authorization (3 tests), edge cases (4 tests), and cross-browser compatibility (3 tests)
- 📁 Files: 7 files created - plan.md (implementation plan), research.md (research findings), data-model.md (3 entities), contracts/signup.yaml (OpenAPI spec), contracts/login.yaml (OpenAPI spec), quickstart.md (24 test cases), CLAUDE.md (updated agent context)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks breakdown. After tasks.md is created, run `/sp.implement` to execute implementation. Follow quickstart.md for manual testing after implementation.
- 🧠 Reflection: Planning phase completed successfully following spec-driven methodology. All research questions answered with clear decisions, rationale, and alternatives considered. Data model defines clear separation between persistent storage (localStorage), runtime state (React Context), and ephemeral form data. API contracts provide complete specifications with all error scenarios documented. Manual testing guide covers all user stories and edge cases. Constitution check performed twice (pre-design and post-design) confirming all requirements met. Key architectural decision: hybrid approach using Client Components for interactivity, React Context for state management, and Next.js Middleware for route protection. Better Auth removal strategy documented with systematic replacement plan. Ready to proceed with task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully without errors
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all principles satisfied), Design Completeness - PASS (all required artifacts created), Technical Decisions - PASS (all decisions documented with rationale)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Generate tasks.md via /sp.tasks to break down implementation into actionable tasks organized by user story
