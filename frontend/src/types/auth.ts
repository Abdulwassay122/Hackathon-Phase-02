/**
 * User session information from Better Auth
 * Stored in browser and used for authentication
 */
export interface UserSession {
  /** JWT token for API authentication */
  token: string;

  /** User ID (extracted from JWT claims) */
  userId: number;

  /** User email */
  email: string;

  /** Token expiration timestamp (ISO 8601 format) */
  expiresAt: string;
}

/**
 * Payload for user signup
 */
export interface SignUpRequest {
  /** User email (required, valid email format) */
  email: string;

  /** User password (required, min 8 characters) */
  password: string;
}

/**
 * Payload for user signin
 */
export interface SignInRequest {
  /** User email (required) */
  email: string;

  /** User password (required) */
  password: string;
}

/**
 * Response from successful authentication
 */
export interface AuthResponse {
  /** JWT token for API requests */
  token: string;

  /** User information */
  user: {
    id: number;
    email: string;
  };
}
