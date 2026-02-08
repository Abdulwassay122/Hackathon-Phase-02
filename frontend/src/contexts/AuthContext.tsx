"use client";

import React, { createContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { setToken, getToken, clearToken } from "@/lib/auth";

/**
 * User interface representing authenticated user data
 */
export interface User {
  id: number;
  email: string;
  name: string;
}

/**
 * Authentication state interface
 */
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
}

/**
 * Create AuthContext with undefined default
 */
export const AuthContext = createContext<AuthState | undefined>(undefined);

/**
 * AuthProvider component that wraps the app and provides authentication state
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Initialize authentication state on mount
   * Check for existing token in localStorage
   */
  useEffect(() => {
    const initAuth = () => {
      const existingToken = getToken();

      if (existingToken) {
        // Decode JWT to extract user info (basic decode, no verification)
        try {
          const payload = JSON.parse(atob(existingToken.split(".")[1]));
          const userData: User = {
            id: parseInt(payload.sub),
            email: payload.email,
            name: payload.name || payload.email,
          };

          setIsAuthenticated(true);
          setUser(userData);
          setTokenState(existingToken);
        } catch (err) {
          // Invalid token, clear it
          clearToken();
          console.error("Failed to decode token:", err);
        }
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  /**
   * Login method - calls backend API and stores token
   */
  const login = async (email: string, password: string): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        },
      );

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Invalid email or password");
        } else if (response.status === 422) {
          throw new Error("Please provide valid email and password");
        } else if (response.status === 500) {
          throw new Error("An error occurred. Please try again.");
        } else {
          throw new Error("Login failed");
        }
      }

      const data = await response.json();

      // Store token in localStorage
      setToken(data.access_token);

      // Update state
      setIsAuthenticated(true);
      setUser(data.user);
      setTokenState(data.access_token);
      setError(null);

      console.log("Success")

      // Redirect to tasks page
      router.push("/tasks");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unable to connect to server";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Signup method - calls backend API and stores token
   */
  const signup = async (
    email: string,
    password: string,
    name: string,
  ): Promise<void> => {
    setLoading(true);
    setError(null);

    try {
      console.log(process.env.NEXT_PUBLIC_API_URL)
      console.log('content: ',{ email, password, name })
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/signup`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, name }),
        },
      );

      if (!response.ok) {
        if (response.status === 400) {
          const data = await response.json();
          throw new Error(data.detail || "Invalid input");
        } else if (response.status === 409) {
          throw new Error("Email already registered");
        } else if (response.status === 422) {
          throw new Error("Invalid email format");
        } else if (response.status === 500) {
          throw new Error("An error occurred. Please try again.");
        } else {
          throw new Error("Signup failed");
        }
      }

      const data = await response.json();

      // Store token in localStorage
      setToken(data.access_token);

      // Update state
      setIsAuthenticated(true);
      setUser(data.user);
      setTokenState(data.access_token);
      setError(null);

      // Redirect to tasks page
      router.push("/tasks");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unable to connect to server";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Logout method - clears token and redirects to login
   */
  const logout = (): void => {
    // Clear token from localStorage
    clearToken();

    // Reset state
    setIsAuthenticated(false);
    setUser(null);
    setTokenState(null);
    setError(null);

    // Redirect to login page
    router.push("/login");
  };

  const value: AuthState = {
    isAuthenticated,
    user,
    token,
    loading,
    error,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
