'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { validateEmail, validatePassword } from '../../lib/utils/validation';
import { useAuth } from '@/hooks/useAuth';

export function SignUpForm() {
  const router = useRouter();
  const { signup, loading: authLoading } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ name?: string; email?: string; password?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});
    setErrorMessage(null);

    // Client-side validation
    const nameError = !name.trim() ? 'Name is required' : undefined;
    const emailError = validateEmail(email);
    const passwordError = validatePassword(password);

    if (nameError || emailError || passwordError) {
      setErrors({
        name: nameError,
        email: emailError || undefined,
        password: passwordError || undefined,
      });
      return;
    }

    setIsLoading(true);

    try {
      // Call AuthContext signup method
      await signup(email, password, name);
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
      {errorMessage && (
        <div className="error">
          {errorMessage}
        </div>
      )}

      <Input
        label="Name"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        error={errors.name}
        required
        autoComplete="name"
        disabled={isLoading || authLoading}
      />

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
        autoComplete="new-password"
        disabled={isLoading || authLoading}
      />

      <Button
        type="submit"
        variant="primary"
        isLoading={isLoading || authLoading}
        className="w-full"
      >
        Sign up
      </Button>
    </form>
  );
}
