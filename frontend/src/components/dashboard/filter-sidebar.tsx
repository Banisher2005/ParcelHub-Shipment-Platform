"use client";

import { cn } from "@/lib/utils";
import { STATUS_CONFIG, ALL_STATUSES } from "@/lib/constants";
import { useAppStore } from "@/stores/app-store";
import { useCarriers } from "@/hooks/use-shipments";
import { CARRIER_DISPLAY } from "@/lib/constants";
import type { ShipmentStatus } from "@/types";

export function FilterSidebar() {
  const { filters, setFilters, resetFilters } = useAppStore();
  const { data: carriers } = useCarriers();

  const toggleStatus = (status: ShipmentStatus) => {
    const current = filters.statuses;
    const next = current.includes(status)
      ? current.filter((s) => s !== status)
      : [...current, status];
    setFilters({ statuses: next });
  };

  const toggleCarrier = (code: string) => {
    const current = filters.carriers;
    const next = current.includes(code)
      ? current.filter((c) => c !== code)
      : [...current, code];
    setFilters({ carriers: next });
  };

  const hasFilters =
    filters.statuses.length > 0 ||
    filters.carriers.length > 0 ||
    filters.trackingSource !== "";

  return (
    <aside className="w-56 shrink-0 space-y-6">
      {/* Status Filters */}
      <div>
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Status
          </h3>
          {hasFilters && (
            <button
              onClick={resetFilters}
              className="text-[11px] text-primary hover:text-primary/80 transition-colors"
            >
              Clear
            </button>
          )}
        </div>
        <div className="mt-2 space-y-0.5">
          {ALL_STATUSES.map((status) => {
            const config = STATUS_CONFIG[status];
            const isActive = filters.statuses.includes(status);
            return (
              <button
                key={status}
                onClick={() => toggleStatus(status)}
                className={cn(
                  "flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm",
                  "transition-colors duration-150",
                  isActive
                    ? "bg-muted text-foreground"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                )}
              >
                <span className="text-[0.7rem]">{config.icon}</span>
                <span className="flex-1">{config.label}</span>
                {isActive && (
                  <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Carrier Filters */}
      {carriers && carriers.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Carrier
          </h3>
          <div className="mt-2 space-y-0.5">
            {carriers.map((carrier: any) => {
              const display = CARRIER_DISPLAY[carrier.code] || {
                name: carrier.name,
                emoji: "📦",
              };
              const isActive = filters.carriers.includes(carrier.code);
              return (
                <button
                  key={carrier.code}
                  onClick={() => toggleCarrier(carrier.code)}
                  className={cn(
                    "flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm",
                    "transition-colors duration-150",
                    isActive
                      ? "bg-muted text-foreground"
                      : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                  )}
                >
                  <span className="text-[0.7rem]">{display.emoji}</span>
                  <span className="flex-1">{display.name}</span>
                  {carrier.carrier_type === "manual_only" && (
                    <span className="text-[9px] uppercase tracking-wider text-muted-foreground/50">
                      Manual
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Source Filter */}
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Source
        </h3>
        <div className="mt-2 space-y-0.5">
          {[
            { key: "", label: "All", emoji: "📋" },
            { key: "api", label: "Auto-tracked", emoji: "🔄" },
            { key: "manual", label: "Manual", emoji: "✏️" },
          ].map((src) => (
            <button
              key={src.key}
              onClick={() =>
                setFilters({
                  trackingSource:
                    filters.trackingSource === src.key ? "" : src.key,
                })
              }
              className={cn(
                "flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm",
                "transition-colors duration-150",
                filters.trackingSource === src.key
                  ? "bg-muted text-foreground"
                  : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
              )}
            >
              <span className="text-[0.7rem]">{src.emoji}</span>
              {src.label}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
