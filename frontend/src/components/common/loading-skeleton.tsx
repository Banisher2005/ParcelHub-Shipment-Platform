"use client";

import { cn } from "@/lib/utils";

export function LoadingSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "rounded-xl border border-border/30 bg-card p-4",
            "animate-shimmer"
          )}
          style={{ animationDelay: `${i * 100}ms` }}
        >
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <div className="h-4 w-40 rounded bg-muted" />
              <div className="h-3 w-24 rounded bg-muted/60" />
            </div>
            <div className="h-6 w-20 rounded-full bg-muted" />
          </div>
          <div className="mt-3 h-3 w-64 rounded bg-muted/40" />
          <div className="mt-3 flex justify-between">
            <div className="h-5 w-20 rounded bg-muted/50" />
            <div className="h-3 w-16 rounded bg-muted/30" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="text-6xl">📦</div>
      <h3 className="mt-4 text-lg font-semibold text-foreground">
        No shipments yet
      </h3>
      <p className="mt-2 max-w-sm text-center text-sm text-muted-foreground">
        Start tracking your packages by clicking the &quot;Track Package&quot;
        button above. Paste any tracking number and we&apos;ll handle the rest.
      </p>
    </div>
  );
}
