import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, TextField, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Alert, Divider, Chip, useTheme,
} from '@mui/material';
import StorefrontIcon from '@mui/icons-material/Storefront';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SearchIcon from '@mui/icons-material/Search';

import { marketService, advisoryService } from '@/services/advisoryService';
import { MarketPrice, PriceForecast } from '@/types';
import { LoadingState } from '@/components/common/States';

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export const Market: React.FC = () => {
  const theme = useTheme();
  const [cropFilter, setCropFilter] = useState('Paddy');
  const [stateFilter, setStateFilter] = useState('Punjab');
  const [prices, setPrices] = useState<MarketPrice[]>([]);
  const [forecast, setForecast] = useState<PriceForecast | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPricesAndForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await marketService.getPrices(cropFilter, stateFilter);
      setPrices(data);
    } catch (err) {
      setError('Market service unavailable. Displaying simulated market intelligence.');
      setPrices([
        { crop_name: 'Paddy', market_name: 'Khanna', state: 'Punjab', modal_price: 2183, min_price: 2100, max_price: 2250, arrival_date: '2026-07-23', unit: 'Quintal' },
        { crop_name: 'Paddy', market_name: 'Rajpura', state: 'Punjab', modal_price: 2190, min_price: 2150, max_price: 2240, arrival_date: '2026-07-23', unit: 'Quintal' },
        { crop_name: 'Wheat', market_name: 'Khanna', state: 'Punjab', modal_price: 2275, min_price: 2200, max_price: 2350, arrival_date: '2026-07-23', unit: 'Quintal' },
      ]);
    } finally {
      setLoading(false);
    }

    setLoadingForecast(true);
    try {
      const forecastData = await advisoryService.forecastPrice(cropFilter, 'MKT_001');
      setForecast(forecastData);
    } catch {
      // Mock forecast data for visualization fallback
      setForecast({
        crop_name: cropFilter,
        market_id: 'MKT_001',
        current_price: 2183,
        forecast_next_7_days: [2195, 2210, 2205, 2220, 2235, 2250, 2245],
      });
    } finally {
      setLoadingForecast(false);
    }
  };

  useEffect(() => {
    fetchPricesAndForecast();
  }, [cropFilter, stateFilter]);

  // Format forecast for chart plotting
  const chartData = forecast?.forecast_next_7_days.map((price, idx) => ({
    day: `Day ${idx + 1}`,
    Price: price,
  })) || [];

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
          Market Intelligence & Price Forecast
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track wholesale market arrivals, min/max modal price thresholds, and forecast upcoming price trends using temporal models.
        </Typography>
      </Box>

      {error && <Alert severity="warning" sx={{ mb: 3 }}>{error}</Alert>}

      <Grid container spacing={3}>
        {/* Filters and search config */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <SearchIcon color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Filter Options
                </Typography>
              </Box>

              <TextField
                fullWidth
                label="Crop Type"
                value={cropFilter}
                onChange={(e) => setCropFilter(e.target.value)}
                sx={{ mb: 3 }}
                placeholder="e.g. Paddy, Wheat, Cotton"
              />

              <TextField
                fullWidth
                label="State / Region"
                value={stateFilter}
                onChange={(e) => setStateFilter(e.target.value)}
                sx={{ mb: 3 }}
                placeholder="e.g. Punjab, Haryana"
              />

              <Button
                fullWidth
                variant="contained"
                onClick={fetchPricesAndForecast}
                startIcon={<StorefrontIcon />}
              >
                Fetch Market Data
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Current Prices Table */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Current Wholesale Market Rates
              </Typography>
              {loading ? (
                <LoadingState message="Fetching live market updates..." />
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Crop</TableCell>
                        <TableCell>Market / Mandi</TableCell>
                        <TableCell>State</TableCell>
                        <TableCell>Min Price</TableCell>
                        <TableCell>Max Price</TableCell>
                        <TableCell>Modal Price</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {prices.map((p, idx) => (
                        <TableRow key={idx}>
                          <TableCell sx={{ fontWeight: 600 }}>{p.crop_name}</TableCell>
                          <TableCell>{p.market_name}</TableCell>
                          <TableCell>{p.state}</TableCell>
                          <TableCell>₹{p.min_price} / {p.unit}</TableCell>
                          <TableCell>₹{p.max_price} / {p.unit}</TableCell>
                          <TableCell>
                            <Chip label={`₹${p.modal_price}`} color="success" variant="outlined" size="small" />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Price Forecast Trend Chart */}
        {forecast && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Box>
                    <Typography variant="h6" fontWeight={700}>
                      7-Day Price Forecast Trend
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Target Crop: {forecast.crop_name} | Baseline Rate: ₹{forecast.current_price}
                    </Typography>
                  </Box>
                  <Chip icon={<TrendingUpIcon />} label="Predictive AI Active" color="primary" />
                </Box>
                <Divider sx={{ mb: 3 }} />

                {loadingForecast ? (
                  <LoadingState message="Running time-series forecasting models..." />
                ) : (
                  <Box sx={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis domain={['auto', 'auto']} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="Price" stroke={theme.palette.primary.main} strokeWidth={3} activeDot={{ r: 8 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};
