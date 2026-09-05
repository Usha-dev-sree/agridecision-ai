import React from 'react';
import { Box, Card, Typography, Button, Chip, List, ListItem, ListItemText, ListItemIcon, Divider } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import StorefrontIcon from '@mui/icons-material/Storefront';

export const Notifications: React.FC = () => {
  const alerts = [
    { id: 1, type: 'WEATHER', title: 'Severe Rain & Hail Alert', desc: 'Heavy precipitation (>35mm) forecast for Green Acres North plot within 24 hours. Ensure adequate field drainage.', time: '10 mins ago', color: 'error' },
    { id: 2, type: 'MARKET', title: 'Basmati Rice Price Surge', desc: 'Mandi rates at Karnal increased by 4.2% to ₹3,890/qtl. Optimal selling window recommended.', time: '2 hours ago', color: 'success' },
    { id: 3, type: 'DISEASE', title: 'Pest Advisory: Aphids Spotted', desc: 'Satellite imagery and regional agronomist reports indicate early aphid infestation in nearby sector.', time: '5 hours ago', color: 'warning' },
  ];

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} fontFamily="Outfit">
            Real-Time Alert & Notification Hub
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Automated weather warnings, disease alerts, and market price notifications.
          </Typography>
        </Box>
        <Button variant="outlined">Mark All Read</Button>
      </Box>

      <Card sx={{ borderRadius: 3, p: 1 }}>
        <List>
          {alerts.map((a, i) => (
            <React.Fragment key={a.id}>
              <ListItem sx={{ py: 2 }}>
                <ListItemIcon sx={{ minWidth: 44 }}>
                  {a.type === 'WEATHER' ? <WbSunnyIcon color="error" /> : a.type === 'MARKET' ? <StorefrontIcon color="success" /> : <WarningAmberIcon color="warning" />}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Typography variant="subtitle1" fontWeight={700}>{a.title}</Typography>
                      <Chip label={a.type} size="small" color={a.color as any} />
                    </Box>
                  }
                  secondary={
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      {a.desc} • <Typography component="span" variant="caption" color="primary">{a.time}</Typography>
                    </Typography>
                  }
                />
              </ListItem>
              {i < alerts.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </Card>
    </Box>
  );
};
