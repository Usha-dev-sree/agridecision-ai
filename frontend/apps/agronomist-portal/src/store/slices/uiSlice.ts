import { createSlice, PayloadAction } from '@reduxjs/toolkit';

type ThemeMode = 'light' | 'dark';

interface UIState {
  themeMode: ThemeMode;
  sidebarOpen: boolean;
  notifications: Notification[];
  snackbar: { open: boolean; message: string; severity: 'success' | 'error' | 'warning' | 'info' };
}

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'success' | 'error';
  read: boolean;
  created_at: string;
}

const initialState: UIState = {
  themeMode: (localStorage.getItem('theme_mode') as ThemeMode) || 'dark',
  sidebarOpen: true,
  notifications: [],
  snackbar: { open: false, message: '', severity: 'info' },
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleTheme: (state) => {
      state.themeMode = state.themeMode === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme_mode', state.themeMode);
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    showSnackbar: (
      state,
      action: PayloadAction<{ message: string; severity?: 'success' | 'error' | 'warning' | 'info' }>
    ) => {
      state.snackbar = {
        open: true,
        message: action.payload.message,
        severity: action.payload.severity || 'info',
      };
    },
    hideSnackbar: (state) => {
      state.snackbar.open = false;
    },
    addNotification: (state, action: PayloadAction<Notification>) => {
      state.notifications.unshift(action.payload);
    },
    markNotificationRead: (state, action: PayloadAction<string>) => {
      const n = state.notifications.find((n) => n.id === action.payload);
      if (n) n.read = true;
    },
  },
});

export const {
  toggleTheme,
  toggleSidebar,
  setSidebarOpen,
  showSnackbar,
  hideSnackbar,
  addNotification,
  markNotificationRead,
} = uiSlice.actions;
export default uiSlice.reducer;
