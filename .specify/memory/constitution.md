<!-- SYNC IMPACT REPORT
Version change: 1.1.0 → 1.2.0
Modified principles: None
Added sections:
  - Principle VIII: Frontend Integration and User Experience (new principle for Phase 3)
  - Updated Technology Stack Requirements to reflect active Next.js usage
  - Updated Development Workflow to include Phase 3 implementation details
Removed sections: None
Templates requiring updates:
  - ✅ plan-template.md: Constitution Check section will automatically reflect new principle
  - ✅ spec-template.md: No changes needed (technology-agnostic)
  - ✅ tasks-template.md: No changes needed (already supports frontend tasks)
Follow-up TODOs: None
-->
# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Correctness of Data Modeling and API Behavior
Backend implementations must ensure precise adherence to the defined data models and API specifications. All API endpoints must behave deterministically and return responses that exactly match the specification. All database operations must accurately represent the intended data relationships and constraints.

### II. Clear Separation of Concerns
Each layer of the application (API, ORM, database) must have well-defined responsibilities with minimal coupling between layers. The API layer handles HTTP request/response logic, the ORM layer manages data mapping and validation, and the database layer provides persistence and data integrity. Cross-cutting concerns like logging and error handling should be centralized and not scattered throughout the codebase.

### III. Deterministic and Reproducible Backend Behavior
All backend operations must produce consistent, predictable results. This includes deterministic API responses, reproducible database operations, and consistent application state. Configuration and environment variables must be managed systematically to ensure identical behavior across different environments. All backend behavior must be specifiable and verifiable through automated tests.

### IV. Spec-Driven, Agentic Implementation
All code implementation must follow the spec-driven development methodology with no manual coding allowed. The agentic development process must be strictly followed: specifications → plan → tasks → implementation via Claude Code. All changes must originate from formal specifications and be traceable back to specific requirements in the project specs.

### V. Comprehensive Testability and Verification
Every API operation must be testable via HTTP requests with clear verification mechanisms. The backend must support independent verification of all functionality without requiring frontend integration. All endpoints must be accessible through standard HTTP methods and return predictable responses suitable for automated testing.

### VI. RESTful API Compliance
All API endpoints must strictly follow HTTP semantics and REST architectural principles. Proper HTTP status codes must be used for all responses, and endpoints must follow standard REST conventions for resource identification, creation, retrieval, update, and deletion operations. Request and response formats must conform to established standards with appropriate content types.

### VII. Authentication and Security
Strong user isolation and data protection must be enforced at all levels. The application must use stateless authentication via JWT tokens with explicit trust boundaries between frontend and backend. Security rules must be enforced at the API level, never relying on UI-level restrictions. Every protected request must require a valid JWT token. The backend must never trust user_id from URL parameters without verification against JWT claims. JWT verification logic must be centralized and reusable across all protected endpoints. Authentication failures must return proper HTTP error codes (401 for unauthorized, 403 for forbidden). Token expiry must be respected and enforced by the backend. All authentication and authorization logic must be testable and auditable.

**Rationale**: Security cannot be an afterthought. By establishing authentication as a core principle, we ensure that user data isolation, token verification, and trust boundaries are consistently applied across all features. This prevents common security vulnerabilities such as insecure direct object references (IDOR) and ensures that authentication logic is not scattered throughout the codebase.

### VIII. Frontend Integration and User Experience
The frontend must maintain clear separation between UI presentation and business logic, with all business rules enforced by the backend API. Secure client-to-server communication must be established through JWT tokens attached to every API request. The UI state must accurately reflect the backend state at all times, with proper synchronization after all mutations. The application must provide a responsive and accessible user experience that works across different devices and screen sizes. All user flows must be reproducible and testable from the browser alone without requiring backend code inspection. Frontend validation serves only as a user experience enhancement and must never be relied upon for security or data integrity. Better Auth must be used exclusively for authentication flows (signup, signin, session management) with JWT tokens obtained from Better Auth and passed to the backend API. The frontend must handle authentication errors gracefully and redirect users appropriately based on authentication state. All API communication must use REST principles with no WebSockets or alternative protocols. UI components must be designed for reusability and maintainability following Next.js App Router conventions.

**Rationale**: A well-architected frontend ensures that security boundaries are respected, user experience is consistent, and the application remains maintainable as it grows. By establishing clear principles for frontend integration, we prevent common pitfalls such as client-side security enforcement, state synchronization issues, and tight coupling between UI and business logic. The exclusive use of Better Auth for authentication ensures a consistent, secure authentication flow while the REST-only constraint maintains simplicity and debuggability.

## Technology Stack Requirements
The application must strictly adhere to the defined technology stack:
- Backend Framework: FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (frontend session management) with JWT verification (backend)
- Frontend Framework: Next.js 16+ with App Router
- Frontend-Backend Communication: REST API over HTTPS
- State Management: React hooks and Next.js built-in capabilities
No deviations from the approved technology stack are permitted without explicit constitutional amendment.

## Development Workflow and Constraints
- Phase 1: Backend-only implementation (no authentication, no frontend)
- Phase 2: Authentication and security layer (JWT verification, user isolation)
- Phase 3: Frontend integration with authenticated API (Next.js + Better Auth)
- Persistent storage using Neon Serverless PostgreSQL is mandatory
- ORM layer must be implemented using SQLModel only
- Frontend must be implemented using Next.js 16+ App Router only
- Authentication flows must use Better Auth exclusively
- Manual edits to generated code are prohibited
- All functionality must be verifiable via API calls before frontend integration
- Frontend functionality must be verifiable via browser testing
- No implementation without corresponding specification
- Each phase must have its own specification, plan, and testing strategy

## Governance
This constitution governs all aspects of the Todo Full-Stack Web Application development. All implementation decisions must align with these principles. Amendments to this constitution require explicit documentation, stakeholder approval, and a migration plan for existing code. All pull requests and code reviews must verify compliance with these principles. The development team must refer to this constitution when making architectural decisions that impact the core principles.

**Version**: 1.2.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-07
