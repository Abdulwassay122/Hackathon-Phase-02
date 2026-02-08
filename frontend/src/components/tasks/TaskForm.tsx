'use client';

import { useState } from 'react';
import { TaskCreate } from '@/types/task';
import { Input, Textarea } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { validateTaskTitle, validateTaskDescription } from '../../lib/utils/validation';

interface TaskFormProps {
  onSubmit: (data: TaskCreate) => Promise<void>;
}

export function TaskForm({ onSubmit }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [errors, setErrors] = useState<{ title?: string; description?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});
    setErrorMessage(null);

    // Client-side validation
    const titleError = validateTaskTitle(title);
    const descriptionError = validateTaskDescription(description);

    if (titleError || descriptionError) {
      setErrors({
        title: titleError || undefined,
        description: descriptionError || undefined,
      });
      return;
    }

    setIsLoading(true);

    try {
      await onSubmit({
        title,
        description: description || null,
      });

      // Clear form on success
      setTitle('');
      setDescription('');
    } catch (error: any) {
      setErrorMessage(error.message || 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {errorMessage && (
        <div className="error mb-4">
          {errorMessage}
        </div>
      )}

      <Input
        label="Title"
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={errors.title}
        placeholder="Enter task title"
        maxLength={200}
        required
      />

      <Textarea
        label="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        error={errors.description}
        placeholder="Enter task description"
        rows={3}
        maxLength={1000}
      />

      <Button
        type="submit"
        variant="primary"
        isLoading={isLoading}
      >
        Create Task
      </Button>
    </form>
  );
}
