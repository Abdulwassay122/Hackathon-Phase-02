# API Client Contract: Todo Frontend Integration

**Feature**: 003-todo-frontend
**Date**: 2026-02-07
**Phase**: 1 - Design & Contracts

## Purpose

This document defines the contract for the centralized API client that handles all communication between the frontend and backend. The API client is responsible for:

- Making HTTP requests to the backend API
- Automatically attaching JWT tokens to requests
- Handling authentication errors (401/403)
- Providing consistent error handling
- Exposing type-safe methods for all API operations

## Core Requirements

### REQ-1: Centralized Configuration
The API client MUST be configured with a base URL from environment variables and provide a single point of configuration for all API communication.

### REQ-2: Automatic JWT Injection
The API client MUST automatically attach JWT tokens to all requests via the `Authorization: Bearer <token>` header.

### REQ-3: Authentication Error Handling
The API client MUST intercept 401 (Unauthorized) and 403 (Forbidden) responses and trigger appropriate actions (e.g., redirect to signin page).

### REQ-4: Type Safety
The API client MUST provide TypeScript type definitions for all request and response payloads.

### REQ-5: Error Consistency
The API client MUST provide consistent error handling across all operations, converting backend errors to a standard format.

## API Client Interface

### Base Client

```typescript
/**
 * Configuration for the API client
 */
interface APIClientConfig {
  /** Base URL for the backend API (from environment variable) */
  baseURL: string;

  /** Function to retrieve the current JWT token */
  getToken: () => string | null;

  /** Function to handle authentication errors (401/403) */
  onAuthError: () => void;
}

/**
 * HTTP request options
 */
interface RequestOptions {
  /** HTTP method */
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

  /** Request headers (Authorization header added automatically) */
  headers?: Record<string, string>;

  /** Request body (will be JSON stringified) */
  body?: unknown;

  /** Query parameters */
  params?: Record<string, string | number | boolean>;
}

/**
 * Base API client class
 */
class APIClient {
  constructor(config: APIClientConfig);

  /**
   * Make an HTTP request to the backend API
   *
   * @param endpoint - API endpoint path (e.g., '/api/tasks')
   * @param options - Request options
   * @returns Promise resolving to response data
   * @throws APIError if request fails
   */
  async request<T>(endpoint: string, options: RequestOptions): Promise<T>;

  /**
   * GET request helper
   */
  async get<T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<T>;

  /**
   * POST request helper
   */
  async post<T>(endpoint: string, body: unknown): Promise<T>;

  /**
   * PUT request helper
   */
  async put<T>(endpoint: string, body: unknown): Promise<T>;

  /**
   * PATCH request helper
   */
  async patch<T>(endpoint: string, body: unknown): Promise<T>;

  /**
   * DELETE request helper
   */
  async delete<T>(endpoint: string): Promise<T>;
}
```

### Task API Methods

```typescript
/**
 * Task-specific API methods
 * Built on top of the base APIClient
 */
interface TaskAPI {
  /**
   * List all tasks for the authenticated user
   *
   * @returns Promise resolving to array of tasks
   * @throws APIError if request fails or user is unauthorized
   */
  list(): Promise<Task[]>;

  /**
   * Get a specific task by ID
   *
   * @param id - Task ID
   * @returns Promise resolving to task
   * @throws APIError if task not found or user is unauthorized
   */
  get(id: number): Promise<Task>;

  /**
   * Create a new task
   *
   * @param data - Task creation payload
   * @returns Promise resolving to created task
   * @throws APIError if validation fails or user is unauthorized
   */
  create(data: TaskCreate): Promise<Task>;

  /**
   * Update an existing task
   *
   * @param id - Task ID
   * @param data - Task update payload (partial)
   * @returns Promise resolving to updated task
   * @throws APIError if task not found, validation fails, or user is unauthorized
   */
  update(id: number, data: TaskUpdate): Promise<Task>;

  /**
   * Delete a task
   *
   * @param id - Task ID
   * @returns Promise resolving when deletion is complete
   * @throws APIError if task not found or user is unauthorized
   */
  delete(id: number): Promise<void>;

  /**
   * Toggle task completion status
   *
   * @param id - Task ID
   * @returns Promise resolving to updated task
   * @throws APIError if task not found or user is unauthorized
   */
  toggleComplete(id: number): Promise<Task>;
}
```

### Authentication API Methods

