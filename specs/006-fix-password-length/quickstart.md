# Quickstart: Fix Password Length Error (72-Byte Limit)

**Feature**: 006-fix-password-length
**Date**: 2026-02-08
**Purpose**: Manual testing guide for password length fix

## Overview

This guide provides step-by-step instructions for manually testing the password length fix. The fix prevents the "password cannot be longer than 72 bytes" error by transparently truncating passwords before hashing and verification.

---

## Prerequisites

1. **Backend API Running**: FastAPI backend must be running on `http://localhost:8000`
2. **Database**: Neon PostgreSQL database must be accessible
3. **Testing Tool**: Use curl, Postman, or browser DevTools
4. **Clean State**: Start with a fresh database or use unique email addresses for each test

---

## Test Suite 1: User Registration with Long Passwords

### Test 1.1: Register with 80-Character Password

**Objective**: Verify that signup succeeds with a password longer than 72 bytes

**Steps**:
1. Send POST request to `/api/auth/signup`:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test1@example.com",
    "password": "ThisIsAVeryLongPasswordThatExceeds72BytesAndShouldStillWorkWithoutAnyErrors123",
    "name": "Test User 1"
  }'
```

**Expected Result**:
- Status: 201 Created
- Response contains `access_token` and `user` object
- No error about password length

**Verification**:
- ✅ Response status is 201
- ✅ JWT token is present in response
- ✅ User object contains correct email and name
- ✅ No "72 bytes" error message

---

### Test 1.2: Register with 100-Character Password

**Objective**: Verify that very long passwords (100+ characters) work

**Steps**:
1. Send POST request with 100-character password:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~`1234567890",
    "name": "Test User 2"
  }'
```

**Expected Result**:
- Status: 201 Created
- Signup succeeds without errors

**Verification**:
- ✅ Response status is 201
- ✅ No byte-length errors

---

### Test 1.3: Register with Password Containing Multi-byte UTF-8 Characters

**Objective**: Verify that passwords with emojis and international characters work

**Steps**:
1. Send POST request with multi-byte characters:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test3@example.com",
    "password": "café☕🔒password🌍test😀emoji🎉party🚀rocket' + 'x' * 40,
    "name": "Test User 3"
  }'
```

**Expected Result**:
- Status: 201 Created
- Multi-byte characters handled correctly

**Verification**:
- ✅ Response status is 201
- ✅ No encoding errors
- ✅ No byte-length errors

---

### Test 1.4: Register with Exactly 72-Byte Password

**Objective**: Verify boundary condition (exactly 72 bytes)

**Steps**:
1. Create a password that is exactly 72 bytes:
```bash
# 72 ASCII characters = 72 bytes
PASSWORD="123456789012345678901234567890123456789012345678901234567890123456789012"

curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"test4@example.com\",
    \"password\": \"$PASSWORD\",
    \"name\": \"Test User 4\"
  }"
```

**Expected Result**:
- Status: 201 Created
- No truncation needed (password is exactly at limit)

**Verification**:
- ✅ Response status is 201
- ✅ No errors

---

## Test Suite 2: User Login with Long Passwords

### Test 2.1: Login with 80-Character Password

**Objective**: Verify that login succeeds with long password

**Prerequisites**: Complete Test 1.1 first (user must exist)

**Steps**:
1. Send POST request to `/api/auth/login`:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test1@example.com",
    "password": "ThisIsAVeryLongPasswordThatExceeds72BytesAndShouldStillWorkWithoutAnyErrors123"
  }'
```

**Expected Result**:
- Status: 200 OK
- Response contains `access_token`
- Authentication succeeds

**Verification**:
- ✅ Response status is 200
- ✅ JWT token is present
- ✅ No byte-length errors

---

### Test 2.2: Login with 100-Character Password

**Objective**: Verify that very long passwords work for login

**Prerequisites**: Complete Test 1.2 first

**Steps**:
1. Send POST request with same 100-character password:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~`1234567890"
  }'
```

**Expected Result**:
- Status: 200 OK
- Authentication succeeds

**Verification**:
- ✅ Response status is 200
- ✅ No errors

---

### Test 2.3: Login with Multi-byte Character Password

**Objective**: Verify multi-byte characters work for login

**Prerequisites**: Complete Test 1.3 first

**Steps**:
1. Send POST request with multi-byte password:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test3@example.com",
    "password": "café☕🔒password🌍test😀emoji🎉party🚀rocket' + 'x' * 40
  }'
```

**Expected Result**:
- Status: 200 OK
- Authentication succeeds

**Verification**:
- ✅ Response status is 200
- ✅ Multi-byte characters handled correctly

---

## Test Suite 3: Backward Compatibility

### Test 3.1: Existing User with Short Password

**Objective**: Verify that existing users with short passwords can still log in

**Prerequisites**: Create a user with a short password (before the fix)

**Steps**:
1. Register user with short password:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "existing@example.com",
    "password": "ShortPass123",
    "name": "Existing User"
  }'
```

2. Login with same short password:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "existing@example.com",
    "password": "ShortPass123"
  }'
```

**Expected Result**:
- Both signup and login succeed
- No regression for short passwords

**Verification**:
- ✅ Signup: 201 Created
- ✅ Login: 200 OK
- ✅ No changes to existing behavior

---

### Test 3.2: Wrong Password Still Fails

**Objective**: Verify that incorrect passwords are still rejected

