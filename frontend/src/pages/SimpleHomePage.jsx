import React from 'react';
import { Typography, Box } from '@mui/material';

const SimpleHomePage = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Welcome to Hord Manager
      </Typography>
      <Typography variant="body1">
        This is a simplified version to test for errors.
      </Typography>
    </Box>
  );
};

export default SimpleHomePage;