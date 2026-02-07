# Phase 0 Research: FastAPI CORS Configuration

**Feature**: Backend CORS Configuration (004-backend-cors-fix)
**Date**: 2026-02-07
**Objective**: Understand FastAPI CORS middleware capabilities, best practices, and security considerations

## FastAPI CORSMiddleware API

### Core Parameters

FastAPI provides `fastapi.middleware.cors.CORSMiddleware` with the following key parameters:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],           # List of allowed origins
    allow_credentials=True,                             # Allow cookies/auth headers
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],  # Allowed HTTP methods
    allow_headers=["Authorization", "Content-Type"],    # Allowed request headers
    expose_headers=[],                                  # Headers exposed to browser
    max_age=600,                                        # Preflight cache duration (seconds)
)
```

### Parameter Details

1. **`allow_origins`** (List[str]):
   - List of origins that are allowed to make cross-origin requests
   - Must be exact matches (e.g., `http://localhost:3000`)
   - Use `["*"]` for wildcard (NOT RECOMMENDED for production)
   - Empty list `[]` blocks all cross-origin requests

2. **`allow_credentials`** (bool):
   - If `True`, allows cookies and Authorization headers
   - Required for JWT authentication
   - Cannot be used with wildcard origins (`["*"]`)

3. **`allow_methods`** (List[str]):
   - HTTP methods allowed for cross-origin requests
   - Common values: `["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]`
   - `OPTIONS` is automatically handled for preflight requests

4. **`allow_headers`** (List[str]):
   - Request headers allowed in cross-origin requests
   - Common values: `["Authorization", "Content-Type", "Accept"]`
   - Browser automatically includes standard headers

5. **`expose_headers`** (List[str]):
   - Response headers that browser can access via JavaScript
   - By default, only simple headers are exposed
   - Not needed for basic CORS functionality

6. **`max_age`** (int):
   - How long (in seconds) browsers cache preflight responses
   - Default: 600 seconds (10 minutes)
   - Reduces preflight request frequency

## Environment Variable Parsing

### Comma-Separated Origins Pattern

**Recommended Approach**:
```python
import os

# Read from environment variable
cors_origins_str = os.getenv("CORS_ORIGINS", "")

# Parse comma-separated values
if cors_origins_str:
    cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
else:
    cors_origins = []
    # Log warning: CORS_ORIGINS not set
```

**Environment Variable Format**:
```bash
# Single origin
CORS_ORIGINS=http://localhost:3000

# Multiple origins (comma-separated, no spaces)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://app.example.com

# Multiple origins (with spaces - strip() handles this)
CORS_ORIGINS=http://localhost:3000, http://localhost:3001, https://app.example.com
```

### Validation Rules

1. **URL Format Validation**:
   - Must start with `http://` or `https://`
   - Must not end with trailing slash (FastAPI is strict about this)
   - Must include protocol (no `localhost:3000` without `http://`)

2. **Security Validation**:
   - Reject wildcard `*` in production environments
   - Warn if using `http://` in production (should use `https://`)
   - Reject empty strings or whitespace-only values

3. **Example Validation Function**:
```python
def validate_cors_origin(origin: str) -> bool:
    """Validate a single CORS origin URL"""
    if not origin or origin.isspace():
        return False
    if origin == "*":
        # Log warning: wildcard not recommended
        return False
    if not origin.startswith(("http://", "https://")):
        return False
    if origin.endswith("/"):
        # Log warning: remove trailing slash
        return False
    return True
```

## Security Implications

### Wildcard Origins (`["*"]`)

**Risk**: Allows ANY website to make requests to your API
- Attacker can create malicious website that calls your API
- User's browser will send cookies/tokens to your API
- Attacker can read responses and steal data

**When Acceptable**:
- Public APIs with no authentication
- Read-only endpoints with public data
- Development/testing environments only

**Never Use With**:
- `allow_credentials=True` (FastAPI will reject this combination)
- Authenticated endpoints
- Production environments with sensitive data

### Wildcard Headers (`["*"]`)

**Risk**: Allows any custom header in requests
- May expose internal headers to attackers
- Harder to audit what headers are actually used
- Violates principle of least privilege

