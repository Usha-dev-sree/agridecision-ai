import React, { useState } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, TextField, MenuItem,
  LinearProgress, Alert, Divider, Chip, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ScienceIcon from '@mui/icons-material/Science';
import BarChartIcon from '@mui/icons-material/BarChart';

import { usePlots } from '@/hooks/useFarm';
import { useAppSelector } from '@/store/hooks';
import { advisoryService } from '@/services/advisoryService';
import { YieldPrediction } from '@/types';
import { LoadingState } from '@/components/common/States';

export const Yield: React.FC = () => {
  const { data: plots } = usePlots();
  const selectedPlotId = useAppSelector((state) => state.farm.selectedPlotId);

  const [crop, setCrop] = useState('Rice');
  const [prediction, setPrediction] = useState<YieldPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activePlot = plots?.find((p) => p.id === selectedPlotId) || plots?.[0];

  const handlePredict = async () => {
    if (!activePlot) return;
    setLoading(true);
    setError(null);
    try {
      const data = await advisoryService.predictYield(activePlot.id, crop);
      setPrediction(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to predict yield. Ensure parameters are correctly set.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
          Crop Yield Prediction
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Predict yield volumes using machine learning ensembles (XGBoost & Random Forest) trained on historic farm records, soil texture, and vegetation indices.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Input parameters */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <ScienceIcon color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Parameters & Target
                </Typography>
              </Box>

              {activePlot ? (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>Active Farm Plot:</Typography>
                  <Typography variant="body1" fontWeight={700} color="primary" sx={{ mb: 3 }}>
                    {activePlot.name} ({activePlot.total_area_ha} Ha)
                  </Typography>

                  <TextField
                    fullWidth
                    select
                    label="Target Crop"
                    value={crop}
                    onChange={(e) => setCrop(e.target.value)}
                    sx={{ mb: 3 }}
                  >
                    <MenuItem value="Rice">Rice (Basmati)</MenuItem>
                    <MenuItem value="Wheat">Wheat (Durum)</MenuItem>
                    <MenuItem value="Cotton">Cotton (Bt Cotton)</MenuItem>
                    <MenuItem value="Maize">Maize (Hybrid)</MenuItem>
                    <MenuItem value="Sugarcane">Sugarcane (Co 86032)</MenuItem>
                  </TextField>

                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handlePredict}
                    disabled={loading}
                    startIcon={<TrendingUpIcon />}
                  >
                    Run Prediction Model
                  </Button>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Please create a plot boundary first to run yield models.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Prediction Output & Shapley Explanations */}
        <Grid item xs={12} lg={8}>
          {loading ? (
            <LoadingState message="Computing ensemble SHAP explanations..." />
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : prediction ? (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6" fontWeight={700}>
                    Yield Output Summary
                  </Typography>
                  <Chip label="Model Type: Random Forest Ensemble" color="primary" variant="outlined" />
                </Box>
                <Divider sx={{ mb: 3 }} />

                <Box sx={{ mb: 4, display: 'flex', alignItems: 'baseline', gap: 1 }}>
                  <Typography variant="h3" fontWeight={800} color="primary" fontFamily="Outfit">
                    {prediction.expected_yield_kg_ha.toLocaleString()}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary">
                    Kg / Hectare expected
                  </Typography>
                </Box>

                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
                  Explainable AI (SHAP Feature Importances)
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 3 }}>
                  Shapley values showing impact weighting for yield parameters.
                </Typography>

                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Feature / Parameter</TableCell>
                        <TableCell>SHAP Impact Weight</TableCell>
                        <TableCell>Status Contribution</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(prediction.explanations).map(([feature, weight]) => (
                        <TableRow key={feature}>
                          <TableCell sx={{ textTransform: 'capitalize' }}>
                            {feature.replace(/_/g, ' ')}
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                              <Box sx={{ width: '100px', mr: 1 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={Math.min(Math.abs(weight) * 10, 100)}
                                  color={weight >= 0 ? 'success' : 'error'}
                                />
                              </Box>
                              <Typography variant="body2" fontWeight={600}>
                                {weight >= 0 ? `+${weight.toFixed(2)}` : weight.toFixed(2)}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={weight >= 0 ? 'Positive Contribution' : 'Negative Constraint'}
                              size="small"
                              color={weight >= 0 ? 'success' : 'error'}
                              variant="outlined"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          ) : (
            <Card sx={{ borderStyle: 'dashed', borderWidth: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
              <Box sx={{ textAlign: 'center', opacity: 0.75 }}>
                <BarChartIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  Ready to Predict Crop Yield
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Configure target options and click run model to view detailed predictions and Shapley contribution factors.
                </Typography>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};
