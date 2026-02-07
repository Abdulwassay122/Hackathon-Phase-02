# Quickstart Guide: Testing CORS Configuration

**Feature**: Backend CORS Configuration (004-backend-cors-fix)
**Date**: 2026-02-07
**Objective**: Step-by-step guide for testing CORS configuration in development and production

## Prerequisites

- Backend running on http://localhost:8000
- Frontend running on http://localhost:3000 (for integration tests)
- Browser with DevTools (Chrome, Firefox, Edge)
- curl command-line tool (for manual testing)

## Setup: Configure CORS Origins

### Step 1: Set Environment Variable

**Option A: Using .env file (Recommended for development)**

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create or edit `.env` file:
   ```bash
   # Development configuration
   CORS_ORIGINS=http://localhost:3000
   ```

3. For multiple origins:
   ```bash
   # Multiple origins (comma-separated)
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

**Option B: Using command line (Temporary testing)**

Windows (PowerShell):
```powershell
$env:CORS_ORIGINS="http://localhost:3000"
python -m uvicorn src.main:app --reload
```

Windows (CMD):
```cmd
set CORS_ORIGINS=http://localhost:3000
python -m uvicorn src.main:app --reload
```

Linux/Mac:
```bash
export CORS_ORIGINS=http://localhost:3000
python -m uvicorn src.main:app --reload
```

### Step 2: Start Backend

```bash
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Creating database tables...
INFO:     Database tables created successfully
============================================================
CORS Configuration
============================================================
Allowed Origins (1):
  - http://localhost:3000
Allow Credentials: True
Allowed Methods: GET, POST, PUT, PATCH, DELETE
Allowed Headers: Authorization, Content-Type
Preflight Cache: 600 seconds
============================================================
INFO:     Application startup complete.
```

### Step 3: Start Frontend

```bash
cd frontend
npm run dev
```

**Expected Output**:
```
> frontend@0.1.0 dev
> next dev

  ▲ Next.js 16.1.6
  - Local:        http://localhost:3000

 ✓ Starting...
 ✓ Ready in 2.3s
```

## Test 1: Verify CORS Headers in Browser DevTools

### Objective
Verify that CORS headers are present in API responses when making requests from the frontend.

### Steps

1. **Open Frontend in Browser**:
   - Navigate to http://localhost:3000
   - Sign in with test credentials

2. **Open Browser DevTools**:
   - Press F12 or right-click → Inspect
   - Go to **Network** tab
   - Check "Preserve log" option

3. **Make an API Request**:
   - Navigate to the tasks page or perform any action that calls the backend
   - Look for API requests to http://localhost:8000

4. **Inspect Response Headers**:
   - Click on any API request (e.g., GET /api/users/123/tasks)
   - Go to **Headers** tab
   - Scroll to **Response Headers** section

5. **Verify CORS Headers Present**:
   ```
   access-control-allow-credentials: true
   access-control-allow-origin: http://localhost:3000
   ```

### Expected Results

✅ **Success Indicators**:
- No CORS errors in Console tab
- Response headers include `access-control-allow-origin: http://localhost:3000`
- Response headers include `access-control-allow-credentials: true`
- API requests complete successfully (status 200, 201, etc.)

❌ **Failure Indicators**:
- Console shows: "Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy"
- Response headers missing CORS headers
- API requests fail with network errors

### Troubleshooting

**Problem**: No CORS headers in response
- **Solution**: Check that CORS_ORIGINS is set correctly in backend .env file
- **Solution**: Restart backend after changing .env file

**Problem**: CORS error despite headers present
- **Solution**: Check that origin matches exactly (no trailing slash)
- **Solution**: Verify frontend is running on port 3000

## Test 2: Verify Preflight Requests (OPTIONS)

### Objective
Verify that preflight OPTIONS requests are handled correctly for complex requests (POST, PUT, PATCH, DELETE with Authorization header).

### Steps

1. **Open Browser DevTools** (F12)
2. **Go to Network tab**
3. **Filter by "OPTIONS" method**
4. **Perform a write operation** (create, update, or delete task)
5. **Observe preflight request**

### Expected Results

**Preflight Request** (automatically sent by browser):
```
Request Method: OPTIONS
Request URL: http://localhost:8000/api/users/123/tasks
Request Headers:
  Origin: http://localhost:3000
  Access-Control-Request-Method: POST
  Access-Control-Request-Headers: authorization,content-type
```

**Preflight Response** (from backend):
```
Status Code: 200 OK
Response Headers:
  access-control-allow-origin: http://localhost:3000
  access-control-allow-methods: GET, POST, PUT, PATCH, DELETE
  access-control-allow-headers: authorization, content-type
  access-control-allow-credentials: true
  access-control-max-age: 600
```

**Actual Request** (sent after successful preflight):
```
Request Method: POST
Request URL: http://localhost:8000/api/users/123/tasks
Request Headers:
  Origin: http://localhost:3000
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
  Content-Type: application/json
```

### Troubleshooting

