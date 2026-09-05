import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { GuestGuard } from '@/components/auth/GuestGuard';
import { RoleGuard } from '@/components/auth/RoleGuard';
import { AppLayout } from '@/components/layout/AppLayout';
import { Login } from '@/pages/Login';
import { Dashboard } from '@/pages/Dashboard';
import { FarmerDashboard } from '@/pages/FarmerDashboard';
import { AdminDashboard } from '@/pages/AdminDashboard';
import { EnterpriseDashboard } from '@/pages/EnterpriseDashboard';
import { Plots } from '@/pages/Plots';
import { Advisory } from '@/pages/Advisory';
import { Disease } from '@/pages/Disease';
import { Yield } from '@/pages/Yield';
import { Weather } from '@/pages/Weather';
import { Market } from '@/pages/Market';
import { Devices } from '@/pages/Devices';
import { Assistant } from '@/pages/Assistant';
import { Analytics } from '@/pages/Analytics';
import { Profile } from '@/pages/Profile';
import { Loans } from '@/pages/Loans';
import { Contracts } from '@/pages/Contracts';
import { Maps } from '@/pages/Maps';
import { Reports } from '@/pages/Reports';
import { Notifications } from '@/pages/Notifications';
import { Settings } from '@/pages/Settings';
import { useAppSelector } from '@/store/hooks';
import { getRoleDashboard } from '@/hooks/useAuth';

/** Smart index redirect — sends each role to their own home dashboard */
const RoleHomeRedirect: React.FC = () => {
  const user = useAppSelector((s) => s.auth.user);
  return <Navigate to={getRoleDashboard(user?.role)} replace />;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public/Guest Routes */}
      <Route
        path="/login"
        element={
          <GuestGuard>
            <Login />
          </GuestGuard>
        }
      />

      {/* Protected Private Routes */}
      <Route
        path="/"
        element={
          <AuthGuard>
            <AppLayout />
          </AuthGuard>
        }
      >
        {/* ── Default: redirect to role's own home ── */}
        <Route index element={<RoleHomeRedirect />} />

        {/* ── Agronomist dashboard (AGRONOMIST only) ── */}
        <Route
          path="dashboard"
          element={
            <RoleGuard allowedRoles={['AGRONOMIST', 'ADMIN']}>
              <Dashboard />
            </RoleGuard>
          }
        />

        {/* ── Farmer dashboard (FARMER only) ── */}
        <Route
          path="farmer-dashboard"
          element={
            <RoleGuard allowedRoles={['FARMER']}>
              <FarmerDashboard />
            </RoleGuard>
          }
        />

        {/* ── Enterprise dashboard (ENTERPRISE only) ── */}
        <Route
          path="enterprise-dashboard"
          element={
            <RoleGuard allowedRoles={['ENTERPRISE']}>
              <EnterpriseDashboard />
            </RoleGuard>
          }
        />

        {/* ── Researcher/Admin dashboard ── */}
        <Route
          path="admin-dashboard"
          element={
            <RoleGuard allowedRoles={['ADMIN', 'RESEARCHER']}>
              <AdminDashboard />
            </RoleGuard>
          }
        />

        {/* ── Shared feature routes (accessible to multiple roles) ── */}
        <Route path="plots"         element={<RoleGuard allowedRoles={['FARMER', 'AGRONOMIST', 'ADMIN']}><Plots /></RoleGuard>} />
        <Route path="maps"          element={<Maps />} />
        <Route path="advisory"      element={<Advisory />} />
        <Route path="disease"       element={<Disease />} />
        <Route path="yield"         element={<Yield />} />
        <Route path="weather"       element={<Weather />} />
        <Route path="market"        element={<Market />} />
        <Route path="loans"         element={<RoleGuard allowedRoles={['FARMER', 'ENTERPRISE', 'AGRONOMIST']}><Loans /></RoleGuard>} />
        <Route path="contracts"     element={<RoleGuard allowedRoles={['ENTERPRISE', 'AGRONOMIST', 'ADMIN']}><Contracts /></RoleGuard>} />
        <Route path="reports"       element={<RoleGuard allowedRoles={['AGRONOMIST', 'ENTERPRISE', 'ADMIN', 'RESEARCHER']}><Reports /></RoleGuard>} />
        <Route path="devices"       element={<RoleGuard allowedRoles={['AGRONOMIST', 'ADMIN', 'FARMER']}><Devices /></RoleGuard>} />
        <Route path="assistant"     element={<Assistant />} />
        <Route path="analytics"     element={<RoleGuard allowedRoles={['AGRONOMIST', 'ENTERPRISE', 'ADMIN', 'RESEARCHER']}><Analytics /></RoleGuard>} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="settings"      element={<Settings />} />
        <Route path="profile"       element={<Profile />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
