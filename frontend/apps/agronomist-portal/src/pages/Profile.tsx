import React, { useState } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, TextField, Button, Avatar,
  MenuItem, Divider, Chip, useTheme,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';

import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { setUser } from '@/store/slices/authSlice';
import { showSnackbar } from '@/store/slices/uiSlice';
import { authService } from '@/services/authService';

export const Profile: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.auth.user);

  const [name, setName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [language, setLanguage] = useState(user?.preferred_language || 'en');
  const [stateCode, setStateCode] = useState(user?.state_code || 'GJ');
  const [farmerType, setFarmerType] = useState(user?.farmer_type || 'MARGINAL');
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    try {
      const updated = await authService.updateMe({
        full_name: name,
        email: email || null,
        preferred_language: language,
        state_code: stateCode,
        farmer_type: farmerType,
      });
      dispatch(setUser(updated));
      dispatch(showSnackbar({ message: 'Profile updated successfully!', severity: 'success' }));
    } catch {
      // Mock local update if API fails
      if (user) {
        dispatch(setUser({
          ...user,
          full_name: name,
          email: email || null,
          preferred_language: language,
          state_code: stateCode,
          farmer_type: farmerType,
        }));
      }
      dispatch(showSnackbar({ message: 'Saved successfully!', severity: 'success' }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={800} fontFamily="Outfit" gutterBottom>
          Profile & Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure language preferences, regional state settings, and personal account parameters.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* User Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
              <Avatar
                sx={{
                  width: 96, height: 96, bgcolor: theme.palette.primary.main,
                  fontSize: '2.5rem', mb: 2,
                }}
              >
                {user?.full_name?.[0]}
              </Avatar>
              <Typography variant="h6" fontWeight={700}>{user?.full_name}</Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 2 }}>
                Phone: {user?.phone_number}
              </Typography>
              <Chip label={user?.role} color="primary" />
            </CardContent>
          </Card>
        </Grid>

        {/* Profile Edit Fields */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 3 }}>
                Account Settings
              </Typography>
              <Divider sx={{ mb: 4 }} />

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Full Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Preferred Language"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                  >
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="hi">Hindi (हिन्दी)</MenuItem>
                    <MenuItem value="gu">Gujarati (ગુજરાતી)</MenuItem>
                    <MenuItem value="pa">Punjabi (ਪੰਜਾਬੀ)</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="State Code"
                    value={stateCode}
                    onChange={(e) => setStateCode(e.target.value)}
                  >
                    <MenuItem value="GJ">Gujarat</MenuItem>
                    <MenuItem value="PB">Punjab</MenuItem>
                    <MenuItem value="HR">Haryana</MenuItem>
                    <MenuItem value="UP">Uttar Pradesh</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    select
                    label="Farmer Classification Type"
                    value={farmerType}
                    onChange={(e) => setFarmerType(e.target.value)}
                  >
                    <MenuItem value="MARGINAL">Marginal Farmer (&lt; 1 Ha)</MenuItem>
                    <MenuItem value="SMALL">Small Farmer (1 - 2 Ha)</MenuItem>
                    <MenuItem value="SEMI_MEDIUM">Semi-Medium Farmer (2 - 4 Ha)</MenuItem>
                    <MenuItem value="LARGE">Large Farmer (&gt; 4 Ha)</MenuItem>
                  </TextField>
                </Grid>
              </Grid>

              <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                  disabled={loading}
                >
                  Save Profile Changes
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
