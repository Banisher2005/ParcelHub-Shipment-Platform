"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/stores/app-store";
import type {
  Shipment,
  ShipmentDetail,
  ShipmentStats,
  PaginatedResponse,
  ShipmentCreateRequest,
} from "@/types";

/** Fetch paginated shipment list with current filters. */
export function useShipments(page = 1, pageSize = 20) {
  const filters = useAppStore((s) => s.filters);

  return useQuery<PaginatedResponse<Shipment>>({
    queryKey: ["shipments", page, pageSize, filters],
    queryFn: () =>
      api.shipments.list({
        page,
        page_size: pageSize,
        status: filters.statuses.length === 1 ? filters.statuses[0] : undefined,
        carrier_code:
          filters.carriers.length === 1 ? filters.carriers[0] : undefined,
        tracking_source: filters.trackingSource || undefined,
        search: filters.search || undefined,
      }),
    staleTime: 30_000, // 30s before refetch
  });
}

/** Fetch single shipment with events. */
export function useShipment(id: string) {
  return useQuery<ShipmentDetail>({
    queryKey: ["shipment", id],
    queryFn: () => api.shipments.get(id),
    enabled: !!id,
  });
}

/** Fetch dashboard stats. */
export function useShipmentStats() {
  return useQuery<ShipmentStats>({
    queryKey: ["shipment-stats"],
    queryFn: () => api.shipments.stats(),
    staleTime: 30_000,
  });
}

/** Add a new shipment. */
export function useAddShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ShipmentCreateRequest) => api.shipments.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["shipments"] });
      queryClient.invalidateQueries({ queryKey: ["shipment-stats"] });
    },
  });
}

/** Refresh tracking for a shipment. */
export function useRefreshShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.shipments.refresh(id),
    onSuccess: (data: ShipmentDetail) => {
      queryClient.setQueryData(["shipment", data.id], data);
      queryClient.invalidateQueries({ queryKey: ["shipments"] });
      queryClient.invalidateQueries({ queryKey: ["shipment-stats"] });
    },
  });
}

/** Archive a shipment (optimistic). */
export function useArchiveShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.shipments.archive(id),
    onMutate: async (id: string) => {
      await queryClient.cancelQueries({ queryKey: ["shipments"] });
      const previous = queryClient.getQueryData(["shipments"]);
      // Optimistically remove from list
      queryClient.setQueriesData(
        { queryKey: ["shipments"] },
        (old: any) => {
          if (!old?.items) return old;
          return {
            ...old,
            items: old.items.filter((s: Shipment) => s.id !== id),
            total: old.total - 1,
          };
        }
      );
      return { previous };
    },
    onError: (_err, _id, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["shipments"], context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["shipments"] });
      queryClient.invalidateQueries({ queryKey: ["shipment-stats"] });
    },
  });
}

/** Update shipment title. */
export function useUpdateShipment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { title?: string } }) =>
      api.shipments.update(id, data),
    onSuccess: (data: ShipmentDetail) => {
      queryClient.setQueryData(["shipment", data.id], data);
      queryClient.invalidateQueries({ queryKey: ["shipments"] });
    },
  });
}

/** Manual status update. */
export function useManualStatusUpdate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { status: string; description?: string; location?: string };
    }) => api.shipments.updateStatus(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["shipment", variables.id],
      });
      queryClient.invalidateQueries({ queryKey: ["shipments"] });
      queryClient.invalidateQueries({ queryKey: ["shipment-stats"] });
    },
  });
}

/** Fetch carriers list. */
export function useCarriers(type?: string) {
  return useQuery({
    queryKey: ["carriers", type],
    queryFn: () => api.carriers.list(type),
    staleTime: 300_000, // 5 min
  });
}

/** Detect carrier from tracking number. */
export function useDetectCarrier() {
  return useMutation({
    mutationFn: (trackingNumber: string) =>
      api.carriers.detect(trackingNumber),
  });
}
