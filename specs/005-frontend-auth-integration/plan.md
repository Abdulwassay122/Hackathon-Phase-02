# Implementation Plan: Frontend Authentication Integration

**Branch**: `005-frontend-auth-integration` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-frontend-auth-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Replace Better Auth library with direct calls to FastAPI authentication endpoints (/api/auth/signup and /api/auth/login). Store JWT tokens in browser localStorage and attach them to all subsequent API requests via Authorization header. Implement client-side route protection and token expiration handling to maintain authenticated sessions across browser navigation.

## Technical Context

**Language/Version**: JavaScript/TypeScript with Next.js 16+ (App Router)
**Primary Dependencies**: Next.js 16+, React 18+, fetch API (or axios/similar HTTP client)
**Storage**: Browser localStorage for JWT token persistence
**Testing**: Browser-based manual testing, Jest/React Testing Library for component tests (if automated tests added)
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend only - integrates with existing FastAPI backend)
**Performance Goals**: <3 seconds for signup/login completion, <2 seconds for authenticated page loads
**Constraints**: Must use localStorage (not cookies/sessionStorage by default), JWT-based auth only, no Better Auth library usage, minimal UI changes to existing pages
**Scale/Scope**: Multi-user web application, 2 authentication pages (signup/login), authentication state management across all protected routes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle IV: Spec-Driven, Agentic Implementation
- ✅ **PASS**: Feature has formal specification in spec.md with clear requirements
- ✅ **PASS**: Implementation will follow spec → plan → tasks → implementation workflow
- ✅ **PASS**: No manual coding - all changes via Claude Code agents

### Principle VII: Authentication and Security
- ✅ **PASS**: JWT tokens will be stored securely in localStorage
- ✅ **PASS**: All API requests will include JWT in Authorization header
- ✅ **PASS**: Backend verification already implemented (feature 001-backend-auth-endpoints)
- ✅ **PASS**: Frontend will handle 401/403 responses and redirect appropriately
- ✅ **PASS**: Token expiration (24 hours) will be respected
- ⚠️ **REVIEW**: Client-side validation is for UX only - backend enforces all security rules

### Principle VIII: Frontend Integration and User Experience
- ✅ **PASS**: Clear separation - UI handles presentation, backend enforces business rules
- ✅ **PASS**: JWT tokens obtained from backend API and attached to all requests
- ✅ **PASS**: Better Auth library will be REMOVED (not used for authentication)
- ✅ **PASS**: REST-only communication with backend (no WebSockets)
- ✅ **PASS**: Next.js 16+ App Router conventions followed
- ✅ **PASS**: Minimal UI changes - updating existing signup/login pages only
- ✅ **PASS**: Authentication state managed via React Context API or hooks

### Technology Stack Compliance
- ✅ **PASS**: Frontend Framework: Next.js 16+ with App Router
- ✅ **PASS**: Backend API: FastAPI (already implemented)
- ✅ **PASS**: Authentication: JWT verification (backend already implemented)
- ✅ **PASS**: Communication: REST API over HTTPS
- ✅ **PASS**: State Management: React hooks and Context API

### Development Workflow Compliance
- ✅ **PASS**: Phase 3 (Frontend integration with authenticated API)
- ✅ **PASS**: Backend authentication already verified (Phase 2 complete)
- ✅ **PASS**: No manual edits - all via agent-generated output
- ✅ **PASS**: Functionality verifiable via browser testing

**Overall Gate Status**: ✅ **PASS** - All constitutional requirements met. Feature aligns with Phase 3 development workflow and follows all security, frontend integration, and technology stack principles.

## Project Structure

### Documentation (this feature)

