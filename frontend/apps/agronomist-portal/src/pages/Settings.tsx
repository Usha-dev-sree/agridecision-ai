import React, { useState } from 'react';
import { Box, Card, Typography, Switch, FormControlLabel, Select, MenuItem, FormControl, Divider } from '@mui/material';

export const Settings: React.FC = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [language, setLanguage] = useState('en');
  const [highContrast, setHighContrast] = useState(false);
  const [offlineSync, setOfflineSync] = useState(true);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <Box>
        <Typography variant="h5" fontWeight={800} fontFamily="Outfit">
          Platform & Accessibility Settings
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Configure app layout, language localization, dark mode, and offline synchronization preferences.
        </Typography>
      </Box>

      <Card sx={{ borderRadius: 3, p: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="subtitle1" fontWeight={700}>Dark Mode Interface</Typography>
              <Typography variant="body2" color="text.secondary">Enable low-light high-contrast theme</Typography>
            </Box>
            <FormControlLabel
              control={<Switch checked={darkMode} onChange={(e) => setDarkMode(e.target.checked)} />}
              label={darkMode ? 'Enabled' : 'Disabled'}
            />
          </Box>

          <Divider />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="subtitle1" fontWeight={700}>Regional Language</Typography>
              <Typography variant="body2" color="text.secondary">Select default voice & interface language</Typography>
            </Box>
            <FormControl size="small" sx={{ minWidth: 160 }}>
              <Select value={language} onChange={(e) => setLanguage(e.target.value as string)}>
                <MenuItem value="en">English (US/IN)</MenuItem>
                <MenuItem value="hi">Hindi (हिन्दी)</MenuItem>
                <MenuItem value="pa">Punjabi (ਪੰਜਾਬੀ)</MenuItem>
                <MenuItem value="te">Telugu (తెలుగు)</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <Divider />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="subtitle1" fontWeight={700}>WCAG 2.1 Accessibility High Contrast</Typography>
              <Typography variant="body2" color="text.secondary">Enhanced visual outline and screen reader compatibility</Typography>
            </Box>
            <FormControlLabel
              control={<Switch checked={highContrast} onChange={(e) => setHighContrast(e.target.checked)} />}
              label={highContrast ? 'Active' : 'Inactive'}
            />
          </Box>

          <Divider />

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="subtitle1" fontWeight={700}>Background Offline Sync</Typography>
              <Typography variant="body2" color="text.secondary">Automatically sync offline field observations when connected to Wi-Fi/Cellular</Typography>
            </Box>
            <FormControlLabel
              control={<Switch checked={offlineSync} onChange={(e) => setOfflineSync(e.target.checked)} />}
              label={offlineSync ? 'Auto-Sync' : 'Manual'}
            />
          </Box>
        </Box>
      </Card>
    </Box>
  );
};
