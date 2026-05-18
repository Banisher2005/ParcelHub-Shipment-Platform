"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/utils";
import { STATUS_CONFIG } from "@/lib/constants";
import type { TrackingEvent, ShipmentStatus } from "@/types";

interface TrackingTimelineProps {
  events: TrackingEvent[];
}

export function TrackingTimeline({ events }: TrackingTimelineProps) {
  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <span className="text-3xl">📭</span>
        <p className="mt-2 text-sm">No tracking events yet</p>
      </div>
    );
  }

  return (
    <div className="relative space-y-0">
      {/* Timeline line */}
      <div className="absolute left-[19px] top-6 bottom-6 w-px bg-border/50" />

      {events.map((event, index) => {
        const config = STATUS_CONFIG[event.status as ShipmentStatus] || STATUS_CONFIG.unknown;
        const isFirst = index === 0;
        const isLast = index === events.length - 1;

        return (
          <motion.div
            key={event.id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.06 }}
            className="relative flex gap-4 pb-6 last:pb-0"
          >
            {/* Timeline dot */}
            <div className="relative z-10 flex shrink-0 items-start pt-0.5">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-full border-2",
                  "transition-all duration-300",
                  isFirst
                    ? "border-primary bg-primary/10 shadow-glow"
                    : "border-border bg-card"
                )}
              >
                <span className="text-sm">{config.icon}</span>
              </div>
            </div>

            {/* Event content */}
            <div className={cn("flex-1 pt-1", isFirst ? "" : "opacity-70")}>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p
                    className={cn(
                      "text-sm font-medium",
                      isFirst ? "text-foreground" : "text-muted-foreground"
                    )}
                  >
                    {event.description}
                  </p>
                  {event.location && (
                    <p className="mt-0.5 text-xs text-muted-foreground/60">
                      📍 {event.location}
                    </p>
                  )}
                </div>
                <span className="shrink-0 text-[11px] tabular-nums text-muted-foreground/50">
                  {formatDate(event.timestamp)}
                </span>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
