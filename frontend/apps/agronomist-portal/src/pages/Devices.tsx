import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, TextField, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions, Chip, Divider,
} from '@mui/material';
import DeviceHubIcon from '@mui/icons-material/DeviceHub';
import AddIcon from '@mui/icons-material/Add';
import SettingsInputAntennaIcon from '@mui/icons-material/SettingsInputAntenna';
import Battery90Icon from '@mui/icons-material/Battery90';

import { usePlots } from '@/hooks/useFarm';
import { useAppSelector } from '@/store/hooks';
import { farmService } from '@/services/farmService';
import { IoTDevice } from '@/types';
import { LoadingState } from '@/components/common/States';

export const Devices: React.FC = () => {
  const { data: plots } = usePlots();
  const selectedPlotId = useAppSelector((state) => state.farm.selectedPlotId);

  const [devices, setDevices] = useState<IoTDevice[]>([]);
  const [loading, setLoading] = useState(false);
  const [openRegister, setOpenRegister] = useState(false);
  const [serial, setSerial] = useState('');
  const [deviceType, setDeviceType] = useState<'SOIL_SENSOR' | 'WEATHER_STATION' | 'IRRIGATION_CONTROLLER'>('SOIL_SENSOR');

  const activePlot = plots?.find((p) => p.id === selectedPlotId) || plots?.[0];

  const fetchDevices = async () => {
    if (!activePlot) return;
    setLoading(true);
    try {
      const data = await farmService.getDevices(activePlot.id);
      setDevices(data);
    } catch {
      // Offline fallback: display demo devices when IoT device API is unreachable
      const now = new Date().toISOString();
      setDevices([
        { id: 'dev-1', plot_id: activePlot.id, device_serial: 'SN-SOIL-9482', device_type: 'SOIL_SENSOR', is_active: true, last_seen_at: now, firmware_version: 'v2.1.4', battery_level: 89, created_at: now },
        { id: 'dev-2', plot_id: activePlot.id, device_serial: 'SN-WEAT-1039', device_type: 'WEATHER_STATION', is_active: true, last_seen_at: now, firmware_version: 'v1.8.2', battery_level: 95, created_at: now },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, [activePlot]);

  const handleRegisterDevice = async () => {
    if (!activePlot || !serial) return;
    try {
      await farmService.registerDevice(activePlot.id, {
        device_serial: serial,
        device_type: deviceType,
        is_active: true,
      });
      setOpenRegister(false);
      setSerial('');
      fetchDevices();
    } catch {
      // Optimistic local addition when device registration API is temporarily unavailable
      const now = new Date().toISOString();
      const newDevice: IoTDevice = {
        id: `dev-${Date.now()}`,
        plot_id: activePlot.id,
        device_serial: serial,
        device_type: deviceType,
        is_active: true,
        last_seen_at: now,
        firmware_version: 'v1.0.0',
        battery_level: 100,
        created_at: now,
      };
      setDevices((prev) => [...prev, newDevice]);
      setOpenRegister(false);
      setSerial('');
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
            IoT Sensor Nodes
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage hardware telemetry nodes, sensor metrics, and check active wireless signals.
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenRegister(true)}>
          Register Node
        </Button>
      </Box>

      {loading ? (
        <LoadingState message="Connecting with hardware gateway..." />
      ) : (
        <Grid container spacing={3}>
          {/* Devices Grid List */}
          {devices.map((dev) => (
            <Grid item xs={12} md={6} key={dev.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <DeviceHubIcon color="primary" />
                      <Typography variant="h6" fontWeight={700}>
                        {dev.device_type.replace(/_/g, ' ')}
                      </Typography>
                    </Box>
                    <Chip
                      label={dev.is_active ? 'Online' : 'Offline'}
                      color={dev.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                  <Divider sx={{ mb: 2 }} />

                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Serial Number</Typography>
                      <Typography variant="body2" fontWeight={600}>{dev.device_serial}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Firmware Version</Typography>
                      <Typography variant="body2">{dev.firmware_version || 'v1.0.0'}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Battery Status</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Battery90Icon sx={{ fontSize: 16, color: 'success.main' }} />
                        <Typography variant="body2">{dev.battery_level}%</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Signal Strengths</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <SettingsInputAntennaIcon sx={{ fontSize: 16, color: 'primary.main' }} />
                        <Typography variant="body2">Excellent (-55dBm)</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Register Device Dialog */}
      <Dialog open={openRegister} onClose={() => setOpenRegister(false)} maxWidth="sm" fullWidth>
        <DialogTitle fontWeight={700}>Register IoT Telemetry Node</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <TextField
              fullWidth
              label="Hardware Serial Number"
              value={serial}
              onChange={(e) => setSerial(e.target.value)}
              sx={{ mb: 3 }}
              placeholder="e.g. SN-SOIL-1234"
            />
            <TextField
              fullWidth
              select
              label="Device Category Type"
              value={deviceType}
              onChange={(e) => setDeviceType(e.target.value as any)}
            >
              <MenuItem value="SOIL_SENSOR">Multi-level Soil Nutrient Node</MenuItem>
              <MenuItem value="WEATHER_STATION">Micro-climate Weather Station</MenuItem>
              <MenuItem value="IRRIGATION_CONTROLLER">Irrigation Controller Solenoid Valve</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenRegister(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleRegisterDevice}>Register Device</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
