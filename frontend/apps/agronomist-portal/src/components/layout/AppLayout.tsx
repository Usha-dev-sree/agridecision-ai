import React from 'react';
import { Box, Toolbar, Snackbar, Alert, useMediaQuery, useTheme } from '@mui/material';
import { Outlet } from 'react-router-dom';
import { Sidebar, DRAWER_WIDTH } from './Sidebar';
import { Topbar } from './Topbar';
import { OfflineBanner } from '@/components/common/OfflineBanner';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { toggleSidebar, setSidebarOpen, hideSnackbar } from '@/store/slices/uiSlice';
import { useCurrentUser } from '@/hooks/useAuth';

export const AppLayout: React.FC = () => {
  useCurrentUser();
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const sidebarOpen = useAppSelector((s) => s.ui.sidebarOpen);
  const snackbar = useAppSelector((s) => s.ui.snackbar);
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  React.useEffect(() => {
    if (isMobile) dispatch(setSidebarOpen(false));
    else dispatch(setSidebarOpen(true));
  }, [isMobile, dispatch]);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar
        open={sidebarOpen}
        onClose={() => dispatch(setSidebarOpen(false))}
        variant={isMobile ? 'temporary' : 'permanent'}
      />

      <Box
        component="main"
        role="main"
        aria-label="Main Application Content"
        sx={{
          flexGrow: 1,
          minWidth: 0,
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          ml: { md: sidebarOpen ? 0 : `-${DRAWER_WIDTH}px` },
        }}
      >
        <Topbar
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => dispatch(toggleSidebar())}
          isMobile={isMobile}
        />
        <Toolbar />
        <OfflineBanner />
        <Box
          sx={{
            p: { xs: 2, sm: 3 },
            minHeight: 'calc(100vh - 64px)',
            background: theme.palette.background.default,
          }}
        >
          <Outlet />
        </Box>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => dispatch(hideSnackbar())}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          severity={snackbar.severity}
          variant="filled"
          onClose={() => dispatch(hideSnackbar())}
          role="status"
          aria-live="polite"
          sx={{ borderRadius: 2 }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};
