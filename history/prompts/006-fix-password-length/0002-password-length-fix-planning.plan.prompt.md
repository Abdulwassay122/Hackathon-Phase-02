---
id: 0002
title: Password Length Fix Planning
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 006-fix-password-length
branch: 006-fix-password-length
user: system
command: /sp.plan
labels: ["password", "authentication", "bug-fix", "backend", "bcrypt", "planning"]
links:
  spec: specs/006-fix-password-length/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-fix-password-length/plan.md
  - specs/006-fix-password-length/research.md
  - specs/006-fix-password-length/data-model.md
  - specs/006-fix-password-length/contracts/README.md
  - specs/006-fix-password-length/quickstart.md
  - CLAUDE.md (updated)
tests:
  - Constitution check passed (all 8 principles)
  - 15 manual test cases defined in quickstart.md
---

## Prompt

(empty - user invoked /sp.plan command)

## Response snapshot

Completed comprehensive implementation planning for fixing the bcrypt 72-byte password length error. The planning phase included:

**Phase 0 - Research** (6 research questions answered):
1. Bcrypt's 72-byte limit behavior and standard solution (pre-truncation)
2. UTF-8 byte-length calculation using `encode('utf-8')[:72]`
3. Centralized implementation in password_utils.py
4. Backward compatibility strategy (no changes needed)
5. Testing strategy (unit + integration + edge cases)
6. Security implications (no new risks introduced)

**Phase 1 - Design & Contracts**:
- **data-model.md**: Documented modified password handling behavior (no schema changes)
- **contracts/README.md**: Confirmed no API contract changes (internal fix only)
- **quickstart.md**: Created 15 manual test cases across 5 test suites
- **CLAUDE.md**: Updated agent context with technology stack

**Key Technical Decisions**:
- Truncate passwords to 72 bytes using `password.encode('utf-8')[:72]`
- Centralize logic in `backend/src/auth/password_utils.py`
- Apply truncation in both `hash_password()` and `verify_password()` functions
- Use `decode('utf-8', errors='ignore')` to handle split multi-byte characters
- No database migrations or schema changes required
- Full backward compatibility with existing password hashes

**Constitution Check**: All 8 principles passed (no violations)

## Outcome

- ✅ Impact: Complete implementation plan for critical authentication bug fix, ready for task breakdown and implementation
- 🧪 Tests: 15 manual test cases defined covering registration, login, backward compatibility, edge cases, and performance
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, contracts/README.md, quickstart.md), 1 updated (CLAUDE.md)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks, /sp.implement to execute fix
- 🧠 Reflection: Clear, focused plan with well-researched technical decisions and comprehensive testing strategy

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully on first attempt
- Graders run and results (PASS/FAIL): Constitution check: PASS (all 8 principles), Design completeness: PASS
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Proceed with /sp.tasks to break down into actionable implementation tasks
