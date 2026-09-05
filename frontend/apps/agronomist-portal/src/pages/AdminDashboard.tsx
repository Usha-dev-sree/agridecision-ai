import React from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

export const AdminDashboard: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} fontFamily="Outfit">
            Research & Operations Console
          </Typography>
          <Typography variant="body2" color="text.secondary">
            AI platform analytics, system health, research data exports, and security audit logs.
          </Typography>
        </Box>
        <Button variant="outlined" color="primary" startIcon={<SecurityIcon />}>
          Run Security Scan
        </Button>
      </Box>


      {/* System Metrics */}
      <Grid container spacing={2.5}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Active Microservices</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1, color: 'primary.main' }}>
                9 / 9
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                <CheckCircleOutlineIcon color="success" fontSize="small" />
                <Typography variant="caption" color="success.main">100% Healthy</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">AI Triton Gateway Latency</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1 }}>
                18.4 ms
              </Typography>
              <Typography variant="caption" color="text.secondary">
                99.9th percentile ONNX execution
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Registered Users</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1 }}>
                14,280
              </Typography>
              <Typography variant="caption" color="success.main">
                +450 new farmers this week
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Redis Cache Hit Ratio</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1, color: 'info.main' }}>
                98.6%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Feature store online layer
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Services Table */}
      <Card sx={{ borderRadius: 3, p: 2 }}>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Microservice Topology & Status
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Service Name</TableCell>
                <TableCell>Endpoint</TableCell>
                <TableCell>Uptime</TableCell>
                <TableCell>CPU / RAM</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {[
                { name: 'user_service', port: ':8001', uptime: '99.98%', resource: '12% / 180MB', status: 'HEALTHY' },
                { name: 'farm_service', port: ':8002', uptime: '99.99%', resource: '18% / 240MB', status: 'HEALTHY' },
                { name: 'advisory_service', port: ':8003', uptime: '99.95%', resource: '25% / 310MB', status: 'HEALTHY' },
                { name: 'ai_inference_gateway', port: ':8000', uptime: '99.99%', resource: '34% / 1.2GB', status: 'HEALTHY' },
                { name: 'financial_service', port: ':8004', uptime: '100.0%', resource: '8% / 150MB', status: 'HEALTHY' },
                { name: 'market_service', port: ':8005', uptime: '99.92%', resource: '14% / 190MB', status: 'HEALTHY' },
              ].map((row) => (
                <TableRow key={row.name}>
                  <TableCell sx={{ fontWeight: 600 }}>{row.name}</TableCell>
                  <TableCell>{row.port}</TableCell>
                  <TableCell>{row.uptime}</TableCell>
                  <TableCell>{row.resource}</TableCell>
                  <TableCell>
                    <Chip label={row.status} color="success" size="small" />
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
