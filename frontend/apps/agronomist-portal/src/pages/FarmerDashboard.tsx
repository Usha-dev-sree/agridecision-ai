import React from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper
} from '@mui/material';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import BugReportIcon from '@mui/icons-material/BugReport';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

export const FarmerDashboard: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Header banner */}
      <Box
        sx={{
          p: 3,
          borderRadius: 3,
          background: 'linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%)',
          color: '#fff',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Box>
          <Typography variant="h5" fontWeight={700} fontFamily="Outfit">
            Welcome back, Ramesh Farmer 👋
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
            Plot: Green Acres North • Season: Kharif 2026 • Soil pH: 6.8 (Optimal)
          </Typography>
        </Box>
        <Button variant="contained" color="secondary" startIcon={<BugReportIcon />}>
          New Scan
        </Button>
      </Box>

      {/* Quick Stat Cards */}
      <Grid container spacing={2.5}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography color="text.secondary" variant="body2">Current Crop</Typography>
                <AgricultureIcon color="primary" />
              </Box>
              <Typography variant="h6" fontWeight={700} sx={{ mt: 1 }}>
                Basmati Rice (R-202)
              </Typography>
              <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip size="small" label="Stage: Tillering" color="success" />
                <Typography variant="caption">45 days left</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography color="text.secondary" variant="body2">Weather Today</Typography>
                <WbSunnyIcon sx={{ color: '#ffb703' }} />
              </Box>
              <Typography variant="h6" fontWeight={700} sx={{ mt: 1 }}>
                29°C / 78% Hum.
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Rain predicted: 12mm tomorrow
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography color="text.secondary" variant="body2">Irrigation Recommendation</Typography>
                <WaterDropIcon color="info" />
              </Box>
              <Typography variant="h6" fontWeight={700} sx={{ mt: 1 }}>
                Irrigate Tomorrow
              </Typography>
              <Typography variant="caption" color="info.main">
                Volume: 25,000 L / ha
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography color="text.secondary" variant="body2">Estimated Yield</Typography>
                <TrendingUpIcon color="success" />
              </Box>
              <Typography variant="h6" fontWeight={700} sx={{ mt: 1 }}>
                4,850 kg / ha
              </Typography>
              <Typography variant="caption" color="success.main">
                +12% vs baseline average
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Advisory & Market Overview */}
      <Grid container spacing={2.5}>
        <Grid item xs={12} md={7}>
          <Card sx={{ borderRadius: 3, p: 2 }}>
            <Typography variant="h6" fontWeight={700} mb={2}>
              Recommended Farm Operations
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Paper sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <CheckCircleIcon color="success" />
                  <Box sx={{ flex: 1 }}>
                    <Typography fontWeight={600} variant="subtitle2">Nitrogen Top-Dressing</Typography>
                    <Typography variant="body2" color="text.secondary">Apply 45 kg/ha Urea before noon</Typography>
                  </Box>
                  <Chip label="High Priority" color="warning" size="small" />
                </Box>
              </Paper>
              <Paper sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <WarningAmberIcon color="warning" />
                  <Box sx={{ flex: 1 }}>
                    <Typography fontWeight={600} variant="subtitle2">Fungal Leaf Blight Watch</Typography>
                    <Typography variant="body2" color="text.secondary">High humidity condition detected. Monitor lower canopy.</Typography>
                  </Box>
                  <Chip label="Medium Priority" color="info" size="small" />
                </Box>
              </Paper>
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card sx={{ borderRadius: 3, p: 2 }}>
            <Typography variant="h6" fontWeight={700} mb={2}>
              Mandis & Market Rates
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Crop</TableCell>
                    <TableCell>Mandi</TableCell>
                    <TableCell align="right">Rate (₹/qtl)</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Paddy (Common)</TableCell>
                    <TableCell>Karnal</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>₹2,350</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Basmati 1509</TableCell>
                    <TableCell>Khanna</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>₹3,890</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Maize</TableCell>
                    <TableCell>Nizamabad</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>₹2,100</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
