import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAppDispatch } from '@/store/hooks';
import { setUser, setTokens, logout } from '@/store/slices/authSlice';
import { showSnackbar } from '@/store/slices/uiSlice';
import { authService } from '@/services/authService';
import type { LoginRequest } from '@/types';

export const queryKeys = {
  me: ['auth', 'me'] as const,
};

export function useCurrentUser() {
  return useQuery({
    queryKey: queryKeys.me,
    queryFn: authService.getMe,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}

export function useLogin() {
  const dispatch = useAppDispatch();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: async (tokens) => {
      dispatch(setTokens({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token }));
      const user = await authService.getMe();
      dispatch(setUser(user));
      queryClient.setQueryData(queryKeys.me, user);
      dispatch(showSnackbar({ message: `Welcome back, ${user.full_name}!`, severity: 'success' }));
    },
    onError: () => {
      dispatch(showSnackbar({ message: 'Invalid credentials. Please try again.', severity: 'error' }));
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
