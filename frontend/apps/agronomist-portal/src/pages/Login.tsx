import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import {
  Box, Card, CardContent, Typography, TextField, Button,
  InputAdornment, IconButton, CircularProgress, alpha, useTheme,
  Tabs, Tab, MenuItem, Alert, Divider, Chip,
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import PhoneIcon from '@mui/icons-material/Phone';
import LockIcon from '@mui/icons-material/Lock';
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import BadgeIcon from '@mui/icons-material/Badge';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import LoginIcon from '@mui/icons-material/Login';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import { useLogin, useRegister } from '@/hooks/useAuth';

const loginSchema = zod.object({
  phone_number: zod.string().min(10, 'Phone number must be at least 10 digits'),
  password: zod.string().min(6, 'Password must be at least 6 characters'),
});

const registerSchema = zod.object({
  full_name: zod.string().min(2, 'Full name is required (at least 2 characters)'),
  phone_number: zod.string().min(10, 'Phone number must be at least 10 digits'),
  email: zod.string().email('Invalid email address').optional().or(zod.literal('')),
  password: zod.string().min(6, 'Password must be at least 6 characters'),
  role: zod.enum(['FARMER', 'AGRONOMIST', 'ENTERPRISE', 'RESEARCHER']),
  state_code: zod.string().min(2, 'State code is required (e.g., IN-MH)'),
});

type LoginFormValues = zod.infer<typeof loginSchema>;
type RegisterFormValues = zod.infer<typeof registerSchema>;

export const Login: React.FC = () => {
  const theme = useTheme();
  const [tab, setTab] = useState<0 | 1>(0);
  const [showPassword, setShowPassword] = useState(false);

  const loginMutation = useLogin();
  const registerMutation = useRegister();

  // Login Form
  const {
    register: registerLogin,
    handleSubmit: handleSubmitLogin,
    formState: { errors: loginErrors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      phone_number: '',
      password: '',
    },
  });

  // Register Form
  const {
    register: registerSignUp,
    handleSubmit: handleSubmitSignUp,
    formState: { errors: registerErrors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: '',
      phone_number: '',
      email: '',
      password: '',
      role: 'FARMER',
      state_code: 'IN-MH',
    },
  });

  const onLoginSubmit = (data: LoginFormValues) => {
    loginMutation.mutate(data);
  };

  const onRegisterSubmit = (data: RegisterFormValues) => {
    registerMutation.mutate(data);
  };

  const isPending = loginMutation.isPending || registerMutation.isPending;

  return (
    <Box
      sx={{
        minHeight: '100vh',
        width: '100vw',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        background: `linear-gradient(rgba(10, 25, 15, 0.85), rgba(5, 15, 10, 0.92)), url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1920&q=80') center/cover no-repeat fixed`,
        p: 2,
      }}
    >
      <Card
        sx={{
          maxWidth: 500,
          width: '100%',
          backdropFilter: 'blur(16px)',
          backgroundColor: theme.palette.mode === 'dark'
            ? 'rgba(15, 35, 20, 0.82)'
            : 'rgba(255, 255, 255, 0.92)',
          boxShadow: `0 20px 60px ${alpha(theme.palette.primary.main, 0.35)}, 0 0 40px ${alpha('#4caf50', 0.2)}`,
          border: `1px solid ${alpha(theme.palette.primary.main, 0.3)}`,
          borderRadius: 4,
          overflow: 'hidden',
        }}
      >
        <CardContent sx={{ p: { xs: 3, sm: 4 }, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {/* Logo & Header */}
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: 3,
              background: `linear-gradient(135deg, #2e7d32, #1b5e20)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: `0 8px 24px ${alpha('#2e7d32', 0.5)}`,
              mb: 2,
            }}
          >
            <AgricultureIcon sx={{ color: '#fff', fontSize: 40 }} />
          </Box>

          <Typography variant="h4" fontWeight={800} fontFamily="Outfit" align="center" gutterBottom sx={{ letterSpacing: -0.5 }}>
            AgriDecision AI
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2 }}>
            Agricultural Decision Support &amp; GIS Intelligence Ecosystem
          </Typography>

          <Chip
            icon={<VerifiedUserIcon sx={{ fontSize: 16 }} />}
            label="Authorized Logins Required"
            size="small"
            color="success"
            variant="outlined"
            sx={{ mb: 3, fontWeight: 600 }}
          />

          {/* Sign In vs Sign Up Tabs */}
          <Tabs
            value={tab}
            onChange={(_, val) => setTab(val)}
            variant="fullWidth"
            sx={{
              width: '100%',
              mb: 3,
              borderBottom: 1,
              borderColor: 'divider',
              '& .MuiTab-root': { fontWeight: 700, textTransform: 'none', fontSize: '1rem' },
            }}
          >
            <Tab icon={<LoginIcon sx={{ fontSize: 20 }} />} iconPosition="start" label="Sign In" />
            <Tab icon={<PersonAddIcon sx={{ fontSize: 20 }} />} iconPosition="start" label="Create Account" />
          </Tabs>

          {/* TAB 0: SIGN IN */}
          {tab === 0 && (
            <Box component="form" onSubmit={handleSubmitLogin(onLoginSubmit)} sx={{ width: '100%' }}>
              <TextField
                fullWidth
                label="Phone Number"
                variant="outlined"
                placeholder="+919876543210"
                error={!!loginErrors.phone_number}
                helperText={loginErrors.phone_number?.message}
                {...registerLogin('phone_number')}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PhoneIcon color="primary" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 3 }}
              />

              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                variant="outlined"
                error={!!loginErrors.password}
                helperText={loginErrors.password?.message}
                {...registerLogin('password')}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockIcon color="primary" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 3 }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={isPending}
                sx={{
                  py: 1.5,
                  borderRadius: 2.5,
                  fontWeight: 700,
                  fontSize: '1rem',
                  background: 'linear-gradient(135deg, #2e7d32, #1b5e20)',
                  boxShadow: '0 8px 20px rgba(46, 125, 50, 0.4)',
                }}
              >
                {loginMutation.isPending ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
              </Button>
            </Box>
          )}

          {/* TAB 1: CREATE ACCOUNT / SIGN UP */}
          {tab === 1 && (
            <Box component="form" onSubmit={handleSubmitSignUp(onRegisterSubmit)} sx={{ width: '100%' }}>
              <TextField
                fullWidth
                label="Full Name"
                variant="outlined"
                placeholder="Rajesh Kumar"
                error={!!registerErrors.full_name}
                helperText={registerErrors.full_name?.message}
                {...registerSignUp('full_name')}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonIcon color="primary" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="Phone Number"
                variant="outlined"
                placeholder="+919876543210"
                error={!!registerErrors.phone_number}
                helperText={registerErrors.phone_number?.message}
                {...registerSignUp('phone_number')}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PhoneIcon color="primary" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="Email Address (Optional)"
                variant="outlined"
                placeholder="farmer@agridecision.ai"
                error={!!registerErrors.email}
                helperText={registerErrors.email?.message}
                {...registerSignUp('email')}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailIcon color="primary" />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />

              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  fullWidth
                  select
                  label="Role"
                  defaultValue="FARMER"
                  error={!!registerErrors.role}
                  helperText={registerErrors.role?.message}
                  {...registerSignUp('role')}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <BadgeIcon color="primary" />
                      </InputAdornment>
                    ),
                  }}
                >
                  <MenuItem value="FARMER">Farmer / Cultivator</MenuItem>
                  <MenuItem value="AGRONOMIST">Agronomist Specialist</MenuItem>
                  <MenuItem value="ENTERPRISE">Enterprise / FPO Manager</MenuItem>
                  <MenuItem value="RESEARCHER">Agricultural Researcher</MenuItem>
                </TextField>

                <TextField
                  fullWidth
                  label="State Code"
                  placeholder="IN-MH"
                  defaultValue="IN-MH"
                  error={!!registerErrors.state_code}
                  helperText={registerErrors.state_code?.message}
                  {...registerSignUp('state_code')}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LocationOnIcon color="primary" />
                      </InputAdornment>
                    ),
                  }}
                />
              </Box>

              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                variant="outlined"
                error={!!registerErrors.password}
                helperText={registerErrors.password?.message}
                {...registerSignUp('password')}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockIcon color="primary" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 3 }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={isPending}
                sx={{
                  py: 1.5,
                  borderRadius: 2.5,
                  fontWeight: 700,
                  fontSize: '1rem',
                  background: 'linear-gradient(135deg, #388e3c, #1b5e20)',
                  boxShadow: '0 8px 20px rgba(56, 142, 60, 0.4)',
                }}
              >
                {registerMutation.isPending ? <CircularProgress size={24} color="inherit" /> : 'Create Authorized Account'}
              </Button>
            </Box>
          )}

          <Divider sx={{ width: '100%', my: 3 }} />

          <Alert severity="info" sx={{ width: '100%', borderRadius: 2 }}>
            Demo Admin Credentials: <strong>+919000000001</strong> / <strong>SecretPassword123</strong>
          </Alert>
        </CardContent>
      </Card>
    </Box>
  );
};
