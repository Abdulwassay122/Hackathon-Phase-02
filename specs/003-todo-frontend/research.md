# Research: Todo Frontend Integration

**Feature**: 003-todo-frontend
**Date**: 2026-02-07
**Phase**: 0 - Outline & Research

## Purpose

This document consolidates research findings, technology decisions, and best practices for implementing the Todo Frontend Integration (Phase 3). All technical unknowns from the planning phase are resolved here before proceeding to detailed design.

## Technology Decisions

### Decision 1: Next.js 16+ with App Router

**Decision**: Use Next.js 16+ with App Router for the frontend framework

**Rationale**:
- **Constitutional Requirement**: Constitution explicitly mandates "Next.js 16+ with App Router" (Principle VIII, Technology Stack Requirements)
- **Modern Architecture**: App Router provides better performance with React Server Components, improved routing, and built-in layouts
- **Developer Experience**: File-system based routing, automatic code splitting, and optimized bundling
- **Production Ready**: Mature ecosystem with extensive documentation and community support
- **Deployment**: Seamless deployment to Vercel, Netlify, or other platforms

**Alternatives Considered**:
- **Pages Router**: Rejected - Constitution explicitly requires App Router, and App Router is the modern standard
- **Create React App**: Rejected - Lacks server-side rendering, routing, and optimization features
- **Vite + React Router**: Rejected - More configuration required, less integrated ecosystem

**Implementation Notes**:
- Use route groups `(auth)` and `(dashboard)` for logical organization
- Leverage `layout.tsx` for shared UI components (header, navigation)
- Use `loading.tsx` and `error.tsx` for loading and error states
- Implement middleware for authentication checks

### Decision 2: Better Auth for Authentication

**Decision**: Use Better Auth exclusively for authentication flows

**Rationale**:
- **Constitutional Requirement**: Constitution mandates "Better Auth exclusively for authentication flows" (Principle VIII)
- **JWT Integration**: Better Auth provides JWT tokens compatible with backend verification
- **Session Management**: Handles session creation, token refresh, and logout
- **Security**: Industry-standard security practices built-in
- **Developer Experience**: Simple API for signup, signin, and session management

**Alternatives Considered**:
- **NextAuth.js**: Rejected - Constitution specifies Better Auth
- **Custom Auth**: Rejected - Violates constitution, increases complexity and security risk
- **Auth0/Clerk**: Rejected - Third-party services not specified in constitution

**Implementation Notes**:
- Configure Better Auth with backend API URL
- Store JWT tokens securely (httpOnly cookies preferred)
- Implement token refresh logic if supported
- Handle authentication errors and redirect appropriately

### Decision 3: TypeScript for Type Safety

**Decision**: Use TypeScript 5.x for all frontend code

**Rationale**:
- **Type Safety**: Catch errors at compile time, especially for API contracts
- **Developer Experience**: Better IDE support, autocomplete, and refactoring
- **Maintainability**: Self-documenting code with explicit types
- **Next.js Integration**: First-class TypeScript support in Next.js
- **Team Collaboration**: Clearer interfaces and contracts

**Alternatives Considered**:
- **JavaScript**: Rejected - Lacks type safety, increases runtime errors
- **Flow**: Rejected - Less popular, smaller ecosystem than TypeScript

**Implementation Notes**:
- Define types for Task, User, API responses
- Use strict TypeScript configuration
- Leverage type inference where possible
- Create shared types between frontend and backend (if feasible)

### Decision 4: Centralized API Client

**Decision**: Implement a centralized API client with JWT token injection

**Rationale**:
- **DRY Principle**: Single place to configure API base URL, headers, error handling
- **JWT Injection**: Automatically attach JWT tokens to all requests
- **Error Handling**: Centralized handling of 401/403 errors, token expiration
- **Consistency**: All API calls follow same patterns
- **Testability**: Easy to mock for testing

**Alternatives Considered**:
- **Direct fetch() calls**: Rejected - Duplicates JWT logic, error handling across components
- **Multiple API clients**: Rejected - Increases complexity, inconsistent patterns

**Implementation Notes**:
- Create `lib/api/client.ts` with base fetch wrapper
- Intercept requests to add Authorization header
- Intercept responses to handle authentication errors
- Provide methods for GET, POST, PUT, PATCH, DELETE
- Create `lib/api/tasks.ts` with task-specific API methods

