import { farmApi } from '@/lib/apiClient';
import type { FarmPlot, SoilProfile, CropSeason, IoTDevice, PlotBoundary } from '@/types';

export const farmService = {
  // Plots
  getPlots: async (): Promise<FarmPlot[]> => {
    const res = await farmApi.get<FarmPlot[]>('/v1/plots');
    return res.data;
  },

  getPlot: async (plotId: string): Promise<FarmPlot> => {
    const res = await farmApi.get<FarmPlot>(`/v1/plots/${plotId}`);
    return res.data;
  },

  createPlot: async (data: Omit<FarmPlot, 'id' | 'owner_id' | 'created_at' | 'updated_at'>): Promise<FarmPlot> => {
    const res = await farmApi.post<FarmPlot>('/v1/plots', data);
    return res.data;
  },

  updatePlot: async (plotId: string, data: Partial<FarmPlot>): Promise<FarmPlot> => {
    const res = await farmApi.patch<FarmPlot>(`/v1/plots/${plotId}`, data);
    return res.data;
  },

  deletePlot: async (plotId: string): Promise<void> => {
    await farmApi.delete(`/v1/plots/${plotId}`);
  },

  // Boundaries
  getPlotBoundary: async (plotId: string): Promise<PlotBoundary> => {
    const res = await farmApi.get<PlotBoundary>(`/v1/plots/${plotId}/boundary`);
    return res.data;
  },

  upsertBoundary: async (plotId: string, geojson: GeoJSON.Geometry): Promise<PlotBoundary> => {
    const res = await farmApi.put<PlotBoundary>(`/v1/plots/${plotId}/boundary`, { geojson });
    return res.data;
  },

  // Soil
  getSoilProfile: async (plotId: string): Promise<SoilProfile> => {
    const res = await farmApi.get<SoilProfile>(`/v1/plots/${plotId}/soil`);
    return res.data;
  },

  updateSoilProfile: async (plotId: string, data: Partial<SoilProfile>): Promise<SoilProfile> => {
    const res = await farmApi.patch<SoilProfile>(`/v1/plots/${plotId}/soil`, data);
    return res.data;
  },

  // Seasons
  getSeasons: async (plotId: string): Promise<CropSeason[]> => {
    const res = await farmApi.get<CropSeason[]>(`/v1/plots/${plotId}/seasons`);
    return res.data;
  },

  createSeason: async (plotId: string, data: Partial<CropSeason>): Promise<CropSeason> => {
    const res = await farmApi.post<CropSeason>(`/v1/plots/${plotId}/seasons`, data);
    return res.data;
  },

  updateSeason: async (plotId: string, seasonId: string, data: Partial<CropSeason>): Promise<CropSeason> => {
    const res = await farmApi.patch<CropSeason>(`/v1/plots/${plotId}/seasons/${seasonId}`, data);
    return res.data;
  },

  // Devices
  getDevices: async (plotId: string): Promise<IoTDevice[]> => {
    const res = await farmApi.get<IoTDevice[]>(`/v1/plots/${plotId}/devices`);
    return res.data;
  },

  registerDevice: async (plotId: string, data: Partial<IoTDevice>): Promise<IoTDevice> => {
    const res = await farmApi.post<IoTDevice>(`/v1/plots/${plotId}/devices`, data);
    return res.data;
  },
};
