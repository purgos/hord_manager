import React, { useState, useEffect } from 'react';
import {
  Grid,
  Button,
  Typography,
  Box,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  AccountBalance,
  Business,
  Diamond,
  Refresh,
} from '@mui/icons-material';
import { LoadingSpinner, PageHeader, InfoCard } from '../components/Common';
import { sessionService, healthService, metalService } from '../services';

const HomePage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [metalPrices, setMetalPrices] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch health status
      const health = await healthService.ping();
      setHealthStatus(health);

      // Fetch session data
      const session = await sessionService.getState();
      setSessionData(session);

      // Fetch recent metal prices
      const metals = await metalService.getCurrentPrices(true);
      setMetalPrices((metals && metals.prices) ? metals.prices.slice(0, 6) : []); // Show first 6 metals

    } catch (err) {
      setError(err);
      console.error('Failed to fetch dashboard data:', err);
      // Set fallback data to prevent crashes
      setHealthStatus({ status: 'error' });
      setSessionData({ current_session: 1 });
      setMetalPrices([]);
    } finally {
      setLoading(false);
    }
  };

  const handleIncrementSession = async () => {
    try {
      const result = await sessionService.incrementSession();
      setSessionData(result);
      // Refresh metal prices after session increment
      const metals = await metalService.getCurrentPrices(true);
      setMetalPrices(metals.prices.slice(0, 6));
    } catch (err) {
      setError(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;

  return (
    <Box>
      <PageHeader
        title="Hord Manager Dashboard"
        subtitle="Welcome to your treasure management system"
        action={
          <Button
            variant="contained"
            startIcon={<Refresh />}
            onClick={fetchData}
          >
            Refresh
          </Button>
        }
      />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Error: {error.message || 'Failed to load dashboard data'}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Session Info */}
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Current Session"
            value={sessionData?.current_session || 0}
            subtitle="Active game session"
            icon={<TrendingUp />}
            color="primary"
          />
        </Grid>

        {/* Health Status */}
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="System Status"
            value={healthStatus?.status === 'ok' ? 'Online' : 'Offline'}
            subtitle="Backend connectivity"
            icon={<AccountBalance />}
            color={healthStatus?.status === 'ok' ? 'success' : 'error'}
          />
        </Grid>

        {/* Total Metals */}
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Tracked Metals"
            value={metalPrices.length}
            subtitle="Price monitoring active"
            icon={<Diamond />}
            color="secondary"
          />
        </Grid>

        {/* Session Control */}
        <Grid item xs={12} sm={6} md={3}>
          <Box>
            <Button
              variant="outlined"
              fullWidth
              startIcon={<TrendingUp />}
              onClick={handleIncrementSession}
              sx={{ height: '100%' }}
            >
              Increment Session
            </Button>
          </Box>
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

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Diamond />}
                href="/treasure"
              >
                Treasure Horde
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<AccountBalance />}
                href="/banking"
              >
                Banking
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Business />}
                href="/business"
              >
                Business
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<TrendingUp />}
                href="/currencies"
              >
                Currencies
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HomePage;