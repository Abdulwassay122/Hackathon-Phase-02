# Research: Fix Password Length Error (72-Byte Limit)

**Feature**: 006-fix-password-length
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document captures research findings and technical decisions for implementing password truncation to fix the bcrypt 72-byte limit error. The research focuses on proper byte-length calculation, truncation strategies, and backward compatibility considerations.

---

## Research Question 1: How does bcrypt handle password length limits?

### Decision
Bcrypt has a hard limit of 72 bytes for password input. Any bytes beyond the 72nd are silently ignored by the algorithm. This is a fundamental limitation of the bcrypt specification, not a bug.

### Rationale
- Bcrypt was designed with a 72-byte limit to balance security and performance
- The algorithm only uses the first 72 bytes of input regardless of actual password length
- Attempting to hash passwords longer than 72 bytes without truncation causes the passlib library to raise an error
- Pre-truncating passwords to 72 bytes is the standard solution and does not reduce security

### Alternatives Considered
1. **Switch to a different hashing algorithm (e.g., Argon2)**
   - Rejected: Violates constraint "no change to hashing algorithm"
   - Rejected: Would require re-hashing all existing passwords (breaking change)
   - Rejected: Adds unnecessary complexity for a simple fix

2. **Reject passwords longer than 72 bytes**
   - Rejected: Poor user experience - users expect long passwords to work
   - Rejected: Doesn't solve the problem for users who already created long passwords
   - Rejected: Violates requirement FR-001 (accept passwords of any length)

3. **Hash the password first, then hash the hash**
   - Rejected: Adds unnecessary complexity
   - Rejected: Non-standard approach that could introduce security issues
   - Rejected: Truncation is simpler and equally secure

### Implementation Approach
Pre-truncate passwords to 72 bytes before passing to bcrypt.hashpw() and bcrypt.checkpw(). This ensures consistent behavior and prevents the error from occurring.

---

## Research Question 2: How to correctly calculate byte length for UTF-8 strings in Python?

### Decision
Use `password.encode('utf-8')[:72]` to truncate passwords to 72 bytes, accounting for multi-byte UTF-8 characters.

### Rationale
- Python strings are Unicode by default, but bcrypt operates on bytes
- A single Unicode character can be 1-4 bytes in UTF-8 encoding
- Character count ≠ byte count for non-ASCII characters
- Truncating by character count could result in >72 bytes
- Truncating by byte count ensures we never exceed the limit

### Example
```python
# Character count vs byte count
password = "café" + "x" * 70  # 74 characters
byte_length = len(password.encode('utf-8'))  # 76 bytes (é is 2 bytes)

# Correct truncation
truncated = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
```

### Alternatives Considered
1. **Truncate by character count**
   - Rejected: Doesn't account for multi-byte characters
   - Rejected: Could still exceed 72 bytes with non-ASCII characters
   - Rejected: Would fail for passwords with emojis or special characters

2. **Reject passwords with multi-byte characters**
   - Rejected: Poor user experience
   - Rejected: Unnecessarily restrictive
   - Rejected: Not required by bcrypt

3. **Use ASCII encoding only**
   - Rejected: Doesn't support international characters
   - Rejected: Reduces password entropy for non-English users
   - Rejected: UTF-8 is the standard

### Edge Case Handling
When truncating at byte 72, we might cut in the middle of a multi-byte character. Use `decode('utf-8', errors='ignore')` to handle this gracefully by dropping incomplete characters.

---

## Research Question 3: Where should password truncation be implemented?

### Decision
Implement password truncation in a centralized utility function in `backend/src/auth/password_utils.py` that is called by both signup and login endpoints.

### Rationale
- Centralized logic ensures consistency across all authentication flows
- Single source of truth for password handling
- Easy to test in isolation
- Follows Principle II (Clear Separation of Concerns)
- Prevents code duplication

### Implementation Pattern
```python
# backend/src/auth/password_utils.py
def truncate_password(password: str) -> bytes:
    """
    Truncate password to 72 bytes for bcrypt compatibility.

    Args:
        password: Raw password string

    Returns:
        Password truncated to 72 bytes as UTF-8 encoded bytes
    """
    return password.encode('utf-8')[:72]

def hash_password(password: str) -> str:
    """Hash password with bcrypt after truncation."""
    truncated = truncate_password(password)
    return bcrypt.hashpw(truncated, bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash after truncation."""
    truncated = truncate_password(password)
    return bcrypt.checkpw(truncated, hashed.encode('utf-8'))
```

### Alternatives Considered
1. **Truncate in API endpoints directly**
   - Rejected: Code duplication (signup and login both need it)
   - Rejected: Violates separation of concerns
   - Rejected: Harder to test and maintain

