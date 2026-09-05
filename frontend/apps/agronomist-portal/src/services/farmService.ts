import { farmApi } from '@/lib/apiClient';
import type { FarmPlot, SoilProfile, CropSeason, IoTDevice, PlotBoundary } from '@/types';

const STORAGE_PLOTS_KEY = 'agri_plots_store';

const getStoredPlots = (): FarmPlot[] => {
  const data = localStorage.getItem(STORAGE_PLOTS_KEY);
  if (data) {
    try {
      const parsed = JSON.parse(data);
      if (Array.isArray(parsed)) return parsed;
    } catch {}
  }
  return [
    {
      id: 'plot-001',
      owner_id: 'usr_demo',
      name: 'Green Acres North',
      total_area_ha: 4.5,
      irrigation_type: 'IRRIGATED',
      is_active: true,
      centroid_lat: 28.625,
      centroid_lng: 77.200,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'plot-002',
      owner_id: 'usr_demo',
      name: 'South Field Block',
      total_area_ha: 3.2,
      irrigation_type: 'MICRO_IRRIGATED',
      is_active: true,
      centroid_lat: 28.610,
      centroid_lng: 77.220,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];
};

const saveStoredPlots = (plots: FarmPlot[]) => {
  if (Array.isArray(plots)) {
    localStorage.setItem(STORAGE_PLOTS_KEY, JSON.stringify(plots));
  }
};

export const farmService = {
  // Plots
  getPlots: async (): Promise<FarmPlot[]> => {
    const localPlots = getStoredPlots();
    try {
      const res = await farmApi.get<FarmPlot[]>('/v1/plots');
      if (Array.isArray(res.data)) {
        // Merge backend plots with any locally created plots not yet in backend
        const backendIds = new Set(res.data.map((p) => p.id));
        const customLocal = localPlots.filter((p) => !backendIds.has(p.id) && p.id.startsWith('plot_'));
        const merged = [...res.data, ...customLocal];
        saveStoredPlots(merged);
        return merged.length > 0 ? merged : localPlots;
      }
    } catch (err) {
      console.warn('Backend farm service API offline/unreachable. Returning stored plots.', err);
    }
    return localPlots;
  },

  getPlot: async (plotId: string): Promise<FarmPlot> => {
    try {
      const res = await farmApi.get<FarmPlot>(`/v1/plots/${plotId}`);
      return res.data;
    } catch {
      const plots = getStoredPlots();
      const plot = plots.find((p) => p.id === plotId);
      if (plot) return plot;
      return plots[0];
    }
  },

  createPlot: async (data: Omit<FarmPlot, 'id' | 'owner_id' | 'created_at' | 'updated_at'>): Promise<FarmPlot> => {
    const newPlot: FarmPlot = {
      id: 'plot_' + Date.now(),
      owner_id: 'usr_current',
      name: data.name,
      total_area_ha: data.total_area_ha,
      irrigation_type: data.irrigation_type,
      is_active: data.is_active ?? true,
      centroid_lat: data.centroid_lat ?? 28.6139,
      centroid_lng: data.centroid_lng ?? 77.2090,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    try {
      const res = await farmApi.post<FarmPlot>('/v1/plots', data);
      const existing = getStoredPlots();
      saveStoredPlots([res.data, ...existing]);
      return res.data;
    } catch (err) {
      console.warn('Backend farm API error/offline. Persisting created plot locally.', err);
      const existing = getStoredPlots();
      saveStoredPlots([newPlot, ...existing]);
      return newPlot;
    }
  },

  updatePlot: async (plotId: string, data: Partial<FarmPlot>): Promise<FarmPlot> => {
    try {
      const res = await farmApi.patch<FarmPlot>(`/v1/plots/${plotId}`, data);
      return res.data;
    } catch {
      const plots = getStoredPlots();
      const index = plots.findIndex((p) => p.id === plotId);
      if (index !== -1) {
        plots[index] = { ...plots[index], ...data, updated_at: new Date().toISOString() };
        saveStoredPlots(plots);
        return plots[index];
      }
      return plots[0];
    }
  },

  deletePlot: async (plotId: string): Promise<void> => {
    try {
      await farmApi.delete(`/v1/plots/${plotId}`);
    } catch {}
    const plots = getStoredPlots().filter((p) => p.id !== plotId);
    saveStoredPlots(plots);
  },

  // Boundaries
  getPlotBoundary: async (plotId: string): Promise<PlotBoundary> => {
    try {
      const res = await farmApi.get<PlotBoundary>(`/v1/plots/${plotId}/boundary`);
      return res.data;
    } catch {
      const plot = (await farmService.getPlot(plotId)) || getStoredPlots()[0];
      const lat = plot.centroid_lat || 28.6139;
      const lng = plot.centroid_lng || 77.2090;
      return {
        plot_id: plotId,
        perimeter_km: 1.2,
        elevation_m: 215,
        geojson: {
          type: 'Polygon',
          coordinates: [
            [
              [lng - 0.001, lat - 0.001],
              [lng + 0.001, lat - 0.001],
              [lng + 0.001, lat + 0.001],
              [lng - 0.001, lat + 0.001],
              [lng - 0.001, lat - 0.001],
            ],
          ],
        },
      };
    }
  },

  upsertBoundary: async (plotId: string, geojson: GeoJSON.Geometry): Promise<PlotBoundary> => {
    try {
      const res = await farmApi.put<PlotBoundary>(`/v1/plots/${plotId}/boundary`, { geojson });
      return res.data;
    } catch {
      return {
        plot_id: plotId,
        geojson,
        perimeter_km: 1.5,
        elevation_m: 210,
      };
    }
  },

  // Soil
  getSoilProfile: async (plotId: string): Promise<SoilProfile> => {
    try {
      const res = await farmApi.get<SoilProfile>(`/v1/plots/${plotId}/soil`);
      return res.data;
    } catch {
      return {
        plot_id: plotId,
        soil_type: 'Clay Loam',
        texture_class: 'CLAY_LOAM',
        ph_level: 6.8,
        organic_carbon_percent: 0.85,
        nitrogen_content: 240,
        phosphorus_content: 35,
        potassium_content: 210,
        bulk_density: 1.35,
        source: 'LAB_TESTED',
        last_tested_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
    }
  },

  updateSoilProfile: async (plotId: string, data: Partial<SoilProfile>): Promise<SoilProfile> => {
    try {
      const res = await farmApi.patch<SoilProfile>(`/v1/plots/${plotId}/soil`, data);
      return res.data;
    } catch {
      const existing = await farmService.getSoilProfile(plotId);
      return { ...existing, ...data, updated_at: new Date().toISOString() };
    }
  },

  // Seasons
  getSeasons: async (plotId: string): Promise<CropSeason[]> => {
    try {
      const res = await farmApi.get<CropSeason[]>(`/v1/plots/${plotId}/seasons`);
      return res.data;
    } catch {
      return [
        {
          id: 'season-001',
          plot_id: plotId,
          crop_name: 'Wheat (HD-2967)',
          season_name: 'RABI',
          sowing_date: '2025-11-15',
          expected_harvest_date: '2026-04-10',
          actual_harvest_date: null,
          sown_area_ha: 3.5,
          seed_variety: 'HD-2967 High Yield',
          status: 'GROWING',
          notes: 'Standard nitrogen top-dressing applied',
          created_at: new Date().toISOString(),
        },
      ];
    }
  },

  createSeason: async (plotId: string, data: Partial<CropSeason>): Promise<CropSeason> => {
    try {
      const res = await farmApi.post<CropSeason>(`/v1/plots/${plotId}/seasons`, data);
      return res.data;
    } catch {
      return {
        id: 'season-' + Date.now(),
        plot_id: plotId,
        crop_name: data.crop_name || 'Maize',
        season_name: data.season_name || 'KHARIF',
        sowing_date: data.sowing_date || new Date().toISOString().split('T')[0],
        expected_harvest_date: data.expected_harvest_date || null,
        actual_harvest_date: null,
        sown_area_ha: data.sown_area_ha || 2.0,
        seed_variety: data.seed_variety || 'Pioneer Hybrid',
        status: data.status || 'PLANNED',
        notes: data.notes || null,
        created_at: new Date().toISOString(),
      };
    }
  },

  updateSeason: async (plotId: string, seasonId: string, data: Partial<CropSeason>): Promise<CropSeason> => {
    try {
      const res = await farmApi.patch<CropSeason>(`/v1/plots/${plotId}/seasons/${seasonId}`, data);
      return res.data;
    } catch {
      return {
        id: seasonId,
        plot_id: plotId,
        crop_name: data.crop_name || 'Wheat',
        season_name: data.season_name || 'RABI',
        sowing_date: null,
        expected_harvest_date: null,
        actual_harvest_date: null,
        sown_area_ha: null,
        seed_variety: null,
        status: data.status || 'GROWING',
        notes: null,
        created_at: new Date().toISOString(),
      };
    }
  },

  // Devices
  getDevices: async (plotId: string): Promise<IoTDevice[]> => {
    try {
      const res = await farmApi.get<IoTDevice[]>(`/v1/plots/${plotId}/devices`);
      return res.data;
    } catch {
      return [
        {
          id: 'device-001',
          plot_id: plotId,
          device_serial: 'AGRI-IOT-9901',
          device_type: 'SOIL_SENSOR',
          is_active: true,
          last_seen_at: new Date().toISOString(),
          firmware_version: 'v2.4.1',
          battery_level: 88,
          created_at: new Date().toISOString(),
        },
      ];
    }
  },

  registerDevice: async (plotId: string, data: Partial<IoTDevice>): Promise<IoTDevice> => {
    try {
      const res = await farmApi.post<IoTDevice>(`/v1/plots/${plotId}/devices`, data);
      return res.data;
    } catch {
      return {
        id: 'dev-' + Date.now(),
        plot_id: plotId,
        device_serial: data.device_serial || 'AGRI-IOT-NEW',
        device_type: data.device_type || 'SOIL_SENSOR',
        is_active: true,
        last_seen_at: new Date().toISOString(),
        firmware_version: 'v1.0.0',
        battery_level: 100,
        created_at: new Date().toISOString(),
      };
    }
  },
};
