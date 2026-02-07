---
id: 0002
title: phase-1-design-contracts
stage: plan
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 003-todo-frontend
branch: 003-todo-frontend
user: user
command: /sp.plan (continuation)
labels: ["frontend", "nextjs", "design", "contracts", "api-client", "data-model", "phase-1"]
links:
  spec: specs/003-todo-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-todo-frontend/data-model.md
  - specs/003-todo-frontend/quickstart.md
  - specs/003-todo-frontend/contracts/api-client.md
tests:
  - N/A (design phase - no code implementation)
---

## Prompt

(Continuation from previous session - user provided empty messages to continue workflow)

Context: Completed Phase 0 (research.md) in previous session. Now continuing with Phase 1: Design & Contracts for the todo-frontend feature (003-todo-frontend).

Task: Create the remaining Phase 1 design artifacts:
1. data-model.md - TypeScript type definitions
2. quickstart.md - Setup and development instructions
3. contracts/api-client.md - API client interface specification

## Response snapshot

Completed Phase 1: Design & Contracts for todo-frontend feature

**Files Created**:

1. **data-model.md** (comprehensive TypeScript type definitions)
   - Core types: Task, TaskCreate, TaskUpdate, UserSession
   - Authentication payloads: SignUpRequest, SignInRequest, AuthResponse
   - API response types: ApiResponse<T>, ApiError
   - Component state types: LoadingState, TaskFormState, TaskListState
   - Validation rules with VALIDATION_RULES constant
   - Type guards: isApiError(), isValidTask()
   - API endpoints and HTTP status constants
   - Notes on data ownership, type safety, validation, null vs undefined, date handling

2. **quickstart.md** (setup and development guide)
   - Prerequisites: Node.js 18+, npm 9+, backend API running
   - Project setup: create-next-app with TypeScript, App Router, Tailwind
   - Dependency installation: better-auth, zod, date-fns
   - Environment configuration: .env.local with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET
   - Project structure: app/ directory with route groups, components/, lib/, types/
   - Development workflow: start backend, start frontend dev server, hot reload
   - Testing integration: verify backend connection, test auth flow, test task operations, test responsive design
   - Common issues and solutions: connection errors, JWT issues, module errors, environment variables, port conflicts
   - Browser DevTools tips: Network, Console, Application, React DevTools tabs

3. **contracts/api-client.md** (API client interface specification)
   - Core requirements: centralized config, automatic JWT injection, auth error handling, type safety, error consistency
   - Base APIClient interface: request(), get(), post(), put(), patch(), delete()
   - TaskAPI methods: list(), get(), create(), update(), delete(), toggleComplete()
   - AuthAPI methods: signUp(), signIn(), signOut(), getSession()
   - Request flow diagrams: standard request, authentication error, network error
   - APIError class with statusCode, code, detail fields
   - Error response mapping table (200, 201, 400, 401, 403, 404, 500, network errors)
   - JWT token management: retrieval, attachment, expiration handling
   - Request headers: Content-Type, Authorization
   - Response handling: success, error, network errors
   - Usage examples: initialize client, use in components
   - Security considerations: token storage, HTTPS, CORS, input validation
   - Performance considerations: caching, deduplication, retry logic

**Design Decisions**:
- TypeScript for type safety across all frontend code
- Centralized API client pattern to avoid duplicating JWT logic
- Better Auth integration for session management
- React hooks for state management (no Redux)
- Mobile-first responsive design approach
- Client-side validation for UX only (backend enforces security)

**Phase 1 Complete**: All design artifacts created. Ready to proceed to Phase 2: Task Breakdown.

## Outcome

- ✅ Impact: Phase 1 design artifacts complete. Provides comprehensive technical foundation for implementation including type definitions, setup instructions, and API client contracts. All design decisions align with constitution principles (Next.js 16+ App Router, Better Auth, REST-only, clear separation of concerns).
- 🧪 Tests: N/A (design phase - no code implementation yet)
- 📁 Files: 3 files created (data-model.md, quickstart.md, contracts/api-client.md)
- 🔁 Next prompts: `/sp.tasks` to generate task breakdown for implementation, or continue with any additional design refinements if needed
- 🧠 Reflection: Design phase successfully completed with comprehensive artifacts. data-model.md provides all TypeScript types mirroring backend contracts. quickstart.md gives clear setup path from zero to running dev environment. contracts/api-client.md defines precise interface for centralized API communication with JWT injection and error handling. All artifacts maintain technology-agnostic business focus while providing necessary technical detail for implementation. No architectural decisions requiring ADR documentation - all choices follow constitution mandates (Next.js App Router, Better Auth, REST).

## Evaluation notes (flywheel)

- Failure modes observed: None - design phase completed successfully without issues
- Graders run and results (PASS/FAIL): Manual review - PASS (all Phase 1 artifacts complete and comprehensive)
- Prompt variant (if applicable): Standard /sp.plan workflow continuation
- Next experiment (smallest change to try): Proceed to task breakdown phase with `/sp.tasks` to generate actionable implementation tasks
