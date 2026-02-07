# Quickstart Guide: Testing Backend Authentication Endpoints

**Feature**: 001-backend-auth-endpoints
**Date**: 2026-02-07
**Objective**: Step-by-step guide for testing user signup and login endpoints

## Prerequisites

- Backend running on http://localhost:8000
- curl command-line tool (for manual testing)
- Python 3.11+ with PyJWT installed (for token inspection)
- PostgreSQL database accessible (Neon or local)

## Setup

### Step 1: Install Dependencies

```bash
cd backend
pip install passlib[bcrypt]
```

**Note**: FastAPI, SQLModel, and PyJWT are already installed from previous features.

### Step 2: Verify Environment Variables

Check that `backend/.env` contains:

```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-at-least-32-characters-long-for-security
JWT_ALGORITHM=HS256
```

**Important**: The `BETTER_AUTH_SECRET` must be at least 32 characters for security.

### Step 3: Start Backend Server

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Creating database tables...
INFO:     Database tables created successfully
INFO:     Application startup complete.
```

**Verify**: Check that the `users` table was created in the database.

---

## Test 1: User Signup (Registration)

### Objective
Verify that new users can register with email, password, and name, and receive a JWT token.

### Test 1.1: Valid Signup

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123",
    "name": "Test User"
  }'
```

**Expected Response** (201 Created):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "testuser@example.com",
    "name": "Test User"
  }
}
```

**Verification Steps**:
1. ✅ Status code is 201 Created
2. ✅ Response includes `access_token` field
3. ✅ Response includes `token_type: "bearer"`
4. ✅ Response includes `user` object with id, email, name
5. ✅ User object does NOT include password or password_hash
6. ✅ Check database: User record exists with hashed password

**Database Verification**:
```sql
SELECT id, email, name, created_at FROM users WHERE email = 'testuser@example.com';
```

Expected: One row with the user data.

### Test 1.2: Duplicate Email (Negative Test)

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "AnotherPass456",
    "name": "Another User"
  }'
```

**Expected Response** (409 Conflict):
```json
{
  "detail": "Email already registered"
}
```

**Verification Steps**:
1. ✅ Status code is 409 Conflict
2. ✅ Error message indicates email is already registered
3. ✅ No new user created in database

### Test 1.3: Password Too Short (Negative Test)

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "Pass1",
    "name": "New User"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "Password must be at least 8 characters"
}
```

**Verification Steps**:
1. ✅ Status code is 400 Bad Request
2. ✅ Error message indicates password length requirement
3. ✅ No user created in database

### Test 1.4: Password Missing Number (Negative Test)

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePassword",
    "name": "New User"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "Password must contain at least one number"
}
```

### Test 1.5: Password Missing Letter (Negative Test)

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "12345678",
    "name": "New User"
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "Password must contain at least one letter"
}
```

### Test 1.6: Invalid Email Format (Negative Test)

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "not-an-email",
    "password": "SecurePass123",
    "name": "New User"
  }'
```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Test 1.7: Empty Name (Negative Test)

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123",
    "name": "   "
  }'
```

**Expected Response** (400 Bad Request):
```json
{
  "detail": "Name cannot be empty"
}
```

---

## Test 2: User Login (Authentication)

### Test 2.1: Valid Login

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "testuser@example.com",
    "name": "Test User"
  }
}
```

**Verification Steps**:
1. ✅ Status code is 200 OK
2. ✅ Response includes `access_token` field
3. ✅ Response includes `token_type: "bearer"`
4. ✅ Response includes `user` object matching the registered user
5. ✅ Token is different from signup token (new token generated)

### Test 2.2: Invalid Password (Negative Test)

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "WrongPassword123"
  }'
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Invalid email or password"
}
```

**Verification Steps**:
1. ✅ Status code is 401 Unauthorized
2. ✅ Error message is generic (doesn't reveal if email exists)
3. ✅ No token returned

### Test 2.3: Non-existent Email (Negative Test)

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Invalid email or password"
}
```

**Verification Steps**:
1. ✅ Status code is 401 Unauthorized
2. ✅ Error message is identical to invalid password (prevents user enumeration)
3. ✅ No token returned

