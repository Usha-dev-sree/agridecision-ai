import React, { useState } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, TextField, MenuItem,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  LinearProgress, Chip, Divider, Alert,
} from '@mui/material';
import YardIcon from '@mui/icons-material/Yard';
import ScienceIcon from '@mui/icons-material/Science';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CalculateIcon from '@mui/icons-material/Calculate';

import { usePlots } from '@/hooks/useFarm';
import { useAppSelector } from '@/store/hooks';
import { advisoryService } from '@/services/advisoryService';
import { CropRecommendation } from '@/types';
import { LoadingState } from '@/components/common/States';

export const Advisory: React.FC = () => {
  const { data: plots } = usePlots();
  const selectedPlotId = useAppSelector((state) => state.farm.selectedPlotId);

  const [season, setSeason] = useState<'KHARIF' | 'RABI' | 'ZAID'>('KHARIF');
  const [recommendation, setRecommendation] = useState<CropRecommendation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // What-if simulation parameters
  const [phOverride, setPhOverride] = useState('');
  const [nitrogenOverride, setNitrogenOverride] = useState('');

  const activePlot = plots?.find((p) => p.id === selectedPlotId) || plots?.[0];

  const handleGenerateRecommendation = async () => {
    if (!activePlot) return;
    setLoading(true);
    setError(null);
    try {
      const data = await advisoryService.getRecommendation(activePlot.id, season);
      setRecommendation(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to fetch recommendations from the AI engine.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
          AI Crop Suitability & Advisory
        </Typography>
        <Typography variant="body1" color="text.secondary">
          ML powered Crop Recommendation Engine based on geospatial features, soil NPK analysis, and historic weather metrics.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Parameters input / configuration */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <ScienceIcon color="primary" />
                <Typography variant="h6" fontWeight={700}>
                  Advisory Parameters
                </Typography>
              </Box>

              {activePlot ? (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>Selected Plot:</Typography>
                  <Typography variant="body1" fontWeight={700} color="primary" sx={{ mb: 3 }}>
                    {activePlot.name} ({activePlot.total_area_ha} Ha)
                  </Typography>

                  <TextField
                    fullWidth
                    select
                    label="Target Season"
                    value={season}
                    onChange={(e) => setSeason(e.target.value as any)}
                    sx={{ mb: 3 }}
                  >
                    <MenuItem value="KHARIF">Kharif (Monsoon)</MenuItem>
                    <MenuItem value="RABI">Rabi (Winter)</MenuItem>
                    <MenuItem value="ZAID">Zaid (Summer)</MenuItem>
                  </TextField>

                  <Typography variant="subtitle2" sx={{ mb: 1 }} fontWeight={600}>
                    What-if Parameters (Optional Override)
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                    Adjust parameters to see how changes affect crop recommendations.
                  </Typography>

                  <TextField
                    fullWidth
                    label="Soil pH Level Override"
                    type="number"
                    value={phOverride}
                    onChange={(e) => setPhOverride(e.target.value)}
                    sx={{ mb: 2 }}
                    placeholder="e.g. 6.5"
                  />

                  <TextField
                    fullWidth
                    label="Nitrogen (N) Content Override"
                    type="number"
                    value={nitrogenOverride}
                    onChange={(e) => setNitrogenOverride(e.target.value)}
                    sx={{ mb: 3 }}
                    placeholder="e.g. 50"
                  />

                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleGenerateRecommendation}
                    disabled={loading}
                    startIcon={loading ? <LinearProgress /> : <AutoAwesomeIcon />}
                  >
                    Compute Crop Advisory
                  </Button>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Please create a plot boundary first to compute recommendations.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Results Panel */}
        <Grid item xs={12} lg={8}>
          {loading ? (
            <LoadingState message="Processing complex ML inference pipelines..." />
          ) : error ? (
            <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
          ) : recommendation ? (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 1.5 }}>
                  <Box>
                    <Typography variant="h6" fontWeight={700}>
                      AI Recommendations
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Model Version: {recommendation.model_version}
                    </Typography>
                  </Box>
                  <Chip
                    label={`Confidence Threshold: ${(recommendation.top_confidence_score ? Number(recommendation.top_confidence_score) * 100 : 0).toFixed(0)}%`}
                    color="primary"
                    variant="outlined"
                  />
                </Box>
                <Divider sx={{ mb: 3 }} />

                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Crop</TableCell>
                        <TableCell>Confidence Score</TableCell>
                        <TableCell>Expected Yield (Kg/Ha)</TableCell>
                        <TableCell>Suitability Factor</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recommendation.recommendations.map((rec, index) => (
                        <TableRow key={index}>
                          <TableCell sx={{ fontWeight: 700 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <YardIcon color="success" />
                              {rec.crop_name}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                              <Box sx={{ width: '100px', mr: 1 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={Number(rec.confidence_score) * 100}
                                  color={Number(rec.confidence_score) > 0.75 ? 'success' : 'warning'}
                                />
                              </Box>
                              <Typography variant="body2" fontWeight={600}>
                                {(Number(rec.confidence_score) * 100).toFixed(1)}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            {rec.expected_yield_kg_ha ?? 'N/A'} kg/ha
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption" color="text.secondary">
                              {rec.suitability_reason || 'Highly suitable for clay loam textured soil profiles.'}
                            </Typography>
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
                <CalculateIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  Ready to Predict Crop Suitability
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Click the Compute button on the left panel to trigger advisory services.
                </Typography>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};
