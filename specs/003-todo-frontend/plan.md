# Implementation Plan: Todo Frontend Integration

**Branch**: `003-todo-frontend` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-todo-frontend/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a responsive Next.js 16+ frontend application that integrates with the secured FastAPI backend to deliver a complete multi-user Todo application. The frontend will implement authentication UI using Better Auth, provide full task CRUD operations, attach JWT tokens to all API requests, and handle loading/error/unauthorized states. The application must be responsive across mobile and desktop devices while maintaining clear separation between UI presentation and business logic.

**Primary Requirement**: Authenticated users can manage their own tasks through a responsive web interface that accurately reflects backend state.

**Technical Approach**: Next.js 16+ App Router with Better Auth for authentication, centralized API client with JWT token injection, React hooks for state management, and responsive CSS for cross-device compatibility.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (React 18+)
**Primary Dependencies**: Next.js 16+, Better Auth, React 18+, TypeScript 5.x
**Storage**: Browser localStorage/sessionStorage for JWT tokens (managed by Better Auth), no local database
**Testing**: Jest + React Testing Library for unit tests, Playwright/Cypress for E2E tests
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge - last 2 versions), responsive design for mobile (320px+) and desktop (up to 1920px)
**Project Type**: Web application (frontend integrating with existing backend)
**Performance Goals**:
- Initial page load < 3 seconds on standard connections
- Task operations complete < 3 seconds
- Time to Interactive (TTI) < 5 seconds
- First Contentful Paint (FCP) < 2 seconds
**Constraints**:
- Must use Next.js 16+ App Router (no Pages Router)
- Must use Better Auth exclusively for authentication
- REST API only (no GraphQL, WebSockets)
- All business logic enforced by backend
- JWT tokens must be attached to every API request
- Must work on mobile devices (minimum 320px width)
**Scale/Scope**:
- 5 main user flows (authentication, view/create/update/delete tasks, logout)
- ~10-15 React components
- 5-7 pages/routes
- Single-user frontend (multi-user handled by backend)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Correctness of Data Modeling and API Behavior
✅ **PASS** - Frontend consumes existing backend API with defined data models. No new data models created in frontend. All API contracts already established in Phase 2.

### Principle II: Clear Separation of Concerns
✅ **PASS** - Frontend maintains clear separation:
- UI components (presentation layer)
- API client (communication layer)
- React hooks (state management)
- Better Auth (authentication layer)
No business logic in frontend - all validation and rules enforced by backend.

### Principle III: Deterministic and Reproducible Backend Behavior
✅ **PASS** - Frontend does not modify backend behavior. All backend operations remain deterministic. Frontend only consumes backend APIs.

### Principle IV: Spec-Driven, Agentic Implementation
✅ **PASS** - This plan follows spec-driven methodology: specification (complete) → plan (this document) → tasks (next phase) → implementation via Claude Code. No manual coding permitted.

### Principle V: Comprehensive Testability and Verification
✅ **PASS** - All frontend functionality testable via browser:
- Authentication flows testable by signup/signin/logout
- Task operations testable by CRUD actions in UI
- Error handling testable by simulating API failures
- Responsive design testable across device sizes

### Principle VI: RESTful API Compliance
✅ **PASS** - Frontend consumes existing RESTful backend API. All HTTP semantics and REST conventions already established in Phase 2. Frontend makes standard HTTP requests with proper methods and headers.

### Principle VII: Authentication and Security
✅ **PASS** - Frontend implements security correctly:
- JWT tokens attached to every API request
- Tokens obtained from Better Auth
- Unauthenticated users redirected to signin
- No security logic in frontend (all enforced by backend)
- Tokens cleared on logout
- HTTPS required in production

### Principle VIII: Frontend Integration and User Experience
✅ **PASS** - This is the primary principle for Phase 3:
- Clear separation between UI and business logic ✓
- JWT tokens on all API requests ✓
- UI state reflects backend state ✓
- Responsive design (mobile + desktop) ✓
- Browser-testable user flows ✓
- Better Auth exclusive for authentication ✓
- REST-only communication ✓
- Next.js App Router conventions ✓

**Constitution Compliance**: ✅ ALL PRINCIPLES PASS - No violations, no complexity justification needed.

## Project Structure

### Documentation (this feature)

```text
specs/003-todo-frontend/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── api-client.md    # API client interface specification
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/                          # NEW: Next.js application
├── src/
│   ├── app/                      # Next.js 16+ App Router
│   │   ├── (auth)/               # Auth route group
│   │   │   ├── signin/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   ├── (dashboard)/          # Protected route group
│   │   │   └── tasks/
│   │   │       └── page.tsx
│   │   ├── layout.tsx            # Root layout
│   │   └── page.tsx              # Landing page
│   ├── components/               # React components
│   │   ├── auth/
│   │   │   ├── SignInForm.tsx
│   │   │   └── SignUpForm.tsx
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskActions.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   └── Navigation.tsx
│   │   └── ui/                   # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       └── LoadingSpinner.tsx
│   ├── lib/                      # Utilities and services
│   │   ├── api/
│   │   │   ├── client.ts         # Centralized API client
│   │   │   └── tasks.ts          # Task API methods
│   │   ├── auth/
│   │   │   └── better-auth.ts    # Better Auth configuration
│   │   └── utils/
│   │       ├── validation.ts
│   │       └── formatting.ts
│   ├── types/                    # TypeScript type definitions
│   │   ├── task.ts
│   │   └── api.ts
│   └── styles/                   # Global styles
│       └── globals.css
├── public/                       # Static assets
├── tests/                        # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.local.example            # Environment variables template
├── next.config.js                # Next.js configuration
├── tsconfig.json                 # TypeScript configuration
└── package.json                  # Dependencies

backend/                          # EXISTING: FastAPI application (Phase 1 & 2)
├── src/
│   ├── api/
│   ├── auth/
│   ├── models/
│   ├── services/
│   └── database/
└── tests/
```

**Structure Decision**: Web application structure with separate frontend and backend directories. Frontend is a new Next.js 16+ application using App Router. Backend already exists from Phase 1 and Phase 2. Frontend will communicate with backend via REST API over HTTPS.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles pass without requiring complexity justification.