### Test 2.4: Missing Password (Negative Test)

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com"
  }'
```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Test 3: JWT Token Verification

### Objective
Verify that tokens issued by signup/login endpoints are compatible with existing JWT verification middleware.

### Test 3.1: Decode Token (Manual Inspection)

**Python Script**:
```python
import jwt

# Copy token from signup or login response
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Decode without verification (for inspection)
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
```

**Expected Output**:
```python
{
  'sub': '1',           # User ID as string
  'email': 'testuser@example.com',
  'exp': 1707436800     # Expiration timestamp
}
```

**Verification Steps**:
1. ✅ Token contains `sub` claim with user ID as string
2. ✅ Token contains `email` claim
3. ✅ Token contains `exp` claim (expiration)
4. ✅ Expiration is ~24 hours from now

### Test 3.2: Use Token with Protected Endpoint

**Request** (using token from signup/login):
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

curl -X GET http://localhost:8000/api/users/1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
[]
```
or
```json
[
  {
    "id": 1,
    "title": "Sample task",
    "description": "Task description",
    "completed": false,
    "user_id": 1
  }
]
```

**Verification Steps**:
1. ✅ Status code is 200 OK (not 401 Unauthorized)
2. ✅ Token is accepted by existing JWT verification middleware
3. ✅ User can access their own tasks
4. ✅ User ID from token matches user ID in URL

### Test 3.3: Token Expiration (Time-based Test)

**Note**: This test requires waiting 24 hours or manually creating an expired token.

**Create Expired Token** (Python):
```python
import jwt
from datetime import datetime, timedelta

SECRET = "your-secret-key-at-least-32-characters-long-for-security"

payload = {
    "sub": "1",
    "email": "testuser@example.com",
    "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
}

expired_token = jwt.encode(payload, SECRET, algorithm="HS256")
print(expired_token)
```

**Request** (using expired token):
```bash
curl -X GET http://localhost:8000/api/users/1/tasks \
  -H "Authorization: Bearer $EXPIRED_TOKEN"
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Token has expired"
}
```

**Verification Steps**:
1. ✅ Status code is 401 Unauthorized
2. ✅ Error message indicates token expiration
3. ✅ Access denied to protected endpoint

---

## Test 4: User Isolation

### Objective
Verify that users can only access their own data using JWT tokens.

### Test 4.1: Create Second User

**Request**:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user2@example.com",
    "password": "SecurePass456",
    "name": "User Two"
  }'
```

**Save the token** from the response as `TOKEN_USER2`.

### Test 4.2: Attempt Cross-User Access (Negative Test)

**Request** (User 2 trying to access User 1's tasks):
```bash
TOKEN_USER2="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

curl -X GET http://localhost:8000/api/users/1/tasks \
  -H "Authorization: Bearer $TOKEN_USER2"
```

**Expected Response** (403 Forbidden):
```json
{
  "detail": "Access forbidden: user ID mismatch"
}
```

**Verification Steps**:
1. ✅ Status code is 403 Forbidden
2. ✅ User 2 cannot access User 1's tasks
3. ✅ User ID from token (2) doesn't match URL user ID (1)

---

## Test 5: Password Security

### Objective
Verify that passwords are securely hashed and never exposed.

### Test 5.1: Check Database for Hashed Passwords

**SQL Query**:
```sql
SELECT id, email, password_hash FROM users WHERE email = 'testuser@example.com';
```

**Expected Result**:
```
id | email                  | password_hash
---+------------------------+--------------------------------------------------------------
 1 | testuser@example.com   | $2b$12$abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQR
```

**Verification Steps**:
1. ✅ `password_hash` field contains bcrypt hash (starts with `$2b$12$`)
2. ✅ Hash is 60 characters long
3. ✅ Hash is different from plaintext password
4. ✅ No plaintext password stored anywhere

### Test 5.2: Verify API Never Exposes Password Hash

**Request** (check all auth responses):
```bash
# Signup response
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user3@example.com", "password": "SecurePass789", "name": "User Three"}'

