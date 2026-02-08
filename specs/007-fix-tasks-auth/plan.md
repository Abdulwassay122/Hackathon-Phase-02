# Implementation Plan: Fix /tasks Page Auth Handling

**Branch**: `007-fix-tasks-auth` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-fix-tasks-auth/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix the /tasks page authentication check to prevent redirect loops for authenticated users after login/signup. The issue is that authenticated users with valid JWT tokens are being incorrectly redirected back to /signin when accessing /tasks. The fix involves correcting the authentication check logic on the /tasks page to properly detect valid tokens from localStorage and allow authenticated access without triggering redirects.

## Technical Context

**Language/Version**: TypeScript/JavaScript with Next.js 16+ (App Router)
**Primary Dependencies**: Next.js 16+, React 18+, existing AuthContext (from feature 005-frontend-auth-integration)
**Storage**: Browser localStorage (JWT token storage)
**Testing**: Manual browser testing (login flow, signup flow, unauthenticated access)
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend component only)
**Performance Goals**: Page load time <2 seconds for authenticated users, authentication check adds <50ms overhead
**Constraints**: Frontend-only fix (no backend API changes), must not break existing authentication flows, must maintain security (unauthenticated users still redirected)
**Scale/Scope**: Single page fix (/tasks page), affects all authenticated users accessing tasks after login/signup

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Correctness of Data Modeling and API Behavior
- ✅ **PASS**: No changes to data models or API behavior (frontend-only fix)
- ✅ **PASS**: Authentication token structure remains unchanged
- ✅ **PASS**: No impact on backend API specifications

### Principle II: Clear Separation of Concerns
- ✅ **PASS**: Authentication check logic will be properly isolated in the /tasks page component
- ✅ **PASS**: Leverages existing AuthContext for authentication state management
- ✅ **PASS**: No mixing of authentication logic with task display logic

### Principle III: Deterministic and Reproducible Backend Behavior
- ✅ **PASS**: Frontend behavior will be deterministic (same token state → same outcome)
- ✅ **PASS**: No backend changes, backend behavior remains unchanged
- ✅ **PASS**: Authentication check produces consistent results across environments

### Principle IV: Spec-Driven, Agentic Implementation
- ✅ **PASS**: Following spec-driven methodology with formal specification
- ✅ **PASS**: Implementation will be via Claude Code agents, no manual coding
- ✅ **PASS**: All changes traceable to requirements in spec.md

### Principle V: Comprehensive Testability and Verification
- ✅ **PASS**: Fix testable via browser (login → navigate to /tasks → verify no redirect)
- ✅ **PASS**: All three user stories have clear acceptance scenarios
- ✅ **PASS**: Can verify both authenticated and unauthenticated access patterns

### Principle VI: RESTful API Compliance
- ✅ **PASS**: No API endpoint changes (frontend-only fix)
- ✅ **PASS**: HTTP semantics unchanged
- ✅ **PASS**: No impact on REST architectural principles

### Principle VII: Authentication and Security
- ✅ **PASS**: Fixes authentication flow without compromising security
- ✅ **PASS**: Maintains JWT token verification (uses existing AuthContext)
- ✅ **PASS**: Unauthenticated users still properly redirected to /signin
- ✅ **PASS**: No changes to token generation or validation logic
- ✅ **PASS**: Security boundaries remain intact (backend still enforces auth)

### Principle VIII: Frontend Integration and User Experience
- ✅ **PASS**: Fixes critical UX issue (redirect loop after login/signup)
- ✅ **PASS**: Maintains clear separation between UI and business logic
- ✅ **PASS**: Uses existing AuthContext (no new authentication mechanisms)
- ✅ **PASS**: Improves user experience by allowing authenticated access to /tasks
- ✅ **PASS**: No changes to Better Auth integration or JWT token handling