### Decision 5: React Hooks for State Management

**Decision**: Use React hooks (useState, useEffect, useContext) for state management

**Rationale**:
- **Constitutional Requirement**: Constitution specifies "React hooks and Next.js built-in capabilities" for state management
- **Simplicity**: No additional libraries required
- **Sufficient for Scope**: Application state is simple (tasks list, loading states, errors)
- **Performance**: React 18+ concurrent features optimize rendering
- **Learning Curve**: Standard React patterns, no additional concepts

**Alternatives Considered**:
- **Redux**: Rejected - Overkill for simple state, adds complexity
- **Zustand/Jotai**: Rejected - Not specified in constitution, unnecessary for scope
- **React Query**: Considered for data fetching but not required for MVP

**Implementation Notes**:
- Use `useState` for component-level state (form inputs, loading flags)
- Use `useEffect` for data fetching and side effects
- Use `useContext` for shared state (authentication status) if needed
- Consider custom hooks for reusable logic (useAuth, useTasks)

### Decision 6: CSS for Styling

**Decision**: Use CSS Modules or Tailwind CSS for styling

**Rationale**:
- **Responsive Design**: Need mobile-first responsive design (320px to 1920px)
- **Next.js Integration**: Both CSS Modules and Tailwind have first-class Next.js support
- **Developer Experience**: CSS Modules provide scoped styles, Tailwind provides utility classes
- **Performance**: Both optimize for production builds

**Alternatives Considered**:
- **Styled Components**: Rejected - Runtime overhead, not necessary for scope
- **Plain CSS**: Rejected - Lacks scoping, harder to maintain
- **Sass/SCSS**: Considered but not necessary for scope

**Implementation Notes**:
- Use CSS Modules for component-specific styles
- Use global CSS for resets and base styles
- Implement responsive breakpoints (mobile: 320-768px, desktop: 769px+)
- Follow mobile-first approach
- Consider Tailwind CSS if rapid prototyping is prioritized

## Best Practices

### Authentication Flow

**Pattern**: Redirect-based authentication with protected routes

**Implementation**:
1. Unauthenticated users land on signin page
2. After successful signin, redirect to `/tasks` dashboard
3. Protected routes check authentication status via middleware
4. Expired tokens trigger automatic redirect to signin
5. Logout clears tokens and redirects to signin

**Code Structure**:
```typescript
// middleware.ts - Route protection
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')
  if (!token && request.nextUrl.pathname.startsWith('/tasks')) {
    return NextResponse.redirect(new URL('/signin', request.url))
  }
}

// lib/auth/better-auth.ts - Better Auth configuration
export const auth = createAuth({
  // Better Auth configuration
})
```

### API Client Pattern

**Pattern**: Centralized fetch wrapper with interceptors

**Implementation**:
```typescript
// lib/api/client.ts
class APIClient {
  private baseURL: string
  private getToken: () => string | null

  async request(endpoint: string, options: RequestInit) {
    const token = this.getToken()
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    })

    if (response.status === 401 || response.status === 403) {
      // Handle authentication errors
      window.location.href = '/signin?expired=true'
    }

    return response
  }
}
```

### Component Organization

**Pattern**: Feature-based component organization

**Structure**:
- `components/auth/` - Authentication-related components
- `components/tasks/` - Task management components
- `components/layout/` - Layout components (header, nav)
- `components/ui/` - Reusable UI primitives (button, input, modal)

**Naming Convention**:
- PascalCase for component files: `TaskList.tsx`
- Descriptive names: `SignInForm.tsx` not `Form.tsx`
- Co-locate styles: `TaskList.module.css` next to `TaskList.tsx`

### Error Handling

**Pattern**: Consistent error handling across all API calls

**Implementation**:
1. API client catches network errors
2. Components display user-friendly error messages
3. Retry mechanisms for transient failures
4. Fallback UI for error states

**Code Structure**:
```typescript
// Component error handling
const [error, setError] = useState<string | null>(null)
const [loading, setLoading] = useState(false)

const handleCreateTask = async (data: TaskCreate) => {
  setLoading(true)
  setError(null)
  try {
    await api.tasks.create(data)
    // Success handling
  } catch (err) {
    setError('Failed to create task. Please try again.')
  } finally {
    setLoading(false)
  }
}
```

