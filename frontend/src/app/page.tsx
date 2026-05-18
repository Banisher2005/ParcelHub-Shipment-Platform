"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useShipments } from "@/hooks/use-shipments";
import { useAppStore } from "@/stores/app-store";
import { StatsBar } from "@/components/dashboard/stats-bar";
import { FilterSidebar } from "@/components/dashboard/filter-sidebar";
import { ShipmentCard } from "@/components/shipments/shipment-card";
import { AddShipmentModal } from "@/components/shipments/add-shipment-modal";
import {
  LoadingSkeleton,
  EmptyState,
} from "@/components/common/loading-skeleton";
import type { Shipment } from "@/types";

export default function DashboardPage() {
  const { data, isLoading, error } = useShipments();
  const { setAddModalOpen, filters, setFilters } = useAppStore();

  const shipments: Shipment[] = data?.items || [];
  const hasShipments = shipments.length > 0;
  const hasFilters =
    filters.statuses.length > 0 ||
    filters.carriers.length > 0 ||
    filters.search !== "" ||
    filters.trackingSource !== "";

  return (
    <div className="min-h-screen bg-background gradient-mesh">
      {/* Header */}
      <header className="border-b border-border/40 bg-background/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📦</span>
            <h1 className="text-xl font-bold tracking-tight text-foreground">
              ParcelHub
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {/* Search */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search shipments…"
                value={filters.search}
                onChange={(e) => setFilters({ search: e.target.value })}
                className={cn(
                  "w-64 rounded-lg border border-border/50 bg-muted/30 px-3 py-2",
                  "text-sm text-foreground placeholder:text-muted-foreground/40",
                  "outline-none transition-all focus:border-primary/50 focus:ring-2 focus:ring-primary/20",
                  "focus:w-80"
                )}
                id="search-input"
              />
            </div>

            {/* Add button */}
            <button
              onClick={() => setAddModalOpen(true)}
              className={cn(
                "flex items-center gap-2 rounded-lg bg-primary px-4 py-2",
                "text-sm font-medium text-primary-foreground",
                "transition-all hover:bg-primary/90 hover:shadow-glow",
                "active:scale-[0.98]"
              )}
              id="add-shipment-button"
            >
              <span>+</span>
              Track Package
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-6 py-6">
        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <StatsBar />
        </motion.div>

        {/* Content Area */}
        <div className="mt-6 flex gap-6">
          {/* Sidebar Filters */}
          <motion.div
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="hidden lg:block"
          >
            <FilterSidebar />
          </motion.div>

          {/* Shipment List */}
          <div className="flex-1 min-w-0">
            {isLoading ? (
              <LoadingSkeleton />
            ) : error ? (
              <div className="flex flex-col items-center justify-center py-20">
                <span className="text-4xl">⚠️</span>
                <p className="mt-3 text-sm text-muted-foreground">
                  Failed to load shipments. Is the backend running?
                </p>
                <p className="mt-1 text-xs text-muted-foreground/50">
                  Run: uvicorn app.main:app --reload --port 8000
                </p>
              </div>
            ) : !hasShipments && !hasFilters ? (
              <EmptyState />
            ) : !hasShipments && hasFilters ? (
              <div className="flex flex-col items-center justify-center py-20">
                <span className="text-4xl">🔍</span>
                <p className="mt-3 text-sm text-muted-foreground">
                  No shipments match your filters
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {shipments.map((shipment, index) => (
                  <ShipmentCard
                    key={shipment.id}
                    shipment={shipment}
                    index={index}
                  />
                ))}

                {/* Pagination info */}
                {data && data.total > data.page_size && (
                  <p className="pt-4 text-center text-xs text-muted-foreground/50">
                    Showing {shipments.length} of {data.total} shipments
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Add Shipment Modal */}
      <AddShipmentModal />
    </div>
  );
}
