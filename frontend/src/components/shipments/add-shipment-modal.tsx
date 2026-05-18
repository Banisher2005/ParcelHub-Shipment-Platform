"use client";

import { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { useAddShipment, useDetectCarrier, useCarriers } from "@/hooks/use-shipments";
import { useAppStore } from "@/stores/app-store";
import { StatusPill } from "./status-pill";
import { CarrierBadge } from "./carrier-badge";
import { ALL_STATUSES, STATUS_CONFIG } from "@/lib/constants";
import { toast } from "sonner";
import type { ShipmentStatus } from "@/types";

export function AddShipmentModal() {
  const { addModalOpen, setAddModalOpen } = useAppStore();
  const addMutation = useAddShipment();
  const detectMutation = useDetectCarrier();
  const { data: carriers } = useCarriers();

  const [trackingNumber, setTrackingNumber] = useState("");
  const [title, setTitle] = useState("");
  const [selectedCarrier, setSelectedCarrier] = useState("");
  const [initialStatus, setInitialStatus] = useState<string>("ordered");
  const [isManualMode, setIsManualMode] = useState(false);
  const [detectedCarrier, setDetectedCarrier] = useState<any>(null);

  const manualCarriers = carriers?.filter(
    (c: any) => c.carrier_type === "manual_only"
  ) || [];

  // Reset form on close
  useEffect(() => {
    if (!addModalOpen) {
      setTrackingNumber("");
      setTitle("");
      setSelectedCarrier("");
      setInitialStatus("ordered");
      setIsManualMode(false);
      setDetectedCarrier(null);
    }
  }, [addModalOpen]);

  // Auto-detect carrier when tracking number changes
  const handleTrackingChange = useCallback(
    (value: string) => {
      setTrackingNumber(value);
      setDetectedCarrier(null);

      if (value.length >= 6 && !isManualMode) {
        detectMutation.mutate(value, {
          onSuccess: (result) => {
            if (result.detected && result.carrier) {
              setDetectedCarrier(result.carrier);
              setSelectedCarrier(result.carrier.code);
              if (result.carrier.carrier_type === "manual_only") {
                setIsManualMode(true);
              }
            }
          },
        });
      }
    },
    [detectMutation, isManualMode]
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackingNumber.trim()) return;

    try {
      await addMutation.mutateAsync({
        tracking_number: trackingNumber.trim(),
        carrier_code: selectedCarrier || undefined,
        title: title.trim() || undefined,
        status: isManualMode ? initialStatus : undefined,
      });
      toast.success("Shipment added successfully");
      setAddModalOpen(false);
    } catch (error: any) {
      toast.error(error?.detail || "Failed to add shipment");
    }
  };

  if (!addModalOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center"
        onClick={() => setAddModalOpen(false)}
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 12 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 12 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className={cn(
            "relative z-10 w-full max-w-md rounded-2xl border border-border/50",
            "bg-card p-6 shadow-2xl"
          )}
          onClick={(e) => e.stopPropagation()}
        >
          <h2 className="text-lg font-semibold text-foreground">
            Track a Package
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Paste your tracking number to get started
          </p>

          <form onSubmit={handleSubmit} className="mt-5 space-y-4">
            {/* Tracking Number */}
            <div>
              <label className="text-xs font-medium text-muted-foreground">
                Tracking Number
              </label>
              <input
                type="text"
                value={trackingNumber}
                onChange={(e) => handleTrackingChange(e.target.value)}
                placeholder="e.g., RR123456789CN"
                autoFocus
                className={cn(
                  "mt-1.5 w-full rounded-lg border border-border bg-background px-3 py-2.5",
                  "font-mono text-sm text-foreground placeholder:text-muted-foreground/40",
                  "outline-none transition-all focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
                )}
                id="add-tracking-number-input"
              />

              {/* Detection status */}
              <AnimatePresence mode="wait">
                {detectMutation.isPending && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-2 text-xs text-muted-foreground"
                  >
                    Detecting carrier…
                  </motion.p>
                )}
                {detectedCarrier && !isManualMode && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-2 flex items-center gap-2"
                  >
                    <span className="text-xs text-muted-foreground">
                      Detected:
                    </span>
                    <CarrierBadge
                      carrierCode={detectedCarrier.code}
                      carrierName={detectedCarrier.name}
                      size="sm"
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Mode Switch */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setIsManualMode(false)}
                className={cn(
                  "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                  !isManualMode
                    ? "bg-primary/15 text-primary"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                Auto-detect
              </button>
              <button
                type="button"
                onClick={() => setIsManualMode(true)}
                className={cn(
                  "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                  isManualMode
                    ? "bg-primary/15 text-primary"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                Manual carrier
              </button>
            </div>

            {/* Manual Mode: Carrier Select + Status */}
            <AnimatePresence>
              {isManualMode && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-4 overflow-hidden"
                >
                  <div>
                    <label className="text-xs font-medium text-muted-foreground">
                      Carrier
                    </label>
                    <select
                      value={selectedCarrier}
                      onChange={(e) => setSelectedCarrier(e.target.value)}
                      className={cn(
                        "mt-1.5 w-full rounded-lg border border-border bg-background px-3 py-2.5",
                        "text-sm text-foreground",
                        "outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
                      )}
                      id="add-carrier-select"
                    >
                      <option value="">Select carrier...</option>
                      {manualCarriers.map((c: any) => (
                        <option key={c.code} value={c.code}>
                          {c.name}
                        </option>
                      ))}
                      {carriers
                        ?.filter((c: any) => c.carrier_type === "api_trackable")
                        .map((c: any) => (
                          <option key={c.code} value={c.code}>
                            {c.name}
                          </option>
                        ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-xs font-medium text-muted-foreground">
                      Current Status
                    </label>
                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                      {ALL_STATUSES.map((status) => (
                        <button
                          key={status}
                          type="button"
                          onClick={() => setInitialStatus(status)}
                          className={cn(
                            "transition-all",
                            initialStatus === status
                              ? "scale-105 ring-2 ring-primary/30"
                              : "opacity-50 hover:opacity-80"
                          )}
                        >
                          <StatusPill status={status as ShipmentStatus} size="sm" />
                        </button>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Title (optional) */}
            <div>
              <label className="text-xs font-medium text-muted-foreground">
                Label{" "}
                <span className="text-muted-foreground/50">(optional)</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., MacBook Pro, Birthday gift"
                className={cn(
                  "mt-1.5 w-full rounded-lg border border-border bg-background px-3 py-2.5",
                  "text-sm text-foreground placeholder:text-muted-foreground/40",
                  "outline-none transition-all focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
                )}
                id="add-title-input"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setAddModalOpen(false)}
                className={cn(
                  "rounded-lg px-4 py-2 text-sm font-medium text-muted-foreground",
                  "transition-colors hover:text-foreground"
                )}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={
                  !trackingNumber.trim() || addMutation.isPending
                }
                className={cn(
                  "rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground",
                  "transition-all hover:bg-primary/90",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  addMutation.isPending && "animate-pulse"
                )}
                id="add-shipment-submit"
              >
                {addMutation.isPending ? "Adding…" : "Track Package"}
              </button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
