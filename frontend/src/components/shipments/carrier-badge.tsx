"use client";

import { cn } from "@/lib/utils";
import { CARRIER_DISPLAY } from "@/lib/constants";

interface CarrierBadgeProps {
  carrierCode: string;
  carrierName: string;
  trackingSource?: string;
  size?: "sm" | "md";
  className?: string;
}

export function CarrierBadge({
  carrierCode,
  carrierName,
  trackingSource,
  size = "md",
  className,
}: CarrierBadgeProps) {
  const display = CARRIER_DISPLAY[carrierCode] || {
    name: carrierName,
    emoji: "📦",
  };
  const isManual = trackingSource === "manual";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md font-medium",
        "bg-muted/50 text-muted-foreground",
        "transition-colors duration-200",
        size === "sm" && "px-1.5 py-0.5 text-[11px]",
        size === "md" && "px-2 py-1 text-xs",
        className
      )}
    >
      <span className="text-[0.7rem] leading-none">{display.emoji}</span>
      {display.name}
      {isManual && (
        <span className="ml-0.5 rounded bg-muted px-1 py-0.5 text-[9px] uppercase tracking-wider text-muted-foreground/60">
          Manual
        </span>
      )}
    </span>
  );
}
