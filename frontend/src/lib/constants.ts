import type { ShipmentStatus } from "@/types";

/** Status display configuration — colors, labels, icons */
export const STATUS_CONFIG: Record<
  ShipmentStatus,
  { label: string; color: string; bgClass: string; textClass: string; icon: string }
> = {
  ordered: {
    label: "Ordered",
    color: "var(--color-status-ordered)",
    bgClass: "bg-status-ordered/15",
    textClass: "text-status-ordered",
    icon: "📦",
  },
  picked_up: {
    label: "Picked Up",
    color: "var(--color-status-picked-up)",
    bgClass: "bg-status-picked-up/15",
    textClass: "text-status-picked-up",
    icon: "🚚",
  },
  in_transit: {
    label: "In Transit",
    color: "var(--color-status-in-transit)",
    bgClass: "bg-status-in-transit/15",
    textClass: "text-status-in-transit",
    icon: "✈️",
  },
  customs: {
    label: "Customs",
    color: "var(--color-status-customs)",
    bgClass: "bg-status-customs/15",
    textClass: "text-status-customs",
    icon: "🛃",
  },
  out_for_delivery: {
    label: "Out for Delivery",
    color: "var(--color-status-out-for-delivery)",
    bgClass: "bg-status-out-for-delivery/15",
    textClass: "text-status-out-for-delivery",
    icon: "🏠",
  },
  delivered: {
    label: "Delivered",
    color: "var(--color-status-delivered)",
    bgClass: "bg-status-delivered/15",
    textClass: "text-status-delivered",
    icon: "✅",
  },
  delayed: {
    label: "Delayed",
    color: "var(--color-status-delayed)",
    bgClass: "bg-status-delayed/15",
    textClass: "text-status-delayed",
    icon: "⚠️",
  },
  exception: {
    label: "Exception",
    color: "var(--color-status-exception)",
    bgClass: "bg-status-exception/15",
    textClass: "text-status-exception",
    icon: "❌",
  },
  unknown: {
    label: "Unknown",
    color: "var(--color-status-unknown)",
    bgClass: "bg-status-unknown/15",
    textClass: "text-status-unknown",
    icon: "❓",
  },
};

/** Carrier display names for well-known carriers */
export const CARRIER_DISPLAY: Record<string, { name: string; emoji: string }> = {
  delhivery: { name: "Delhivery", emoji: "🇮🇳" },
  bluedart: { name: "BlueDart", emoji: "🔵" },
  india_post: { name: "India Post", emoji: "🇮🇳" },
  dhl: { name: "DHL", emoji: "🟡" },
  fedex: { name: "FedEx", emoji: "🟣" },
  ups: { name: "UPS", emoji: "🟤" },
  yunexpress: { name: "YunExpress", emoji: "🇨🇳" },
  cainiao: { name: "Cainiao", emoji: "🧡" },
  yanwen: { name: "Yanwen", emoji: "🇨🇳" },
  "4px": { name: "4PX", emoji: "📦" },
  amazon: { name: "Amazon", emoji: "📦" },
  flipkart: { name: "Flipkart", emoji: "🛒" },
  other: { name: "Other", emoji: "📋" },
};

/** API base URL */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** All statuses for filtering */
export const ALL_STATUSES: ShipmentStatus[] = [
  "ordered",
  "picked_up",
  "in_transit",
  "customs",
  "out_for_delivery",
  "delivered",
  "delayed",
  "exception",
];