# Login response
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user3@example.com", "password": "SecurePass789"}'
```

**Verification Steps**:
1. ✅ Response does NOT include `password` field
2. ✅ Response does NOT include `password_hash` field
3. ✅ Response only includes `id`, `email`, `name` in user object

---

## Test 6: Integration with Existing Features

### Objective
Verify that authentication endpoints integrate seamlessly with existing task management features.

### Test 6.1: Complete User Flow

**Step 1: Signup**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "flowtest@example.com",
    "password": "FlowTest123",
    "name": "Flow Test User"
  }'
```

Save the `access_token` from response.

**Step 2: Create Task**
```bash
TOKEN="<access_token_from_signup>"

curl -X POST http://localhost:8000/api/users/1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "My first task",
    "description": "Created after signup"
  }'
```

**Step 3: Login**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "flowtest@example.com",
    "password": "FlowTest123"
  }'
```

Save the new `access_token`.

**Step 4: Retrieve Tasks**
```bash
NEW_TOKEN="<access_token_from_login>"

curl -X GET http://localhost:8000/api/users/1/tasks \
  -H "Authorization: Bearer $NEW_TOKEN"
```

**Expected Result**: Task created in Step 2 is returned.

**Verification Steps**:
1. ✅ User can signup and immediately create tasks
2. ✅ User can login and access previously created tasks
3. ✅ Tokens from signup and login both work with task endpoints
4. ✅ User isolation is maintained (user_id matches token)

---

## Troubleshooting

### Issue 1: "Email already registered" on first signup

**Cause**: User already exists in database from previous test.

**Solution**:
```sql
DELETE FROM users WHERE email = 'testuser@example.com';
```

### Issue 2: "Invalid email or password" on valid credentials

**Possible Causes**:
1. Password was changed after signup
2. Database was reset but user is trying old credentials
3. Password hashing is not working correctly

**Solution**:
1. Try signing up again with new email
2. Check backend logs for password verification errors
3. Verify passlib[bcrypt] is installed

### Issue 3: Token not accepted by protected endpoints

**Possible Causes**:
1. BETTER_AUTH_SECRET mismatch between token generation and verification
2. JWT_ALGORITHM mismatch
3. Token format incorrect

**Solution**:
1. Verify `.env` has same BETTER_AUTH_SECRET for both
2. Check that JWT_ALGORITHM is "HS256"
3. Decode token manually to inspect structure

### Issue 4: 500 Internal Server Error

**Possible Causes**:
1. Database connection failed
2. passlib not installed
3. Code error in implementation

**Solution**:
1. Check backend logs for stack trace
2. Verify DATABASE_URL is correct
3. Ensure all dependencies installed: `pip install passlib[bcrypt]`

---

## Success Criteria Checklist

Use this checklist to verify complete authentication functionality:

- [ ] User can signup with valid email, password, and name (201 Created)
- [ ] Signup returns JWT token and user data
- [ ] Duplicate email signup is rejected (409 Conflict)
- [ ] Weak passwords are rejected (400 Bad Request)
- [ ] Invalid email format is rejected (422 Unprocessable Entity)
- [ ] User can login with correct credentials (200 OK)
- [ ] Login returns JWT token and user data
- [ ] Invalid credentials are rejected (401 Unauthorized)
- [ ] Generic error message for login failures (no user enumeration)
- [ ] JWT tokens contain correct claims (sub, email, exp)
- [ ] Tokens expire after 24 hours
- [ ] Tokens work with existing protected endpoints
- [ ] User isolation is enforced (403 for cross-user access)
- [ ] Passwords are hashed in database (bcrypt)
- [ ] Password hashes never exposed in API responses
- [ ] All HTTP status codes match specification

---

## Next Steps

After verifying authentication endpoints:

1. **Run /sp.tasks** to generate implementation task breakdown
2. **Implement User model** in backend/src/models/user_model.py
3. **Implement password utilities** in backend/src/auth/password.py
4. **Implement auth routes** in backend/src/api/auth_routes.py
5. **Add token generation** to backend/src/auth/jwt_handler.py
6. **Register routes** in backend/src/main.py
7. **Test with this quickstart guide**
8. **Prepare for frontend integration** (Phase 3)
