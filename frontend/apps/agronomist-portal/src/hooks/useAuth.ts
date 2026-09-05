import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch } from '@/store/hooks';
import { setUser, setTokens, logout, sessionRestored } from '@/store/slices/authSlice';
import { showSnackbar } from '@/store/slices/uiSlice';
import { authService } from '@/services/authService';
import type { LoginRequest, User } from '@/types';

export const queryKeys = {
  me: ['auth', 'me'] as const,
};

/** Map each backend role to its home dashboard route */
export function getRoleDashboard(role: User['role'] | string | undefined): string {
  switch (role) {
    case 'FARMER':      return '/farmer-dashboard';
    case 'AGRONOMIST':  return '/dashboard';
    case 'ENTERPRISE':  return '/enterprise-dashboard';
    case 'RESEARCHER':
    case 'ADMIN':       return '/admin-dashboard';
    default:            return '/dashboard';
  }
}

export function useCurrentUser() {
  const dispatch = useAppDispatch();
  return useQuery({
    queryKey: queryKeys.me,
    queryFn: async () => {
      try {
        const user = await authService.getMe();
        dispatch(sessionRestored(user));
        return user;
      } catch {
        dispatch(sessionRestored(null));
        return null;
      }
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

export function useLogin() {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: async (tokens) => {
      dispatch(setTokens({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token }));
      try {
        const user = await authService.getMe();
        dispatch(setUser(user));
        queryClient.setQueryData(queryKeys.me, user);
        dispatch(showSnackbar({ message: `Welcome back, ${user.full_name}!`, severity: 'success' }));
        // ✅ Role-based redirect
        navigate(getRoleDashboard(user.role), { replace: true });
      } catch {
        navigate('/dashboard', { replace: true });
      }
    },
    onError: () => {
      dispatch(showSnackbar({ message: 'Invalid credentials. Please try again.', severity: 'error' }));
    },
  });
}

export function useRegister() {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: any) => authService.register(data),
    onSuccess: async (tokens) => {
      dispatch(setTokens({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token }));
      try {
        const user = await authService.getMe();
        dispatch(setUser(user));
        queryClient.setQueryData(queryKeys.me, user);
        dispatch(showSnackbar({ message: `Account created successfully! Welcome, ${user.full_name}!`, severity: 'success' }));
        // ✅ Role-based redirect
        navigate(getRoleDashboard(user.role), { replace: true });
      } catch {
        navigate('/dashboard', { replace: true });
      }
    },
    onError: () => {
      dispatch(showSnackbar({ message: 'Failed to create account. Please check your details and try again.', severity: 'error' }));
    },
  });
}

export function useLogout() {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: authService.logout,
    onSettled: () => {
      dispatch(logout());
      queryClient.clear();
    },
  });
}
