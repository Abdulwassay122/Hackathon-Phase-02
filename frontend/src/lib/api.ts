/**
 * API client wrapper with automatic JWT token attachment
 * Handles authentication headers and global error responses
 */

import { getToken, clearToken } from './auth';

/**
 * Check if JWT token is expired
 * @param token - JWT token string
 * @returns true if token is expired, false otherwise
 */
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp;

    if (!exp) return false;

    // Check if token is expired (with 10 second buffer)
    const now = Math.floor(Date.now() / 1000);
    return now >= exp;
  } catch {
    // If we can't decode, assume it's invalid/expired
    return true;
  }
}

/**
 * Make an authenticated API request with automatic Authorization header
 * @param url - API endpoint URL
 * @param options - Fetch options
 * @returns Response object
 */
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();

  // Check if token is expired before making request (optimization)
  if (token && isTokenExpired(token)) {
    clearToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw new Error('Token expired');
  }

  // Prepare headers with Authorization if token exists
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized globally
    if (response.status === 401) {
      // Clear token and redirect to login
      clearToken();

      // Only redirect if we're in the browser
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }

    return response;
  } catch (error) {
    // Network error or fetch failed
    console.error('API request failed:', error);
    throw new Error('Unable to connect to server');
  }
}

/**
 * Helper function for GET requests
 */
export async function apiGet(url: string): Promise<Response> {
  return authenticatedFetch(url, { method: 'GET' });
}

/**
 * Helper function for POST requests
 */
export async function apiPost(url: string, data: unknown): Promise<Response> {
  return authenticatedFetch(url, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Helper function for PUT requests
 */
export async function apiPut(url: string, data: unknown): Promise<Response> {
  return authenticatedFetch(url, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Helper function for DELETE requests
 */
export async function apiDelete(url: string): Promise<Response> {
  return authenticatedFetch(url, { method: 'DELETE' });
}
