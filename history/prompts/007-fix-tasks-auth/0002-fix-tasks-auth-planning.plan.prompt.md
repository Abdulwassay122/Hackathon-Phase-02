---
id: 0002
title: fix-tasks-auth-planning
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 007-fix-tasks-auth
branch: 007-fix-tasks-auth
user: system
command: /sp.plan
labels: ["authentication", "frontend", "bug-fix", "redirect-loop", "next.js", "planning"]
links:
  spec: specs/007-fix-tasks-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-fix-tasks-auth/plan.md
  - specs/007-fix-tasks-auth/research.md
  - specs/007-fix-tasks-auth/data-model.md
  - specs/007-fix-tasks-auth/contracts/README.md
  - specs/007-fix-tasks-auth/quickstart.md
  - CLAUDE.md (updated)
tests:
  - Constitution check passed (all 8 principles)
  - 15 manual test cases defined in quickstart.md
  - No automated tests (frontend-only fix, manual browser testing)
---

## Prompt

(empty - user invoked /sp.plan command)

## Response snapshot

Completed comprehensive implementation planning for fixing /tasks page authentication redirect loop. The planning phase included:

**Phase 0 - Research** (6 research questions answered):
1. Current authentication check implementation on /tasks page (none - relies on middleware)
2. AuthContext authentication state management (isAuthenticated, user, token, loading flags)
3. Root cause of redirect loop: Middleware checks cookies, token stored in localStorage (server-side cannot access client-side storage)
4. Correct pattern for protecting routes in Next.js App Router (client-side check with useAuth hook)
5. Token validation approach (use AuthContext's existing validation, no additional checks needed)
6. Edge case handling (token expiry, malformed tokens, race conditions, localStorage unavailable)

**Phase 1 - Design & Contracts**:
- **research.md**: Root cause analysis and solution approach
- **data-model.md**: Authentication flow changes (before/after), no database changes
- **contracts/README.md**: No API contract changes (frontend-only fix)
- **quickstart.md**: 15 manual test cases across 5 test suites
- **CLAUDE.md**: Updated agent context with Next.js 16+, React 18+, AuthContext

**Key Technical Decisions**:
- Remove /tasks from middleware protected paths (middleware cannot access localStorage)
- Add client-side authentication check to /tasks page using useAuth hook
- Check AuthContext.loading flag before checking isAuthenticated (prevent race conditions)
- Return null during redirect to prevent flash of unauthenticated content
- Use existing AuthContext validation (no duplication needed)

**Root Cause Identified**: Middleware runs server-side and checks for token in cookies, but authentication system stores token in client-side localStorage. Server cannot access localStorage, causing middleware to always redirect authenticated users.

**Solution**: Align authentication check mechanism with token storage location (both client-side) by removing middleware protection and adding client-side check using AuthContext.

**Constitution Check**: All 8 principles passed (no violations)

## Outcome

- ✅ Impact: Complete implementation plan for critical authentication bug fix, ready for task breakdown and implementation
- 🧪 Tests: 15 manual test cases defined covering login flow, signup flow, unauthenticated access, edge cases, and performance
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, contracts/README.md, quickstart.md), 1 updated (CLAUDE.md)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks, /sp.implement to execute fix
- 🧠 Reflection: Clear root cause identified with well-researched solution approach, comprehensive testing strategy, and all constitutional requirements satisfied

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with root cause clearly identified
- Graders run and results (PASS/FAIL): Constitution check: PASS (all 8 principles), Design completeness: PASS
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Proceed with /sp.tasks to break down into actionable implementation tasks
