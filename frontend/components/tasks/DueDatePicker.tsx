"use client";

import { useState } from "react";
import { Calendar, Bell } from "lucide-react";

interface DueDatePickerProps {
  value?: string | null;
  onChange: (date: string | null) => void;
  onAddReminder?: (remindAt: string) => void;
}

export function DueDatePicker({ value, onChange, onAddReminder }: DueDatePickerProps) {
  const [showReminders, setShowReminders] = useState(false);

  return (
    <div className="space-y-2">
      <label className="flex items-center gap-2 text-[10px] font-black text-gray-400 uppercase tracking-widest">
        <Calendar className="w-3 h-3" />
        Due Date
      </label>
      <input
        type="datetime-local"
        value={value ? value.slice(0, 16) : ""}
        onChange={(e) => onChange(e.target.value ? new Date(e.target.value).toISOString() : null)}
        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#00f2ff]/50 transition-colors [color-scheme:dark]"
      />

      {value && onAddReminder && (
        <div className="space-y-2">
          <button
            type="button"
            onClick={() => setShowReminders(!showReminders)}
            className="flex items-center gap-1 text-[10px] text-[#ff00c8] hover:text-[#ff00c8]/80 font-bold uppercase tracking-widest"
          >
            <Bell className="w-3 h-3" />
            {showReminders ? "Hide Reminders" : "Add Reminder"}
          </button>

          {showReminders && (
            <div className="flex flex-wrap gap-2">
              {[
                { label: "1 day before", hours: 24 },
                { label: "1 hour before", hours: 1 },
                { label: "30 min before", hours: 0.5 },
              ].map((preset) => (
                <button
                  key={preset.label}
                  type="button"
                  onClick={() => {
                    const dueDate = new Date(value);
                    const remindAt = new Date(dueDate.getTime() - preset.hours * 60 * 60 * 1000);
                    onAddReminder(remindAt.toISOString());
                  }}
                  className="text-[10px] px-2 py-1 rounded bg-[#ff00c8]/10 text-[#ff00c8] border border-[#ff00c8]/20 hover:bg-[#ff00c8]/20 transition-colors"
                >
                  {preset.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
