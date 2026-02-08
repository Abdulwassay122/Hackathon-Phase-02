/**
 * Authentication token storage utilities
 * Manages JWT tokens in browser localStorage
 */

const TOKEN_KEY = 'auth_token';

/**
 * Check if localStorage is available
 * @returns true if localStorage is available, false otherwise
 */
export function isStorageAvailable(): boolean {
  if (typeof window === 'undefined') return false;

  try {
    const testKey = '__storage_test__';
    localStorage.setItem(testKey, 'test');
    localStorage.removeItem(testKey);
    return true;
  } catch {
    return false;
  }
}

/**
 * Store JWT token in localStorage
 * @param token - JWT token string
 * @throws Error if localStorage is unavailable
 */
export function setToken(token: string): void {
  if (typeof window === 'undefined') return;

  if (!isStorageAvailable()) {
    throw new Error('Browser storage unavailable. Please enable cookies and local storage, or disable private browsing mode.');
  }

  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch (error) {
    console.error('Failed to store token:', error);
    throw new Error('Browser storage unavailable. Please enable cookies and local storage, or disable private browsing mode.');
  }
}

/**
 * Retrieve JWT token from localStorage
 * @returns JWT token string or null if not found
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;

  if (!isStorageAvailable()) {
    return null;
  }

  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch (error) {
    console.error('Failed to retrieve token:', error);
    return null;
  }
}

/**
 * Remove JWT token from localStorage
 */
export function clearToken(): void {
  if (typeof window === 'undefined') return;

  if (!isStorageAvailable()) {
    return;
  }

  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch (error) {
    console.error('Failed to clear token:', error);
  }
}

/**
 * Check if a valid token exists in localStorage
 * @returns true if token exists, false otherwise
 */
export function hasToken(): boolean {
  return getToken() !== null;
}
