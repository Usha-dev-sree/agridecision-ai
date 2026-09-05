import React from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';

export const EnterpriseDashboard: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} fontFamily="Outfit">
            Enterprise Agri-Corporation Portal
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Contract off-take monitoring, cluster yield aggregation, and supply chain telemetry.
          </Typography>
        </Box>
        <Button variant="contained" color="primary" startIcon={<ReceiptLongIcon />}>
          Export ESG Report
        </Button>
      </Box>

      {/* Enterprise KPI Summary */}
      <Grid container spacing={2.5}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Contracted Land</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1 }}>
                24,500 ha
              </Typography>
              <Typography variant="caption" color="success.main">
                12 Cluster Regions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Projected Season Procurement</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1, color: 'primary.main' }}>
                98,400 MT
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Confidence: 94.2% (ResNet & LSTM)
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Active Off-Take Contracts</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1 }}>
                184 Contracts
              </Typography>
              <Chip label="98.5% Fulfillment Rate" color="success" size="small" sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Carbon Offset (ESG)</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1, color: 'info.main' }}>
                14,200 tCO2e
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Verified Regenerative Soil Practices
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Regional Procurement Table */}
      <Card sx={{ borderRadius: 3, p: 2 }}>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Regional Off-Take & Yield Forecast Summary
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Region / Cluster</TableCell>
                <TableCell>Primary Crop</TableCell>
                <TableCell>Total Farmers</TableCell>
                <TableCell>Expected Yield (MT)</TableCell>
                <TableCell>Fulfillment Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {[
                { region: 'Punjab North-East', crop: 'Basmati Rice', farmers: 450, yield: '18,500', status: 'ON TRACK' },
                { region: 'Haryana Central', crop: 'Wheat (HD-3086)', farmers: 380, yield: '22,100', status: 'ON TRACK' },
                { region: 'Telangana South', crop: 'Cotton (Bt-II)', farmers: 620, yield: '14,800', status: 'ALERT (PEST)' },
                { region: 'Madhya Pradesh West', crop: 'Soybean (JS-335)', farmers: 510, yield: '26,400', status: 'ON TRACK' },
              ].map((row) => (
                <TableRow key={row.region}>
                  <TableCell sx={{ fontWeight: 600 }}>{row.region}</TableCell>
                  <TableCell>{row.crop}</TableCell>
                  <TableCell>{row.farmers}</TableCell>
                  <TableCell>{row.yield} MT</TableCell>
                  <TableCell>
                    <Chip
                      label={row.status}
                      color={row.status.includes('ALERT') ? 'warning' : 'success'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
};