**Problem**: Preflight request fails (status 4xx or 5xx)
- **Solution**: Check that CORSMiddleware is added before route registration in main.py
- **Solution**: Verify allow_methods includes the requested method

**Problem**: Actual request blocked after successful preflight
- **Solution**: Check that Authorization header is in allow_headers list
- **Solution**: Verify allow_credentials is True

## Test 3: Test with curl (Manual Preflight)

### Objective
Test CORS configuration without a browser using curl commands.

### Test 3.1: Simple GET Request

```bash
curl -X GET http://localhost:8000/api/users/123/tasks \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -v
```

**Expected Output**:
```
< HTTP/1.1 200 OK
< access-control-allow-origin: http://localhost:3000
< access-control-allow-credentials: true
< content-type: application/json
...
[{"id": 1, "title": "Test task", ...}]
```

### Test 3.2: Preflight OPTIONS Request

```bash
curl -X OPTIONS http://localhost:8000/api/users/123/tasks \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  -v
```

**Expected Output**:
```
< HTTP/1.1 200 OK
< access-control-allow-origin: http://localhost:3000
< access-control-allow-methods: GET, POST, PUT, PATCH, DELETE
< access-control-allow-headers: authorization, content-type
< access-control-allow-credentials: true
< access-control-max-age: 600
```

### Test 3.3: POST Request with JSON Body

```bash
curl -X POST http://localhost:8000/api/users/123/tasks \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Test description"}' \
  -v
```

**Expected Output**:
```
< HTTP/1.1 201 Created
< access-control-allow-origin: http://localhost:3000
< access-control-allow-credentials: true
< content-type: application/json
...
{"id": 456, "title": "Test task", ...}
```

## Test 4: Test Origin Blocking (Negative Test)

### Objective
Verify that requests from origins NOT in the allowed list are blocked by the browser.

### Steps

1. **Start frontend on a different port**:
   ```bash
   cd frontend
   PORT=3001 npm run dev
   ```

2. **Open browser to http://localhost:3001**

3. **Try to make API requests**:
   - Sign in (if authentication works)
   - Try to fetch tasks or perform any API operation

4. **Check Console for CORS errors**:
   ```
   Access to fetch at 'http://localhost:8000/api/users/123/tasks'
   from origin 'http://localhost:3001' has been blocked by CORS policy:
   No 'Access-Control-Allow-Origin' header is present on the requested resource.
   ```

### Expected Results

✅ **Success Indicators** (blocking works correctly):
- Console shows CORS error
- API requests fail with network error
- Response headers do NOT include `access-control-allow-origin: http://localhost:3001`

❌ **Failure Indicators** (blocking not working):
- No CORS errors (requests succeed)
- This indicates wildcard (*) may be configured (security issue!)

### Troubleshooting

**Problem**: Requests from port 3001 succeed (should fail)
- **Solution**: Check CORS_ORIGINS doesn't contain wildcard (*)
- **Solution**: Verify CORS_ORIGINS doesn't include http://localhost:3001
- **Solution**: Check that validation is rejecting wildcards

## Test 5: Test All HTTP Methods

### Objective
Verify that all required HTTP methods work with CORS.

### Test Matrix

| Method | Endpoint | Expected Status | CORS Headers Present |
|--------|----------|-----------------|---------------------|
| GET | /api/users/123/tasks | 200 OK | ✅ Yes |
| POST | /api/users/123/tasks | 201 Created | ✅ Yes |
| PUT | /api/users/123/tasks/456 | 200 OK | ✅ Yes |
| PATCH | /api/users/123/tasks/456 | 200 OK | ✅ Yes |
| DELETE | /api/users/123/tasks/456 | 204 No Content | ✅ Yes |

### Steps

1. **Open Browser DevTools** → Network tab
2. **Perform each operation from frontend**:
   - GET: View tasks list
   - POST: Create new task
   - PUT: Update entire task
   - PATCH: Update task field (e.g., toggle completion)
   - DELETE: Delete task

3. **Verify each request**:
   - Check for preflight OPTIONS request (for POST/PUT/PATCH/DELETE)
   - Check actual request includes CORS headers in response
   - Check no CORS errors in Console

### Expected Results

All methods should work without CORS errors. Each response should include:
```
access-control-allow-origin: http://localhost:3000
access-control-allow-credentials: true
```

## Test 6: Test Authorization Header

### Objective
Verify that the Authorization header with JWT token is allowed and sent correctly.

### Steps

1. **Sign in to frontend** (obtain JWT token)

2. **Open DevTools** → Network tab

3. **Make any authenticated API request**

