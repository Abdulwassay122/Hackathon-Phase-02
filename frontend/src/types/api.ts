/**
 * Error response from backend API
 * Matches FastAPI HTTPException format
 */
export interface ApiError {
  /** Error message describing what went wrong */
  detail: string;

  /** Optional error code for client-side handling */
  code?: string;
}

/**
 * Generic success response
 * Backend may return data directly or wrapped in this structure
 */
export interface ApiResponse<T> {
  /** Response data */
  data: T;

  /** Optional success message */
  message?: string;
}

/**
 * Loading state for async operations
 */
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

/**
 * Form state for task creation/editing
 */
export interface TaskFormState {
  /** Current form values */
  values: {
    title: string;
    description: string;
  };

  /** Validation errors by field */
  errors: {
    title?: string;
    description?: string;
  };

  /** Form submission state */
  status: LoadingState;

  /** General error message (e.g., API error) */
  errorMessage: string | null;
}

/**
 * Task list state
 */
export interface TaskListState {
  /** Array of tasks */
  tasks: any[];

  /** Loading state */
  status: LoadingState;

  /** Error message if loading failed */
  error: string | null;
}
