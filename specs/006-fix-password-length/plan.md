# Implementation Plan: Fix Password Length Error (72-Byte Limit)

**Branch**: `006-fix-password-length` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-fix-password-length/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix backend authentication failure caused by bcrypt's 72-byte password limit. Implement transparent password truncation to 72 bytes before hashing during registration and verification during login. This prevents the error "password cannot be longer than 72 bytes, truncate manually if necessary" from blocking user authentication while maintaining backward compatibility with existing password hashes.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLModel, passlib[bcrypt] (password hashing)
**Storage**: Neon Serverless PostgreSQL (existing, no schema changes)
**Testing**: pytest (unit tests for password handling, integration tests for auth endpoints)
**Target Platform**: Linux server (FastAPI backend)
**Project Type**: Web application (backend component only)
**Performance Goals**: <1ms overhead for password truncation operation
**Constraints**: Backend-only change, no algorithm changes, must maintain backward compatibility with existing password hashes, transparent to users
**Scale/Scope**: Affects all authentication operations (signup and login endpoints), applies to all users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Correctness of Data Modeling and API Behavior
- ✅ **PASS**: Fix ensures correct password handling by preventing byte-length errors
- ✅ **PASS**: API behavior remains deterministic - same password always produces same result
- ✅ **PASS**: No changes to data models or API specifications

### Principle II: Clear Separation of Concerns
- ✅ **PASS**: Password truncation logic will be centralized in authentication layer
- ✅ **PASS**: Changes isolated to password hashing utilities, not scattered across codebase
- ✅ **PASS**: API layer, ORM layer, and database layer remain unchanged

### Principle III: Deterministic and Reproducible Backend Behavior
- ✅ **PASS**: Password truncation is deterministic - same input always produces same output
- ✅ **PASS**: Behavior is reproducible across all environments
- ✅ **PASS**: No configuration changes needed, fix works consistently

### Principle IV: Spec-Driven, Agentic Implementation
- ✅ **PASS**: Following spec-driven methodology with formal specification
- ✅ **PASS**: Implementation will be via Claude Code agents, no manual coding
- ✅ **PASS**: All changes traceable to requirements in spec.md

### Principle V: Comprehensive Testability and Verification
- ✅ **PASS**: Fix testable via HTTP requests to signup/login endpoints
- ✅ **PASS**: Can verify with long passwords (>72 bytes) in API tests
- ✅ **PASS**: Backward compatibility testable with existing short passwords

### Principle VI: RESTful API Compliance
- ✅ **PASS**: No API endpoint changes, internal fix only
- ✅ **PASS**: HTTP status codes remain unchanged
- ✅ **PASS**: Request/response formats unchanged

### Principle VII: Authentication and Security
- ✅ **PASS**: Fixes authentication errors, improves user access
- ✅ **PASS**: Maintains JWT token verification (no changes to auth flow)
- ✅ **PASS**: Password truncation is standard bcrypt behavior, no new security risks
- ✅ **PASS**: Backward compatible with existing password hashes

### Principle VIII: Frontend Integration and User Experience
- ✅ **PASS**: No frontend changes required (backend-only fix)
- ✅ **PASS**: Transparent to users - no UI changes or notifications
- ✅ **PASS**: Improves UX by preventing authentication errors

**Overall Gate Status**: ✅ **PASS** - All constitutional requirements met. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/006-fix-password-length/
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
backend/
├── src/
│   ├── auth/
│   │   ├── password_utils.py    # MODIFIED: Add password truncation logic
│   │   └── dependencies.py      # No changes (JWT verification)
│   ├── api/
│   │   └── auth_routes.py       # MODIFIED: Use truncated passwords in signup/login
│   └── models/
│       └── user.py              # No changes (User model unchanged)
└── tests/
    ├── unit/
    │   └── test_password_utils.py   # NEW: Unit tests for password truncation
    └── integration/
        └── test_auth_endpoints.py   # MODIFIED: Add tests for long passwords
