import React, { useEffect, useState } from 'react';
import { Box, Card, Typography, Button, Chip, Grid, Paper, Alert, CircularProgress } from '@mui/material';
import LayersIcon from '@mui/icons-material/Layers';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import GpsFixedIcon from '@mui/icons-material/GpsFixed';
import { MapContainer, TileLayer, Polygon, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default icon path broken by Vite bundling
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom user location marker icon
const userLocationIcon = L.divIcon({
  className: 'user-location-marker',
  html: `<div style="background-color: #2196f3; width: 18px; height: 18px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 12px rgba(33,150,243,0.8); animation: pulse 2s infinite;"></div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

/** Helper component to re-center Leaflet map dynamically */
function RecenterMap({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1.5 });
  }, [center, zoom, map]);
  return null;
}

import { getAccurateLocation } from '@/lib/location';

export const Maps: React.FC = () => {
  // Default center (India center if geolocation is loading)
  const [mapCenter, setMapCenter] = useState<[number, number]>([20.5937, 78.9629]);
  const [zoomLevel, setZoomLevel] = useState<number>(5);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [locationStatus, setLocationStatus] = useState<string>('Requesting your exact GPS location…');
  const [locationSource, setLocationSource] = useState<'gps' | 'wifi' | 'ip' | 'default' | null>(null);
  const [locationAccuracy, setLocationAccuracy] = useState<number | null>(null);
  const [isLocating, setIsLocating] = useState<boolean>(false);

  // Dynamic plot polygons calculated relative to current location
  const generatePlotsAroundLocation = (lat: number, lng: number) => [
    {
      name: 'Primary Plot (Current GPS Zone)',
      ndvi: 0.78,
      positions: [
        [lat + 0.002, lng - 0.002] as [number, number],
        [lat + 0.003, lng + 0.001] as [number, number],
        [lat - 0.001, lng + 0.003] as [number, number],
        [lat - 0.002, lng - 0.001] as [number, number],
      ],
    },
    {
      name: 'Adjacent Block B (Telemetred)',
      ndvi: 0.54,
      positions: [
        [lat - 0.003, lng - 0.004] as [number, number],
        [lat - 0.001, lng - 0.001] as [number, number],
        [lat - 0.004, lng + 0.001] as [number, number],
        [lat - 0.006, lng - 0.003] as [number, number],
      ],
    },
  ];

  const [activePlots, setActivePlots] = useState(generatePlotsAroundLocation(28.6139, 77.2090));

  // Request accurate GPS or Network IP position
  const handleLocateUser = async () => {
    setIsLocating(true);
    setLocationSource(null);
    setLocationAccuracy(null);
    setLocationStatus('📡 Requesting your exact GPS location — please allow access in the browser prompt…');

    try {
      const loc = await getAccurateLocation();
      const coords: [number, number] = [loc.lat, loc.lng];
      setUserLocation(coords);
      setMapCenter(coords);
      setLocationSource(loc.source);
      setLocationAccuracy(loc.accuracy ?? null);
      setZoomLevel(loc.source === 'gps' ? 17 : loc.source === 'wifi' ? 15 : 12);
      setActivePlots(generatePlotsAroundLocation(loc.lat, loc.lng));
      setIsLocating(false);
      setLocationStatus(loc.label);
    } catch (err) {
      setIsLocating(false);
      setLocationStatus('⚠️ Could not determine current position. Please allow location access.');
    }
  };

  useEffect(() => {
    // Attempt auto-location on initial page load
    handleLocateUser();

    // Ensure Leaflet CSS is loaded
    const link = document.querySelector('link[href*="leaflet"]');
    if (!link) {
      const el = document.createElement('link');
      el.rel = 'stylesheet';
      el.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(el);
    }
  }, []);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} fontFamily="Outfit">
            GIS Plot Mapping &amp; Satellite Telemetry
          </Typography>
          <Typography variant="body2" color="text.secondary">
            High-resolution NDVI satellite layers, soil moisture heatmaps, and GPS current-location plot plotting.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={isLocating ? <CircularProgress size={18} color="inherit" /> : <GpsFixedIcon />}
            onClick={handleLocateUser}
            disabled={isLocating}
          >
            {isLocating ? 'Locating...' : 'Use My Current Location'}
          </Button>
          <Button variant="outlined" startIcon={<LayersIcon />}>Layers</Button>
        </Box>
      </Box>

      {/* Location alert status bar */}
      <Alert
        severity={userLocation ? (locationSource === 'gps' ? 'success' : locationSource === 'wifi' ? 'info' : 'warning') : 'info'}
        icon={<MyLocationIcon />}
        action={
          locationSource && (
            <Chip
              size="small"
              label={
                locationSource === 'gps' ? `GPS ±${locationAccuracy != null ? Math.round(locationAccuracy) + ' m' : 'exact'}` :
                locationSource === 'wifi' ? `Wi-Fi ±${locationAccuracy != null ? Math.round(locationAccuracy) + ' m' : '~100 m'}` :
                locationSource === 'ip' ? 'IP (city-level)' : 'Default'
              }
              color={
                locationSource === 'gps' ? 'success' :
                locationSource === 'wifi' ? 'info' : 'warning'
              }
              variant="filled"
            />
          )
        }
      >
        {locationStatus}
      </Alert>

      <Grid container spacing={2.5}>
        <Grid item xs={12} md={8}>
          <Card
            sx={{
              borderRadius: 3,
              height: 520,
              overflow: 'hidden',
              position: 'relative',
              border: '1px solid rgba(255,255,255,0.1)',
            }}
          >
            {/* Real Leaflet Map centered on Current GPS Location */}
            <MapContainer
              center={mapCenter}
              zoom={zoomLevel}
              style={{ width: '100%', height: '100%' }}
              zoomControl={true}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <RecenterMap center={mapCenter} zoom={zoomLevel} />

              {/* Plotted Field Polygons */}
              {activePlots.map((plot) => (
                <Polygon
                  key={plot.name}
                  positions={plot.positions}
                  pathOptions={{
                    color: plot.ndvi > 0.6 ? '#4caf50' : '#ff9800',
                    fillColor: plot.ndvi > 0.6 ? '#4caf50' : '#ff9800',
                    fillOpacity: 0.3,
                    weight: 2.5,
                  }}
                >
                  <Popup>
                    <strong>{plot.name}</strong>
                    <br />
                    NDVI Vegetation Index: <strong>{plot.ndvi}</strong>
                    <br />
                    Status: {plot.ndvi > 0.6 ? '🟢 Healthy Canopy' : '🟡 Moderate Moisture'}
                  </Popup>
                </Polygon>
              ))}

              {/* Marker for Current GPS User Location */}
              {userLocation && (
                <Marker position={userLocation} icon={userLocationIcon}>
                  <Popup>
                    <strong>📍 Your Current Position</strong>
                    <br />
                    Latitude: {userLocation[0].toFixed(6)}°
                    <br />
                    Longitude: {userLocation[1].toFixed(6)}°
                    <br />
                    {locationAccuracy != null && <span>Accuracy: ±{Math.round(locationAccuracy)} m<br /></span>}
                    Source: {locationSource === 'gps' ? '🛰️ GPS' : locationSource === 'wifi' ? '📶 Wi-Fi' : locationSource === 'ip' ? '🌐 IP Network' : '🗺️ Default'}
                  </Popup>
                </Marker>
              )}

              {/* Re-center / GPS Locate Floating Button inside Map */}
              <Button
                variant="contained"
                startIcon={<MyLocationIcon />}
                size="small"
                onClick={handleLocateUser}
                sx={{
                  position: 'absolute',
                  top: 12,
                  right: 12,
                  zIndex: 1000,
                  bgcolor: 'background.paper',
                  color: 'text.primary',
                  '&:hover': { bgcolor: 'action.hover' },
                }}
              >
                GPS Locate Me
              </Button>
            </MapContainer>

            {/* Map Legend */}
            <Box
              sx={{
                position: 'absolute',
                bottom: 12,
                left: 12,
                zIndex: 1000,
                bgcolor: 'rgba(0,0,0,0.75)',
                backdropFilter: 'blur(8px)',
                borderRadius: 2,
                px: 2,
                py: 1,
                display: 'flex',
                gap: 1.5,
                alignItems: 'center',
              }}
            >
              <Chip size="small" label="NDVI > 0.6 (Healthy)" sx={{ bgcolor: '#4caf50', color: '#fff' }} />
              <Chip size="small" label="NDVI ≤ 0.6 (Moderate)" sx={{ bgcolor: '#ff9800', color: '#fff' }} />
              <Chip size="small" label="📍 My Location" sx={{ bgcolor: '#2196f3', color: '#fff' }} />
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, p: 2.5, height: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Typography variant="h6" fontWeight={700}>
              GPS Coordinates &amp; Telemetry
            </Typography>

            <Paper sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
              <Typography color="text.secondary" variant="body2">Current Coordinates</Typography>
              <Typography variant="subtitle1" fontWeight={800} color="primary">
                {userLocation ? `${userLocation[0].toFixed(6)}° N, ${userLocation[1].toFixed(6)}° E` : 'Requesting GPS…'}
              </Typography>
              {locationAccuracy != null && (
                <Typography variant="caption" color="success.main">±{Math.round(locationAccuracy)} m accuracy</Typography>
              )}
            </Paper>

            <Paper sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
              <Typography color="text.secondary" variant="body2">NDVI Vegetation Health</Typography>
              <Typography variant="h5" fontWeight={800} color="success.main">
                0.78 (Dense Canopy)
              </Typography>
            </Paper>

            <Paper sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
              <Typography color="text.secondary" variant="body2">Root Zone Soil Moisture</Typography>
              <Typography variant="h5" fontWeight={800} color="info.main">
                28.4% Volumetric
              </Typography>
            </Paper>

            <Paper sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
              <Typography color="text.secondary" variant="body2">Active Plotted Zones</Typography>
              <Typography variant="h5" fontWeight={800}>
                {activePlots.length} plots active
              </Typography>
            </Paper>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
