import { authApi } from '@/lib/apiClient';
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '@/types';

// Storage key helpers for user persistence
const REGISTERED_USERS_KEY = 'agri_registered_users';
const ACTIVE_USER_KEY = 'agri_active_user';

const getRegisteredUsers = (): Record<string, { password?: string; user: User }> => {
  const data = localStorage.getItem(REGISTERED_USERS_KEY);
  if (data) {
    try {
      return JSON.parse(data);
    } catch {}
  }
  // Default authorized accounts
  return {
    '+919000000001': {
      password: 'SecretPassword123',
      user: {
        id: 'a0000000-0000-0000-0000-000000000001',
        full_name: 'Platform Admin',
        phone_number: '+919000000001',
        email: 'admin@agridecision.ai',
        role: 'ADMIN',
        account_status: 'ACTIVE',
        has_verified_phone: true,
        has_verified_agronomist_credential: true,
        preferred_language: 'en',
        state_code: 'IN-MH',
        district_name: 'Mumbai',
        farmer_type: 'LARGE_COMMERCIAL',
        referral_code: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        profile: null,
      },
    },
    '+919876543210': {
      password: 'SecretPassword123',
      user: {
        id: 'a0000000-0000-0000-0000-000000000002',
        full_name: 'Rajesh Kumar (Demo Farmer)',
        phone_number: '+919876543210',
        email: 'rajesh@agridecision.ai',
        role: 'FARMER',
        account_status: 'ACTIVE',
        has_verified_phone: true,
        has_verified_agronomist_credential: false,
        preferred_language: 'hi',
        state_code: 'IN-MH',
        district_name: 'Nashik',
        farmer_type: 'SMALL_COMMERCIAL',
        referral_code: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        profile: null,
      },
    },
  };
};

const saveRegisteredUser = (phone: string, password: string, user: User) => {
  const users = getRegisteredUsers();
  users[phone] = { password, user };
  localStorage.setItem(REGISTERED_USERS_KEY, JSON.stringify(users));
};

const getActiveUser = (): User | null => {
  const data = localStorage.getItem(ACTIVE_USER_KEY);
  if (data) {
    try {
      return JSON.parse(data);
    } catch {}
  }
  return null;
};

const setActiveUser = (user: User) => {
  localStorage.setItem(ACTIVE_USER_KEY, JSON.stringify(user));
};

export const authService = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    try {
      const params = new URLSearchParams();
      params.append('username', data.phone_number);
      params.append('password', data.password);
      const res = await authApi.post<TokenResponse>('/v1/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      // Sync active user profile from backend
      try {
        const userRes = await authApi.get<User>('/v1/users/me');
        setActiveUser(userRes.data);
      } catch {}
      return res.data;
    } catch (err: any) {
      console.warn('Backend API login error/offline mode. Checking registered authorized accounts.', err);

      // Authorized Logins Check: ONLY allow login if phone number is registered!
      const users = getRegisteredUsers();
      const account = users[data.phone_number];

      if (!account) {
        throw new Error('Account not found. Please Sign Up (Create Account) first before signing in.');
      }

      if (account.password && account.password !== data.password) {
        throw new Error('Invalid password. Please check your login credentials.');
      }

      // Login authorized! Store active user profile so getMe() returns the correct profile name
      setActiveUser(account.user);

      return {
        access_token: 'demo_access_token_' + Date.now(),
        refresh_token: 'demo_refresh_token_' + Date.now(),
        token_type: 'bearer',
        expires_in: 3600,
      };
    }
  },

  register: async (data: RegisterRequest): Promise<TokenResponse> => {
    const users = getRegisteredUsers();
    if (users[data.phone_number]) {
      throw new Error('An account with this phone number already exists. Please Sign In.');
    }

    const newUser: User = {
      id: 'usr_' + Date.now(),
      full_name: data.full_name,
      phone_number: data.phone_number,
      email: data.email || null,
      role: (data.role as any) || 'FARMER',
      account_status: 'ACTIVE',
      has_verified_phone: true,
      has_verified_agronomist_credential: false,
      preferred_language: 'en',
      state_code: data.state_code || 'IN-MH',
      district_name: 'District',
      farmer_type: 'SMALL_COMMERCIAL',
      referral_code: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      profile: null,
    };

    try {
      const res = await authApi.post<TokenResponse>('/v1/auth/register', data);
      saveRegisteredUser(data.phone_number, data.password, newUser);
      setActiveUser(newUser);
      return res.data;
    } catch (err) {
      console.warn('Backend API offline. Registering user locally.', err);
      saveRegisteredUser(data.phone_number, data.password, newUser);
      setActiveUser(newUser);
      return {
        access_token: 'demo_access_token_' + Date.now(),
        refresh_token: 'demo_refresh_token_' + Date.now(),
        token_type: 'bearer',
        expires_in: 3600,
      };
    }
  },

  getMe: async (): Promise<User> => {
    try {
      const res = await authApi.get<User>('/v1/users/me');
      setActiveUser(res.data);
      return res.data;
    } catch (err) {
      // Only return cached user if there is a real active session stored.
      // DO NOT fall back to a hardcoded default — that would auto-authenticate
      // unauthenticated users and hide the login page.
      const active = getActiveUser();
      if (active) return active;
      throw new Error('No active session. Please log in.');
    }
  },

  updateMe: async (data: Partial<User>): Promise<User> => {
    const active = getActiveUser();
    const updated: User = {
      ...(active || getRegisteredUsers()['+919876543210'].user),
      ...data,
      updated_at: new Date().toISOString(),
    };
    try {
      const res = await authApi.patch<User>('/v1/users/me', data);
      setActiveUser(res.data);
      return res.data;
    } catch {
      setActiveUser(updated);
      return updated;
    }
  },

  logout: async (): Promise<void> => {
    localStorage.removeItem(ACTIVE_USER_KEY);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    try {
      await authApi.post('/v1/auth/logout');
    } catch {}
  },

  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    try {
      const res = await authApi.post<TokenResponse>('/v1/auth/refresh', { refresh_token: refreshToken });
      return res.data;
    } catch {
      return {
        access_token: 'demo_access_token_' + Date.now(),
        refresh_token: refreshToken,
        token_type: 'bearer',
        expires_in: 3600,
      };
    }
  },
};
