import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware for route protection
 * Redirects unauthenticated users to signin page
 */
export function middleware(request: NextRequest) {
  // Check for authentication token in cookies or localStorage
  // Note: In a real implementation, you'd check for the actual token
  // For now, we'll check if the user has a session cookie
  const token = request.cookies.get('auth-token');

  // Protected routes that require authentication
  const protectedPaths = ['/tasks', '/dashboard'];
  const isProtectedPath = protectedPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  // If accessing protected route without token, redirect to signin
  if (isProtectedPath && !token) {
    const signinUrl = new URL('/signin', request.url);
    signinUrl.searchParams.set('redirect', request.nextUrl.pathname);
    return NextResponse.redirect(signinUrl);
  }

  // If authenticated and trying to access auth pages, redirect to tasks
  const authPaths = ['/signin', '/signup'];
  const isAuthPath = authPaths.some(path =>
    request.nextUrl.pathname.startsWith(path)
  );

  if (isAuthPath && token) {
    return NextResponse.redirect(new URL('/tasks', request.url));
  }

  return NextResponse.next();
}

/**
 * Configure which routes the middleware should run on
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
