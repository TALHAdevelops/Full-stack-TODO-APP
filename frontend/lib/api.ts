import { Task, TaskCreateData, TaskUpdateData, ApiError, User } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getAuthHeaders() {
  const token = localStorage.getItem("auth_token");
  if (!token) {
    throw new Error("Unauthorized");
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function getCurrentUser(): Promise<User> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/auth/me`, {
    headers,
  });

  if (response.status === 401) {
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Failed to fetch user"
    );
  }

  return response.json();
}

export async function getTasks(): Promise<Task[]> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/tasks`, {
    headers,
  });

  if (response.status === 401) {
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Failed to fetch tasks"
    );
  }

  return response.json();
}

export async function createTask(data: TaskCreateData): Promise<Task> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/tasks`, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });

  if (response.status === 401) {
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Failed to create task"
    );
  }

  return response.json();
}

export async function updateTask(
  taskId: number,
  data: TaskUpdateData
): Promise<Task> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/tasks/${taskId}`, {
    method: "PUT",
    headers,
    body: JSON.stringify(data),
  });

  if (response.status === 401) {
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Failed to update task"
    );
  }

  return response.json();
}

export async function deleteTask(taskId: number): Promise<void> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/tasks/${taskId}`, {
    method: "DELETE",
    headers,
  });

  if (response.status === 401) {
    throw new Error("Unauthorized");
  }

  if (!response.ok && response.status !== 204) {
    const error: ApiError = await response.json();
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Failed to delete task"
    );
  }
}

export async function toggleTaskStatus(taskId: number): Promise<Task> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/api/tasks/${taskId}/complete`, {
    method: "PATCH",
    headers,
  });

  if (response.status === 401) {
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Failed to toggle task"
    );
  }

  return response.json();
}
