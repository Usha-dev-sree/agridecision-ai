import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from '@/store/hooks';
import { getRoleDashboard } from '@/hooks/useAuth';

interface RoleGuardProps {
  /** Roles allowed to access this route */
  allowedRoles: string[];
  children: React.ReactNode;
}

/**
 * Protects a route to only allow specific roles.
 * If the authenticated user's role is not in `allowedRoles`,
 * they are silently redirected to their own role's home dashboard.
 */
export const RoleGuard: React.FC<RoleGuardProps> = ({ allowedRoles, children }) => {
  const user = useAppSelector((s) => s.auth.user);

  // If user profile not yet loaded, allow through (AuthGuard handles unauthenticated)
  if (!user) return <>{children}</>;

  if (!allowedRoles.includes(user.role)) {
    // Redirect to the user's own home dashboard instead of showing a 403
    return <Navigate to={getRoleDashboard(user.role)} replace />;
  }

  return <>{children}</>;
};
