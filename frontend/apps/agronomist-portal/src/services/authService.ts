import { authApi } from '@/lib/apiClient';
import type { LoginRequest, TokenResponse, User } from '@/types';

export const authService = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const params = new URLSearchParams();
    params.append('username', data.phone_number);
    params.append('password', data.password);
    const res = await authApi.post<TokenResponse>('/v1/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return res.data;
  },

  getMe: async (): Promise<User> => {
    const res = await authApi.get<User>('/v1/users/me');
    return res.data;
  },

  updateMe: async (data: Partial<User>): Promise<User> => {
    const res = await authApi.patch<User>('/v1/users/me', data);
    return res.data;
  },

  logout: async (): Promise<void> => {
    await authApi.post('/v1/auth/logout');
  },

  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const res = await authApi.post<TokenResponse>('/v1/auth/refresh', { refresh_token: refreshToken });
    return res.data;
  },
};