```typescript
/**
 * Authentication-specific API methods
 * Integrates with Better Auth
 */
interface AuthAPI {
  /**
   * Sign up a new user
   *
   * @param data - Signup payload (email, password)
   * @returns Promise resolving to authentication response
   * @throws APIError if validation fails or email already exists
   */
  signUp(data: SignUpRequest): Promise<AuthResponse>;

  /**
   * Sign in an existing user
   *
   * @param data - Signin payload (email, password)
   * @returns Promise resolving to authentication response
   * @throws APIError if credentials are invalid
   */
  signIn(data: SignInRequest): Promise<AuthResponse>;

  /**
   * Sign out the current user
   *
   * @returns Promise resolving when signout is complete
   */
  signOut(): Promise<void>;

  /**
   * Get the current user session
   *
   * @returns Promise resolving to user session or null if not authenticated
   */
  getSession(): Promise<UserSession | null>;
}
```

## Request Flow

### 1. Standard Request Flow

```
Component
  ↓ calls API method
TaskAPI.create(data)
  ↓ calls base client
APIClient.post('/api/tasks', data)
  ↓ adds headers
  - Content-Type: application/json
  - Authorization: Bearer <token>
  ↓ makes fetch request
Backend API
  ↓ validates JWT
  ↓ processes request
  ↓ returns response
APIClient
  ↓ checks status code
  ↓ parses JSON
  ↓ returns typed data
Component
```

### 2. Authentication Error Flow

```
Component
  ↓ calls API method
TaskAPI.list()
  ↓ calls base client
APIClient.get('/api/tasks')
  ↓ makes fetch request
Backend API
  ↓ JWT expired or invalid
  ↓ returns 401 Unauthorized
APIClient
  ↓ detects 401 status
  ↓ calls onAuthError()
  ↓ redirects to signin page
  ↓ throws APIError
Component
  ↓ catches error
  ↓ displays error message
```

### 3. Network Error Flow

```
Component
  ↓ calls API method
TaskAPI.create(data)
  ↓ calls base client
APIClient.post('/api/tasks', data)
  ↓ makes fetch request
Network Error (timeout, offline, etc.)
  ↓ fetch throws error
APIClient
  ↓ catches error
  ↓ wraps in APIError
  ↓ throws APIError
Component
  ↓ catches error
  ↓ displays user-friendly message
```

## Error Handling

### APIError Class

```typescript
/**
 * Custom error class for API errors
 */
class APIError extends Error {
  /** HTTP status code (if available) */
  statusCode?: number;

  /** Error code from backend (if available) */
  code?: string;

  /** Original error detail from backend */
  detail: string;

  constructor(message: string, statusCode?: number, code?: string);
}
```

### Error Response Mapping

| Backend Response | Frontend Error | Action |
|-----------------|----------------|--------|
| 200 OK | No error | Return data |
| 201 Created | No error | Return data |
| 204 No Content | No error | Return void |
| 400 Bad Request | APIError | Display validation error |
| 401 Unauthorized | APIError | Redirect to signin |
| 403 Forbidden | APIError | Redirect to signin |
| 404 Not Found | APIError | Display "not found" message |
| 500 Internal Server Error | APIError | Display generic error |
| Network Error | APIError | Display "connection failed" message |

### Error Message Examples

```typescript
// Validation error (400)
{
  message: "Validation failed",
  statusCode: 400,
  detail: "Title is required"
}

// Authentication error (401)
{
  message: "Unauthorized",
  statusCode: 401,
  detail: "Invalid or expired token"
}

// Not found error (404)
{
  message: "Not found",
  statusCode: 404,
  detail: "Task not found"
}

// Network error
{
  message: "Network error",
  statusCode: undefined,
  detail: "Failed to connect to server"
}
```

## JWT Token Management

### Token Retrieval

The API client MUST retrieve the JWT token using the `getToken` function provided in the configuration. This function should:

1. Check if a valid token exists in storage (localStorage, sessionStorage, or cookies)
2. Verify the token has not expired (optional client-side check)
3. Return the token string or `null` if not available

```typescript
// Example getToken implementation
function getToken(): string | null {
  const session = localStorage.getItem('user-session');
  if (!session) return null;

  const parsed = JSON.parse(session);
  const now = new Date().getTime();
  const expiresAt = new Date(parsed.expiresAt).getTime();

  if (now >= expiresAt) {
    // Token expired
    localStorage.removeItem('user-session');
    return null;
  }

  return parsed.token;
}
```

### Token Attachment

The API client MUST attach the token to every request (except authentication endpoints) using the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration Handling

