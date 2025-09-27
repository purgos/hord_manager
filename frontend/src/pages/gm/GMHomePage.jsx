import React, { useState, useEffect } from 'react';
import {
  Grid,
  Typography,
  Box,
  Alert,
  Card,
  CardContent,
  CardActionArea,
  Paper,
  Container,
  Button
} from '@mui/material';
import {
  AccountBalance,
  Business,
  Diamond,
  Refresh,
  Settings as SettingsIcon,
  AttachMoney as CurrencyIcon,
  Diamond as GemstoneIcon,
  DeleteForever as ResetIcon,
  Inbox as InboxIcon,
  Build as MaterialsIcon,
  TrendingUp
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { LoadingSpinner, PageHeader, InfoCard } from '../../components/Common';
import { sessionService, healthService, metalService } from '../../services';

const GMHomePage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [metalPrices, setMetalPrices] = useState([]);
  const [updating, setUpdating] = useState(false);

  const gmQuickActions = [
    {
      title: 'Economic Settings',
      description: 'Configure rates, fees, and growth factors',
      icon: <SettingsIcon sx={{ fontSize: 32 }} />,
      path: '/gm/settings',
      color: 'secondary.main'
    },
    {
      title: 'Currency Management',
      description: 'Manage currencies and exchange rates',
      icon: <CurrencyIcon sx={{ fontSize: 32 }} />,
      path: '/gm/currencies',
      color: 'success.main'
    },
    {
      title: 'Gemstone Management',
      description: 'Edit gemstone values and pricing',
      icon: <GemstoneIcon sx={{ fontSize: 32 }} />,
      path: '/gm/gemstones',
      color: 'info.main'
    },
    {
      title: 'Materials Management',
      description: 'Configure metal and material price ranges',
      icon: <MaterialsIcon sx={{ fontSize: 32 }} />,
      path: '/gm/materials',
      color: 'primary.dark'
    },
    {
      title: 'GM Inbox',
      description: 'Review and respond to player requests',
      icon: <InboxIcon sx={{ fontSize: 32 }} />,
      path: '/gm/inbox',
      color: 'warning.main'
    },
    {
      title: 'Data Management',
      description: 'Reset or manage game data',
      icon: <ResetIcon sx={{ fontSize: 32 }} />,
      path: '/gm/data',
      color: 'error.main'
    }
  ];

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
      setMetalPrices(metals.prices.slice(0, 4)); // Show first 4 metals for GM view

    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleIncrementSession = async () => {
    setUpdating(true);
    try {
      const result = await sessionService.increment();
      setSessionData(result);
      // Refresh metal prices after session increment
      const metals = await metalService.getCurrentPrices(true, result.current_session);
      setMetalPrices(metals.prices.slice(0, 4));
    } catch (err) {
      setError('Failed to increment session');
    } finally {
      setUpdating(false);
    }
  };

  const handleQuickActionClick = (path) => {
    navigate(path);
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
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <PageHeader 
          title="Game Master Dashboard" 
          subtitle={`Current Session: ${sessionData?.current_session || 'Unknown'} | Manage your game world`}
          onRefresh={handleRefresh}
        />

        {/* Quick Session Control */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h6" gutterBottom>
                Session Control
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Current session: <strong>{sessionData?.current_session || 'Unknown'}</strong>
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                startIcon={<TrendingUp />}
                onClick={handleIncrementSession}
                disabled={updating}
                sx={{ height: 56 }}
              >
                {updating ? 'Incrementing...' : 'Increment Session'}
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* System Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <InfoCard
              title="Current Session"
              value={sessionData?.current_session || 'N/A'}
              subtitle="Game session number"
              icon={<AccountBalance />}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <InfoCard
              title="System Status"
              value={healthStatus?.status || 'Unknown'}
              subtitle="API connection"
              icon={<Refresh />}
              color={healthStatus?.status === 'healthy' ? 'success' : 'error'}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <InfoCard
              title="Tracked Metals"
              value={metalPrices.length}
              subtitle="Price monitoring active"
              icon={<Diamond />}
              color="secondary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <InfoCard
              title="Active Players"
              value="N/A" // This could be dynamic based on player data
              subtitle="Connected users"
              icon={<Business />}
              color="info"
            />
          </Grid>
        </Grid>

        {/* GM Quick Actions */}
        <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
          Game Management Tools
        </Typography>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {gmQuickActions.map((action) => (
            <Grid item xs={12} sm={6} md={4} key={action.title}>
              <Card 
                sx={{ 
                  height: '100%',
                  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                  }
                }}
              >
                <CardActionArea 
                  onClick={() => handleQuickActionClick(action.path)}
                  sx={{ height: '100%', p: 2 }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ color: action.color, mr: 2 }}>
                        {action.icon}
                      </Box>
                      <Typography variant="h6" component="h3">
                        {action.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {action.description}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Recent Metal Prices */}
        <Typography variant="h5" gutterBottom>
          Current Market Prices
        </Typography>
        <Grid container spacing={2}>
          {metalPrices.map((metal) => (
            <Grid item xs={12} sm={6} md={3} key={metal.metal_name}>
              <InfoCard
                title={metal.metal_name}
                value={`$${metal.price_per_unit_usd.toFixed(2)}`}
                subtitle={`per ${metal.unit}`}
                color="info"
              />
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default GMHomePage;