2. **Truncate in the User model**
   - Rejected: Models should not contain business logic
   - Rejected: Password hashing is authentication concern, not data model concern
   - Rejected: Violates separation of concerns

3. **Modify passlib library directly**
   - Rejected: Not maintainable
   - Rejected: Would be overwritten on library updates
   - Rejected: Unnecessary when we can wrap the calls

---

## Research Question 4: How to ensure backward compatibility with existing passwords?

### Decision
Existing password hashes will continue to work without modification because bcrypt already ignores bytes beyond 72. The truncation logic only affects new password hashing and verification operations.

### Rationale
- Existing hashes were created from the first 72 bytes of the original password
- Our truncation logic produces the same first 72 bytes
- No database migration needed
- No user impact - existing users can continue logging in

### Verification Strategy
1. Test that existing short passwords (<72 bytes) still authenticate correctly
2. Test that existing long passwords (if any exist) authenticate with first 72 bytes
3. Verify no changes to password_hash column in database

### Alternatives Considered
1. **Re-hash all existing passwords**
   - Rejected: Unnecessary - existing hashes already work
   - Rejected: Would require users to reset passwords
   - Rejected: Adds complexity with no benefit

2. **Add a migration flag to track truncated passwords**
   - Rejected: Unnecessary - truncation is transparent
   - Rejected: Adds database schema changes
   - Rejected: No functional benefit

---

## Research Question 5: What testing strategy should be used?

### Decision
Implement three levels of testing:
1. **Unit tests**: Test truncate_password() function with various inputs
2. **Integration tests**: Test signup/login endpoints with long passwords
3. **Edge case tests**: Test boundary conditions (exactly 72 bytes, multi-byte characters)

### Rationale
- Unit tests verify truncation logic in isolation
- Integration tests verify end-to-end authentication flow
- Edge case tests ensure robustness with unusual inputs
- Follows Principle V (Comprehensive Testability and Verification)

### Test Cases
**Unit Tests** (test_password_utils.py):
- Password shorter than 72 bytes (no truncation)
- Password exactly 72 bytes (no truncation)
- Password longer than 72 bytes (truncation occurs)
- Password with multi-byte UTF-8 characters
- Password with emojis (4-byte characters)
- Empty password (edge case)

**Integration Tests** (test_auth_endpoints.py):
- Signup with 80-character password → success
- Login with 80-character password → success
- Signup with 100-character password → success
- Login with 100-character password → success
- Signup with password containing emojis → success
- Verify backward compatibility with existing short passwords

### Alternatives Considered
1. **Manual testing only**
   - Rejected: Not reproducible
   - Rejected: Doesn't catch regressions
   - Rejected: Violates Principle V

2. **Integration tests only**
   - Rejected: Doesn't test truncation logic in isolation
   - Rejected: Harder to debug failures
   - Rejected: Incomplete coverage

---

## Research Question 6: What are the security implications of password truncation?

### Decision
Password truncation to 72 bytes does not introduce new security risks because bcrypt already only uses the first 72 bytes. This fix makes the existing behavior explicit and prevents errors.

### Rationale
- Bcrypt's 72-byte limit is a known characteristic of the algorithm
- Users who create passwords longer than 72 bytes can already authenticate with just the first 72 bytes
- Truncation makes this behavior explicit rather than implicit
- No reduction in password entropy for passwords under 72 bytes
- For passwords over 72 bytes, entropy is limited by bcrypt's design, not our truncation

### Security Considerations
1. **Password entropy**: 72 bytes = 576 bits of potential entropy, far exceeding security requirements
2. **Brute force resistance**: Bcrypt's computational cost is the primary defense, not password length
3. **User awareness**: Users are not notified of truncation (transparent), which is acceptable because:
   - Bcrypt already truncates silently
   - 72 bytes is sufficient for any practical password
   - Notification would confuse users without security benefit

### Alternatives Considered
1. **Notify users when passwords are truncated**
   - Rejected: Violates constraint "transparent handling"
   - Rejected: Confusing to users
   - Rejected: No security benefit

2. **Enforce maximum password length**
   - Rejected: Poor user experience
   - Rejected: Doesn't solve existing long password problem
   - Rejected: Truncation is simpler and equally secure

---

## Summary of Decisions

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

1. ✅ **Phase 0 Complete**: Research findings documented
2. ⏭️ **Phase 1 Next**: Generate data-model.md, contracts/, quickstart.md
3. ⏭️ **Phase 2 Next**: Generate tasks.md via `/sp.tasks` command
4. ⏭️ **Implementation**: Execute tasks via `/sp.implement` command

**Research Complete**: All technical decisions documented with rationale. Ready to proceed with design phase.
