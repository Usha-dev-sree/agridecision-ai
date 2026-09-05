import React from 'react';
import { Box, Card, Typography, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import DownloadIcon from '@mui/icons-material/Download';

export const Reports: React.FC = () => {
  const reports = [
    { id: 'REP-2026-07', title: 'Monthly Agronomic & Yield Telemetry Audit', date: '2026-07-28', format: 'PDF', size: '2.4 MB' },
    { id: 'REP-2026-06', title: 'Seasonal Soil & Nutrient Analysis Report', date: '2026-06-30', format: 'PDF', size: '1.8 MB' },
    { id: 'REP-2026-05', title: 'Climate & Irrigation Risk Assessment', date: '2026-05-31', format: 'PDF', size: '3.1 MB' },
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} fontFamily="Outfit">
            Analytics & Agronomic Reports
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Download verified agronomic performance metrics, soil health, and financial audits.
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<PictureAsPdfIcon />}>
          Generate Custom Report
        </Button>
      </Box>

      <Card sx={{ borderRadius: 3, p: 2 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Report ID</TableCell>
                <TableCell>Report Title</TableCell>
                <TableCell>Generated Date</TableCell>
                <TableCell>File Size</TableCell>
                <TableCell align="right">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reports.map((r) => (
                <TableRow key={r.id}>
                  <TableCell sx={{ fontWeight: 600 }}>{r.id}</TableCell>
                  <TableCell>{r.title}</TableCell>
                  <TableCell>{r.date}</TableCell>
                  <TableCell>{r.size}</TableCell>
                  <TableCell align="right">
                    <Button size="small" startIcon={<DownloadIcon />}>
                      Download
                    </Button>
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
