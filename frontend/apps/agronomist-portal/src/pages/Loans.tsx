import React, { useState } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Button, TextField, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

export const Loans: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [amount, setAmount] = useState('50000');
  const [purpose, setPurpose] = useState('Drip Irrigation Equipment');

  const loansList = [
    { id: 'LN-2026-001', amount: '₹75,000', purpose: 'Seeds & Fertilizer', tenure: '6 Months', status: 'DISBURSED', rate: '7.5%' },
    { id: 'LN-2026-002', amount: '₹1,20,000', purpose: 'Solar Pump Installation', tenure: '12 Months', status: 'UNDER REVIEW', rate: '6.8%' },
    { id: 'LN-2025-089', amount: '₹40,000', purpose: 'Crop Insurance Premium', tenure: '4 Months', status: 'PAID', rate: '7.0%' },
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} fontFamily="Outfit">
            Farmer Microloans & Credit Scoring
          </Typography>
          <Typography variant="body2" color="text.secondary">
            AI-driven credit assessment based on plot yield history, satellite health, and financial data.
          </Typography>
        </Box>
        <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => setOpen(true)}>
          Apply for Microloan
        </Button>
      </Box>

      {/* Credit Score & Overview Cards */}
      <Grid container spacing={2.5}>
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ borderRadius: 3, background: 'linear-gradient(135deg, #0d3b66 0%, #104f55 100%)', color: '#fff' }}>
            <CardContent>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>Agri AI Credit Score</Typography>
              <Typography variant="h3" fontWeight={800} sx={{ mt: 1 }}>
                784 <Typography component="span" variant="h6">/ 900</Typography>
              </Typography>
              <Chip label="Excellent Risk Profile" color="success" size="small" sx={{ mt: 1 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Active Microloan Credit Limit</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1 }}>
                ₹ 2,50,000
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Pre-approved based on 5 ha Green Acres plot
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              <Typography color="text.secondary" variant="body2">Total Outstanding Balance</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ mt: 1, color: 'warning.main' }}>
                ₹ 75,000
              </Typography>
              <Typography variant="caption" color="success.main">
                Next EMI due: 15 Aug 2026 (₹ 13,200)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Loans Table */}
      <Card sx={{ borderRadius: 3, p: 2 }}>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Application & Active Loan History
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Loan ID</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Purpose</TableCell>
                <TableCell>Interest Rate</TableCell>
                <TableCell>Tenure</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loansList.map((row) => (
                <TableRow key={row.id}>
                  <TableCell sx={{ fontWeight: 600 }}>{row.id}</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>{row.amount}</TableCell>
                  <TableCell>{row.purpose}</TableCell>
                  <TableCell>{row.rate}</TableCell>
                  <TableCell>{row.tenure}</TableCell>
                  <TableCell>
                    <Chip
                      label={row.status}
                      color={row.status === 'DISBURSED' ? 'success' : row.status === 'PAID' ? 'info' : 'warning'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Application Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle fontWeight={700}>Apply for Agri Microloan</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Loan Amount (₹)"
              fullWidth
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            <TextField
              label="Purpose"
              fullWidth
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
            />
            <Typography variant="caption" color="text.secondary">
              * Your application will be evaluated instantly using your AI farm performance telemetry and satellite imagery records.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpen(false)}>Submit Application</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
