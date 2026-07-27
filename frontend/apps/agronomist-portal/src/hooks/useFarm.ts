import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAppDispatch } from '@/store/hooks';
import { setSelectedPlot, setPlots } from '@/store/slices/farmSlice';
import { showSnackbar } from '@/store/slices/uiSlice';
import { farmService } from '@/services/farmService';
import type { FarmPlot, SoilProfile, CropSeason } from '@/types';

export const farmQueryKeys = {
  plots: ['farm', 'plots'] as const,
  plot: (id: string) => ['farm', 'plots', id] as const,
  soil: (plotId: string) => ['farm', 'soil', plotId] as const,
  seasons: (plotId: string) => ['farm', 'seasons', plotId] as const,
  devices: (plotId: string) => ['farm', 'devices', plotId] as const,
};

export function usePlots() {
  const dispatch = useAppDispatch();
  return useQuery({
    queryKey: farmQueryKeys.plots,
    queryFn: async () => {
      const plots = await farmService.getPlots();
      dispatch(setPlots(plots));
      return plots;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function usePlot(plotId: string) {
  return useQuery({
    queryKey: farmQueryKeys.plot(plotId),
    queryFn: () => farmService.getPlot(plotId),
    enabled: !!plotId,
  });
}

export function useSoilProfile(plotId: string) {
  return useQuery({
    queryKey: farmQueryKeys.soil(plotId),
    queryFn: () => farmService.getSoilProfile(plotId),
    enabled: !!plotId,
    retry: false,
  });
}

export function useSeasons(plotId: string) {
  return useQuery({
    queryKey: farmQueryKeys.seasons(plotId),
    queryFn: () => farmService.getSeasons(plotId),
    enabled: !!plotId,
  });
}

export function useDevices(plotId: string) {
  return useQuery({
    queryKey: farmQueryKeys.devices(plotId),
    queryFn: () => farmService.getDevices(plotId),
    enabled: !!plotId,
  });
}

export function useCreatePlot() {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Omit<FarmPlot, 'id' | 'owner_id' | 'created_at' | 'updated_at'>) =>
      farmService.createPlot(data),
    onSuccess: (newPlot) => {
      queryClient.invalidateQueries({ queryKey: farmQueryKeys.plots });
      dispatch(setSelectedPlot(newPlot.id));
      dispatch(showSnackbar({ message: `Plot "${newPlot.name}" created successfully!`, severity: 'success' }));
    },
    onError: () => {
      dispatch(showSnackbar({ message: 'Failed to create plot. Please try again.', severity: 'error' }));
    },
  });
}

export function useUpdateSoil(plotId: string) {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<SoilProfile>) => farmService.updateSoilProfile(plotId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: farmQueryKeys.soil(plotId) });
      dispatch(showSnackbar({ message: 'Soil profile updated successfully!', severity: 'success' }));
    },
  });
}

export function useCreateSeason(plotId: string) {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<CropSeason>) => farmService.createSeason(plotId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: farmQueryKeys.seasons(plotId) });
      dispatch(showSnackbar({ message: 'Season created successfully!', severity: 'success' }));
    },
  });
}
