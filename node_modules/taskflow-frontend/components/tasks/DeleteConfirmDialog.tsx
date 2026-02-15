"use client";

import { Button } from "@/components/ui/Button";
import { AlertCircle } from "lucide-react";

interface DeleteConfirmDialogProps {
  isOpen: boolean;
  taskTitle: string;
  onConfirm: () => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

export function DeleteConfirmDialog({
  isOpen,
  taskTitle,
  onConfirm,
  onCancel,
  loading,
}: DeleteConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="glass-card w-full max-w-md rounded-2xl border border-white/10 overflow-hidden">
        <div className="p-6 space-y-4">
          <div className="flex items-center gap-4">
            <div className="bg-red-500/20 p-3 rounded-lg border border-red-500/30">
              <AlertCircle className="w-6 h-6 text-red-400" />
            </div>
            <h3 className="text-lg font-bold text-white uppercase">
              TERMINATE OPERATION?
            </h3>
          </div>

          <p className="text-gray-300 text-sm">
            Confirm deletion of{" "}
            <span className="text-red-400 font-bold">"{taskTitle}"</span>
          </p>

          <p className="text-xs text-red-400 font-mono uppercase tracking-widest">
            ⚠️ IRREVERSIBLE ACTION - DATA WILL BE PERMANENTLY PURGED
          </p>
        </div>

        <div className="border-t border-white/5 p-6 flex justify-end gap-3">
          <Button variant="ghost" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={loading}>
            Confirm Deletion
          </Button>
        </div>
      </div>
    </div>
  );
}
