import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { store } from '@/store';
import { logout, setTokens } from '@/store/slices/authSlice';

const BASE_URLS = {
  auth: '/api/auth',
  farm: '/api/farm',
  advisory: '/api/advisory',
  market: '/api/market',
  weather: '/api/weather',
  ai: '/api/ai',
};

function createAxiosInstance(baseURL: string): AxiosInstance {
  const instance = axios.create({
    baseURL,
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
  });

  // Request interceptor – attach Bearer token
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = store.getState().auth.accessToken;
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor – handle 401 / token refresh
  instance.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error) => {
      const original = error.config;
      if (error.response?.status === 401 && !original._retry) {
        original._retry = true;
        const refreshToken = store.getState().auth.refreshToken;
        if (refreshToken) {
          try {
            const { data } = await axios.post(`${BASE_URLS.auth}/v1/auth/refresh`, {
              refresh_token: refreshToken,
            });
            store.dispatch(setTokens({ accessToken: data.access_token, refreshToken: data.refresh_token }));
            original.headers.Authorization = `Bearer ${data.access_token}`;
            return instance(original);
          } catch {
            store.dispatch(logout());
          }
        } else {
          store.dispatch(logout());
        }
      }
      return Promise.reject(error);
    }
  );

  return instance;
}

export const authApi = createAxiosInstance(BASE_URLS.auth);
export const farmApi = createAxiosInstance(BASE_URLS.farm);
export const advisoryApi = createAxiosInstance(BASE_URLS.advisory);
export const marketApi = createAxiosInstance(BASE_URLS.market);
export const weatherApi = createAxiosInstance(BASE_URLS.weather);
export const aiApi = createAxiosInstance(BASE_URLS.ai);
