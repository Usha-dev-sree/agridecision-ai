import React from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Divider, MenuItem, TextField, useTheme,
} from '@mui/material';
import BarChartIcon from '@mui/icons-material/BarChart';
import ShowChartIcon from '@mui/icons-material/ShowChart';

import { usePlots } from '@/hooks/useFarm';
import { useAppSelector } from '@/store/hooks';
import { ResponsiveContainer, LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export const Analytics: React.FC = () => {
  const theme = useTheme();
  const { data: plots } = usePlots();
  const selectedPlotId = useAppSelector((state) => state.farm.selectedPlotId);

  const activePlot = plots?.find((p) => p.id === selectedPlotId) || plots?.[0];

  // Demo seed telemetry data (used as fallback when live satellite API is unavailable)
  const ndviData = [
    { date: 'May 01', NDVI: 0.25, EVI: 0.18 },
    { date: 'May 15', NDVI: 0.32, EVI: 0.22 },
    { date: 'Jun 01', NDVI: 0.45, EVI: 0.31 },
    { date: 'Jun 15', NDVI: 0.62, EVI: 0.45 },
    { date: 'Jul 01', NDVI: 0.78, EVI: 0.58 },
    { date: 'Jul 15', NDVI: 0.81, EVI: 0.61 },
  ];

  const soilMoistureData = [
    { time: '00:00', depth_10cm: 32, depth_30cm: 28, depth_60cm: 22 },
    { time: '04:00', depth_10cm: 31, depth_30cm: 28, depth_60cm: 22 },
    { time: '08:00', depth_10cm: 30, depth_30cm: 27, depth_60cm: 23 },
    { time: '12:00', depth_10cm: 28, depth_30cm: 27, depth_60cm: 23 },
    { time: '16:00', depth_10cm: 35, depth_30cm: 29, depth_60cm: 24 }, // after irrigation
    { time: '20:00', depth_10cm: 33, depth_30cm: 29, depth_60cm: 24 },
  ];

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
            Agronomic Analytics
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Advanced spectral indicators, Normalized Difference Vegetation Index (NDVI), and multi-layer soil moisture telemetry profiles.
          </Typography>
        </Box>
        {activePlot && (
          <TextField
            select
            size="small"
            label="Focus Area"
            value={activePlot.id}
            sx={{ minWidth: 160 }}
          >
            <MenuItem value={activePlot.id}>{activePlot.name}</MenuItem>
          </TextField>
        )}
      </Box>

      <Grid container spacing={3}>
        {/* NDVI Satellite Indexes */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <ShowChartIcon color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  NDVI & EVI Vegetation Index History
                </Typography>
              </Box>
              <Divider sx={{ mb: 3 }} />

              <Box sx={{ width: '100%', height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={ndviData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="NDVI" name="NDVI Index" stroke={theme.palette.primary.main} strokeWidth={3} />
                    <Line type="monotone" dataKey="EVI" name="EVI Index" stroke={theme.palette.secondary.main} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Multi-depth Soil moisture sensor profiles */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <BarChartIcon color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Multi-Layer Soil Moisture (%)
                </Typography>
              </Box>
              <Divider sx={{ mb: 3 }} />

              <Box sx={{ width: '100%', height: 320 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={soilMoistureData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis domain={[0, 50]} />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="depth_10cm" name="Top Layer (10cm)" stroke={theme.palette.primary.main} fill={theme.palette.primary.main} fillOpacity={0.1} />
                    <Area type="monotone" dataKey="depth_30cm" name="Root Layer (30cm)" stroke={theme.palette.secondary.main} fill={theme.palette.secondary.main} fillOpacity={0.1} />
                    <Area type="monotone" dataKey="depth_60cm" name="Deep Soil (60cm)" stroke={theme.palette.info.main} fill={theme.palette.info.main} fillOpacity={0.1} />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
