"use client";

import { cn } from "@/lib/utils";
import { STATUS_CONFIG } from "@/lib/constants";
import type { ShipmentStatus } from "@/types";

interface StatusPillProps {
  status: ShipmentStatus;
  size?: "sm" | "md";
  className?: string;
}

export function StatusPill({ status, size = "md", className }: StatusPillProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.unknown;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full font-medium",
        "transition-all duration-200",
        size === "sm" && "px-2 py-0.5 text-xs",
        size === "md" && "px-2.5 py-1 text-xs",
        config.bgClass,
        config.textClass,
        className
      )}
    >
      <span className="text-[0.65rem] leading-none">{config.icon}</span>
      {config.label}
    </span>
  );
}
