"use client";

import { use, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { formatDate, formatETA } from "@/lib/utils";
import {
  useShipment,
  useRefreshShipment,
  useManualStatusUpdate,
  useUpdateShipment,
  useArchiveShipment,
} from "@/hooks/use-shipments";
import { StatusPill } from "@/components/shipments/status-pill";
import { CarrierBadge } from "@/components/shipments/carrier-badge";
import { TrackingTimeline } from "@/components/tracking/tracking-timeline";
import { ALL_STATUSES, STATUS_CONFIG } from "@/lib/constants";
import { toast } from "sonner";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ShipmentStatus } from "@/types";

export default function ShipmentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { data: shipment, isLoading, error } = useShipment(id);
  const refreshMutation = useRefreshShipment();
  const statusMutation = useManualStatusUpdate();
  const updateMutation = useUpdateShipment();
  const archiveMutation = useArchiveShipment();

  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [showStatusPicker, setShowStatusPicker] = useState(false);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background gradient-mesh">
        <div className="mx-auto max-w-3xl px-6 py-8">
          <div className="h-8 w-32 rounded bg-muted animate-shimmer" />
          <div className="mt-6 h-12 w-80 rounded bg-muted animate-shimmer" />
          <div className="mt-4 space-y-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex gap-4">
                <div className="h-10 w-10 rounded-full bg-muted animate-shimmer" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-48 rounded bg-muted animate-shimmer" />
                  <div className="h-3 w-32 rounded bg-muted/60 animate-shimmer" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error || !shipment) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-center">
          <span className="text-5xl">😞</span>
          <p className="mt-4 text-lg font-medium text-foreground">
            Shipment not found
          </p>
          <Link
            href="/"
            className="mt-2 inline-block text-sm text-primary hover:underline"
          >
            ← Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  const isManual = shipment.tracking_source === "manual";

  const handleRefresh = () => {
    refreshMutation.mutate(shipment.id, {
      onSuccess: () => toast.success("Tracking refreshed"),
      onError: () => toast.error("Failed to refresh"),
    });
  };

  const handleStatusUpdate = (status: string) => {
    statusMutation.mutate(
      { id: shipment.id, data: { status } },
      {
        onSuccess: () => {
          toast.success(`Status updated to ${STATUS_CONFIG[status as ShipmentStatus]?.label || status}`);
          setShowStatusPicker(false);
        },
        onError: () => toast.error("Failed to update status"),
      }
    );
  };

  const handleSaveTitle = () => {
    if (editTitle.trim() !== (shipment.title || "")) {
      updateMutation.mutate(
        { id: shipment.id, data: { title: editTitle.trim() || undefined } },
        {
          onSuccess: () => toast.success("Title updated"),
        }
      );
    }
    setIsEditingTitle(false);
  };

  const handleArchive = () => {
    archiveMutation.mutate(shipment.id, {
      onSuccess: () => {
        toast.success("Shipment archived");
        router.push("/");
      },
    });
  };

  return (
    <div className="min-h-screen bg-background gradient-mesh">
      {/* Header */}
      <header className="border-b border-border/40 bg-background/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            ← Back
          </Link>
          <div className="flex items-center gap-2">
            {!isManual && (
              <button
                onClick={handleRefresh}
                disabled={refreshMutation.isPending}
                className={cn(
                  "rounded-lg border border-border/50 px-3 py-1.5 text-xs font-medium",
                  "text-muted-foreground transition-all hover:bg-muted hover:text-foreground",
                  refreshMutation.isPending && "animate-pulse"
                )}
                id="refresh-button"
              >
                {refreshMutation.isPending ? "Refreshing…" : "🔄 Refresh"}
              </button>
            )}
            <button
              onClick={handleArchive}
              className="rounded-lg border border-border/50 px-3 py-1.5 text-xs font-medium text-muted-foreground transition-all hover:border-destructive/50 hover:text-destructive"
              id="archive-button"
            >
              Archive
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-8">
        {/* Shipment Header */}
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-3"
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <span className="font-mono text-xl font-bold text-foreground">
                  {shipment.tracking_number}
                </span>
                <StatusPill status={shipment.status} />
              </div>

              {/* Editable title */}
              {isEditingTitle ? (
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onBlur={handleSaveTitle}
                  onKeyDown={(e) => e.key === "Enter" && handleSaveTitle()}
                  autoFocus
                  className="mt-1 w-full border-b border-primary bg-transparent py-1 text-sm text-foreground outline-none"
                  placeholder="Add a label…"
                />
              ) : (
                <button
                  onClick={() => {
                    setEditTitle(shipment.title || "");
                    setIsEditingTitle(true);
                  }}
                  className="mt-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  {shipment.title || "Add a label…"}
                </button>
              )}
            </div>
          </div>

          {/* Meta info */}
          <div className="flex flex-wrap items-center gap-3">
            <CarrierBadge
              carrierCode={shipment.carrier_code}
              carrierName={shipment.carrier_name}
              trackingSource={shipment.tracking_source}
            />
            {shipment.origin && (
              <span className="text-xs text-muted-foreground">
                From: {shipment.origin}
              </span>
            )}
            {shipment.destination && (
              <span className="text-xs text-muted-foreground">
                To: {shipment.destination}
              </span>
            )}
            {shipment.estimated_delivery && (
              <span className="text-xs text-muted-foreground">
                ETA: {formatETA(shipment.estimated_delivery)}
              </span>
            )}
          </div>

          {/* Manual Status Update */}
          {isManual && (
            <div className="mt-2">
              <button
                onClick={() => setShowStatusPicker(!showStatusPicker)}
                className={cn(
                  "rounded-lg border border-dashed border-border px-3 py-2 text-xs",
                  "text-muted-foreground transition-all hover:border-primary/50 hover:text-primary"
                )}
                id="update-status-button"
              >
                ✏️ Update Status
              </button>

              {showStatusPicker && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mt-2 flex flex-wrap gap-1.5"
                >
                  {ALL_STATUSES.map((status) => (
                    <button
                      key={status}
                      onClick={() => handleStatusUpdate(status)}
                      disabled={statusMutation.isPending}
                      className={cn(
                        "transition-all hover:scale-105",
                        shipment.status === status && "ring-2 ring-primary/30"
                      )}
                    >
                      <StatusPill status={status as ShipmentStatus} size="sm" />
                    </button>
                  ))}
                </motion.div>
              )}
            </div>
          )}
        </motion.div>

        {/* Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className={cn(
            "mt-8 rounded-xl border border-border/40 bg-card/60 p-6",
            "backdrop-blur-sm"
          )}
        >
          <h2 className="mb-6 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Tracking History
          </h2>
          <TrackingTimeline events={shipment.events} />
        </motion.div>
      </main>
    </div>
  );
}