4. **Inspect request headers**:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   Origin: http://localhost:3000
   ```

5. **Inspect response headers**:
   ```
   access-control-allow-origin: http://localhost:3000
   access-control-allow-credentials: true
   ```

### Expected Results

✅ **Success Indicators**:
- Authorization header is sent in request
- Backend receives and validates JWT token
- Response includes CORS headers
- Request succeeds (200, 201, etc.)

❌ **Failure Indicators**:
- Authorization header missing from request
- CORS error about Authorization header not allowed
- 401 Unauthorized (token not received by backend)

### Troubleshooting

**Problem**: Authorization header not sent by browser
- **Solution**: Verify allow_credentials=True in CORS config
- **Solution**: Check that "Authorization" is in allow_headers list

**Problem**: CORS error about Authorization header
- **Solution**: Ensure preflight response includes "authorization" in access-control-allow-headers

## Test 7: Test Error Responses

### Objective
Verify that CORS headers are present even on error responses (4xx, 5xx).

### Steps

1. **Trigger a 401 Unauthorized error**:
   - Make API request with invalid JWT token
   - Or make request without Authorization header

2. **Trigger a 404 Not Found error**:
   - Request non-existent task: GET /api/users/123/tasks/99999

3. **Trigger a 500 Internal Server Error**:
   - (If possible, create a scenario that causes server error)

4. **Check response headers for each error**

### Expected Results

All error responses should include CORS headers:
```
HTTP/1.1 401 Unauthorized
access-control-allow-origin: http://localhost:3000
access-control-allow-credentials: true
content-type: application/json
...
{"detail": "Invalid authentication credentials"}
```

**Why This Matters**: Without CORS headers on error responses, the browser blocks the error details, making debugging difficult.

## Test 8: Production Simulation

### Objective
Test CORS configuration with HTTPS origins (simulating production).

### Steps

1. **Update CORS_ORIGINS** for production-like origin:
   ```bash
   CORS_ORIGINS=https://app.example.com
   ```

2. **Restart backend**

3. **Test with curl** (simulating production frontend):
   ```bash
   curl -X GET http://localhost:8000/api/users/123/tasks \
     -H "Origin: https://app.example.com" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -v
   ```

4. **Verify response includes**:
   ```
   access-control-allow-origin: https://app.example.com
   ```

5. **Test that localhost:3000 is now blocked**:
   ```bash
   curl -X GET http://localhost:8000/api/users/123/tasks \
     -H "Origin: http://localhost:3000" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -v
   ```

6. **Verify response does NOT include CORS headers** (origin not allowed)

## Common Issues and Solutions

### Issue 1: CORS errors persist after configuration

**Symptoms**:
- CORS_ORIGINS is set correctly
- Backend logs show correct configuration
- Still getting CORS errors in browser

**Solutions**:
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Check for service workers (may cache old responses)
4. Verify frontend is actually running on the configured port
5. Check for typos in origin URL (trailing slash, protocol, port)

### Issue 2: Preflight requests failing

**Symptoms**:
- OPTIONS requests return 404 or 405
- CORS errors on POST/PUT/PATCH/DELETE but not GET

**Solutions**:
1. Verify CORSMiddleware is added BEFORE route registration
2. Check that allow_methods includes the requested method
3. Ensure FastAPI version supports automatic OPTIONS handling

### Issue 3: Authorization header not sent

**Symptoms**:
- Backend receives requests without Authorization header
- Frontend has token in localStorage
- 401 Unauthorized errors

**Solutions**:
1. Verify allow_credentials=True in CORS config
2. Check that "Authorization" is in allow_headers list
3. Verify frontend is attaching Authorization header to requests
4. Check that token is not expired

### Issue 4: Multiple origins not working

**Symptoms**:
- First origin works, others don't
- Parsing errors in backend logs

**Solutions**:
1. Check comma separation (no semicolons)
2. Verify no extra spaces (or that strip() is used)
3. Check each origin is valid (protocol, no trailing slash)
4. Review backend logs for validation warnings

## Verification Checklist

Use this checklist to verify complete CORS functionality:

- [ ] Backend starts without errors
- [ ] CORS configuration logged at startup
- [ ] Frontend can make GET requests without CORS errors
- [ ] Frontend can make POST requests without CORS errors
- [ ] Frontend can make PUT requests without CORS errors
- [ ] Frontend can make PATCH requests without CORS errors
- [ ] Frontend can make DELETE requests without CORS errors
- [ ] Preflight OPTIONS requests succeed
- [ ] Authorization header is sent and received
- [ ] Response headers include access-control-allow-origin
- [ ] Response headers include access-control-allow-credentials
- [ ] Requests from disallowed origins are blocked
- [ ] Error responses (4xx, 5xx) include CORS headers
- [ ] No wildcard (*) in any CORS setting
- [ ] Multiple origins work (if configured)
- [ ] curl tests pass for all methods

## Next Steps

After verifying CORS configuration:

1. **Document any issues** encountered during testing
2. **Update .env.example** with CORS_ORIGINS documentation
3. **Add CORS setup to README** for other developers
4. **Test with actual frontend** integration
5. **Prepare for production** deployment with HTTPS origins

## Additional Resources

- FastAPI CORS Documentation: https://fastapi.tiangolo.com/tutorial/cors/
- MDN CORS Guide: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- Chrome DevTools Network Tab: https://developer.chrome.com/docs/devtools/network/