**Overall Gate Status**: ✅ **PASS** - All constitutional requirements met. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/007-fix-tasks-auth/
├── spec.md              # Feature specification (already created)
├── plan.md              # This file (/sp.plan command output)
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
│   ├── app/
│   │   └── (dashboard)/
│   │       └── tasks/
│   │           └── page.tsx          # MODIFIED: Fix authentication check logic
│   ├── contexts/
│   │   └── AuthContext.tsx           # EXISTING: Authentication state management
│   ├── hooks/
│   │   └── useAuth.ts                # EXISTING: Authentication hook
│   └── lib/
│       └── auth.ts                   # EXISTING: Token storage utilities
└── tests/
    └── manual/                        # Manual browser testing procedures
```

**Structure Decision**: Web application structure (Option 2) with frontend-only changes. This fix modifies the existing /tasks page component to correctly check authentication state using the existing AuthContext. No backend changes required. The fix is isolated to the authentication check logic within the /tasks page component.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitutional requirements are met.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Phase 0: Research

### Research Questions

Based on the technical context and feature requirements, the following areas require research to inform implementation decisions:

1. **What is the current authentication check implementation on the /tasks page?**
   - Understanding the existing code structure
   - Identifying why authenticated users are being redirected

2. **How does the AuthContext provide authentication state?**
   - What methods/properties are available
   - How to properly check if a user is authenticated

3. **What is causing the redirect loop?**
   - Is the auth check running multiple times?
   - Is there a timing issue with token retrieval?
   - Is the redirect logic incorrectly triggered?

4. **What is the correct pattern for protecting routes in Next.js App Router?**
   - Best practices for authentication checks in server/client components
   - How to prevent flash of unauthenticated content
   - How to handle redirects without loops

5. **How should token validation be performed on the client side?**
   - Should we check token expiry on the client?
   - Should we validate token format?
   - What happens if localStorage is unavailable?

6. **What are the edge cases that need to be handled?**
   - Token expiry during page load
   - Malformed tokens
   - Race conditions in auth state updates

**Status**: ✅ All research questions answered in research.md

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

### Deliverables Created

1. **research.md**: Comprehensive research findings with 6 research questions answered
   - Root cause identified: Middleware checks cookies, token stored in localStorage
   - Solution approach: Remove middleware protection, add client-side check
   - Authentication patterns for Next.js App Router
   - Token validation strategy (use AuthContext)
   - Edge case handling approach

2. **data-model.md**: Modified behavior documentation
   - Authentication flow changes (before/after)
   - Protected route authentication mechanism
   - User session state management
   - Edge case handling (token expiry, malformed tokens, localStorage unavailable)
   - No database schema changes

3. **contracts/README.md**: API contract documentation
   - No changes to API contracts (frontend-only fix)
   - Contract compliance verification
   - Backward compatibility maintained
   - Error handling contract improved

4. **quickstart.md**: Manual testing guide with 15 test cases
   - Test Suite 1: Login flow (3 tests)
   - Test Suite 2: Signup flow (2 tests)
   - Test Suite 3: Unauthenticated access (3 tests)
   - Test Suite 4: Edge cases (3 tests)
   - Test Suite 5: Performance verification (2 tests)
   - Success criteria verification checklist

5. **CLAUDE.md**: Updated agent context
   - Added TypeScript/JavaScript with Next.js 16+ (App Router)
   - Added Next.js 16+, React 18+, existing AuthContext
   - Added Browser localStorage (JWT token storage)

---

## Post-Design Constitution Re-evaluation

After completing Phase 0 (Research) and Phase 1 (Design & Contracts), re-evaluating constitutional compliance:

### Principle I: Correctness of Data Modeling and API Behavior
- ✅ **PASS**: No changes to data models or API behavior
- ✅ **PASS**: Authentication flow corrected to match token storage location
- ✅ **PASS**: Deterministic behavior (same auth state → same outcome)

### Principle II: Clear Separation of Concerns
- ✅ **PASS**: Authentication check properly isolated in /tasks page component
- ✅ **PASS**: Uses existing AuthContext (no new authentication logic)
- ✅ **PASS**: Clean separation between auth check and task display logic

### Principle III: Deterministic and Reproducible Backend Behavior
- ✅ **PASS**: Frontend behavior is deterministic and reproducible
- ✅ **PASS**: No backend changes, backend behavior unchanged
- ✅ **PASS**: Authentication check produces consistent results

### Principle IV: Spec-Driven, Agentic Implementation
- ✅ **PASS**: All design artifacts created following spec-driven methodology
- ✅ **PASS**: Research decisions documented with rationale
- ✅ **PASS**: Ready for agentic implementation via /sp.tasks and /sp.implement

### Principle V: Comprehensive Testability and Verification
- ✅ **PASS**: Comprehensive testing strategy defined (15 test cases)
- ✅ **PASS**: All user stories independently testable via browser
- ✅ **PASS**: Edge case coverage (token expiry, malformed tokens, race conditions)
- ✅ **PASS**: Performance verification tests included

### Principle VI: RESTful API Compliance
- ✅ **PASS**: No API changes, internal fix only
- ✅ **PASS**: HTTP semantics unchanged
- ✅ **PASS**: Contract compliance maintained

### Principle VII: Authentication and Security
- ✅ **PASS**: Fixes authentication flow without compromising security
- ✅ **PASS**: Maintains JWT token verification via AuthContext
- ✅ **PASS**: Unauthenticated users still properly redirected
- ✅ **PASS**: Security boundaries remain intact (backend enforces auth)
- ✅ **PASS**: No new security risks introduced

### Principle VIII: Frontend Integration and User Experience
- ✅ **PASS**: Fixes critical UX issue (redirect loop eliminated)
- ✅ **PASS**: Maintains clear separation between UI and business logic
- ✅ **PASS**: Uses existing AuthContext (no new mechanisms)
- ✅ **PASS**: Improves user experience significantly
- ✅ **PASS**: No changes to Better Auth integration

**Final Gate Status**: ✅ **PASS** - All constitutional requirements remain satisfied after design phase. No violations introduced. Implementation can proceed.

---

## Summary of Key Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| **Root Cause** | Middleware checks cookies, token in localStorage | Server-side middleware cannot access client-side localStorage |
| **Solution Approach** | Remove middleware protection, add client-side check | Aligns check mechanism with token storage location |
| **Protection Pattern** | Client-side check using useAuth hook | Standard Next.js App Router pattern for client components |
| **Token Validation** | Use AuthContext's isAuthenticated flag | Validation already implemented, no duplication needed |
| **Loading State** | Check AuthContext.loading before redirecting | Prevents premature redirects during initialization |
| **Edge Cases** | Handled by AuthContext's existing logic | Token expiry, malformed tokens already covered |

---

## Implementation Risks

1. **Flash of Unauthenticated Content**
   - Risk: User might see task content briefly before redirect
   - Mitigation: Return null during redirect, show loading spinner while checking auth
   - Severity: Low (handled by implementation pattern)

2. **Race Condition During Auth Initialization**
   - Risk: Redirect might trigger before AuthContext finishes initializing
   - Mitigation: Check `loading` flag before checking `isAuthenticated`
   - Severity: Low (AuthContext provides loading state)

3. **Middleware Still Redirecting**
   - Risk: If middleware changes not applied, redirect loop persists
   - Mitigation: Verify middleware changes in code review, test thoroughly
   - Severity: Medium (would block entire fix)

---

## Next Steps

1. ✅ **Phase 0 Complete**: Research findings documented in research.md
2. ✅ **Phase 1 Complete**: Design artifacts created (data-model.md, contracts/, quickstart.md)
3. ⏭️ **Phase 2 Next**: Generate tasks.md via `/sp.tasks` command
4. ⏭️ **Implementation**: Execute tasks via `/sp.implement` command
5. ⏭️ **Testing**: Follow quickstart.md manual testing procedures

**Planning Complete**: All design artifacts ready. Proceed with `/sp.tasks` to generate implementation tasks.
