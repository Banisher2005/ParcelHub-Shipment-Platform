/**
 * Typed API client for ParcelHub backend.
 * Clean fetch wrapper with error handling and JSON parsing.
 */

import { API_BASE_URL } from "./constants";

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public code?: string
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "An error occurred";
    try {
      const errorBody = await response.json();
      detail = errorBody.detail || detail;
    } catch {
      // ignore parse error
    }
    throw new ApiError(response.status, detail);
  }

  return response.json();
}

/** ParcelHub API client */
export const api = {
  shipments: {
    list: (params?: {
      page?: number;
      page_size?: number;
      status?: string;
      carrier_code?: string;
      tracking_source?: string;
      search?: string;
    }) => {
      const searchParams = new URLSearchParams();
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== "") {
            searchParams.set(key, String(value));
          }
        });
      }
      const query = searchParams.toString();
      return request<any>(`/api/v1/shipments${query ? `?${query}` : ""}`);
    },

    get: (id: string) =>
      request<any>(`/api/v1/shipments/${id}`),

    create: (data: {
      tracking_number: string;
      carrier_code?: string;
      title?: string;
      status?: string;
    }) =>
      request<any>("/api/v1/shipments", {
        method: "POST",
        body: JSON.stringify(data),
      }),

    update: (id: string, data: { title?: string; is_archived?: boolean }) =>
      request<any>(`/api/v1/shipments/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),

    archive: (id: string) =>
      request<any>(`/api/v1/shipments/${id}`, {
        method: "DELETE",
      }),

    refresh: (id: string) =>
      request<any>(`/api/v1/shipments/${id}/refresh`, {
        method: "POST",
      }),

    updateStatus: (
      id: string,
      data: { status: string; description?: string; location?: string }
    ) =>
      request<any>(`/api/v1/shipments/${id}/status`, {
        method: "POST",
        body: JSON.stringify(data),
      }),

    stats: () => request<any>("/api/v1/shipments/stats"),
  },

  carriers: {
    list: (carrier_type?: string) => {
      const params = carrier_type ? `?carrier_type=${carrier_type}` : "";
      return request<any[]>(`/api/v1/carriers${params}`);
    },

    detect: (tracking_number: string) =>
      request<any>("/api/v1/carriers/detect", {
        method: "POST",
        body: JSON.stringify({ tracking_number }),
      }),
  },

  tracking: {
    refreshAll: () =>
      request<any>("/api/v1/tracking/refresh-all", {
        method: "POST",
      }),
  },
};
