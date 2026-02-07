# Quickstart Guide: Todo Frontend Integration

**Feature**: 003-todo-frontend
**Date**: 2026-02-07
**Phase**: 1 - Design & Contracts

## Purpose

This guide provides step-by-step instructions for setting up, developing, and running the Todo Frontend application locally. Follow these instructions to get the frontend running and integrated with the backend API.

## Prerequisites

Before starting, ensure you have:

- **Node.js**: Version 18.x or higher (LTS recommended)
- **npm**: Version 9.x or higher (comes with Node.js)
- **Backend API**: Phase 2 backend must be running (see `specs/002-jwt-auth/quickstart.md`)
- **Database**: Neon PostgreSQL database must be accessible by backend
- **Git**: For version control
- **Code Editor**: VS Code recommended with TypeScript and ESLint extensions

**Verify Prerequisites**:
```bash
node --version    # Should show v18.x or higher
npm --version     # Should show v9.x or higher
```

## Project Setup

### 1. Create Next.js Application

Navigate to the project root and create the frontend directory:

```bash
# From project root (F:\Q 04 Hackathon 02\Phase 02)
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"
```

**Configuration Prompts** (if asked):
- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes (or No if using CSS Modules)
- `src/` directory: No (use `app/` directly)
- App Router: Yes
- Import alias: `@/*`

### 2. Navigate to Frontend Directory

```bash
cd frontend
```

### 3. Install Dependencies

Install core dependencies:

```bash
npm install
```

Install Better Auth (authentication):

```bash
npm install better-auth
```

Install additional utilities:

```bash
npm install zod          # Schema validation
npm install date-fns     # Date formatting (optional)
```

Install development dependencies:

```bash
npm install --save-dev @types/node @types/react @types/react-dom
npm install --save-dev eslint-config-next
```

### 4. Configure Environment Variables

Create `.env.local` file in the `frontend/` directory:

```bash
# Copy example file
cp .env.local.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars

# Optional: Environment
NODE_ENV=development
```