**Best Practice**: Explicitly list required headers
```python
allow_headers=["Authorization", "Content-Type"]  # Good
allow_headers=["*"]  # Bad
```

### Credentials and Authentication

**Key Points**:
1. `allow_credentials=True` is REQUIRED for JWT authentication
2. Browser will NOT send Authorization header without this setting
3. Cannot combine with wildcard origins (security restriction)
4. Credentials include: cookies, Authorization header, TLS client certificates

**Security Checklist**:
- ✅ Use explicit origin list (no wildcards)
- ✅ Enable `allow_credentials=True` for JWT
- ✅ Use HTTPS in production
- ✅ Validate JWT tokens on backend (CORS doesn't replace auth)
- ✅ Set appropriate token expiry times

## Preflight Request Handling

### What is a Preflight Request?

Browser automatically sends an OPTIONS request before certain cross-origin requests:
- Requests with custom headers (e.g., Authorization)
- Requests with methods other than GET/POST
- Requests with Content-Type other than simple types

### FastAPI Automatic Handling

**Good News**: FastAPI's CORSMiddleware handles preflight automatically
- No need to define OPTIONS routes manually
- Middleware intercepts OPTIONS requests
- Returns appropriate CORS headers

**Preflight Flow**:
1. Browser sends OPTIONS request with:
   - `Origin: http://localhost:3000`
   - `Access-Control-Request-Method: POST`
   - `Access-Control-Request-Headers: authorization,content-type`

2. FastAPI CORSMiddleware responds with:
   - `Access-Control-Allow-Origin: http://localhost:3000`
   - `Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE`
   - `Access-Control-Allow-Headers: authorization, content-type`
   - `Access-Control-Allow-Credentials: true`
   - `Access-Control-Max-Age: 600`

3. Browser caches response for `max_age` seconds

4. Browser sends actual request (e.g., POST with Authorization header)

### Testing Preflight Requests

**Using curl**:
```bash
# Simulate preflight request
curl -X OPTIONS http://localhost:8000/api/users/123/tasks \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  -v

# Check for CORS headers in response
```

**Using Browser DevTools**:
1. Open Network tab
2. Filter by "OPTIONS" method
3. Look for preflight requests before actual requests
4. Inspect response headers

## Common CORS Misconfigurations

### 1. Missing `allow_credentials=True`

**Symptom**: Authorization header not sent by browser
**Error**: "Request header field authorization is not allowed by Access-Control-Allow-Headers"
**Fix**: Set `allow_credentials=True` in CORSMiddleware

### 2. Trailing Slash in Origin

**Symptom**: CORS errors even with correct origin
**Error**: Origin mismatch
**Fix**: Remove trailing slash from origin URL
```python
# Wrong
allow_origins=["http://localhost:3000/"]

# Correct
allow_origins=["http://localhost:3000"]
```

### 3. Missing Protocol in Origin

**Symptom**: CORS errors
**Error**: Origin format invalid
**Fix**: Include `http://` or `https://`
```python
# Wrong
allow_origins=["localhost:3000"]

# Correct
allow_origins=["http://localhost:3000"]
```

### 4. Wildcard with Credentials

**Symptom**: FastAPI startup error or CORS errors
**Error**: "Cannot use wildcard origin with credentials"
**Fix**: Use explicit origin list
```python
# Wrong
allow_origins=["*"],
allow_credentials=True

# Correct
allow_origins=["http://localhost:3000"],
allow_credentials=True
```

### 5. CORS Middleware Order

**Symptom**: CORS headers missing on some responses
**Error**: Middleware not applied to all routes
**Fix**: Add CORSMiddleware BEFORE other middleware and route registration
```python
# Correct order
app = FastAPI()
app.add_middleware(CORSMiddleware, ...)  # First
app.add_middleware(OtherMiddleware, ...)  # After CORS
app.include_router(router)  # After all middleware
```

### 6. Missing CORS on Error Responses

**Symptom**: CORS errors on 4xx/5xx responses
**Error**: Browser blocks error responses
**Fix**: CORSMiddleware automatically adds headers to all responses (including errors)
- No special handling needed if middleware is configured correctly

## Testing Strategies

### 1. Unit Tests (pytest)

Test configuration parsing and validation:
```python
def test_parse_cors_origins_single():
    os.environ["CORS_ORIGINS"] = "http://localhost:3000"
    origins = parse_cors_origins()
    assert origins == ["http://localhost:3000"]

def test_parse_cors_origins_multiple():
    os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://localhost:3001"
    origins = parse_cors_origins()
    assert len(origins) == 2

def test_validate_cors_origin_invalid():
    assert not validate_cors_origin("localhost:3000")  # Missing protocol
    assert not validate_cors_origin("http://localhost:3000/")  # Trailing slash
    assert not validate_cors_origin("")  # Empty
```

### 2. Integration Tests (pytest + TestClient)

Test CORS headers in responses:
```python
from fastapi.testclient import TestClient

def test_cors_preflight_request():
    response = client.options(
        "/api/users/123/tasks",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "authorization" in response.headers["access-control-allow-headers"].lower()

def test_cors_actual_request():
    response = client.get(
        "/api/users/123/tasks",
        headers={
            "Origin": "http://localhost:3000",
            "Authorization": "Bearer test-token"
        }
    )
    assert "access-control-allow-origin" in response.headers
```

### 3. Manual Browser Tests

**Test Checklist**:
- [ ] Start backend with CORS_ORIGINS=http://localhost:3000
- [ ] Start frontend on localhost:3000
- [ ] Open browser DevTools (F12) → Network tab
- [ ] Make API request from frontend
- [ ] Verify no CORS errors in Console tab
- [ ] Verify OPTIONS preflight request appears (for POST/PUT/PATCH/DELETE)
- [ ] Verify response headers include Access-Control-Allow-Origin
- [ ] Test with Authorization header (JWT token)
- [ ] Test all HTTP methods (GET, POST, PUT, PATCH, DELETE)
- [ ] Test with frontend on different port (should fail)

### 4. curl Tests

Test without browser:
```bash
# Test simple GET request
curl -X GET http://localhost:8000/api/users/123/tasks \
  -H "Origin: http://localhost:3000" \
  -v

# Test preflight for POST request
curl -X OPTIONS http://localhost:8000/api/users/123/tasks \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  -v

# Test with Authorization header
curl -X GET http://localhost:8000/api/users/123/tasks \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer test-token" \
  -v
```

## Best Practices Summary

1. **Never use wildcards in production**
   - Explicit origin list only
   - Explicit header list only
   - Explicit method list only

2. **Always enable credentials for JWT auth**
   - `allow_credentials=True`
   - Cannot combine with wildcard origins

3. **Use environment variables for configuration**
   - Different origins for dev/staging/prod
   - No hardcoded values in code

4. **Validate origin URLs**
   - Check protocol (http:// or https://)
   - Check for trailing slashes
   - Reject malformed URLs

5. **Add CORS middleware early**
   - Before other middleware
   - Before route registration
   - Ensures all responses include CORS headers

6. **Test thoroughly**
   - Unit tests for parsing/validation
   - Integration tests for headers
   - Manual browser tests for real-world behavior

7. **Log configuration at startup**
   - Log allowed origins
   - Warn if CORS_ORIGINS not set
   - Warn if using wildcards

8. **Use HTTPS in production**
   - HTTP acceptable for localhost development
   - HTTPS required for production security

## References

- FastAPI CORS Documentation: https://fastapi.tiangolo.com/tutorial/cors/
- MDN CORS Guide: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- OWASP CORS Security: https://owasp.org/www-community/attacks/CORS_OriginHeaderScrutiny

## Implementation Checklist

- [ ] Read CORS_ORIGINS from environment variable
- [ ] Parse comma-separated origins
- [ ] Validate origin URLs (protocol, no trailing slash)
- [ ] Add CORSMiddleware to FastAPI app
- [ ] Set allow_credentials=True
- [ ] Explicitly list allowed headers: ["Authorization", "Content-Type"]
- [ ] Explicitly list allowed methods: ["GET", "POST", "PUT", "PATCH", "DELETE"]
- [ ] Log configuration at startup
- [ ] Warn if CORS_ORIGINS not set
- [ ] Add unit tests for parsing/validation
- [ ] Add integration tests for CORS headers
- [ ] Document in .env.example
- [ ] Test with browser and frontend
