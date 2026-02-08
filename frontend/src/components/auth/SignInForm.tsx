'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { validateEmail, validatePassword } from '../../lib/utils/validation';
import { useAuth } from '@/hooks/useAuth';

export function SignInForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, loading: authLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Check if redirected due to expired session
  const expired = searchParams.get('expired');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});
    setErrorMessage(null);

    // Client-side validation
    const emailError = validateEmail(email);
    const passwordError = !password ? 'Password is required' : undefined;

    if (emailError || passwordError) {
      setErrors({
        email: emailError || undefined,
        password: passwordError,
      });
      return;
    }

    setIsLoading(true);

    try {
      // Call AuthContext login method
      await login(email, password);
      // Redirect is handled by AuthContext
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'An unexpected error occurred. Please try again.';
      setErrorMessage(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-8 space-y-6">
      {expired && (
        <div className="error">
          Your session has expired. Please sign in again.
        </div>
      )}

      {errorMessage && (
        <div className="error">
          {errorMessage}
        </div>
      )}

      <Input
        label="Email address"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        error={errors.email}
        required
        autoComplete="email"
        disabled={isLoading || authLoading}
      />

      <Input
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        error={errors.password}
        required
        autoComplete="current-password"
        disabled={isLoading || authLoading}
      />

      <Button
        type="submit"
        variant="primary"
        isLoading={isLoading || authLoading}
        className="w-full"
      >
        Sign in
      </Button>
    </form>
  );
}
