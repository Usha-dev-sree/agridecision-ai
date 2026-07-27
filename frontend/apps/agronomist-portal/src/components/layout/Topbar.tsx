import React, { useState } from 'react';
import {
  AppBar, Toolbar, IconButton, Typography, Box, Badge,
  Menu, MenuItem, Avatar, Tooltip, Chip, alpha, useTheme,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import NotificationsIcon from '@mui/icons-material/Notifications';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import LogoutIcon from '@mui/icons-material/Logout';
import PersonIcon from '@mui/icons-material/Person';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { toggleTheme } from '@/store/slices/uiSlice';
import { useLogout } from '@/hooks/useAuth';
import { DRAWER_WIDTH } from './Sidebar';

interface TopbarProps {
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
  isMobile: boolean;
}

export const Topbar: React.FC<TopbarProps> = ({ sidebarOpen, onToggleSidebar, isMobile }) => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const user = useAppSelector((s) => s.auth.user);
  const themeMode = useAppSelector((s) => s.ui.themeMode);
  const selectedPlotId = useAppSelector((s) => s.farm.selectedPlotId);
  const plots = useAppSelector((s) => s.farm.plots);
  const selectedPlot = plots.find((p) => p.id === selectedPlotId);
  const logoutMutation = useLogout();

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notifAnchor, setNotifAnchor] = useState<null | HTMLElement>(null);

  return (
    <AppBar
      position="fixed"
      color="inherit"
      role="banner"
      aria-label="Application Top Header"
      sx={{
        width: { md: sidebarOpen ? `calc(100% - ${DRAWER_WIDTH}px)` : '100%' },
        ml: { md: sidebarOpen ? `${DRAWER_WIDTH}px` : 0 },
        transition: theme.transitions.create(['width', 'margin'], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.leavingScreen,
        }),
        zIndex: theme.zIndex.drawer - 1,
      }}
    >
      <Toolbar sx={{ gap: 1 }}>
        <IconButton
          onClick={onToggleSidebar}
          edge="start"
          color="inherit"
          size="small"
          aria-label={sidebarOpen ? "Collapse navigation sidebar" : "Expand navigation sidebar"}
        >
          <MenuIcon />
        </IconButton>

        {isMobile && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AgricultureIcon color="primary" />
            <Typography variant="h6" fontFamily="Outfit" fontWeight={700} color="primary">
              AgriDecision
            </Typography>
          </Box>
        )}

        <Box sx={{ flex: 1 }} />

        {/* Selected Plot Badge */}
        {selectedPlot && (
          <Chip
            icon={<AgricultureIcon sx={{ fontSize: 14 }} />}
            label={selectedPlot.name}
            size="small"
            color="primary"
            variant="outlined"
            onClick={() => navigate('/plots')}
            aria-label={`Active plot: ${selectedPlot.name}. Click to open plots manager.`}
            sx={{ display: { xs: 'none', sm: 'flex' } }}
          />
        )}

        {/* Theme Toggle */}
        <Tooltip title={themeMode === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
          <IconButton
            onClick={() => dispatch(toggleTheme())}
            size="small"
            color="inherit"
            aria-label={`Toggle theme. Current mode: ${themeMode}`}
          >
            {themeMode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
          </IconButton>
        </Tooltip>

        {/* Notifications */}
        <Tooltip title="Notifications">
          <IconButton
            size="small"
            color="inherit"
            onClick={(e) => setNotifAnchor(e.currentTarget)}
            aria-label="View notifications. 3 unread alerts."
          >
            <Badge badgeContent={3} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Tooltip>
        <Menu
          anchorEl={notifAnchor}
          open={Boolean(notifAnchor)}
          onClose={() => setNotifAnchor(null)}
          aria-label="Notification alerts menu"
        >
          <MenuItem dense>
            <Typography variant="body2">🌧️ Rain forecast for Plot A tomorrow</Typography>
          </MenuItem>
          <MenuItem dense>
            <Typography variant="body2">🌿 Crop recommendation ready</Typography>
          </MenuItem>
          <MenuItem dense>
            <Typography variant="body2">⚡ IoT device low battery alert</Typography>
          </MenuItem>
        </Menu>

        {/* User Menu */}
        <Tooltip title="Account settings">
          <IconButton
            size="small"
            onClick={(e) => setAnchorEl(e.currentTarget)}
            aria-label={`User profile for ${user?.full_name || 'Account'}`}
          >
            <Avatar
              src={user?.profile?.avatar_url || undefined}
              sx={{ width: 32, height: 32, bgcolor: theme.palette.primary.main, fontSize: '0.875rem' }}
            >
              {user?.full_name?.[0]}
            </Avatar>
          </IconButton>
        </Tooltip>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
          PaperProps={{ sx: { mt: 1, minWidth: 180 } }}
          aria-label="User account actions"
        >
          <Box sx={{ px: 2, py: 1, borderBottom: `1px solid ${alpha(theme.palette.divider, 0.5)}` }}>
            <Typography variant="subtitle2" fontWeight={600}>{user?.full_name}</Typography>
            <Typography variant="caption" color="text.secondary">{user?.phone_number}</Typography>
          </Box>
          <MenuItem onClick={() => { navigate('/profile'); setAnchorEl(null); }}>
            <PersonIcon fontSize="small" sx={{ mr: 1.5 }} /> Profile
          </MenuItem>
          <MenuItem
            onClick={() => { logoutMutation.mutate(); setAnchorEl(null); }}
            sx={{ color: 'error.main' }}
          >
            <LogoutIcon fontSize="small" sx={{ mr: 1.5 }} /> Sign Out
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};
