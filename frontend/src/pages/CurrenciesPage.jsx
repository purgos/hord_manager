import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Chip
} from '@mui/material';
import { metalService, currencyService, gemstoneService } from '../services';

function CurrenciesPage() {
  const [pricesHistory, setPricesHistory] = useState([]);
  const [currencies, setCurrencies] = useState([]);
  const [gemstones, setGemstones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    console.log('CurrenciesPage mounted, loading data...');
    loadData();
  }, []);

  const loadData = async () => {
    try {
      console.log('Starting loadData...');
      setLoading(true);
      setError('');
      
      const [metalResponse, currencyResponse, gemstoneResponse] = await Promise.all([
        metalService.getCurrentPrices(),
        currencyService.getAllCurrencies(),
        gemstoneService.getCurrentPrices()
      ]);
      
      console.log('Metal API response:', metalResponse);
      console.log('Currency API response:', currencyResponse);
      console.log('Gemstone API response:', gemstoneResponse);
      
      const pricesData = metalResponse.prices || [];
      const currencyData = currencyResponse || [];
      const gemstoneData = gemstoneResponse.prices || [];
      
      console.log('Prices data:', pricesData);
      console.log('Currency data:', currencyData);
      console.log('Gemstone data:', gemstoneData);
      
      // Transform the data to match expected format and calculate gold equivalent
      const goldPrice = pricesData.find(p => p.metal_name === 'Gold')?.price_per_unit_usd || 1880.33;
      console.log('Gold price:', goldPrice);
      
      const transformedData = pricesData.map(price => ({
        metal: price.metal_name,
        unit: price.unit,
        price_usd: price.price_per_unit_usd,
        price_gold: price.metal_name === 'Gold' ? 1 : price.price_per_unit_usd / goldPrice
      }));

      const transformedGemstones = gemstoneData.map(gemstone => ({
        name: gemstone.gemstone_name,
        unit: gemstone.unit,
        price_usd: gemstone.price_per_unit_usd,
        price_gold: gemstone.price_per_unit_usd / goldPrice
      }));
      
      console.log('Transformed data:', transformedData);
      console.log('Transformed gemstones:', transformedGemstones);
      setPricesHistory(transformedData);
      setCurrencies(currencyData);
      setGemstones(transformedGemstones);
    } catch (err) {
      console.error('Error loading data:', err);
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  console.log('Render - loading:', loading, 'error:', error, 'pricesHistory.length:', pricesHistory.length, 'currencies.length:', currencies.length, 'gemstones.length:', gemstones.length);

  if (loading) {
    console.log('Rendering loading state');
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Currencies & Metals
        </Typography>
        <Typography>Loading metal prices and currencies...</Typography>
      </Box>
    );
  }

  if (error) {
    console.log('Rendering error state:', error);
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Currencies & Metals
        </Typography>
        <Alert severity="error">
          {error}
        </Alert>
        <Typography>Debug info: pricesHistory={pricesHistory.length}, currencies={currencies.length}, gemstones={gemstones.length}</Typography>
      </Box>
    );
  }

  console.log('Rendering main component');

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Currencies & Metals
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        {/* Currencies Section - Now First */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Currencies (1 currency)
              </Typography>
              
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Currency</TableCell>
                      <TableCell align="right">Gold Equivalent (oz)</TableCell>
                      <TableCell>Denominations</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {/* Add USD Dollar as first row */}
                    <TableRow>
                      <TableCell>
                        <Chip 
                          label="USD Dollar" 
                          size="small" 
                          color="primary"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'gold' }}>
                          {(() => {
                            const goldPrice = pricesHistory.find(p => p.metal === 'Gold')?.price_usd || 1880.33;
                            return (1 / goldPrice).toFixed(6);
                          })()} oz gold
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          Base currency
                        </Typography>
                      </TableCell>
                    </TableRow>

                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Metal Prices Section - Now Second */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Metal Prices in Gold Equivalent ({pricesHistory.length} metals)
                </Typography>
              </Box>
              
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Metal</TableCell>
                      <TableCell>Unit</TableCell>
                      <TableCell align="right">Gold Equivalent (oz)</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pricesHistory.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={3} align="center">
                          <Typography color="text.secondary">
                            No metal price data available
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      pricesHistory.map((price, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Chip 
                              label={price.metal} 
                              size="small" 
                              color={price.metal === 'Gold' ? 'warning' : 'default'}
                            />
                          </TableCell>
                          <TableCell>{price.unit}</TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'gold' }}>
                              {price.price_gold.toFixed(6)} oz gold
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Gemstone Prices Section */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Gemstone Prices in Gold Equivalent ({gemstones.length} gemstones)
                </Typography>
              </Box>
              
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Gemstone</TableCell>
                      <TableCell>Unit</TableCell>
                      <TableCell align="right">Gold Equivalent (oz)</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {gemstones.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={3} align="center">
                          <Typography color="text.secondary">
                            No gemstone price data available
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      gemstones.map((gemstone, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Chip 
                              label={gemstone.name} 
                              size="small" 
                              color="secondary"
                            />
                          </TableCell>
                          <TableCell>{gemstone.unit}</TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'gold' }}>
                              {gemstone.price_gold.toFixed(6)} oz gold
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default CurrenciesPage;
