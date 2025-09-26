import React from 'react';
import { Box, Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import Header from './Header';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
});

const Layout = ({ children, sessionNumber, user }) => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header sessionNumber={sessionNumber} user={user} />
        <Container maxWidth="lg" sx={{ flex: 1, py: 3 }}>
          {children}
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default Layout;