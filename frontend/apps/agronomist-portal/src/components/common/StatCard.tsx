import React from 'react';
import { Card, CardContent, Box, Typography, Skeleton, alpha, useTheme } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  trend?: { value: number; label: string };
  loading?: boolean;
}

export const StatCard: React.FC<StatCardProps> = ({
  title, value, subtitle, icon, color = 'primary', trend, loading = false,
}) => {
  const theme = useTheme();
  const palette = theme.palette[color];

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={500} textTransform="uppercase" letterSpacing="0.06em">
              {title}
            </Typography>
            {loading ? (
              <Skeleton variant="text" width={80} height={40} />
            ) : (
              <Typography variant="h4" fontWeight={800} fontFamily="Outfit" color="text.primary" mt={0.5}>
                {value}
              </Typography>
            )}
            {subtitle && (
              <Typography variant="caption" color="text.secondary">{subtitle}</Typography>
            )}
          </Box>
          <Box
            sx={{
              width: 48, height: 48, borderRadius: 2,
              background: `linear-gradient(135deg, ${alpha(palette.main, 0.2)}, ${alpha(palette.main, 0.1)})`,
              border: `1px solid ${alpha(palette.main, 0.25)}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: palette.main,
            }}
          >
            {icon}
          </Box>
        </Box>

        {trend && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {trend.value >= 0 ? (
              <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main' }} />
            ) : (
              <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main' }} />
            )}
            <Typography
              variant="caption"
              color={trend.value >= 0 ? 'success.main' : 'error.main'}
              fontWeight={600}
            >
              {Math.abs(trend.value)}% {trend.label}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
