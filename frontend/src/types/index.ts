/** Universal shipment status — matches backend ShipmentStatus enum. */
export type ShipmentStatus =
  | "ordered"
  | "picked_up"
  | "in_transit"
  | "customs"
  | "out_for_delivery"
  | "delivered"
  | "delayed"
  | "exception"
  | "unknown";

/** How tracking data is obtained. */
export type TrackingSource = "api" | "manual" | "email" | "extension";

/** Carrier classification. */
export type CarrierType = "api_trackable" | "manual_only";

export interface Shipment {
  id: string;
  tracking_number: string;
  carrier_code: string;
  carrier_name: string;
  title: string | null;
  status: ShipmentStatus;
  tracking_source: TrackingSource;
  origin: string | null;
  destination: string | null;
  estimated_delivery: string | null;
  last_event_at: string | null;
  last_event_description: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface ShipmentDetail extends Shipment {
  events: TrackingEvent[];
}

export interface TrackingEvent {
  id: string;
  shipment_id: string;
  status: ShipmentStatus;
  description: string;
  location: string | null;
  timestamp: string;
  raw_status: string | null;
  provider_code: string | null;
  created_at: string;
}

export interface Carrier {
  id: string;
  code: string;
  name: string;
  carrier_type: CarrierType;
  country: string | null;
  tracking_url_template: string | null;
  logo_url: string | null;
  is_active: boolean;
}

export interface ShipmentStats {
  total: number;
  ordered: number;
  picked_up: number;
  in_transit: number;
  customs: number;
  out_for_delivery: number;
  delivered: number;
  delayed: number;
  exception: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ShipmentCreateRequest {
  tracking_number: string;
  carrier_code?: string;
  title?: string;
  status?: string;
}

export interface ShipmentUpdateRequest {
  title?: string;
  is_archived?: boolean;
}

export interface ManualStatusUpdateRequest {
  status: string;
  description?: string;
  location?: string;
}

export interface CarrierDetectResponse {
  detected: boolean;
  carrier: Carrier | null;
  confidence: number;
  suggestions: Carrier[];
}
