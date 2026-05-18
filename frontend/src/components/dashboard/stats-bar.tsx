"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useShipmentStats } from "@/hooks/use-shipments";
import { STATUS_CONFIG, ALL_STATUSES } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { ShipmentStatus, ShipmentStats } from "@/types";

export function StatsBar() {
  const { data: stats, isLoading } = useShipmentStats();

  if (isLoading) {
    return (
      <div className="flex gap-2 overflow-x-auto pb-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-[68px] w-[120px] shrink-0 rounded-lg bg-card animate-shimmer"
          />
        ))}
      </div>
    );
  }

  if (!stats) return null;

  const statItems: { key: string; label: string; value: number; status?: ShipmentStatus }[] =
    [
      { key: "total", label: "Total", value: stats.total },
      ...ALL_STATUSES
        .filter((s) => (stats[s as keyof ShipmentStats] as number) > 0)
        .map((s) => ({
          key: s,
          label: STATUS_CONFIG[s].label,
          value: stats[s as keyof ShipmentStats] as number,
          status: s as ShipmentStatus,
        })),
    ];

  return (
    <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
      <AnimatePresence mode="popLayout">
        {statItems.map((item) => (
          <motion.div
            key={item.key}
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className={cn(
              "flex shrink-0 flex-col items-center justify-center rounded-lg border border-border/40 px-4 py-3",
              "min-w-[100px] bg-card/60 backdrop-blur-sm",
              "transition-colors hover:border-border/70"
            )}
          >
            <motion.span
              key={item.value}
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                "text-xl font-bold tabular-nums",
                item.status
                  ? STATUS_CONFIG[item.status].textClass
                  : "text-foreground"
              )}
            >
              {item.value}
            </motion.span>
            <span className="mt-0.5 text-[11px] font-medium text-muted-foreground">
              {item.label}
            </span>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