**Important**:
- `NEXT_PUBLIC_API_URL` must match your backend API URL (default: http://localhost:8000)
- `BETTER_AUTH_SECRET` must be at least 32 characters (generate with: `openssl rand -base64 32`)
- Never commit `.env.local` to version control

### 5. Create Environment Example File

Create `.env.local.example` for documentation:

```bash
cat > .env.local.example << 'EOF'
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=generate-with-openssl-rand-base64-32

# Optional: Environment
NODE_ENV=development
EOF
```

## Project Structure

After setup, your frontend directory should look like:

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Auth route group
│   │   ├── signin/
│   │   │   └── page.tsx
│   │   └── signup/
│   │       └── page.tsx
│   ├── (dashboard)/         # Protected route group
│   │   └── tasks/
│   │       └── page.tsx
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Landing page
│   └── globals.css          # Global styles
├── components/              # React components
│   ├── auth/
│   ├── tasks/
│   ├── layout/
│   └── ui/
├── lib/                     # Utilities and services
│   ├── api/
│   │   ├── client.ts
│   │   └── tasks.ts
│   ├── auth/
│   │   └── better-auth.ts
│   └── utils/
├── types/                   # TypeScript types
│   ├── task.ts
│   └── api.ts
├── public/                  # Static assets
├── .env.local              # Environment variables (not committed)
├── .env.local.example      # Environment template
├── next.config.js          # Next.js configuration
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.js      # Tailwind configuration (if using)
└── package.json            # Dependencies
```

## Development Workflow

### 1. Start Backend API

Before starting the frontend, ensure the backend is running:

```bash
# In a separate terminal, from project root
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

Verify backend is running: http://localhost:8000/docs

### 2. Start Frontend Development Server

```bash
# From frontend/ directory
npm run dev
```

The application will start at: http://localhost:3000

### 3. Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server (after build)
npm run start

# Run linter
npm run lint

# Run type checking
npx tsc --noEmit

# Format code (if prettier installed)
npm run format
```

### 4. Hot Reload

Next.js supports hot module replacement (HMR):
- Changes to `.tsx`, `.ts`, `.css` files automatically reload
- Changes to `next.config.js` require server restart
- Changes to `.env.local` require server restart

## Testing the Integration

### 1. Verify Backend Connection

Create a simple test page to verify API connectivity:

```typescript
// app/test/page.tsx
export default async function TestPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  return (
    <div>
      <h1>API Connection Test</h1>
      <p>API URL: {apiUrl}</p>
      <p>Try accessing: {apiUrl}/docs</p>
    </div>
  );
}
```

Visit: http://localhost:3000/test

### 2. Test Authentication Flow

1. Navigate to http://localhost:3000/signup
2. Create a new account with email and password
3. Verify redirect to tasks dashboard
4. Check browser DevTools → Network tab for JWT token in requests
5. Test logout and signin

### 3. Test Task Operations

1. Sign in to the application
2. Create a new task
3. Verify task appears in list
4. Edit task title/description
5. Toggle task completion
6. Delete task
7. Check browser DevTools → Network tab to verify API calls

### 4. Test Responsive Design

1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test different screen sizes:
   - Mobile: 320px, 375px, 414px
   - Tablet: 768px, 1024px
   - Desktop: 1280px, 1920px
4. Verify layout adapts correctly

## Common Issues and Solutions

### Issue: "Cannot connect to backend API"

**Symptoms**: Network errors, CORS errors, 404 responses

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/docs`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is configured in backend (should allow http://localhost:3000)
4. Check browser console for specific error messages

### Issue: "JWT token not attached to requests"

**Symptoms**: 401 Unauthorized errors on protected endpoints

**Solutions**:
1. Verify Better Auth is configured correctly
2. Check token is stored after signin (DevTools → Application → Storage)
3. Verify API client is attaching Authorization header
4. Check token format: `Bearer <token>`

### Issue: "Module not found" errors

**Symptoms**: TypeScript or import errors

**Solutions**:
1. Verify all dependencies installed: `npm install`
2. Check import paths use `@/` alias correctly
3. Restart TypeScript server in VS Code: Ctrl+Shift+P → "TypeScript: Restart TS Server"
4. Clear Next.js cache: `rm -rf .next` and restart dev server

### Issue: "Environment variables not loading"

**Symptoms**: `undefined` values for environment variables

**Solutions**:
1. Verify `.env.local` exists in `frontend/` directory
2. Restart development server (environment variables load on startup)
3. Check variable names start with `NEXT_PUBLIC_` for client-side access
4. Verify no syntax errors in `.env.local` (no quotes needed for values)

### Issue: "Port 3000 already in use"

**Symptoms**: Cannot start dev server

**Solutions**:
1. Kill process using port 3000: `npx kill-port 3000`
2. Or use different port: `npm run dev -- -p 3001`
3. Update `NEXT_PUBLIC_AUTH_URL` if using different port

## Browser DevTools Tips

### Network Tab
- Filter by "Fetch/XHR" to see API calls
- Check request headers for Authorization token
- Verify response status codes (200, 201, 401, etc.)
- Inspect request/response payloads

### Console Tab
- Check for JavaScript errors
- View console.log statements
- Monitor authentication state changes

### Application Tab
- View localStorage/sessionStorage for tokens
- Check cookies if using httpOnly cookies
- Inspect service workers (if PWA features added later)

### React DevTools
- Install React DevTools extension
- Inspect component props and state
- Profile component rendering performance

## Next Steps

After completing setup:

1. **Implement Authentication**: Create signin/signup forms with Better Auth integration
2. **Build API Client**: Implement centralized API client with JWT injection
3. **Create Task Components**: Build task list, form, and action components
4. **Add Routing**: Configure protected routes with middleware
5. **Style Application**: Apply responsive CSS/Tailwind styles
6. **Test Integration**: Verify all user flows work end-to-end

## Additional Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **Better Auth Documentation**: [Better Auth docs]
- **React Documentation**: https://react.dev
- **TypeScript Documentation**: https://www.typescriptlang.org/docs
- **Backend API Docs**: http://localhost:8000/docs (when running)
- **Phase 2 Specification**: `specs/002-jwt-auth/spec.md`

## Support

If you encounter issues not covered in this guide:

1. Check the specification: `specs/003-todo-frontend/spec.md`
2. Review the plan: `specs/003-todo-frontend/plan.md`
3. Check backend logs for API errors
4. Review browser console for frontend errors
5. Verify all prerequisites are met
