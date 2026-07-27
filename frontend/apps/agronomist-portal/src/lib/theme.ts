import { createTheme, alpha } from '@mui/material/styles';

const agriGreen = {
  50: '#e8f5e9',
  100: '#c8e6c9',
  200: '#a5d6a7',
  300: '#81c784',
  400: '#66bb6a',
  500: '#2e7d32',
  600: '#256827',
  700: '#1b5e20',
  800: '#145214',
  900: '#0d3b0d',
};

const agriAmber = {
  50: '#fff8e1',
  100: '#ffecb3',
  200: '#ffe082',
  300: '#ffd54f',
  400: '#ffca28',
  500: '#ffa000',
  600: '#ff8f00',
  700: '#ff6f00',
};

export const createAppTheme = (mode: 'light' | 'dark') =>
  createTheme({
    palette: {
      mode,
      primary: {
        main: agriGreen[500],
        light: agriGreen[300],
        dark: agriGreen[700],
        contrastText: '#ffffff',
      },
      secondary: {
        main: agriAmber[500],
        light: agriAmber[300],
        dark: agriAmber[700],
        contrastText: '#000000',
      },
      background: {
        default: mode === 'dark' ? '#0a0f0d' : '#f4f6f4',
        paper: mode === 'dark' ? '#111b14' : '#ffffff',
      },
      error: { main: '#ef5350' },
      warning: { main: '#ff9800' },
      info: { main: '#29b6f6' },
      success: { main: '#66bb6a' },
      text: {
        primary: mode === 'dark' ? '#e8f5e9' : '#1b2e1c',
        secondary: mode === 'dark' ? '#a5d6a7' : '#4a7a4e',
      },
    },
    typography: {
      fontFamily: '"Inter", "Outfit", system-ui, sans-serif',
      h1: { fontFamily: '"Outfit", sans-serif', fontWeight: 800, letterSpacing: '-0.02em' },
      h2: { fontFamily: '"Outfit", sans-serif', fontWeight: 700, letterSpacing: '-0.01em' },
      h3: { fontFamily: '"Outfit", sans-serif', fontWeight: 600 },
      h4: { fontFamily: '"Outfit", sans-serif', fontWeight: 600 },
      h5: { fontFamily: '"Outfit", sans-serif', fontWeight: 600 },
      h6: { fontFamily: '"Outfit", sans-serif', fontWeight: 600 },
      button: { fontWeight: 600, letterSpacing: '0.02em' },
    },
    shape: { borderRadius: 12 },
    components: {
      MuiCard: {
        styleOverrides: {
          root: ({ theme }) => ({
            backgroundImage: 'none',
            border: `1px solid ${alpha(theme.palette.primary.main, mode === 'dark' ? 0.15 : 0.12)}`,
            backdropFilter: 'blur(12px)',
            transition: 'all 0.2s ease',
            '&:hover': {
              borderColor: alpha(theme.palette.primary.main, 0.4),
              transform: 'translateY(-1px)',
              boxShadow: `0 8px 30px ${alpha(theme.palette.primary.main, 0.15)}`,
            },
          }),
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: 10,
            padding: '10px 20px',
            fontWeight: 600,
          },
          containedPrimary: {
            background: `linear-gradient(135deg, ${agriGreen[500]}, ${agriGreen[700]})`,
            boxShadow: `0 4px 15px ${alpha(agriGreen[500], 0.4)}`,
            '&:hover': {
              boxShadow: `0 6px 20px ${alpha(agriGreen[500], 0.5)}`,
              transform: 'translateY(-1px)',
            },
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: ({ theme }) => ({
            '& .MuiOutlinedInput-root': {
              borderRadius: 10,
              '&.Mui-focused fieldset': {
                borderColor: theme.palette.primary.main,
                boxShadow: `0 0 0 3px ${alpha(theme.palette.primary.main, 0.15)}`,
              },
            },
          }),
        },
      },
      MuiChip: {
        styleOverrides: {
          root: { borderRadius: 8, fontWeight: 500 },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: ({ theme }) => ({
            backgroundImage: 'none',
            background: mode === 'dark'
              ? `linear-gradient(180deg, #0d1f10 0%, #111b14 100%)`
              : `linear-gradient(180deg, #e8f5e9 0%, #ffffff 100%)`,
            borderRight: `1px solid ${alpha(theme.palette.primary.main, 0.15)}`,
          }),
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: ({ theme }) => ({
            backgroundImage: 'none',
            background: mode === 'dark'
              ? alpha('#0a0f0d', 0.92)
              : alpha('#ffffff', 0.92),
            backdropFilter: 'blur(20px)',
            borderBottom: `1px solid ${alpha(theme.palette.primary.main, 0.12)}`,
            boxShadow: 'none',
          }),
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            margin: '2px 8px',
            '&.Mui-selected': {
              background: `linear-gradient(135deg, ${alpha(agriGreen[500], 0.2)}, ${alpha(agriGreen[700], 0.1)})`,
              borderLeft: `3px solid ${agriGreen[500]}`,
              '&:hover': { background: alpha(agriGreen[500], 0.25) },
            },
            '&:hover': { background: alpha(agriGreen[500], 0.08) },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: { backgroundImage: 'none' },
        },
      },
      MuiTableHead: {
        styleOverrides: {
          root: ({ theme }) => ({
            '& .MuiTableCell-head': {
              background: alpha(theme.palette.primary.main, 0.08),
              fontWeight: 700,
              fontSize: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            },
          }),
        },
      },
    },
  });
