# Implementation Plan: Fix Token Retrieval for API Requests

**Branch**: `008-fix-token-retrieval` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-fix-token-retrieval/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix authentication token retrieval for API requests by replacing the current `getSession()`/`getToken()` approach with direct JWT access from localStorage. The current implementation fails to retrieve tokens reliably, causing 403 Forbidden errors on `/api/tasks` endpoints. The fix will read the JWT token directly from the "auth-token" key in localStorage and attach it as an Authorization Bearer header to all API requests.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (App Router)
**Primary Dependencies**: Next.js 16+, React 18+, native fetch API
**Storage**: Browser localStorage for JWT token persistence
**Testing**: Manual browser testing (no automated tests requested in spec)
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend-only changes)
**Performance Goals**: Token retrieval <1ms, no impact on API request latency
**Constraints**: Must work with existing AuthContext, must not break current authentication flow
**Scale/Scope**: Single-user browser session, affects all authenticated API requests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Correctness of Data Modeling and API Behavior
✅ **PASS** - No backend changes required. Frontend token retrieval fix ensures correct Authorization headers are sent to backend API.

### Principle II: Clear Separation of Concerns
✅ **PASS** - Fix maintains separation: session.ts handles token storage/retrieval, APIClient handles HTTP communication, AuthContext manages authentication state.

### Principle III: Deterministic and Reproducible Backend Behavior
✅ **PASS** - No backend changes. Backend behavior remains deterministic.

### Principle IV: Spec-Driven, Agentic Implementation
✅ **PASS** - Following spec-driven workflow: spec → plan → tasks → implementation via Claude Code.

### Principle V: Comprehensive Testability and Verification
✅ **PASS** - All functionality verifiable via browser testing. Success criteria include measurable outcomes (200 OK responses, non-null tokens).

### Principle VI: RESTful API Compliance
✅ **PASS** - No API changes. Fix ensures proper Authorization headers are sent per REST/HTTP standards.

### Principle VII: Authentication and Security
✅ **PASS** - Fix improves security by ensuring JWT tokens are consistently attached to all API requests. No changes to JWT verification logic or trust boundaries.

### Principle VIII: Frontend Integration and User Experience
✅ **PASS** - Fix improves user experience by eliminating 403 errors. Maintains clear separation between UI and business logic. No changes to Better Auth integration or authentication flows.

**Constitution Check Result**: ✅ ALL GATES PASSED - No violations, no complexity justification needed.

**Post-Design Re-evaluation** (after Phase 1 completion):
- ✅ Principle I-VIII: All principles remain satisfied after design phase
- ✅ No new complexity introduced
- ✅ Solution maintains separation of concerns (session.ts handles storage, APIClient handles HTTP)
- ✅ Fix is minimal and focused (single function modification)
- ✅ All contracts maintained (backward compatible)
- ✅ Testing strategy defined (manual browser testing)

**Final Constitution Check**: ✅ PASS - Ready for task generation and implementation

## Project Structure

### Documentation (this feature)

```text
specs/008-fix-token-retrieval/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (already created)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── lib/
│   │   ├── auth/
│   │   │   └── session.ts          # MODIFY: Fix getToken() to read directly from localStorage
│   │   └── api/
│   │       └── client.ts            # VERIFY: Ensure getToken callback works correctly
│   ├── app/
│   │   └── (dashboard)/
│   │       └── tasks/
│   │           └── page.tsx         # VERIFY: Ensure API client initialization works
│   └── contexts/
│       └── AuthContext.tsx          # VERIFY: No changes needed, but verify token storage
└── tests/                           # Manual browser testing only (no automated tests)
```

**Structure Decision**: Web application structure with frontend-only changes. The fix is isolated to the `frontend/src/lib/auth/session.ts` file, specifically the `getToken()` function. All other files require verification only to ensure the fix works correctly across the authentication flow.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution gates passed. No complexity justification needed.