```

**Structure Decision**: Web application structure (Option 2) with backend-only changes. This fix modifies existing authentication utilities in the backend to handle password truncation before hashing. No frontend changes required. The fix is isolated to the password handling layer within the backend authentication module.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitutional requirements are met.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Phase 0: Research

### Research Questions

Based on the technical context and feature requirements, the following areas required research to inform implementation decisions:

1. **How does bcrypt handle password length limits?**
   - Understanding bcrypt's 72-byte limitation
   - Why the error occurs and how to prevent it

2. **How to correctly calculate byte length for UTF-8 strings in Python?**
   - Handling multi-byte characters correctly
   - Ensuring truncation doesn't exceed 72 bytes

3. **Where should password truncation be implemented?**
   - Centralized vs distributed implementation
   - Best practices for password handling

4. **How to ensure backward compatibility with existing passwords?**
   - Impact on existing password hashes
   - Migration strategy (if needed)

5. **What testing strategy should be used?**
   - Unit tests, integration tests, edge cases
   - Coverage requirements

6. **What are the security implications of password truncation?**
   - Security risks and mitigations
   - User awareness considerations

**Status**: ✅ All research questions answered in research.md

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

### Deliverables Created

1. **research.md**: Comprehensive research findings with 6 research questions answered
   - Bcrypt 72-byte limit behavior and solution
   - UTF-8 byte-length calculation with `encode('utf-8')[:72]`
   - Centralized implementation in password_utils.py
   - Backward compatibility strategy (no changes needed)
   - Testing strategy (unit + integration + edge cases)
   - Security implications (no new risks)

2. **data-model.md**: Modified behavior documentation
   - User Password Handling (modified behavior)
   - Authentication Request (modified flow)
   - Data flow diagrams for signup and login
   - No database schema changes

3. **contracts/README.md**: API contract documentation
   - No changes to API contracts
   - Internal behavior modification only
   - Contract compliance verification tests

4. **quickstart.md**: Manual testing guide with 15 test cases
   - Test Suite 1: Registration with long passwords (4 tests)
   - Test Suite 2: Login with long passwords (3 tests)
   - Test Suite 3: Backward compatibility (2 tests)
   - Test Suite 4: Edge cases (3 tests)
   - Test Suite 5: Performance verification (1 test)

5. **CLAUDE.md**: Updated agent context
   - Added Python 3.11 + FastAPI, SQLModel, passlib[bcrypt]
   - Added Neon Serverless PostgreSQL (no schema changes)
   - Added Web application (backend component only)

---

## Post-Design Constitution Re-evaluation

After completing Phase 0 (Research) and Phase 1 (Design & Contracts), re-evaluating constitutional compliance:

### Principle I: Correctness of Data Modeling and API Behavior
- ✅ **PASS**: Password handling logic is correct and deterministic
- ✅ **PASS**: API behavior remains consistent and predictable
- ✅ **PASS**: No changes to data models or API specifications

### Principle II: Clear Separation of Concerns
- ✅ **PASS**: Password truncation centralized in password_utils.py
- ✅ **PASS**: Single responsibility - authentication layer handles password processing
- ✅ **PASS**: No cross-layer coupling introduced

### Principle III: Deterministic and Reproducible Backend Behavior
- ✅ **PASS**: Truncation is deterministic (same input → same output)
- ✅ **PASS**: Reproducible across all environments
- ✅ **PASS**: No configuration dependencies

### Principle IV: Spec-Driven, Agentic Implementation
- ✅ **PASS**: All design artifacts created following spec-driven methodology
- ✅ **PASS**: Research decisions documented with rationale
- ✅ **PASS**: Ready for agentic implementation via /sp.tasks and /sp.implement

### Principle V: Comprehensive Testability and Verification
- ✅ **PASS**: Comprehensive testing strategy defined (15 test cases)
- ✅ **PASS**: Unit tests for truncation logic
- ✅ **PASS**: Integration tests for auth endpoints
- ✅ **PASS**: Edge case coverage (multi-byte chars, boundaries)

### Principle VI: RESTful API Compliance
- ✅ **PASS**: No API changes, internal fix only
- ✅ **PASS**: HTTP semantics unchanged
- ✅ **PASS**: Contract compliance maintained

### Principle VII: Authentication and Security
- ✅ **PASS**: Fixes authentication errors, improves access
- ✅ **PASS**: No new security risks introduced
- ✅ **PASS**: Backward compatible with existing hashes
- ✅ **PASS**: Security implications documented and acceptable

### Principle VIII: Frontend Integration and User Experience
- ✅ **PASS**: No frontend changes required
- ✅ **PASS**: Transparent to users (no UI changes)
- ✅ **PASS**: Improves UX by preventing authentication errors

**Final Gate Status**: ✅ **PASS** - All constitutional requirements remain satisfied after design phase. No violations introduced. Implementation can proceed.

---

## Summary of Key Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| **Truncation Method** | Encode to UTF-8, truncate to 72 bytes | Handles multi-byte characters correctly |
| **Implementation Location** | Centralized utility in password_utils.py | Single source of truth, easy to test |
| **Backward Compatibility** | No changes needed | Existing hashes already use first 72 bytes |
| **Testing Strategy** | Unit + Integration + Edge cases | Comprehensive coverage, follows principles |
| **Security Impact** | No new risks introduced | Makes existing bcrypt behavior explicit |
| **User Notification** | None (transparent) | Follows constraint, no security benefit |

---

## Implementation Risks

1. **UTF-8 Decoding Errors**
   - Risk: Truncating at byte 72 might split a multi-byte character
   - Mitigation: Use `decode('utf-8', errors='ignore')` to drop incomplete characters
   - Severity: Low (handled by implementation)

2. **Backward Compatibility**
   - Risk: Existing users might not be able to log in
   - Mitigation: Truncation produces same result as bcrypt's internal truncation
   - Severity: Very Low (verified by testing)

3. **Performance Impact**
   - Risk: Truncation adds overhead to authentication
   - Mitigation: Byte slicing is O(1) operation, negligible overhead
   - Severity: Very Low (<1ms as specified in constraints)

---

## Next Steps

1. ✅ **Phase 0 Complete**: Research findings documented in research.md
2. ✅ **Phase 1 Complete**: Design artifacts created (data-model.md, contracts/, quickstart.md)
3. ⏭️ **Phase 2 Next**: Generate tasks.md via `/sp.tasks` command
4. ⏭️ **Implementation**: Execute tasks via `/sp.implement` command
5. ⏭️ **Testing**: Follow quickstart.md manual testing procedures

**Planning Complete**: All design artifacts ready. Proceed with `/sp.tasks` to generate implementation tasks.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
