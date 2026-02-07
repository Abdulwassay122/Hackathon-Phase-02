'use client';

import { useState } from 'react';
import { Task } from '@/types/task';
import { Input, Textarea } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { validateTaskTitle, validateTaskDescription } from '@/lib/utils/validation';

interface TaskItemProps {
  task: Task;
  onUpdate: (id: number, data: Partial<Task>) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onToggleComplete: (id: number) => Promise<void>;
}

export function TaskItem({ task, onUpdate, onDelete, onToggleComplete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [errors, setErrors] = useState<{ title?: string; description?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleToggleComplete = async () => {
    setIsLoading(true);
    try {
      await onToggleComplete(task.id);
    } catch (error: any) {
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setErrors({});
    setErrorMessage(null);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setErrors({});
    setErrorMessage(null);
  };

  const handleSaveEdit = async () => {
    // Validate
    const titleError = validateTaskTitle(editTitle);
    const descriptionError = validateTaskDescription(editDescription);

    if (titleError || descriptionError) {
      setErrors({
        title: titleError || undefined,
        description: descriptionError || undefined,
      });
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      await onUpdate(task.id, {
        title: editTitle,
        description: editDescription || null,
      });
      setIsEditing(false);
    } catch (error: any) {
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await onDelete(task.id);
      setIsDeleting(false);
    } catch (error: any) {
      setErrorMessage(error.message);
      setIsLoading(false);
    }
  };

  if (isEditing) {
    return (
      <div className="border rounded-lg p-4 bg-white">
        {errorMessage && <div className="error mb-4">{errorMessage}</div>}

        <Input
          label="Title"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          error={errors.title}
          maxLength={200}
        />

        <Textarea
          label="Description"
          value={editDescription}
          onChange={(e) => setEditDescription(e.target.value)}
          error={errors.description}
          rows={3}
          maxLength={1000}
        />

        <div className="flex gap-2 mt-4">
          <Button onClick={handleSaveEdit} isLoading={isLoading}>
            Save
          </Button>
          <Button onClick={handleCancelEdit} variant="secondary" disabled={isLoading}>
            Cancel
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="border rounded-lg p-4 bg-white hover:shadow-md transition-shadow">
        <div className="flex items-start gap-3">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggleComplete}
            disabled={isLoading}
            className="mt-1 w-5 h-5 cursor-pointer"
          />

          <div className="flex-1">
            <h3 className={`text-lg font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
              {task.title}
            </h3>
            {task.description && (
              <p className={`mt-1 text-sm ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
                {task.description}
              </p>
            )}
            <p className="mt-2 text-xs text-gray-400">
              Created: {new Date(task.created_at).toLocaleDateString()}
            </p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleEdit}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              disabled={isLoading}
            >
              Edit
            </button>
            <button
              onClick={() => setIsDeleting(true)}
              className="text-red-600 hover:text-red-800 text-sm font-medium"
              disabled={isLoading}
            >
              Delete
            </button>
          </div>
        </div>

        {errorMessage && <div className="error mt-4">{errorMessage}</div>}
      </div>

      <Modal
        isOpen={isDeleting}
        onClose={() => setIsDeleting(false)}
        title="Delete Task"
      >
        <p className="mb-4">Are you sure you want to delete this task? This action cannot be undone.</p>
        <div className="flex gap-2 justify-end">
          <Button onClick={handleDelete} variant="danger" isLoading={isLoading}>
            Delete
          </Button>
          <Button onClick={() => setIsDeleting(false)} variant="secondary" disabled={isLoading}>
            Cancel
          </Button>
        </div>
      </Modal>
    </>
  );
}
