import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer, List, ListItemButton, ListItemIcon, ListItemText,
  Toolbar, Box, Typography, Divider, Avatar, Chip, alpha, useTheme,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import YardIcon from '@mui/icons-material/Yard';
import BugReportIcon from '@mui/icons-material/BugReport';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import StorefrontIcon from '@mui/icons-material/Storefront';
import DeviceHubIcon from '@mui/icons-material/DeviceHub';
import MicIcon from '@mui/icons-material/Mic';
import BarChartIcon from '@mui/icons-material/BarChart';
import PersonIcon from '@mui/icons-material/Person';
import { useAppSelector } from '@/store/hooks';

const DRAWER_WIDTH = 256;

const navItems = [
  { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { label: 'My Plots', icon: <AgricultureIcon />, path: '/plots' },
  { label: 'Crop Advisory', icon: <YardIcon />, path: '/advisory' },
  { label: 'Disease Detection', icon: <BugReportIcon />, path: '/disease' },
  { label: 'Yield Prediction', icon: <TrendingUpIcon />, path: '/yield' },
  { label: 'Weather', icon: <WbSunnyIcon />, path: '/weather' },
  { label: 'Market Prices', icon: <StorefrontIcon />, path: '/market' },
  { label: 'IoT Devices', icon: <DeviceHubIcon />, path: '/devices' },
  { label: 'AI Assistant', icon: <MicIcon />, path: '/assistant' },
  { label: 'Analytics', icon: <BarChartIcon />, path: '/analytics' },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  variant: 'permanent' | 'temporary';
}

export const Sidebar: React.FC<SidebarProps> = ({ open, onClose, variant }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const user = useAppSelector((s) => s.auth.user);

  const handleNav = (path: string) => {
    navigate(path);
    if (variant === 'temporary') onClose();
  };

  const drawerContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Logo */}
      <Toolbar sx={{ px: 2, py: 1.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 38, height: 38, borderRadius: 2,
              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.4)}`,
            }}
          >
            <AgricultureIcon sx={{ color: '#fff', fontSize: 20 }} />
          </Box>
          <Box>
            <Typography variant="subtitle1" fontWeight={800} fontFamily="Outfit" lineHeight={1.1}>
              AgriDecision
            </Typography>
            <Typography variant="caption" color="text.secondary">AI Platform</Typography>
          </Box>
        </Box>
      </Toolbar>

      <Divider sx={{ opacity: 0.15 }} />

      {/* Nav Items */}
      <List sx={{ flex: 1, py: 1.5 }}>
        {navItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path);
          return (
            <ListItemButton
              key={item.path}
              selected={isActive}
              onClick={() => handleNav(item.path)}
              sx={{ mx: 1, mb: 0.5 }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 38,
                  color: isActive ? theme.palette.primary.main : 'text.secondary',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{
                  fontSize: '0.875rem',
                  fontWeight: isActive ? 600 : 400,
                  color: isActive ? theme.palette.primary.main : 'text.primary',
                }}
              />
            </ListItemButton>
          );
        })}
      </List>

      <Divider sx={{ opacity: 0.15 }} />

      {/* User Footer */}
      <Box sx={{ p: 2 }}>
        <ListItemButton
          onClick={() => handleNav('/profile')}
          sx={{ borderRadius: 2, px: 1.5, py: 1 }}
        >
          <Avatar
            src={user?.profile?.avatar_url || undefined}
            sx={{ width: 36, height: 36, mr: 1.5, bgcolor: theme.palette.primary.main }}
          >
            {user?.full_name?.[0]}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="body2" fontWeight={600} noWrap>{user?.full_name}</Typography>
            <Chip
              label={user?.role}
              size="small"
              color="primary"
              variant="outlined"
              sx={{ height: 18, fontSize: '0.65rem', mt: 0.25 }}
            />
          </Box>
          <PersonIcon fontSize="small" sx={{ color: 'text.secondary' }} />
        </ListItemButton>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant={variant}
      open={open}
      onClose={onClose}
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box', overflow: 'hidden' },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export { DRAWER_WIDTH };
