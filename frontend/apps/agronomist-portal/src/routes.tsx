import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { GuestGuard } from '@/components/auth/GuestGuard';
import { AppLayout } from '@/components/layout/AppLayout';
import { Login } from '@/pages/Login';
import { Dashboard } from '@/pages/Dashboard';
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
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="plots" element={<Plots />} />
        <Route path="advisory" element={<Advisory />} />
        <Route path="disease" element={<Disease />} />
        <Route path="yield" element={<Yield />} />
        <Route path="weather" element={<Weather />} />
        <Route path="market" element={<Market />} />
        <Route path="devices" element={<Devices />} />
        <Route path="assistant" element={<Assistant />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
