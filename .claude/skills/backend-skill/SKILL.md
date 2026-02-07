---
name: backend-skill
description: Generate API routes, handle requests and responses, and connect to databases efficiently for backend applications.
---

# Backend Skill

## Instructions

1. **Route Generation**
   - Create RESTful API routes
   - Define proper HTTP methods (GET, POST, PUT, DELETE)
   - Organize routes for maintainability and scalability

2. **Request & Response Handling**
   - Validate incoming requests and parameters
   - Send structured and meaningful responses
   - Handle errors gracefully and consistently

3. **Database Connection**
   - Connect to relational or NoSQL databases
   - Perform CRUD operations efficiently
   - Use ORM or query builders where appropriate

## Best Practices
- Keep route handlers concise and focused
- Validate inputs to prevent injection attacks
- Maintain consistent response formats
- Use environment variables for sensitive configuration
- Log important events and errors for debugging

## Example Structure
```js
// Express.js example
const express = require('express');
const app = express();
app.use(express.json());

// Database connection
const db = require('./db');

// Route: Get all users
app.get('/users', async (req, res) => {
  try {
    const users = await db.query('SELECT * FROM users');
    res.json(users);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});

// Route: Create a new user
app.post('/users', async (req, res) => {
  const { name, email } = req.body;
  try {
    const result = await db.query('INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *', [name, email]);
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: 'Server error' });
  }
});
