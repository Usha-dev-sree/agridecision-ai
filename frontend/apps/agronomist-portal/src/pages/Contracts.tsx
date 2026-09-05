import React from 'react';
import {
  Box, Card, Typography, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';

export const Contracts: React.FC = () => {
  const contracts = [
    { id: 'CTR-9081', buyer: 'AgriCorp Global Inc.', crop: 'Basmati Rice 1509', quantity: '50 MT', price: '₹4,200 / qtl', status: 'ACTIVE' },
    { id: 'CTR-8842', buyer: 'FreshOrganics Ltd.', crop: 'Organic Wheat', quantity: '30 MT', price: '₹3,100 / qtl', status: 'ACTIVE' },
    { id: 'CTR-7521', buyer: 'BioFeeds India', crop: 'Yellow Maize', quantity: '20 MT', price: '₹2,250 / qtl', status: 'COMPLETED' },
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} fontFamily="Outfit">
            Produce Off-Take Contracts
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Digitally signed corporate off-take agreements, price locks, and delivery schedules.
          </Typography>
        </Box>
        <Button variant="contained" color="primary" startIcon={<DescriptionIcon />}>
          New Contract
        </Button>
      </Box>

      <Card sx={{ borderRadius: 3, p: 2 }}>
        <Typography variant="h6" fontWeight={700} mb={2}>
          Contract Portfolio
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Contract ID</TableCell>
                <TableCell>Buyer / Enterprise</TableCell>
                <TableCell>Crop Type</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Locked Price</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {contracts.map((c) => (
                <TableRow key={c.id}>
                  <TableCell sx={{ fontWeight: 600 }}>{c.id}</TableCell>
                  <TableCell>{c.buyer}</TableCell>
                  <TableCell>{c.crop}</TableCell>
                  <TableCell>{c.quantity}</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>{c.price}</TableCell>
                  <TableCell>
                    <Chip label={c.status} color={c.status === 'ACTIVE' ? 'success' : 'default'} size="small" />
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
