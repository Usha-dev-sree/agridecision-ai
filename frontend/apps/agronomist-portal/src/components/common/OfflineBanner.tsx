import React, { useState, useEffect } from 'react';
import { Box, Alert, Slide } from '@mui/material';
import WifiOffIcon from '@mui/icons-material/WifiOff';
import WifiIcon from '@mui/icons-material/Wifi';

export const OfflineBanner: React.FC = () => {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [showBackOnline, setShowBackOnline] = useState<boolean>(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowBackOnline(true);
      const timer = setTimeout(() => setShowBackOnline(false), 3000);
      return () => clearTimeout(timer);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowBackOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline && !showBackOnline) {
    return null;
  }

  return (
    <Slide direction="down" in={!isOnline || showBackOnline} mountOnEnter unmountOnExit>
      <Box
        role="status"
        aria-live="polite"
        aria-label={isOnline ? 'Network connection restored' : 'Offline mode active'}
        sx={{
          position: 'fixed',
          top: 64,
          left: 0,
          right: 0,
          zIndex: (theme) => theme.zIndex.snackbar,
          display: 'flex',
          justifyContent: 'center',
          px: 2,
          py: 0.5,
        }}
      >
        <Alert
          severity={isOnline ? 'success' : 'warning'}
          icon={isOnline ? <WifiIcon fontSize="small" /> : <WifiOffIcon fontSize="small" />}
          variant="filled"
          sx={{
            py: 0.25,
            px: 2,
            borderRadius: 2,
            fontSize: '0.8125rem',
            fontWeight: 600,
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          }}
        >
          {isOnline
            ? 'Connection restored. Syncing latest agricultural data...'
            : 'You are working offline. Changes will automatically synchronize when connectivity is restored.'}
        </Alert>
      </Box>
    </Slide>
  );
};
