"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { TaskList } from "../../../components/tasks/TaskList";
import { TaskForm } from "../../../components/tasks/TaskForm";
import { LoadingSpinner } from "../../../components/ui/LoadingSpinner";
import { Task, TaskCreate } from "../../../types/task";
import { APIClient } from "../../../lib/api/client";
import { TaskAPI } from "../../../lib/api/tasks";
import { getToken, clearSession } from "../../../lib/auth/session";
import { useAuth } from "../../../hooks/useAuth";

export default function TasksPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check authentication and redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/signin");
    }
  }, [isAuthenticated, authLoading, router]);

  // Initialize API client
  const apiClient = new APIClient({
    baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    getToken,
    onAuthError: () => {
      clearSession();
      router.push("/signin?expired=true");
    },
  });

  const taskAPI = new TaskAPI(apiClient);

  // Fetch tasks on mount
  useEffect(() => {
    if (isAuthenticated) {
      fetchTasks();
    }
  }, [isAuthenticated]);

  const fetchTasks = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const fetchedTasks = await taskAPI.list();
      setTasks(fetchedTasks);
    } catch (err: any) {
      setError(err.detail || "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (data: TaskCreate) => {
    try {
      const newTask = await taskAPI.create(data);
      setTasks([...tasks, newTask]);
    } catch (err: any) {
      throw new Error(err.detail || "Failed to create task");
    }
  };

  const handleUpdateTask = async (id: number, data: Partial<Task>) => {
    try {
      const updatedTask = await taskAPI.update(id, data);
      setTasks(tasks.map((t) => (t.id === id ? updatedTask : t)));
    } catch (err: any) {
      throw new Error(err.detail || "Failed to update task");
    }
  };

  const handleDeleteTask = async (id: number) => {
    try {
      await taskAPI.delete(id);
      setTasks(tasks.filter((t) => t.id !== id));
    } catch (err: any) {
      throw new Error(err.detail || "Failed to delete task");
    }
  };

  const handleToggleComplete = async (id: number) => {
    try {
      const updatedTask = await taskAPI.toggleComplete(id);
      setTasks(tasks.map((t) => (t.id === id ? updatedTask : t)));
    } catch (err: any) {
      throw new Error(err.detail || "Failed to toggle task completion");
    }
  };

  // Show loading spinner while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  // Prevent flash of content while redirecting
  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container max-w-4xl mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 ">My Tasks</h1>
          <p className="text-gray-600">Manage your tasks and stay organized</p>
        </div>

        {error && <div className="error mb-6">{error}</div>}

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
          <TaskForm onSubmit={handleCreateTask} />
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Your Tasks</h2>
          <TaskList
            tasks={tasks}
            onUpdate={handleUpdateTask}
            onDelete={handleDeleteTask}
            onToggleComplete={handleToggleComplete}
          />
        </div>
      </div>
    </div>
  );
}