### Responsive Design

**Pattern**: Mobile-first responsive design with breakpoints

**Breakpoints**:
- Mobile: 320px - 768px
- Tablet: 769px - 1024px
- Desktop: 1025px+

**Implementation**:
```css
/* Mobile-first base styles */
.container {
  padding: 1rem;
}

/* Tablet and up */
@media (min-width: 769px) {
  .container {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

## Integration Points

### Backend API Integration

**Endpoint Base URL**: Configured via environment variable `NEXT_PUBLIC_API_URL`

**API Endpoints** (from Phase 2):
- `POST /api/tasks` - Create task
- `GET /api/tasks` - List tasks
- `GET /api/tasks/{id}` - Get task
- `PUT /api/tasks/{id}` - Update task
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `DELETE /api/tasks/{id}` - Delete task

**Authentication Header**: `Authorization: Bearer {jwt_token}`

**Response Format**: JSON with standard structure
```typescript
// Success response
{ id: number, title: string, description: string, completed: boolean, user_id: number, created_at: string, updated_at: string }

// Error response
{ detail: string }
```

### Better Auth Integration

**Configuration**:
- Auth provider URL: Configured via environment variable
- JWT token storage: httpOnly cookies (preferred) or localStorage
- Token format: Standard JWT with `sub` claim containing user ID
- Token expiration: Handled by Better Auth

**Auth Methods**:
- `auth.signUp(email, password)` - Create account
- `auth.signIn(email, password)` - Authenticate
- `auth.signOut()` - End session
- `auth.getSession()` - Get current session/token

## Environment Configuration

**Required Environment Variables**:
```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
NEXT_PUBLIC_AUTH_URL=https://auth.example.com
BETTER_AUTH_SECRET=your-secret-key

# Optional
NODE_ENV=development
```

## Performance Considerations

**Optimization Strategies**:
1. **Code Splitting**: Automatic with Next.js App Router
2. **Image Optimization**: Use Next.js `<Image>` component if images added
3. **Lazy Loading**: Load components on demand for non-critical UI
4. **Caching**: Leverage Next.js caching for static assets
5. **Bundle Size**: Monitor bundle size, avoid large dependencies

**Performance Targets** (from spec):
- Initial page load < 3 seconds
- Task operations < 3 seconds
- Time to Interactive < 5 seconds
- First Contentful Paint < 2 seconds

## Security Considerations

**Security Measures**:
1. **HTTPS Only**: All API communication over HTTPS in production
2. **JWT Storage**: Use httpOnly cookies to prevent XSS attacks
3. **CSRF Protection**: Implement CSRF tokens if using cookies
4. **Input Validation**: Client-side validation for UX (backend enforces security)
5. **Content Security Policy**: Configure CSP headers
6. **Dependency Scanning**: Regular security audits of npm packages

## Testing Strategy

**Testing Approach**:
1. **Unit Tests**: Jest + React Testing Library for components
2. **Integration Tests**: Test component interactions and API calls
3. **E2E Tests**: Playwright/Cypress for full user flows
4. **Manual Testing**: Browser testing across devices and screen sizes

**Test Coverage Goals**:
- Critical paths: 100% (authentication, task CRUD)
- UI components: 80%+
- Utility functions: 90%+

## Deployment Considerations

**Deployment Platform**: Vercel (recommended) or Netlify

**Deployment Steps**:
1. Build Next.js application: `npm run build`
2. Configure environment variables on platform
3. Deploy to production
4. Verify HTTPS and API connectivity
5. Test authentication flow end-to-end

**CI/CD**:
- Automated builds on git push
- Run tests before deployment
- Preview deployments for pull requests

## Open Questions

None - All technical decisions resolved based on constitution requirements and specification.

## References

- Next.js 16+ Documentation: https://nextjs.org/docs
- Better Auth Documentation: [Better Auth docs]
- React 18 Documentation: https://react.dev
- TypeScript Documentation: https://www.typescriptlang.org/docs
- Backend API Specification: `specs/002-jwt-auth/spec.md`
