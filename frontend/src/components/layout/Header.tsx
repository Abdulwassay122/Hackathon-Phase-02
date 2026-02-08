'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';

export function Header() {
  const router = useRouter();
  const { logout } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const handleLogout = async () => {
    setIsLoading(true);

    try {
      // Call AuthContext logout method
      logout();
      // Redirect is handled by AuthContext
    } catch (error) {
      console.error('Logout failed:', error);
      // Even if logout fails, redirect to signin
      router.push('/signin');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container max-w-6xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-blue-600">Todo App</h1>
          </div>

          <nav className="flex items-center gap-4">
            <a
              href="/tasks"
              className="text-gray-700 hover:text-blue-600 font-medium"
            >
              My Tasks
            </a>
            <Button
              onClick={handleLogout}
              variant="secondary"
              isLoading={isLoading}
            >
              Logout
            </Button>
          </nav>
        </div>
      </div>
    </header>
  );
}