```text
specs/005-frontend-auth-integration/
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
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Authentication route group
│   │   │   ├── login/         # Login page
│   │   │   │   └── page.tsx
│   │   │   └── signup/        # Signup page
│   │   │       └── page.tsx
│   │   └── (protected)/       # Protected routes requiring authentication
│   │       └── tasks/         # Tasks page (example protected route)
│   │           └── page.tsx
│   ├── components/            # Reusable UI components
│   │   ├── auth/             # Authentication-specific components
│   │   │   ├── LoginForm.tsx
│   │   │   └── SignupForm.tsx
│   │   └── layout/           # Layout components
│   ├── contexts/             # React Context providers
│   │   └── AuthContext.tsx   # Authentication state management
│   ├── hooks/                # Custom React hooks
│   │   └── useAuth.ts        # Authentication hook
│   ├── lib/                  # Utility libraries
│   │   ├── api.ts           # API client configuration
│   │   └── auth.ts          # Authentication utilities (token storage, retrieval)
│   └── middleware.ts         # Next.js middleware for route protection
└── tests/                    # Frontend tests (if automated tests added)
    ├── components/
    └── integration/

backend/                       # Existing backend (no changes in this feature)
├── src/
│   ├── api/
│   │   └── auth_routes.py    # Already implemented (feature 001)
│   └── auth/
│       ├── jwt_handler.py    # Already implemented (feature 001)
│       └── dependencies.py   # Already implemented (feature 002)
```

**Structure Decision**: Web application structure (Option 2) with frontend/backend separation. This feature focuses exclusively on the frontend directory, updating authentication flows to integrate with the existing backend API. The backend authentication endpoints are already implemented and functional (features 001 and 004). No backend changes are required for this feature.

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

1. **Next.js 16+ App Router Authentication Patterns**
   - How to implement authentication state management with App Router
   - Server Components vs Client Components for authentication
   - Middleware patterns for route protection

2. **JWT Token Storage Best Practices**
   - localStorage vs sessionStorage vs cookies for JWT storage
   - Security implications of each storage method
   - XSS protection strategies

3. **React Context API for Authentication State**
   - Context provider patterns for authentication
   - Performance considerations with Context API
   - Integration with Next.js App Router

4. **HTTP Client Configuration**
   - Interceptor patterns for attaching Authorization headers
   - Error handling for 401/403 responses
   - Token refresh strategies (if needed)

5. **Form Validation Patterns**
   - Client-side validation best practices
   - Integration with backend validation
   - Error message display patterns

6. **Better Auth Removal Strategy**
   - Identifying all Better Auth dependencies
   - Migration path from Better Auth to custom implementation
   - Ensuring no breaking changes to existing functionality

**Status**: ✅ All research questions answered in research.md

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

### Deliverables Created

1. **research.md**: Comprehensive research findings with 6 research questions answered
   - Next.js 16+ App Router authentication patterns
   - JWT token storage best practices (localStorage with XSS mitigation)
   - React Context API for authentication state
   - HTTP client configuration (fetch API with wrapper)
   - Form validation patterns (dual validation)
   - Better Auth removal strategy

2. **data-model.md**: Data model with 3 key entities
   - JWT Token (localStorage persistence)
   - Authentication State (React Context)
   - Form State (ephemeral component state)

3. **contracts/signup.yaml**: OpenAPI specification for signup endpoint
   - Request/response schemas
   - Error scenarios (400, 409, 422, 500)
   - Frontend implementation notes

4. **contracts/login.yaml**: OpenAPI specification for login endpoint
   - Request/response schemas
   - Error scenarios (401, 422, 500)
   - Security considerations

5. **quickstart.md**: Manual testing guide with 24 test cases
   - User Story 1: Signup flow (7 tests)
   - User Story 2: Login flow (4 tests)
   - User Story 3: Session persistence (5 tests)
   - Integration tests (3 tests)
   - Edge cases (4 tests)
   - Cross-browser compatibility (3 tests)

6. **CLAUDE.md**: Updated agent context with new technologies
   - JavaScript/TypeScript with Next.js 16+
   - React 18+, fetch API
   - Browser localStorage

