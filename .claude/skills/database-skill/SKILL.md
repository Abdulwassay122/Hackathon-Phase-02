---
name: database-skill
description: Handle database tasks including table creation, schema design, and migrations for relational databases.
---

# Database Skill

## Instructions

1. **Table Creation**
   - Design tables according to data requirements
   - Define proper column types and constraints
   - Ensure relationships between tables (foreign keys, indexes)

2. **Schema Design**
   - Plan normalized database structures
   - Optimize for query performance and scalability
   - Consider future extensibility and maintainability

3. **Migrations**
   - Implement database migrations for schema updates
   - Version control schema changes
   - Ensure smooth data migration without loss

## Best Practices
- Use consistent naming conventions
- Apply primary and foreign keys appropriately
- Index columns for frequently queried fields
- Regularly backup database before migrations

## Example Structure
```sql
-- Create Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create Posts table with foreign key
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  title VARCHAR(150) NOT NULL,
  content TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