**Prerequisites**: User from Test 3.1 exists

**Steps**:
1. Attempt login with wrong password:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "existing@example.com",
    "password": "WrongPassword123"
  }'
```

**Expected Result**:
- Status: 401 Unauthorized
- Error message: "Invalid email or password"

**Verification**:
- ✅ Response status is 401
- ✅ Generic error message (no user enumeration)
- ✅ Authentication properly rejects wrong passwords

---

## Test Suite 4: Edge Cases

### Test 4.1: Password with Only Multi-byte Characters

**Objective**: Test password that is short in character count but long in byte count

**Steps**:
1. Create password with 30 emoji characters (120+ bytes):
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "emoji@example.com",
    "password": "😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚☺️🙂🤗🤩🤔🤨😐😑😶🙄😏😣😥",
    "name": "Emoji User"
  }'
```

**Expected Result**:
- Status: 201 Created
- Truncation handles multi-byte characters correctly

**Verification**:
- ✅ Response status is 201
- ✅ No encoding errors
- ✅ Can login with same password

---

### Test 4.2: Empty Password (Should Fail Validation)

**Objective**: Verify that empty passwords are still rejected

**Steps**:
1. Attempt signup with empty password:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "empty@example.com",
    "password": "",
    "name": "Empty Password User"
  }'
```

**Expected Result**:
- Status: 422 Unprocessable Entity
- Validation error for password field

**Verification**:
- ✅ Response status is 422
- ✅ Password validation still works
- ✅ Empty passwords rejected

---

### Test 4.3: Password at Truncation Boundary (73 bytes)

**Objective**: Test password that is just over the 72-byte limit

**Steps**:
1. Create 73-byte password:
```bash
# 73 ASCII characters = 73 bytes
PASSWORD="1234567890123456789012345678901234567890123456789012345678901234567890123"

curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"boundary@example.com\",
    \"password\": \"$PASSWORD\",
    \"name\": \"Boundary User\"
  }"
```

2. Login with same password:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"boundary@example.com\",
    \"password\": \"$PASSWORD\"
  }"
```

**Expected Result**:
- Signup: 201 Created
- Login: 200 OK
- Truncation occurs transparently

**Verification**:
- ✅ Both operations succeed
- ✅ No byte-length errors

---

## Test Suite 5: Performance Verification

### Test 5.1: Measure Authentication Time

**Objective**: Verify that truncation adds negligible overhead (<1ms)

**Steps**:
1. Time a login request:
```bash
time curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test1@example.com",
    "password": "ThisIsAVeryLongPasswordThatExceeds72BytesAndShouldStillWorkWithoutAnyErrors123"
  }'
```

2. Compare with short password login time

**Expected Result**:
- Total time difference <1ms
- Truncation overhead negligible

**Verification**:
- ✅ Response time acceptable
- ✅ No performance degradation

---

## Success Criteria Verification

After completing all tests, verify the following success criteria from spec.md:

- ✅ **SC-001**: Users can successfully register with passwords up to 200 characters long
- ✅ **SC-002**: Users can successfully authenticate with passwords up to 200 characters long
- ✅ **SC-003**: The error "password cannot be longer than 72 bytes" no longer appears
- ✅ **SC-004**: 100% of registration attempts with long passwords succeed
- ✅ **SC-005**: 100% of login attempts with correct long passwords succeed
- ✅ **SC-006**: Backward compatibility maintained for existing short passwords

---

## Troubleshooting

### Issue: "password cannot be longer than 72 bytes" error still appears

**Diagnosis**: Fix not applied correctly
**Solution**: Verify that password_utils.py has truncation logic and is being called

### Issue: Multi-byte characters cause encoding errors

**Diagnosis**: Incorrect UTF-8 handling
**Solution**: Verify using `encode('utf-8')[:72]` and `decode('utf-8', errors='ignore')`

### Issue: Existing users cannot log in

**Diagnosis**: Backward compatibility broken
**Solution**: Verify truncation logic is identical for signup and login

---

## Test Summary Template

```
Test Suite 1: Registration with Long Passwords
  Test 1.1: 80-char password         [ PASS / FAIL ]
  Test 1.2: 100-char password        [ PASS / FAIL ]
  Test 1.3: Multi-byte characters    [ PASS / FAIL ]
  Test 1.4: Exactly 72 bytes         [ PASS / FAIL ]

Test Suite 2: Login with Long Passwords
  Test 2.1: 80-char password         [ PASS / FAIL ]
  Test 2.2: 100-char password        [ PASS / FAIL ]
  Test 2.3: Multi-byte characters    [ PASS / FAIL ]

Test Suite 3: Backward Compatibility
  Test 3.1: Short password           [ PASS / FAIL ]
  Test 3.2: Wrong password fails     [ PASS / FAIL ]

Test Suite 4: Edge Cases
  Test 4.1: Only multi-byte chars    [ PASS / FAIL ]
  Test 4.2: Empty password fails     [ PASS / FAIL ]
  Test 4.3: 73-byte boundary         [ PASS / FAIL ]

Test Suite 5: Performance
  Test 5.1: Authentication time      [ PASS / FAIL ]

Overall Result: [ PASS / FAIL ]
```

---

## Next Steps

After all tests pass:
1. Document any issues found
2. Verify fix in staging environment
3. Deploy to production
4. Monitor for any authentication errors
5. Confirm error "password cannot be longer than 72 bytes" no longer appears in logs
