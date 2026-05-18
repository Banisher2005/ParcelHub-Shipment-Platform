import { create } from "zustand";
import type { ShipmentStatus } from "@/types";

interface Filters {
  statuses: ShipmentStatus[];
  carriers: string[];
  search: string;
  trackingSource: string;
}

interface AppState {
  // Filters
  filters: Filters;
  setFilters: (filters: Partial<Filters>) => void;
  resetFilters: () => void;

  // UI
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  addModalOpen: boolean;
  setAddModalOpen: (open: boolean) => void;
}

const defaultFilters: Filters = {
  statuses: [],
  carriers: [],
  search: "",
  trackingSource: "",
};

export const useAppStore = create<AppState>((set) => ({
  // Filters
  filters: { ...defaultFilters },
  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),
  resetFilters: () => set({ filters: { ...defaultFilters } }),

  // UI
  sidebarOpen: true,
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  addModalOpen: false,
  setAddModalOpen: (open) => set({ addModalOpen: open }),
}));
