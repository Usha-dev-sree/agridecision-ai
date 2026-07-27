import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid, Card, CardContent, Typography, Box, Button, Chip, Divider,
  IconButton, List, ListItem, ListItemText, ListItemAvatar, Avatar, useTheme,
} from '@mui/material';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import DeviceHubIcon from '@mui/icons-material/DeviceHub';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import BugReportIcon from '@mui/icons-material/BugReport';
import YardIcon from '@mui/icons-material/Yard';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import NotificationsIcon from '@mui/icons-material/Notifications';

import { usePlots } from '@/hooks/useFarm';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { setSelectedPlot } from '@/store/slices/farmSlice';
import { StatCard } from '@/components/common/StatCard';
import { LoadingState } from '@/components/common/States';

// Recharts or simple visualizations
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar, CartesianGrid, Legend } from 'recharts';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { data: plots, isLoading } = usePlots();
  const selectedPlotId = useAppSelector((state) => state.farm.selectedPlotId);

  // Fallback mocks if plots are empty or loading
  const totalPlots = plots?.length || 0;
  const activePlots = plots?.filter((p) => p.is_active).length || 0;
  const totalArea = plots?.reduce((sum, p) => sum + Number(p.total_area_ha || 0), 0) || 0;

  // Selected plot information
  const selectedPlot = plots?.find((p) => p.id === selectedPlotId) || plots?.[0];

  React.useEffect(() => {
    if (plots && plots.length > 0 && !selectedPlotId) {
      dispatch(setSelectedPlot(plots[0].id));
    }
  }, [plots, selectedPlotId, dispatch]);

  if (isLoading) {
    return <LoadingState message="Loading dashboard..." />;
  }

  // Sample data for charts
  const soilHistoryData = [
    { month: 'Jan', Nitrogen: 45, Phosphorus: 30, Potassium: 80 },
    { month: 'Feb', Nitrogen: 48, Phosphorus: 32, Potassium: 82 },
    { month: 'Mar', Nitrogen: 55, Phosphorus: 35, Potassium: 85 },
    { month: 'Apr', Nitrogen: 60, Phosphorus: 38, Potassium: 90 },
    { month: 'May', Nitrogen: 58, Phosphorus: 36, Potassium: 88 },
    { month: 'Jun', Nitrogen: 65, Phosphorus: 42, Potassium: 95 },
  ];

  const yieldStats = [
    { year: '2021', Rice: 4.2, Wheat: 3.8, Maize: 5.1 },
    { year: '2022', Rice: 4.5, Wheat: 4.0, Maize: 5.3 },
    { year: '2023', Rice: 4.8, Wheat: 4.2, Maize: 5.6 },
    { year: '2024', Rice: 5.1, Wheat: 4.5, Maize: 6.0 },
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Welcome header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
            Farm Intelligence Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time insights, ML recommendations, and multi-spectral advisory.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Button
            variant="outlined"
            onClick={() => navigate('/plots')}
            startIcon={<AgricultureIcon />}
          >
            Manage Plots
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate('/advisory')}
            startIcon={<YardIcon />}
          >
            Get Advisory
          </Button>
        </Box>
      </Box>

      {/* KPI Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Land Holding"
            value={`${totalArea.toFixed(2)} Ha`}
            subtitle={`${totalPlots} total plot boundaries`}
            icon={<AgricultureIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Crop Seasons"
            value={plots ? activePlots : 0}
            subtitle="Crops currently in fields"
            icon={<YardIcon />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="IoT Nodes Status"
            value="12 Active"
            subtitle="Telemetry transmitting normal"
            icon={<DeviceHubIcon />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Alerts Pending"
            value="3 Alert"
            subtitle="Requires immediate agronomic focus"
            icon={<NotificationsIcon />}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Main Panel */}
      <Grid container spacing={3}>
        {/* Soil health history chart */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Box>
                  <Typography variant="h6" fontWeight={700}>
                    Soil NPK Nutrients Status (PPM)
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Multi-spectral data trend over past 6 months
                  </Typography>
                </Box>
                <Chip label="Real-time Node Telemetry" color="success" size="small" variant="outlined" />
              </Box>
              <Box sx={{ width: '100%', height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={soilHistoryData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorNitrogen" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.4}/>
                        <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorPotassium" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={theme.palette.secondary.main} stopOpacity={0.4}/>
                        <stop offset="95%" stopColor={theme.palette.secondary.main} stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="month" stroke={theme.palette.text.secondary} />
                    <YAxis stroke={theme.palette.text.secondary} />
                    <Tooltip contentStyle={{ backgroundColor: theme.palette.background.paper }} />
                    <Legend />
                    <Area type="monotone" dataKey="Nitrogen" stroke={theme.palette.primary.main} fillOpacity={1} fill="url(#colorNitrogen)" />
                    <Area type="monotone" dataKey="Potassium" stroke={theme.palette.secondary.main} fillOpacity={1} fill="url(#colorPotassium)" />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Selected plot status */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Plot Details & Diagnostics
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                Currently Selected Focus Area
              </Typography>

              {selectedPlot ? (
                <Box>
                  <Typography variant="subtitle1" fontWeight={700} color="primary">
                    {selectedPlot.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Area: {selectedPlot.total_area_ha} Ha | Irrigation: {selectedPlot.irrigation_type}
                  </Typography>
                  <Divider sx={{ my: 1.5 }} />

                  {/* Soil details */}
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    Last Soil Diagnostic:
                  </Typography>
                  <Grid container spacing={1} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Soil Type:</Typography>
                      <Typography variant="body2" fontWeight={500}>Black Cotton</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">pH Level:</Typography>
                      <Typography variant="body2" fontWeight={500}>7.2 (Neutral)</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Organic Carbon:</Typography>
                      <Typography variant="body2" fontWeight={500}>0.85%</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Texture:</Typography>
                      <Typography variant="body2" fontWeight={500}>Clayey Loam</Typography>
                    </Grid>
                  </Grid>
                  <Divider sx={{ my: 1.5 }} />

                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    Active Crop Season:
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2" fontWeight={500}>Rice (Basmati)</Typography>
                    <Chip label="Growing" color="success" size="small" />
                  </Box>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No plot selected. Please add or select a plot in the plot configuration.
                </Typography>
              )}
            </CardContent>
            <Divider />
            <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                size="small"
                onClick={() => navigate('/plots')}
                endIcon={<ArrowForwardIcon />}
              >
                Go to Plot Config
              </Button>
            </Box>
          </Card>
        </Grid>

        {/* Crop Yield predictions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Historical Yield Comparison (Tons/Ha)
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 3 }}>
                Performance across various major crops
              </Typography>
              <Box sx={{ width: '100%', height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={yieldStats}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Rice" fill={theme.palette.primary.main} />
                    <Bar dataKey="Wheat" fill={theme.palette.secondary.main} />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Diagnostic / Alert Center */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Agronomic Recommendations & Bulletins
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                Generated from disease & IoT monitors
              </Typography>

              <List>
                <ListItem
                  secondaryAction={
                    <IconButton edge="end" onClick={() => navigate('/disease')}>
                      <ArrowForwardIcon />
                    </IconButton>
                  }
                  disablePadding
                  sx={{ mb: 1.5 }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'error.main' }}>
                      <BugReportIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="Possible Leaf Rust detected in Plot B"
                    secondary="Confidence score: 94%. Treatment recommendations ready."
                  />
                </ListItem>
                <ListItem
                  secondaryAction={
                    <IconButton edge="end" onClick={() => navigate('/weather')}>
                      <ArrowForwardIcon />
                    </IconButton>
                  }
                  disablePadding
                  sx={{ mb: 1.5 }}
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'warning.main' }}>
                      <WbSunnyIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="High solar radiation expected next 3 days"
                    secondary="Adjust irrigation schedules to prevent moisture stress."
                  />
                </ListItem>
                <ListItem
                  secondaryAction={
                    <IconButton edge="end" onClick={() => navigate('/advisory')}>
                      <ArrowForwardIcon />
                    </IconButton>
                  }
                  disablePadding
                >
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: 'info.main' }}>
                      <YardIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="Sowing season Rabi recommendations ready"
                    secondary="Optimal crops: Wheat (GW-496) based on current soil parameters."
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