---

## Post-Design Constitution Re-evaluation

After completing Phase 0 (Research) and Phase 1 (Design & Contracts), re-evaluating constitutional compliance:

### Principle IV: Spec-Driven, Agentic Implementation
- ✅ **PASS**: All design artifacts created following spec-driven methodology
- ✅ **PASS**: Research decisions documented with rationale
- ✅ **PASS**: Data model, contracts, and testing procedures defined

### Principle VII: Authentication and Security
- ✅ **PASS**: JWT token storage strategy defined with XSS mitigation
- ✅ **PASS**: Authorization header pattern documented in contracts
- ✅ **PASS**: Token expiration handling strategy defined
- ✅ **PASS**: Generic error messages prevent user enumeration (contracts)
- ✅ **PASS**: Client-side validation explicitly marked as UX-only

### Principle VIII: Frontend Integration and User Experience
- ✅ **PASS**: Clear separation between UI and business logic (Context pattern)
- ✅ **PASS**: JWT tokens obtained from backend API (contracts defined)
- ✅ **PASS**: Better Auth removal strategy documented
- ✅ **PASS**: REST-only communication (no WebSockets)
- ✅ **PASS**: Next.js App Router patterns followed (research decisions)
- ✅ **PASS**: Minimal UI changes (updating existing pages only)

### Technology Stack Compliance
- ✅ **PASS**: Next.js 16+ with App Router (confirmed in research)
- ✅ **PASS**: React hooks and Context API (data model)
- ✅ **PASS**: REST API communication (contracts)
- ✅ **PASS**: No Better Auth usage (removal strategy defined)

### Development Workflow Compliance
- ✅ **PASS**: Phase 3 implementation (frontend integration)
- ✅ **PASS**: Backend authentication verified (dependencies documented)
- ✅ **PASS**: Browser-based testing strategy (quickstart.md)

**Final Gate Status**: ✅ **PASS** - All constitutional requirements remain satisfied after design phase. No violations introduced. Implementation can proceed.

---

## Summary of Key Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| **Architecture** | Client Components + Context API + Middleware | Balances security, UX, and Next.js 16+ best practices |
| **Token Storage** | localStorage with XSS mitigation | Meets spec requirements, simple implementation |
| **State Management** | React Context API | Built-in, sufficient for auth state |
| **HTTP Client** | fetch API with wrapper | No dependencies, meets all requirements |
| **Validation** | Dual (client + backend) | UX enhancement + security enforcement |
| **Better Auth** | Complete removal | Spec requirement, simpler architecture |

---

## Implementation Risks

1. **XSS Vulnerabilities**
   - Risk: localStorage tokens vulnerable to XSS attacks
   - Mitigation: CSP headers, input sanitization, HTTPS-only
   - Severity: Medium (standard web app risk)

2. **Token Expiration Edge Cases**
   - Risk: User makes request with expired token
   - Mitigation: Global 401 handler, automatic redirect
   - Severity: Low (handled by backend)

3. **Browser Compatibility**
   - Risk: localStorage not available (private browsing)
   - Mitigation: Detect and show error message
   - Severity: Low (edge case documented in spec)

4. **State Synchronization**
   - Risk: Auth state out of sync with backend
   - Mitigation: Validate token on app load, handle 401 globally
   - Severity: Low (standard pattern)

---

## Next Steps

1. ✅ **Phase 0 Complete**: Research findings documented in research.md
2. ✅ **Phase 1 Complete**: Design artifacts created (data-model.md, contracts/, quickstart.md)
3. ⏭️ **Phase 2 Next**: Generate tasks.md via `/sp.tasks` command
4. ⏭️ **Implementation**: Execute tasks via `/sp.implement` command
5. ⏭️ **Testing**: Follow quickstart.md manual testing procedures

**Planning Complete**: All design artifacts ready. Proceed with `/sp.tasks` to generate implementation tasks.
