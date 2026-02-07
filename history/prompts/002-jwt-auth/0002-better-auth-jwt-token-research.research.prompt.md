---
id: 0002
title: Better Auth JWT token format research
stage: research
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 002-jwt-auth
branch: 002-jwt-auth
user: user
command: none
labels: ["authentication", "jwt", "better-auth", "research", "security", "token-verification", "pyjwt"]
links:
  spec: specs/002-jwt-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-jwt-auth/better-auth-jwt-research.md
tests:
  - N/A (research stage)
---

## Prompt

Research Better Auth JWT token format and structure. Determine:
1. Standard JWT claims used by Better Auth (sub, exp, iat, etc.)
2. Token signing algorithm (HS256, RS256, etc.)
3. How user identity is encoded in the token
4. Token expiration handling
5. Shared secret configuration

Provide the expected token structure and verification requirements.

## Response snapshot

Conducted comprehensive research on Better Auth JWT token format and structure through multiple sources including Better Auth documentation, GitHub repository, PyJWT library documentation, and JWT standards (RFC 7519).

**Key Findings:**

1. **Better Auth Architecture**: Primarily uses cookie-based session management, not standalone JWT bearer tokens. JWT is supported as one of three cookie cache encoding strategies (compact, jwt, jwe).

2. **JWT Cookie Cache Strategy**:
   - Algorithm: HS256 (HMAC-SHA256)
   - Security: Signed but not encrypted (readable but tamper-proof)
   - Use case: External system interoperability
   - Library: jose (v6.1.3)

3. **Session Data Payload Structure**:
   ```typescript
   {
     session: { id, userId, token, expiresAt, ipAddress, userAgent },
     user: { id, email, name, emailVerified, image },
     updatedAt: number,
     version: string
   }
   ```

4. **Standard JWT Claims**:
   - `sub` (subject): User identifier
   - `exp` (expiration): Unix timestamp
   - `iat` (issued at): Unix timestamp
   - `iss` (issuer): Optional
   - `aud` (audience): Optional

5. **Token Signing**:
   - Algorithm: HS256 (HMAC with SHA-256)
   - Type: Symmetric signing with shared secret
   - Key requirement: Minimum 32 bytes recommended
   - Secret: `BETTER_AUTH_SECRET` environment variable

6. **Token Expiration**:
   - Session default: 7 days
   - Cookie cache default: 5 minutes
   - PyJWT automatically validates `exp` claim
   - Raises `jwt.ExpiredSignatureError` if expired

7. **Critical Gap Identified**: Better Auth documentation does not explicitly cover issuing standalone JWT tokens for API authentication with `Authorization: Bearer <token>` headers. The JWT strategy is only documented for cookie cache encoding, not service-to-service authentication.

**Deliverables:**
- Comprehensive research document with JWT structure, verification requirements, and PyJWT implementation examples
- Sample JWT token generation and verification code
- Security considerations and recommendations
- Identified gap between project assumptions and Better Auth capabilities

**Technical Testing:**
- Installed and tested PyJWT library (v2.11.0)
- Generated sample JWT tokens with HS256 algorithm
- Verified token encoding/decoding functionality
- Documented token structure with header, payload, and signature components

## Outcome

- ✅ Impact: Created comprehensive research document identifying Better Auth JWT token structure, standard claims, signing algorithm (HS256), and verification requirements. Discovered critical architectural gap between project assumptions and Better Auth's documented capabilities.
- 🧪 Tests: N/A (research stage - created PyJWT verification examples for future implementation)
- 📁 Files: Created specs/002-jwt-auth/better-auth-jwt-research.md with complete JWT token analysis
- 🔁 Next prompts: Verify Better Auth configuration for bearer token authentication, test actual token format with Better Auth instance, implement FastAPI JWT verification middleware
- 🧠 Reflection: Research revealed that Better Auth is designed for cookie-based browser authentication rather than standalone JWT bearer tokens. The project's CLAUDE.md assumes Better Auth can issue JWT tokens for API use, but this pattern is not documented. This gap needs to be addressed either through custom Better Auth configuration, cookie extraction, or alternative authentication approach. The research provides solid foundation for JWT verification implementation using PyJWT with HS256 algorithm and standard claims structure.

## Evaluation notes (flywheel)

- Failure modes observed: Web search API failures required pivoting to direct documentation fetching. Initial PyJWT import conflicts due to conflicting 'jwt' package required troubleshooting and reinstallation.
- Graders run and results (PASS/FAIL): Research completeness PASS (all 5 research questions answered), Documentation quality PASS (comprehensive with code examples), Gap identification PASS (critical architectural assumption identified)
- Prompt variant (if applicable): Standard research workflow with multiple source verification
- Next experiment (smallest change to try): Test Better Auth JWT token issuance with actual implementation to verify payload structure and determine if custom configuration is needed for bearer token authentication pattern
