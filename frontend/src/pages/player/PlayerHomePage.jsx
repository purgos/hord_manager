import React, { useState, useEffect } from 'react';
import {
  Grid,
  Typography,
  Box,
  Alert,
} from '@mui/material';
import {
  AccountBalance,
  Business,
  Diamond,
  Refresh,
} from '@mui/icons-material';
import { LoadingSpinner, PageHeader, InfoCard } from '../../components/Common';
import { sessionService, healthService, metalService } from '../../services';

const PlayerHomePage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [metalPrices, setMetalPrices] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch session state
      const session = await sessionService.getState();
      setSessionData(session);

      // Fetch health status
      const health = await healthService.ping();
      setHealthStatus(health);

      // Fetch metal prices
      const metals = await metalService.getCurrentPrices(true, session.current_session);
      setMetalPrices(metals.prices.slice(0, 6)); // Show first 6 metals

    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    await fetchData();
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader 
        title="Player Dashboard" 
        subtitle={`Current Session: ${sessionData?.current_session || 'Unknown'}`}
        onRefresh={handleRefresh}
      />

      <Grid container spacing={3}>
        {/* Session Info */}
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Current Session"
            value={sessionData?.current_session || 'N/A'}
            subtitle="Game session number"
            icon={<AccountBalance />}
            color="primary"
          />
        </Grid>

        {/* System Status */}
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="System Status"
            value={healthStatus?.status || 'Unknown'}
            subtitle="API connection"
            icon={<Refresh />}
            color={healthStatus?.status === 'healthy' ? 'success' : 'error'}
          />
        </Grid>

        {/* Tracked Metals */}
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Tracked Metals"
            value={metalPrices.length}
            subtitle="Price monitoring active"
            icon={<Diamond />}
            color="secondary"
          />
        </Grid>

        {/* Player Stats Placeholder */}
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Your Businesses"
            value="0" // This could be dynamic based on player data
            subtitle="Active ventures"
            icon={<Business />}
            color="info"
          />
        </Grid>

        {/* Recent Metal Prices */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Current Metal Prices
          </Typography>
          <Grid container spacing={2}>
            {metalPrices.map((metal) => (
              <Grid item xs={12} sm={6} md={4} key={metal.metal_name}>
                <InfoCard
                  title={metal.metal_name}
                  value={`$${metal.price_per_unit_usd.toFixed(2)}`}
                  subtitle={`per ${metal.unit}`}
                  color="info"
                />
              </Grid>
            ))}
          </Grid>
        </Grid>

        {/* Welcome Message */}
        <Grid item xs={12}>
          <Box sx={{ 
            textAlign: 'center', 
            py: 4, 
            backgroundColor: 'background.paper', 
            borderRadius: 2,
            border: 1,
            borderColor: 'divider'
          }}>
            <Typography variant="h6" gutterBottom>
              Welcome to Your Adventure Hub!
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Track your treasure, manage businesses, and monitor the economy. 
              Use the navigation menu to access your portfolio and trading tools.
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PlayerHomePage;