import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, TextField, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions, Chip, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, useTheme,
  Alert, CircularProgress,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import AddIcon from '@mui/icons-material/Add';
import MapIcon from '@mui/icons-material/Map';
import EditIcon from '@mui/icons-material/Edit';
import RefreshIcon from '@mui/icons-material/Refresh';
import LayersIcon from '@mui/icons-material/Layers';
import GpsFixedIcon from '@mui/icons-material/GpsFixed';
import MyLocationIcon from '@mui/icons-material/MyLocation';

// Map component imports
import { MapContainer, TileLayer, Polygon, Marker, Popup, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';

import { usePlots, useCreatePlot, useSoilProfile, useSeasons } from '@/hooks/useFarm';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { setSelectedPlot } from '@/store/slices/farmSlice';
import { LoadingState } from '@/components/common/States';

// Configurable Leaflet Marker SVG Icon
const DefaultIcon = L.divIcon({
  className: 'custom-leaflet-marker',
  html: `<div style="background-color: #2e7d32; width: 14px; height: 14px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 8px rgba(0,0,0,0.5);"></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});
L.Marker.prototype.options.icon = DefaultIcon;

const userLocationIcon = L.divIcon({
  className: 'user-location-marker',
  html: `<div style="background-color: #2196f3; width: 16px; height: 16px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 10px rgba(33,150,243,0.8);"></div>`,
  iconSize: [22, 22],
  iconAnchor: [11, 11],
});

// Map component helper to capture clicks for creating boundaries
const MapEventsHelper = ({ onMapClick }: { onMapClick: (latlng: L.LatLng) => void }) => {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng);
    },
  });
  return null;
};

/** Re-center map component */
function RecenterMap({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1.2 });
  }, [center, zoom, map]);
  return null;
}

import { getAccurateLocation } from '@/lib/location';

export const Plots: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { data: plots, isLoading, refetch } = usePlots();
  const selectedPlotId = useAppSelector((state) => state.farm.selectedPlotId);
  const createPlotMutation = useCreatePlot();

  // Soil details & seasons for the selected plot
  const { data: soil } = useSoilProfile(selectedPlotId || '');
  const { data: seasons } = useSeasons(selectedPlotId || '');

  // Add plot modal state
  const [openAdd, setOpenAdd] = useState(false);
  const [name, setName] = useState('');
  const [area, setArea] = useState('');
  const [irrigation, setIrrigation] = useState<'RAINFED' | 'IRRIGATED' | 'MICRO_IRRIGATED'>('IRRIGATED');

  // Drawn coordinates for boundary creation (simple list of latlng points)
  const [drawnPoints, setDrawnPoints] = useState<[number, number][]>([]);

  // Geolocation state for plot modal & main view
  const [currentGps, setCurrentGps] = useState<[number, number] | null>(null);
  const [modalMapCenter, setModalMapCenter] = useState<[number, number]>([21.1702, 72.8311]);
  const [isLocating, setIsLocating] = useState<boolean>(false);
  const [gpsNotice, setGpsNotice] = useState<string>('');

  // Fetch current position using browser Geolocation + IP Fallback
  const handleFetchCurrentLocation = async () => {
    setIsLocating(true);
    setGpsNotice('Acquiring current location via GPS / Network...');

    try {
      const loc = await getAccurateLocation();
      const coords: [number, number] = [loc.lat, loc.lng];

      setCurrentGps(coords);
      setModalMapCenter(coords);
      setIsLocating(false);
      setGpsNotice(`📍 ${loc.label}`);

      // If no points drawn yet, generate initial plot boundary box around user's location
      if (drawnPoints.length === 0) {
        setDrawnPoints([
          [loc.lat + 0.001, loc.lng - 0.001],
          [loc.lat + 0.001, loc.lng + 0.001],
          [loc.lat - 0.001, loc.lng + 0.001],
          [loc.lat - 0.001, loc.lng - 0.001],
        ]);
      }
    } catch (err) {
      setIsLocating(false);
      setGpsNotice('Could not acquire location.');
    }
  };

  const handleMapClick = (latlng: L.LatLng) => {
    setDrawnPoints((prev) => [...prev, [latlng.lat, latlng.lng]]);
  };

  const handleCreatePlotSubmit = () => {
    if (!name || !area) return;

    // Build simple geojson centroid and polygon if points exist
    let centroidLat = currentGps ? currentGps[0] : 21.1702;
    let centroidLng = currentGps ? currentGps[1] : 72.8311;

    if (drawnPoints.length > 0) {
      const lats = drawnPoints.map((p) => p[0]);
      const lngs = drawnPoints.map((p) => p[1]);
      centroidLat = lats.reduce((a, b) => a + b, 0) / lats.length;
      centroidLng = lngs.reduce((a, b) => a + b, 0) / lngs.length;
    }

    createPlotMutation.mutate({
      name,
      total_area_ha: Number(area),
      irrigation_type: irrigation,
      is_active: true,
      centroid_lat: centroidLat,
      centroid_lng: centroidLng,
    }, {
      onSuccess: () => {
        setOpenAdd(false);
        setName('');
        setArea('');
        setIrrigation('IRRIGATED');
        setDrawnPoints([]);
      }
    });
  };

  const selectedPlot = plots?.find((p) => p.id === selectedPlotId) || plots?.[0];

  useEffect(() => {
    if (plots && plots.length > 0 && !selectedPlotId) {
      dispatch(setSelectedPlot(plots[0].id));
    }
  }, [plots, selectedPlotId, dispatch]);

  if (isLoading) {
    return <LoadingState message="Loading plots..." />;
  }

  // Sample static boundary coordinates for visualization if no dynamic coordinates exist
  const defaultBoundary: [number, number][] = selectedPlot?.centroid_lat
    ? [
        [selectedPlot.centroid_lat + 0.001, selectedPlot.centroid_lng! - 0.001],
        [selectedPlot.centroid_lat + 0.001, selectedPlot.centroid_lng! + 0.001],
        [selectedPlot.centroid_lat - 0.001, selectedPlot.centroid_lng! + 0.001],
        [selectedPlot.centroid_lat - 0.001, selectedPlot.centroid_lng! - 0.001],
      ]
    : [
        [21.1702, 72.8311],
        [21.1712, 72.8311],
        [21.1712, 72.8325],
        [21.1702, 72.8325],
      ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
            Plot Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Configure plot boundaries using live GPS geolocation, irrigation profiles, and track soil diagnostics.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Refresh
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setOpenAdd(true); handleFetchCurrentLocation(); }}>
            Add New Plot
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Plots List & Grid */}
        <Grid item xs={12} md={4}>
          <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
            Plot Directory
          </Typography>
          <Grid container spacing={2}>
            {plots?.map((plot) => {
              const isSelected = plot.id === selectedPlotId;
              return (
                <Grid item xs={12} key={plot.id}>
                  <Card
                    onClick={() => dispatch(setSelectedPlot(plot.id))}
                    sx={{
                      cursor: 'pointer',
                      borderColor: isSelected ? theme.palette.primary.main : 'divider',
                      backgroundColor: isSelected ? alpha(theme.palette.primary.main, 0.05) : 'background.paper',
                      borderWidth: isSelected ? 2 : 1,
                    }}
                  >
                    <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="subtitle1" fontWeight={700}>
                          {plot.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Area: {plot.total_area_ha} Ha | {plot.irrigation_type}
                        </Typography>
                      </Box>
                      <AgricultureIcon color={isSelected ? 'primary' : 'disabled'} />
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </Grid>

        {/* Selected Plot Map & Profile Details */}
        <Grid item xs={12} md={8}>
          {selectedPlot ? (
            <Grid container spacing={3}>
              {/* Map Boundary Visualization */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <MapIcon color="primary" />
                        <Typography variant="h6" fontWeight={700}>
                          Geospatial Boundary Map
                        </Typography>
                      </Box>
                      <Button variant="text" startIcon={<EditIcon />} size="small">
                        Redraw Boundary
                      </Button>
                    </Box>
                    <Box sx={{ height: 350, borderRadius: 2, overflow: 'hidden', border: `1px solid ${theme.palette.divider}` }}>
                      <MapContainer
                        center={[selectedPlot.centroid_lat || 21.1702, selectedPlot.centroid_lng || 72.8311]}
                        zoom={16}
                        style={{ height: '100%', width: '100%' }}
                      >
                        <TileLayer
                          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        <Polygon
                          pathOptions={{ fillColor: theme.palette.primary.main, color: theme.palette.primary.dark }}
                          positions={defaultBoundary}
                        />
                        <Marker position={[selectedPlot.centroid_lat || 21.1702, selectedPlot.centroid_lng || 72.8311]}>
                          <Popup>
                            <strong>{selectedPlot.name}</strong> <br />
                            Plot Centroid Marker
                          </Popup>
                        </Marker>
                      </MapContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Soil diagnostics & parameter configuration */}
              <Grid item xs={12} sm={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <LayersIcon color="primary" />
                      <Typography variant="h6" fontWeight={700}>
                        Soil Quality Diagnostics
                      </Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />

                    {soil ? (
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Nitrogen (N)</Typography>
                          <Typography variant="body1" fontWeight={600}>{soil.nitrogen_content ?? 'N/A'} ppm</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Phosphorus (P)</Typography>
                          <Typography variant="body1" fontWeight={600}>{soil.phosphorus_content ?? 'N/A'} ppm</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Potassium (K)</Typography>
                          <Typography variant="body1" fontWeight={600}>{soil.potassium_content ?? 'N/A'} ppm</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">pH Level</Typography>
                          <Typography variant="body1" fontWeight={600}>{soil.ph_level ?? 'N/A'}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Organic Carbon</Typography>
                          <Typography variant="body1" fontWeight={600}>{soil.organic_carbon_percent ?? 'N/A'} %</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Source</Typography>
                          <Chip label={soil.source} color="info" size="small" variant="outlined" />
                        </Grid>
                      </Grid>
                    ) : (
                      <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          No active soil profile details exist for this plot.
                        </Typography>
                        <Button variant="outlined" size="small" color="primary" sx={{ mt: 1 }}>
                          Configure Soil Parameters
                        </Button>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Seasons Listing */}
              <Grid item xs={12} sm={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" fontWeight={700}>
                        Crop Seasons
                      </Typography>
                      <Chip label={`${seasons?.length || 0} Seasons`} color="primary" size="small" />
                    </Box>
                    <Divider sx={{ mb: 2 }} />

                    {seasons && seasons.length > 0 ? (
                      <TableContainer component={Paper} variant="outlined" sx={{ border: 'none' }}>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Crop</TableCell>
                              <TableCell>Season</TableCell>
                              <TableCell>Status</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {seasons.map((season) => (
                              <TableRow key={season.id}>
                                <TableCell sx={{ fontWeight: 600 }}>{season.crop_name}</TableCell>
                                <TableCell>{season.season_name}</TableCell>
                                <TableCell>
                                  <Chip label={season.status} size="small" color={season.status === 'GROWING' ? 'success' : 'default'} />
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No crop seasons recorded yet for this plot. Add dynamic crop season telemetry.
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          ) : (
            <Card>
              <CardContent>
                <Typography variant="body1" align="center" color="text.secondary">
                  Please select a plot to view detailed maps, boundaries, and soil parameters.
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* Add Plot Modal with Current GPS Location Plotting */}
      <Dialog open={openAdd} onClose={() => setOpenAdd(false)} maxWidth="md" fullWidth>
        <DialogTitle fontWeight={700}>Add New Farm Plot Boundary</DialogTitle>
        <DialogContent>
          {gpsNotice && (
            <Alert severity="info" icon={<MyLocationIcon />} sx={{ mb: 2 }}>
              {gpsNotice}
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Plot Name / Reference"
                value={name}
                onChange={(e) => setName(e.target.value)}
                sx={{ mb: 2.5 }}
              />
              <TextField
                fullWidth
                label="Total Area (Hectares)"
                type="number"
                value={area}
                onChange={(e) => setArea(e.target.value)}
                sx={{ mb: 2.5 }}
              />
              <TextField
                fullWidth
                select
                label="Irrigation Classification"
                value={irrigation}
                onChange={(e) => setIrrigation(e.target.value as any)}
                sx={{ mb: 2.5 }}
              >
                <MenuItem value="RAINFED">Rainfed Irrigation</MenuItem>
                <MenuItem value="IRRIGATED">Canal / Tube-well Irrigated</MenuItem>
                <MenuItem value="MICRO_IRRIGATED">Drip / Sprinkler Micro-irrigation</MenuItem>
              </TextField>

              <Button
                fullWidth
                variant="outlined"
                color="secondary"
                startIcon={isLocating ? <CircularProgress size={18} color="inherit" /> : <GpsFixedIcon />}
                onClick={handleFetchCurrentLocation}
                disabled={isLocating}
                sx={{ mb: 2 }}
              >
                {isLocating ? 'Acquiring GPS...' : 'Center Map at My Current GPS Location'}
              </Button>

              {drawnPoints.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    Captured Polygon Boundary Nodes:
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {drawnPoints.length} boundary nodes defined around current coordinates.
                  </Typography>
                </Box>
              )}
            </Grid>

            {/* Interactive map boundary drawer */}
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2" fontWeight={600}>
                  Geospatial Boundary Node Capture
                </Typography>
                <Button size="small" onClick={() => setDrawnPoints([])}>
                  Clear Points
                </Button>
              </Box>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                Click anywhere on the map to add boundary nodes around your location.
              </Typography>
              <Box sx={{ height: 280, borderRadius: 2, overflow: 'hidden', border: `1px solid ${theme.palette.divider}` }}>
                <MapContainer
                  center={modalMapCenter}
                  zoom={15}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <RecenterMap center={modalMapCenter} zoom={15} />
                  <MapEventsHelper onMapClick={handleMapClick} />

                  {currentGps && (
                    <Marker position={currentGps} icon={userLocationIcon}>
                      <Popup>Your Current GPS Location</Popup>
                    </Marker>
                  )}

                  {drawnPoints.length > 0 && (
                    <Polygon
                      pathOptions={{ fillColor: theme.palette.primary.main, color: theme.palette.primary.dark }}
                      positions={drawnPoints}
                    />
                  )}
                  {drawnPoints.map((pt, idx) => (
                    <Marker key={idx} position={pt} />
                  ))}
                </MapContainer>
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAdd(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreatePlotSubmit}>Create Plot</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
