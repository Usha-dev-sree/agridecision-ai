import React, { useState } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, Alert, useTheme,
} from '@mui/material';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import RainIcon from '@mui/icons-material/Umbrella';
import AirIcon from '@mui/icons-material/Air';
import WaterDropIcon from '@mui/icons-material/WaterDrop';

import { usePlots } from '@/hooks/useFarm';
import { useAppSelector } from '@/store/hooks';
import { weatherService } from '@/services/advisoryService';
import { WeatherForecast } from '@/types';
import { LoadingState } from '@/components/common/States';

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export const Weather: React.FC = () => {
  const theme = useTheme();
  const { data: plots } = usePlots();
  const selectedPlotId = useAppSelector((state) => state.farm.selectedPlotId);

  const [forecast, setForecast] = useState<WeatherForecast[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activePlot = plots?.find((p) => p.id === selectedPlotId) || plots?.[0];

  React.useEffect(() => {
    const fetchWeather = async () => {
      if (!activePlot) return;
      setLoading(true);
      setError(null);
      try {
        const lat = activePlot.centroid_lat || 21.1702;
        const lon = activePlot.centroid_lng || 72.8311;
        const data = await weatherService.getForecast(lat, lon);
        setForecast(data);
      } catch (err: any) {
        setError('Failed to fetch weather forecast data. Showing fallback metrics.');
        // Fallback static forecast data displayed when live Open-Meteo API is unreachable
        setForecast([
          { date: '2026-07-24', temp_max_c: 32.5, temp_min_c: 24.1, precipitation_mm: 12.5, windspeed_max_kmh: 18.2, solar_radiation_mj_m2: 22.4, eto_fao_mm_day: 4.8 },
          { date: '2026-07-25', temp_max_c: 31.0, temp_min_c: 23.5, precipitation_mm: 22.0, windspeed_max_kmh: 22.1, solar_radiation_mj_m2: 18.1, eto_fao_mm_day: 3.9 },
          { date: '2026-07-26', temp_max_c: 30.5, temp_min_c: 23.0, precipitation_mm: 35.2, windspeed_max_kmh: 24.5, solar_radiation_mj_m2: 15.2, eto_fao_mm_day: 3.2 },
          { date: '2026-07-27', temp_max_c: 33.0, temp_min_c: 25.0, precipitation_mm: 5.1, windspeed_max_kmh: 15.0, solar_radiation_mj_m2: 25.6, eto_fao_mm_day: 5.5 },
          { date: '2026-07-28', temp_max_c: 34.2, temp_min_c: 25.8, precipitation_mm: 0.0, windspeed_max_kmh: 12.8, solar_radiation_mj_m2: 27.1, eto_fao_mm_day: 6.1 },
          { date: '2026-07-29', temp_max_c: 33.5, temp_min_c: 25.2, precipitation_mm: 2.5, windspeed_max_kmh: 14.1, solar_radiation_mj_m2: 24.8, eto_fao_mm_day: 5.4 },
          { date: '2026-07-30', temp_max_c: 32.0, temp_min_c: 24.5, precipitation_mm: 15.8, windspeed_max_kmh: 19.5, solar_radiation_mj_m2: 20.3, eto_fao_mm_day: 4.5 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
  }, [activePlot]);

  if (loading) {
    return <LoadingState message="Loading multi-spectral weather grid..." />;
  }

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
          Agro-Meteorological Forecast
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track FAO-56 Reference Evapotranspiration (ETo), precipitation, temperature ranges, and solar radiation parameters.
        </Typography>
      </Box>

      {error && <Alert severity="warning" sx={{ mb: 3 }}>{error}</Alert>}

      <Grid container spacing={3}>
        {/* Weather Line Chart */}
        {forecast && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={700} gutterBottom>
                  FAO-56 Evapotranspiration (ETo) vs Precipitation
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 3 }}>
                  Optimizes water requirements and irrigation scheduling.
                </Typography>
                <Box sx={{ width: '100%', height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={forecast}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="eto_fao_mm_day" name="ETo (mm/day)" stroke={theme.palette.secondary.main} strokeWidth={2} />
                      <Line type="monotone" dataKey="precipitation_mm" name="Precipitation (mm)" stroke={theme.palette.primary.main} strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Detailed Grid Table */}
        {forecast && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                  7-Day Detailed Forecast Grid
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Max/Min Temp (°C)</TableCell>
                        <TableCell>Precipitation (mm)</TableCell>
                        <TableCell>Wind Speed (km/h)</TableCell>
                        <TableCell>Solar Radiation (MJ/m²)</TableCell>
                        <TableCell>FAO ETo (mm/day)</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {forecast.map((w, idx) => (
                        <TableRow key={idx}>
                          <TableCell sx={{ fontWeight: 600 }}>{w.date}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <WbSunnyIcon sx={{ fontSize: 16, color: 'warning.main' }} />
                              {w.temp_max_c}°C / {w.temp_min_c}°C
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <RainIcon sx={{ fontSize: 16, color: 'info.main' }} />
                              {w.precipitation_mm} mm
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <AirIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                              {w.windspeed_max_kmh} km/h
                            </Box>
                          </TableCell>
                          <TableCell>{w.solar_radiation_mj_m2} MJ/m²</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <WaterDropIcon sx={{ fontSize: 16, color: 'primary.main' }} />
                              {w.eto_fao_mm_day} mm/day
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};
