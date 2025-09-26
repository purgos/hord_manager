import React from 'react';
import { ThemeProvider, createTheme, CssBaseline, Typography, Box } from '@mui/material';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
});

function MaterialApp() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Hord Manager - Material-UI Test
        </Typography>
        <Typography variant="body1">
          Material-UI is working! Time: {new Date().toLocaleString()}
        </Typography>
      </Box>
    </ThemeProvider>
  );
}

export default MaterialApp;