When the backend returns a 401 Unauthorized response:

1. The API client MUST call the `onAuthError` callback
2. The callback SHOULD clear the stored token
3. The callback SHOULD redirect the user to the signin page
4. The API client MUST throw an APIError with appropriate message

## Request Headers

### Standard Headers

All requests MUST include:

```
Content-Type: application/json
```

### Authentication Headers

All requests (except signin/signup) MUST include:

```
Authorization: Bearer <jwt_token>
```

### Optional Headers

Requests MAY include:

```
Accept: application/json
X-Request-ID: <unique_request_id>  (for debugging)
```

## Response Handling

### Success Responses

For successful responses (2xx status codes):

1. Parse response body as JSON
2. Validate response structure (optional runtime validation)
3. Return typed data to caller

### Error Responses

For error responses (4xx, 5xx status codes):

1. Parse response body as JSON (if available)
2. Extract error detail from `detail` field
3. Create APIError with status code and detail
4. If 401/403, call `onAuthError` before throwing
5. Throw APIError to caller

### Network Errors

For network errors (fetch throws):

1. Catch the error
2. Create APIError with user-friendly message
3. Throw APIError to caller

## Usage Examples

### Initialize API Client

```typescript
import { APIClient, TaskAPI } from '@/lib/api';

// Create base client
const apiClient = new APIClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL!,
  getToken: () => {
    // Retrieve token from storage
    const session = localStorage.getItem('user-session');
    return session ? JSON.parse(session).token : null;
  },
  onAuthError: () => {
    // Clear token and redirect
    localStorage.removeItem('user-session');
    window.location.href = '/signin?expired=true';
  },
});

// Create task API
const taskAPI = new TaskAPI(apiClient);
```

### Use in Components

```typescript
// List tasks
try {
  const tasks = await taskAPI.list();
  setTasks(tasks);
} catch (error) {
  if (error instanceof APIError) {
    setError(error.detail);
  }
}

// Create task
try {
  const newTask = await taskAPI.create({
    title: 'New task',
    description: 'Task description',
  });
  setTasks([...tasks, newTask]);
} catch (error) {
  if (error instanceof APIError) {
    setError(error.detail);
  }
}

// Update task
try {
  const updatedTask = await taskAPI.update(taskId, {
    title: 'Updated title',
  });
  setTasks(tasks.map(t => t.id === taskId ? updatedTask : t));
} catch (error) {
  if (error instanceof APIError) {
    setError(error.detail);
  }
}

// Delete task
try {
  await taskAPI.delete(taskId);
  setTasks(tasks.filter(t => t.id !== taskId));
} catch (error) {
  if (error instanceof APIError) {
    setError(error.detail);
  }
}
```

## Testing Considerations

### Unit Tests

The API client SHOULD be unit tested with:

1. Mock fetch responses for success cases
2. Mock fetch responses for error cases
3. Verify JWT token is attached to requests
4. Verify `onAuthError` is called for 401/403
5. Verify error messages are user-friendly

### Integration Tests

The API client SHOULD be integration tested with:

1. Real backend API (or mock server)
2. Valid and invalid JWT tokens
3. Network error scenarios
4. Concurrent requests

## Security Considerations

### Token Storage

- Tokens SHOULD be stored in httpOnly cookies (preferred) or secure localStorage
- Tokens MUST NOT be exposed in URLs or logs
- Tokens MUST be cleared on logout

### HTTPS

- All API communication MUST use HTTPS in production
- HTTP is acceptable for local development only

### CORS

- Backend MUST configure CORS to allow frontend origin
- Frontend MUST NOT bypass CORS restrictions

### Input Validation

- Client-side validation is for UX only
- Backend enforces all security and business rules
- Never trust client-side validation alone

## Performance Considerations

### Request Caching

- The API client MAY implement caching for GET requests
- Cache MUST be invalidated on mutations (POST, PUT, PATCH, DELETE)
- Cache MUST respect backend cache headers

### Request Deduplication

- The API client MAY deduplicate identical concurrent requests
- Deduplication MUST preserve request order and semantics

### Retry Logic

- The API client MAY implement retry logic for transient failures
- Retries MUST use exponential backoff
- Retries MUST NOT be applied to non-idempotent operations without user consent

## References

- Backend API Specification: `specs/002-jwt-auth/spec.md`
- Data Model: `specs/003-todo-frontend/data-model.md`
- TypeScript Documentation: https://www.typescriptlang.org/docs
- Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
