import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import AgricultureIcon from '@mui/icons-material/Agriculture';

interface LoadingStateProps {
  message?: string;
  fullPage?: boolean;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ message = 'Loading…', fullPage = false }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 2,
      minHeight: fullPage ? '100vh' : 300,
    }}
  >
    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
      <CircularProgress size={56} color="primary" thickness={3} />
      <Box
        sx={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        <AgricultureIcon color="primary" sx={{ fontSize: 24 }} />
      </Box>
    </Box>
    <Typography color="text.secondary" variant="body2">{message}</Typography>
  </Box>
);

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, subtitle, action }) => (
  <Box
    sx={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', gap: 2, py: 8, textAlign: 'center',
    }}
  >
    {icon && (
      <Box sx={{ opacity: 0.35, fontSize: 64, color: 'primary.main' }}>
        {icon}
      </Box>
    )}
    <Typography variant="h6" fontWeight={600}>{title}</Typography>
    {subtitle && <Typography color="text.secondary" variant="body2" maxWidth={320}>{subtitle}</Typography>}
    {action}
  </Box>
);

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message = 'Something went wrong.',
  onRetry,
}) => (
  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, py: 8 }}>
    <Typography variant="h6" color="error">⚠ {message}</Typography>
    {onRetry && (
      <Typography
        variant="body2"
        color="primary"
        sx={{ cursor: 'pointer', textDecoration: 'underline' }}
        onClick={onRetry}
      >
        Retry
      </Typography>
    )}
  </Box>
);
