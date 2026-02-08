'use client';

import { useContext } from 'react';
import { AuthContext, AuthState } from '@/contexts/AuthContext';

/**
 * Custom hook to access authentication context
 * Must be used within AuthProvider
 * @returns AuthState object with authentication state and methods
 * @throws Error if used outside of AuthProvider
 */
export function useAuth(): AuthState {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}
