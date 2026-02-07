---
name: auth-skill
description: Handle secure authentication flows including signup, signin, password hashing, JWT tokens, and integration with authentication systems.
---

# Auth Skill

## Instructions

1. **User Signup & Signin**
   - Implement secure registration with hashed passwords
   - Validate inputs and enforce strong password policies
   - Provide secure login with proper error handling

2. **Password Security**
   - Use bcrypt or equivalent for password hashing
   - Ensure salts and secure hashing algorithms are applied
   - Protect against brute-force attacks

3. **Token Management**
   - Generate and validate JWT access and refresh tokens
   - Ensure proper token expiration and revocation
   - Handle secure storage on client-side

4. **Authentication Integration**
   - Support integration with frontend and backend systems
   - Implement middleware or guards for protected routes
   - Suggest improvements for auth flow efficiency and security

## Best Practices
- Never store plaintext passwords
- Use HTTPS for all auth requests
- Follow principle of least privilege for user roles
- Regularly refresh and validate tokens

## Example Structure
```js
// User signup
const hashedPassword = await bcrypt.hash(password, 10);
const user = await User.create({ email, password: hashedPassword });

// JWT generation
const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });

// Token validation middleware
function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).send("Unauthorized");
  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) return res.status(403).send("Forbidden");
    req.user = decoded;
    next();
  });
}
```