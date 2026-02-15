"use client";

import { useState } from "react";
import { Repeat } from "lucide-react";

interface RecurrenceFormProps {
  value?: string | null;
  onChange: (rule: string | null) => void;
}

const RECURRENCE_OPTIONS = [
  { label: "None", value: "" },
  { label: "Daily", value: "FREQ=DAILY" },
  { label: "Weekly", value: "FREQ=WEEKLY" },
  { label: "Weekdays (Mon-Fri)", value: "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR" },
  { label: "Monthly", value: "FREQ=MONTHLY" },
];

export function RecurrenceForm({ value, onChange }: RecurrenceFormProps) {
  const [selected, setSelected] = useState(value || "");

  const handleChange = (newValue: string) => {
    setSelected(newValue);
    onChange(newValue || null);
  };

  return (
    <div className="space-y-2">
      <label className="flex items-center gap-2 text-[10px] font-black text-gray-400 uppercase tracking-widest">
        <Repeat className="w-3 h-3" />
        Recurrence
      </label>
      <select
        value={selected}
        onChange={(e) => handleChange(e.target.value)}
        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#00f2ff]/50 transition-colors"
      >
        {RECURRENCE_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value} className="bg-[#0a0014]">
            {opt.label}
          </option>
        ))}
      </select>
      {selected && (
        <p className="text-[10px] text-[#00f2ff]/60 font-mono">
          Rule: {selected}
        </p>
      )}
    </div>
  );
}
