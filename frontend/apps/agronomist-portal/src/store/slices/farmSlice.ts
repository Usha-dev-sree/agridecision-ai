import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { FarmPlot } from '@/types';

interface FarmState {
  selectedPlotId: string | null;
  plots: FarmPlot[];
  isMapView: boolean;
}

const initialState: FarmState = {
  selectedPlotId: localStorage.getItem('selected_plot_id'),
  plots: [],
  isMapView: false,
};

const farmSlice = createSlice({
  name: 'farm',
  initialState,
  reducers: {
    setSelectedPlot: (state, action: PayloadAction<string | null>) => {
      state.selectedPlotId = action.payload;
      if (action.payload) {
        localStorage.setItem('selected_plot_id', action.payload);
      } else {
        localStorage.removeItem('selected_plot_id');
      }
    },
    setPlots: (state, action: PayloadAction<FarmPlot[]>) => {
      state.plots = action.payload;
    },
    toggleMapView: (state) => {
      state.isMapView = !state.isMapView;
    },
  },
});

export const { setSelectedPlot, setPlots, toggleMapView } = farmSlice.actions;
export default farmSlice.reducer;
