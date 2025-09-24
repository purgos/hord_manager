import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Typography,
  Box,
  Chip,
  Alert,
} from '@mui/material';
import { Refresh, TrendingUp } from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { LoadingSpinner, PageHeader } from '../components/Common';
import { metalService } from '../services';

const CurrenciesPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metalPrices, setMetalPrices] = useState([]);
  const [priceHistory, setPriceHistory] = useState([]);
  const [supportedMetals, setSupportedMetals] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch current prices
      const currentPrices = await metalService.getCurrentPrices(true);
      setMetalPrices(currentPrices.prices);

      // Fetch supported metals info
      const supported = await metalService.getSupportedMetals();
      setSupportedMetals(supported.metals);

      // Fetch price history for chart
      const history = await metalService.getPriceHistory();
      setPriceHistory(history.records || []);

    } catch (err) {
      setError(err);
      console.error('Failed to fetch currencies data:', err);
    } finally {
      setLoading(false);
    }
  };

  const triggerScraping = async () => {
    try {
      await metalService.triggerScraping(true);
      await fetchData(); // Refresh data after scraping
    } catch (err) {
      setError(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner />;

  // Prepare chart data
  const chartData = priceHistory
    .filter(record => ['Gold', 'Silver', 'Copper'].includes(record.metal_name))
    .reduce((acc, record) => {
      const existing = acc.find(item => item.session === record.session_number);
      if (existing) {
        existing[record.metal_name] = record.price_per_unit_usd;
      } else {
        acc.push({
          session: record.session_number,
          [record.metal_name]: record.price_per_unit_usd,
        });
      }
      return acc;
    }, [])
    .sort((a, b) => a.session - b.session);

  return (
    <Box>
      <PageHeader
        title="Currencies & Metal Prices"
        subtitle="Track metal prices and currency values"
        action={
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<TrendingUp />}
              onClick={triggerScraping}
            >
              Update Prices
            </Button>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={fetchData}
            >
              Refresh
            </Button>
          </Box>
        }
      />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Error: {error.message || 'Failed to load currencies data'}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Price Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Metal Price Trends
            </Typography>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="session" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [`$${value?.toFixed(2)}`, name]}
                    labelFormatter={(session) => `Session ${session}`}
                  />
                  <Line type="monotone" dataKey="Gold" stroke="#FFD700" strokeWidth={2} />
                  <Line type="monotone" dataKey="Silver" stroke="#C0C0C0" strokeWidth={2} />
                  <Line type="monotone" dataKey="Copper" stroke="#B87333" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Typography color="text.secondary">
                No historical data available
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Current Metal Prices */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Current Metal Prices
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Metal</TableCell>
                    <TableCell align="right">Price (USD)</TableCell>
                    <TableCell align="right">Unit</TableCell>
                    <TableCell align="right">Gold Ratio</TableCell>
                    <TableCell align="center">Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {metalPrices.map((metal) => (
                    <TableRow key={metal.metal_name}>
                      <TableCell component="th" scope="row">
                        <Typography variant="subtitle2">
                          {metal.metal_name}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        ${metal.price_per_unit_usd.toFixed(2)}
                      </TableCell>
                      <TableCell align="right">
                        {metal.unit}
                      </TableCell>
                      <TableCell align="right">
                        {metal.metal_name === 'Gold' ? '1.00' : 
                         (metal.price_per_unit_usd / metalPrices.find(m => m.metal_name === 'Gold')?.price_per_unit_usd || 1).toFixed(4)
                        }
                      </TableCell>
                      <TableCell align="center">
                        <Chip 
                          label="Active" 
                          color="success" 
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Supported Metals Info */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Supported Metals ({supportedMetals.length})
            </Typography>
            <Grid container spacing={2}>
              {supportedMetals.map((metal) => (
                <Grid item xs={12} sm={6} md={4} key={metal.name}>
                  <Box 
                    sx={{ 
                      border: 1, 
                      borderColor: 'grey.300', 
                      borderRadius: 1, 
                      p: 2 
                    }}
                  >
                    <Typography variant="subtitle1" gutterBottom>
                      {metal.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Unit: {metal.unit}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Range: ${metal.min_price_range} - ${metal.max_price_range}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CurrenciesPage;