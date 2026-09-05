import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { User } from '@/types';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  /** True when a token exists in localStorage, used to trigger session-restore attempt */
  hasStoredToken: boolean;
}

const getStoredToken = () => localStorage.getItem('access_token');
const getStoredRefresh = () => localStorage.getItem('refresh_token');

const initialState: AuthState = {
  accessToken: getStoredToken(),
  refreshToken: getStoredRefresh(),
  user: null,
  // Start as false — a stored token alone does NOT mean the session is valid.
  // isAuthenticated is only set to true after setTokens (successful login) or
  // after useCurrentUser confirms the session via setUser.
  isAuthenticated: false,
  isLoading: !!getStoredToken(), // Show loading spinner while we attempt session restore
  hasStoredToken: !!getStoredToken(),
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setTokens: (state, action: PayloadAction<{ accessToken: string; refreshToken: string }>) => {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.isAuthenticated = true;
      state.isLoading = false;
      localStorage.setItem('access_token', action.payload.accessToken);
      localStorage.setItem('refresh_token', action.payload.refreshToken);
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
      state.isLoading = false;
    },
    /** Called after session-restore attempt (useCurrentUser) succeeds or fails */
    sessionRestored: (state, action: PayloadAction<User | null>) => {
      state.isLoading = false;
      if (action.payload) {
        state.user = action.payload;
        state.isAuthenticated = true;
      } else {
        // Session restore failed — stale token. Clear everything.
        state.isAuthenticated = false;
        state.accessToken = null;
        state.refreshToken = null;
        state.hasStoredToken = false;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    logout: (state) => {
      state.accessToken = null;
      state.refreshToken = null;
      state.user = null;
      state.isAuthenticated = false;
      state.isLoading = false;
      state.hasStoredToken = false;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
  },
});

export const { setTokens, setUser, setLoading, logout, sessionRestored } = authSlice.actions;
export default authSlice.reducer;
