"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { TaskForm } from "@/components/tasks/TaskForm";
import { TaskList } from "@/components/tasks/TaskList";
import { DeleteConfirmDialog } from "@/components/tasks/DeleteConfirmDialog";
import { Task } from "@/lib/types";
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  toggleTaskStatus,
  getCurrentUser,
} from "@/lib/api";
import { LayoutDashboard, Target, Layers } from "lucide-react";

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  // Edit/Delete state
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deletingTaskId, setDeletingTaskId] = useState<number | null>(null);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const token = localStorage.getItem("auth_token");
        if (!token) {
          router.push("/");
          return;
        }

        // Fetch current user and tasks
        const userData = await getCurrentUser();
        setUser(userData);

        const tasksData = await getTasks();
        setTasks(tasksData);
      } catch (err) {
        if (err instanceof Error && err.message === "Unauthorized") {
          localStorage.removeItem("auth_token");
          router.push("/");
        } else {
          console.error(err);
          // Still allow browsing even if we can't get user info
          try {
            const tasksData = await getTasks();
            setTasks(tasksData);
            setUser({ authenticated: true });
          } catch {
            localStorage.removeItem("auth_token");
            router.push("/");
          }
        }
      } finally {
        setLoading(false);
      }
    };
    checkSession();
  }, [router]);

  const handleCreateTask = async (title: string, description: string) => {
    setActionLoading(true);
    try {
      const newTask = await createTask({ title, description });
      setTasks([newTask, ...tasks]);
    } catch (err) {
      alert("Failed to create task");
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateTask = async (title: string, description: string) => {
    if (!editingTask) return;
    setActionLoading(true);
    try {
      const updated = await updateTask(editingTask.id, { title, description });
      setTasks(tasks.map((t) => (t.id === editingTask.id ? updated : t)));
      setEditingTask(null);
    } catch (err) {
      alert("Failed to update task");
    } finally {
      setActionLoading(false);
    }
  };

  const handleToggleTask = async (taskId: number) => {
    // Optimistic update
    setTasks(
      tasks.map((t) =>
        t.id === taskId ? { ...t, completed: !t.completed } : t
      )
    );
    try {
      await toggleTaskStatus(taskId);
    } catch (err) {
      // Revert on error
      const refreshedTasks = await getTasks();
      setTasks(refreshedTasks);
    }
  };

  const handleDeleteTask = async () => {
    if (!deletingTaskId) return;
    setActionLoading(true);
    try {
      await deleteTask(deletingTaskId);
      setTasks(tasks.filter((t) => t.id !== deletingTaskId));
      setDeletingTaskId(null);
    } catch (err) {
      alert("Failed to delete task");
    } finally {
      setActionLoading(false);
    }
  };

  const handleSignOut = async () => {
    router.push("/");
  };

  const deletingTask = tasks.find((t) => t.id === deletingTaskId);

  return (
    <div className="min-h-screen bg-[#05010d] flex flex-col selection:bg-[#00f2ff]/30 selection:text-white">
      <Header userEmail={user?.email} onSignOut={handleSignOut} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10">
        <div className="flex items-center gap-4 mb-10 fade-in slide-in-top">
          <div className="p-3 rounded-2xl bg-gradient-to-br from-[#00f2ff]/20 to-transparent border border-[#00f2ff]/20">
            <LayoutDashboard className="w-6 h-6 text-[#00f2ff]" />
          </div>
          <div>
            <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic leading-none">
              Operation Center
            </h1>
            <p className="text-gray-500 text-[10px] uppercase font-bold tracking-[0.3em] mt-2">
              Active Grid Synchronization: ONLINE
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
          {/* Left: Input Console */}
          <div className="lg:col-span-4 space-y-6 sticky top-24 fade-in slide-in-left">
            <div className="flex items-center gap-2 mb-2 px-2">
              <Target className="w-4 h-4 text-[#9d00ff]" />
              <h2 className="text-xs font-black text-[#9d00ff] uppercase tracking-widest">
                Input Console
              </h2>
            </div>
            <TaskForm
              onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
              onCancel={editingTask ? () => setEditingTask(null) : undefined}
              initialTask={editingTask || undefined}
              loading={actionLoading}
            />
            {/* System Status Mock */}
            <div className="glass-card p-6 rounded-2xl border-white/5 space-y-4">
              <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-widest">
                System Telemetry
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-[10px] font-mono">
                  <span className="text-gray-600">DATABASE LATENCY</span>
                  <span className="text-[#00f2ff]">12ms</span>
                </div>
                <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                  <div className="w-1/3 h-full bg-[#00f2ff] animate-pulse"></div>
                </div>
                <div className="flex justify-between items-center text-[10px] font-mono">
                  <span className="text-gray-600">CORE TEMPERATURE</span>
                  <span className="text-[#ff00c8]">OPTIMAL</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Active Grid */}
          <div className="lg:col-span-8 fade-in slide-in-right">
            <div className="flex justify-between items-center mb-6 px-2">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-[#00f2ff]" />
                <h2 className="text-xs font-black text-white uppercase tracking-widest">
                  Active Operations Grid
                </h2>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">
                  Load Density
                </span>
                <span className="bg-[#00f2ff]/10 text-[#00f2ff] px-2 py-0.5 rounded text-[10px] font-black border border-[#00f2ff]/20">
                  {tasks.length} UNIT{tasks.length !== 1 ? "S" : ""}
                </span>
              </div>
            </div>

            <div className="space-y-4">
              <TaskList
                tasks={tasks}
                loading={loading}
                onEdit={setEditingTask}
                onDelete={setDeletingTaskId}
                onToggle={handleToggleTask}
              />
            </div>
          </div>
        </div>
      </main>

      <DeleteConfirmDialog
        isOpen={deletingTaskId !== null}
        taskTitle={deletingTask?.title || ""}
        onConfirm={handleDeleteTask}
        onCancel={() => setDeletingTaskId(null)}
        loading={actionLoading}
      />
    </div>
  );
}
