import React from 'react';
import { Typography, Box, Paper, Grid, Button } from '@mui/material';
import { Diamond, Palette, HomeWork } from '@mui/icons-material';
import { PageHeader } from '../../components/Common';

const TreasurePage = () => {
  return (
    <Box>
      <PageHeader
        title="Treasure Horde"
        subtitle="Manage your valuable assets and collections"
      />

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Diamond sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Gemstones
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Track your gemstone collection with per-carat values and total worth calculations.
            </Typography>
            <Button variant="outlined" fullWidth>
              Manage Gemstones
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Palette sx={{ fontSize: 48, color: 'secondary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Art Collection
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Catalog artwork, request appraisals, and track the value of your art collection.
            </Typography>
            <Button variant="outlined" fullWidth>
              Manage Art
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <HomeWork sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Real Estate
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Track property values, rental income, and request property appraisals.
            </Typography>
            <Button variant="outlined" fullWidth>
              Manage Properties
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Coming Soon
        </Typography>
        <Typography variant="body1" color="text.secondary">
          The treasure management system is under development. You'll be able to:
        </Typography>
        <Box component="ul" sx={{ mt: 2 }}>
          <li>Add and categorize your valuable items</li>
          <li>Request appraisals from the GM</li>
          <li>Track value changes over time</li>
          <li>Calculate total treasure worth</li>
          <li>Export treasure inventories</li>
        </Box>
      </Paper>
    </Box>
  );
};

export default TreasurePage;