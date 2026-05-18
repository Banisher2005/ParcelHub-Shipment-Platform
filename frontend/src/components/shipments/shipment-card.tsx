"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { formatRelativeTime, formatETA, truncate } from "@/lib/utils";
import { StatusPill } from "./status-pill";
import { CarrierBadge } from "./carrier-badge";
import type { Shipment } from "@/types";
import Link from "next/link";

interface ShipmentCardProps {
  shipment: Shipment;
  index?: number;
}

export function ShipmentCard({ shipment, index = 0 }: ShipmentCardProps) {
  const eta = formatETA(shipment.estimated_delivery);
  const lastUpdate = shipment.last_event_at
    ? formatRelativeTime(shipment.last_event_at)
    : "No updates";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.04 }}
    >
      <Link href={`/shipment/${shipment.id}`} id={`shipment-card-${shipment.id}`}>
        <div
          className={cn(
            "group relative rounded-xl border border-border/50 bg-card p-4",
            "transition-all duration-200 ease-out",
            "hover:border-border hover:bg-card/80 hover:shadow-card",
            "cursor-pointer"
          )}
        >
          {/* Top row: tracking number + status */}
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm font-semibold text-foreground">
                  {shipment.tracking_number}
                </span>
              </div>
              {shipment.title && (
                <p className="mt-0.5 text-sm text-muted-foreground">
                  {truncate(shipment.title, 50)}
                </p>
              )}
            </div>
            <StatusPill status={shipment.status} size="sm" />
          </div>

          {/* Middle: last event */}
          {shipment.last_event_description && (
            <p className="mt-3 text-xs leading-relaxed text-muted-foreground/80">
              {truncate(shipment.last_event_description, 80)}
            </p>
          )}

          {/* Bottom row: carrier + meta */}
          <div className="mt-3 flex items-center justify-between">
            <CarrierBadge
              carrierCode={shipment.carrier_code}
              carrierName={shipment.carrier_name}
              trackingSource={shipment.tracking_source}
              size="sm"
            />
            <div className="flex items-center gap-3 text-[11px] text-muted-foreground/60">
              {eta !== "—" && (
                <span>ETA {eta}</span>
              )}
              <span>{lastUpdate}</span>
            </div>
          </div>

          {/* Subtle hover glow */}
          <div
            className={cn(
              "pointer-events-none absolute inset-0 rounded-xl opacity-0",
              "transition-opacity duration-300 group-hover:opacity-100",
              "bg-gradient-to-r from-primary/[0.03] to-transparent"
            )}
          />
        </div>
      </Link>
    </motion.div>
  );
}
