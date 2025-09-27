import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Alert,
  CircularProgress,
  Container,
  Breadcrumbs,
  Link,
  Fab,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  AttachMoney as CurrencyIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { currencyService, metalService, sessionService, materialService } from '../../services';

const calculateCurrencyValuations = (currencies, goldPriceUSD, metalPriceMap, materialPriceMap) => {
  if (!Array.isArray(currencies) || currencies.length === 0) {
    return {};
  }

  const normalizedGoldPrice = Number(goldPriceUSD) || 0;
  const currencyByName = new Map();
  const currencyByUpperName = new Map();
  currencies.forEach((currency) => {
    if (currency?.name) {
      currencyByName.set(currency.name, currency);
      currencyByUpperName.set(currency.name.toUpperCase(), currency);
    }
  });

  const memo = new Map();

  const computeGold = (currency, stack) => {
    if (!currency?.name) {
      return null;
    }

    if (memo.has(currency.name)) {
      return memo.get(currency.name);
    }

    if (stack.has(currency.name)) {
      return null;
    }

    stack.add(currency.name);

    const pegType = (currency.peg_type || 'CURRENCY').toUpperCase();
    const pegTarget = (currency.peg_target || '').toString();
    const pegTargetUpper = pegTarget.toUpperCase();
    const baseValue = Number(currency.base_unit_value ?? 0);
    let result = null;

    if (Number.isNaN(baseValue) || baseValue < 0) {
      result = null;
    } else if (pegType === 'METAL') {
      if (pegTargetUpper === 'GOLD') {
        result = baseValue;
      } else {
        const priceEntry = metalPriceMap[pegTargetUpper];
        if (priceEntry) {
          if (priceEntry.price_per_oz_gold && priceEntry.price_per_oz_gold > 0) {
            result = baseValue * priceEntry.price_per_oz_gold;
          } else if (priceEntry.price_per_unit_usd && normalizedGoldPrice > 0) {
            result = (baseValue * priceEntry.price_per_unit_usd) / normalizedGoldPrice;
          }
        }
      }
    } else if (pegType === 'MATERIAL') {
      const priceEntry = materialPriceMap[pegTargetUpper];
      if (priceEntry) {
        if (priceEntry.price_per_oz_gold && priceEntry.price_per_oz_gold > 0) {
          result = baseValue * priceEntry.price_per_oz_gold;
        } else if (priceEntry.price_per_unit_usd && normalizedGoldPrice > 0) {
          result = (baseValue * priceEntry.price_per_unit_usd) / normalizedGoldPrice;
        }
      }
    } else {
      if (pegTargetUpper === 'USD') {
        if (normalizedGoldPrice > 0) {
          result = baseValue / normalizedGoldPrice;
        }
      } else if (pegTargetUpper === 'GOLD') {
        result = baseValue;
      } else if (pegTarget) {
  const targetCurrency = currencyByName.get(pegTarget) || currencyByUpperName.get(pegTargetUpper);
        if (targetCurrency) {
          const nested = computeGold(targetCurrency, stack);
          if (nested != null) {
            result = baseValue * nested;
          }
        }
      }
    }

    if (result == null && currency.base_unit_value_oz_gold != null) {
      const fallback = Number(currency.base_unit_value_oz_gold);
      if (!Number.isNaN(fallback)) {
        result = fallback;
      }
    }

    stack.delete(currency.name);
    memo.set(currency.name, result);
    return result;
  };

  const valuations = {};
  currencies.forEach((currency) => {
    const gold = computeGold(currency, new Set());
    const usd = gold != null && normalizedGoldPrice > 0 ? gold * normalizedGoldPrice : null;
    valuations[currency.id] = {
      gold,
      usd,
    };
  });

  return valuations;
};

function GMCurrencies() {
  const navigate = useNavigate();
  const [currencies, setCurrencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCurrency, setEditingCurrency] = useState(null);
  const [message, setMessage] = useState('');
  const [goldPriceUSD, setGoldPriceUSD] = useState(2000); // Default fallback
  const [metals, setMetals] = useState([]);
  const [metalPriceMap, setMetalPriceMap] = useState({});
  const [materials, setMaterials] = useState([]);
  const [materialPriceMap, setMaterialPriceMap] = useState({});
  const [currencyValuations, setCurrencyValuations] = useState({});
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteSubmitting, setDeleteSubmitting] = useState(false);
  
  // Form state
  const [currencyForm, setCurrencyForm] = useState({
    name: '',
    peg_type: 'CURRENCY',
    peg_target: 'USD',
    base_unit_value: 1.0,
    denominations: []
  });

  const loadCurrencies = useCallback(async () => {
    try {
      // Get current session for metal prices
      const session = await sessionService.getState();
      const currentSession = session.current_session;

      const fetchMetalPrices = async () => {
        try {
          return await metalService.getCurrentPrices(false, currentSession);
        } catch (error) {
          if (error?.response?.status === 404) {
            await metalService.triggerScraping(true);
            return await metalService.getCurrentPrices(false, currentSession);
          }
          throw error;
        }
      };

      const fetchMaterialPrices = async () => {
        try {
          return await materialService.getCurrentPrices(currentSession, false);
        } catch (error) {
          if (error?.response?.status === 404) {
            await materialService.triggerUpdate(currentSession, true);
            return await materialService.getCurrentPrices(currentSession, false);
          }
          throw error;
        }
      };

      // Load currencies, pricing, and reference data in parallel
      const [
        currencyData,
        metalPrices,
        supportedMetals,
        availableMaterials,
        materialPrices
      ] = await Promise.all([
        currencyService.getAllCurrencies(),
        fetchMetalPrices(),
        metalService.getSupportedMetals(),
        materialService.getAvailableMaterials(),
        fetchMaterialPrices()
      ]);

      const metalPriceList = Array.isArray(metalPrices?.prices) ? metalPrices.prices : [];
      const materialPriceList = Array.isArray(materialPrices?.prices) ? materialPrices.prices : [];

      const metalMap = metalPriceList.reduce((acc, entry) => {
        if (entry?.metal_name) {
          acc[entry.metal_name.toUpperCase()] = entry;
        }
        return acc;
      }, {});

      const materialMap = materialPriceList.reduce((acc, entry) => {
        if (entry?.material_name) {
          acc[entry.material_name.toUpperCase()] = entry;
        }
        return acc;
      }, {});

      const supportedMetalNames = supportedMetals?.metals?.map((metal) => metal.name) || [];
      const priceMetalNames = metalPriceList.map((entry) => entry.metal_name).filter(Boolean);
      const combinedMetalNames = Array.from(new Set([...supportedMetalNames, ...priceMetalNames]));

      const availableMaterialNames = availableMaterials?.materials?.map((material) => material.name) || [];
      const priceMaterialNames = materialPriceList.map((entry) => entry.material_name).filter(Boolean);
      const combinedMaterialNames = Array.from(new Set([...availableMaterialNames, ...priceMaterialNames]));

      setCurrencies(currencyData);
      setMetals(combinedMetalNames);
      setMaterials(combinedMaterialNames);
      setMetalPriceMap(metalMap);
      setMaterialPriceMap(materialMap);

      const goldPriceEntry = metalPriceList.find((price) => price.metal_name === 'Gold');
      if (goldPriceEntry?.price_per_unit_usd) {
        const updatedGoldPrice = goldPriceEntry.price_per_unit_usd;
        if (updatedGoldPrice !== goldPriceUSD) {
          setGoldPriceUSD(updatedGoldPrice);
        }
      }

    } catch (error) {
      console.error('Failed to load currencies:', error);
      setMessage('Failed to load currencies');
    } finally {
      setLoading(false);
    }
  }, [goldPriceUSD]);

  useEffect(() => {
    loadCurrencies();
  }, [loadCurrencies]);

  useEffect(() => {
    if (loading) {
      return;
    }

    setCurrencyValuations(
      calculateCurrencyValuations(currencies, goldPriceUSD, metalPriceMap, materialPriceMap)
    );
  }, [currencies, goldPriceUSD, metalPriceMap, materialPriceMap, loading]);

  const getPegTargetOptions = useCallback((type) => {
    const normalizedType = (type || 'CURRENCY').toUpperCase();
    if (normalizedType === 'METAL') {
      return metals;
    }
    if (normalizedType === 'MATERIAL') {
      return materials;
    }
    return currencies.map((currency) => currency.name);
  }, [currencies, metals, materials]);

  const ensureValidPegTarget = useCallback((type, target) => {
    const options = getPegTargetOptions(type);
    if (!options || options.length === 0) {
      return '';
    }
    if (target && options.includes(target)) {
      return target;
    }
    return options[0];
  }, [getPegTargetOptions]);

  const handlePegTypeChange = (event) => {
    const selectedType = (event.target.value || 'CURRENCY').toUpperCase();
    setCurrencyForm((prev) => ({
      ...prev,
      peg_type: selectedType,
      peg_target: ensureValidPegTarget(selectedType, prev.peg_target)
    }));
  };

  const handlePegTargetChange = (event) => {
    const value = event.target.value;
    setCurrencyForm((prev) => ({
      ...prev,
      peg_target: value
    }));
  };

  useEffect(() => {
    setCurrencyForm((prev) => {
      const nextTarget = ensureValidPegTarget(prev.peg_type, prev.peg_target);
      if (nextTarget === prev.peg_target) {
        return prev;
      }
      return {
        ...prev,
        peg_target: nextTarget
      };
    });
  }, [currencies, metals, materials, ensureValidPegTarget]);

  const handleOpenDialog = (currency = null) => {
    if (currency) {
      setEditingCurrency(currency);
      setCurrencyForm({
        name: currency.name,
        peg_type: (currency.peg_type || 'CURRENCY').toUpperCase(),
        peg_target: ensureValidPegTarget((currency.peg_type || 'CURRENCY').toUpperCase(), currency.peg_target || ''),
        base_unit_value: currency.base_unit_value ?? 1.0,
        denominations: (currency.denominations || []).map((denom) => ({ ...denom }))
      });
    } else {
      setEditingCurrency(null);
      setCurrencyForm({
        name: '',
        peg_type: 'CURRENCY',
        peg_target: ensureValidPegTarget('CURRENCY', 'USD'),
        base_unit_value: 1.0,
        denominations: []
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingCurrency(null);
    setCurrencyForm({
      name: '',
      peg_type: 'CURRENCY',
      peg_target: ensureValidPegTarget('CURRENCY', 'USD'),
      base_unit_value: 1.0,
      denominations: []
    });
  };

  const handleSaveCurrency = async () => {
    const normalizedPegType = (currencyForm.peg_type || 'CURRENCY').toUpperCase();
    const payloadPegTarget = ensureValidPegTarget(normalizedPegType, currencyForm.peg_target);
    const baseUnitValue = Number(currencyForm.base_unit_value);
    const trimmedName = currencyForm.name?.trim() || '';
    const sanitizeDenomination = (denom) => ({
      name: denom.name?.trim() || '',
      value_in_base_units: Number(denom.value_in_base_units)
    });
    const denominationsForUpdate = currencyForm.denominations.map((denom) => {
      const sanitized = sanitizeDenomination(denom);
      return denom.id ? { id: denom.id, ...sanitized } : sanitized;
    });
    const denominationsForCreate = currencyForm.denominations.map((denom) => sanitizeDenomination(denom));

    try {
      if (editingCurrency) {
        // Update existing currency
        await currencyService.updateCurrency(editingCurrency.id, {
          peg_type: normalizedPegType,
          peg_target: payloadPegTarget,
          base_unit_value: baseUnitValue,
          denominations_add_or_update: denominationsForUpdate
        });
        setMessage('Currency updated successfully!');
      } else {
        // Create new currency
        await currencyService.createCurrency({
          name: trimmedName,
          peg_type: normalizedPegType,
          peg_target: payloadPegTarget,
          base_unit_value: baseUnitValue,
          denominations: denominationsForCreate
        });
        setMessage('Currency created successfully!');
      }
      
      await loadCurrencies();
      handleCloseDialog();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Failed to save currency:', error);
      const detail = error?.response?.data?.detail;
      setMessage(detail ? `Failed to save currency: ${detail}` : 'Failed to save currency');
    }
  };

  const requestDeleteCurrency = (currencyId, currencyName) => {
    const targetId = Number(currencyId);
    const originalName = (currencyName ?? '').trim();
    const normalizedName = originalName.toUpperCase();

    if (Number.isNaN(targetId)) {
      setMessage('Invalid currency reference. Please refresh and try again.');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    if (normalizedName === 'USD') {
      setMessage('USD is the base currency and cannot be deleted.');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    setDeleteTarget({ id: targetId, name: originalName || currencyName || 'Unnamed Currency' });
  };

  const cancelDeleteCurrency = () => {
    if (deleteSubmitting) {
      return;
    }
    setDeleteTarget(null);
  };

  const handleDeleteCurrency = async () => {
    if (!deleteTarget) {
      return;
    }

    const { id: targetId, name } = deleteTarget;

    if (Number.isNaN(targetId)) {
      setMessage('Invalid currency reference. Please refresh and try again.');
      setTimeout(() => setMessage(''), 3000);
      setDeleteTarget(null);
      return;
    }

    if ((name || '').toUpperCase() === 'USD') {
      setMessage('USD is the base currency and cannot be deleted.');
      setTimeout(() => setMessage(''), 3000);
      setDeleteTarget(null);
      return;
    }

    setDeleteSubmitting(true);

    try {
      await currencyService.deleteCurrency(targetId);
      setCurrencies((prev) => prev.filter((item) => Number(item.id) !== targetId));
      await loadCurrencies();
      setMessage(`Currency "${name || 'Unnamed Currency'}" deleted successfully!`);
      setTimeout(() => setMessage(''), 3000);
      setDeleteTarget(null);
    } catch (error) {
      console.error('Failed to delete currency:', error);
      if (error?.response?.status === 405) {
        setMessage('Currency deletion is not supported by the server yet.');
        setTimeout(() => setMessage(''), 3000);
      } else {
        const detail = error?.response?.data?.detail;
        setMessage(detail ? `Failed to delete currency: ${detail}` : 'Failed to delete currency');
        setTimeout(() => setMessage(''), 3000);
      }
    } finally {
      setDeleteSubmitting(false);
    }
  };

  const handleAddDenomination = () => {
    setCurrencyForm(prev => ({
      ...prev,
      denominations: [
        ...prev.denominations,
        { name: '', value_in_base_units: 1 }
      ]
    }));
  };

  const handleDenominationChange = (index, field, value) => {
    setCurrencyForm(prev => ({
      ...prev,
      denominations: prev.denominations.map((denom, i) => 
        i === index ? { ...denom, [field]: value } : denom
      )
    }));
  };

  const handleRemoveDenomination = (index) => {
    setCurrencyForm(prev => ({
      ...prev,
      denominations: prev.denominations.filter((_, i) => i !== index)
    }));
  };

  const normalizedPegType = (currencyForm.peg_type || 'CURRENCY').toUpperCase();
  const pegTargetOptions = getPegTargetOptions(normalizedPegType);
  const hasPegTargets = pegTargetOptions.length > 0;
  const effectivePegTarget = currencyForm.peg_target || (hasPegTargets ? pegTargetOptions[0] : '');
  const parsedBaseUnitValue = Number(currencyForm.base_unit_value);
  const isSaveDisabled =
    !currencyForm.name?.trim() ||
    !effectivePegTarget ||
    !hasPegTargets ||
    Number.isNaN(parsedBaseUnitValue) ||
    parsedBaseUnitValue <= 0;

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Breadcrumb Navigation */}
        <Breadcrumbs sx={{ mb: 3 }}>
          <Link 
            color="inherit" 
            onClick={() => navigate('/gm')}
            sx={{ cursor: 'pointer' }}
          >
            GM Dashboard
          </Link>
          <Typography color="text.primary">Currency Management</Typography>
        </Breadcrumbs>

        {/* Page Header */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', md: 'row' },
              alignItems: { xs: 'flex-start', md: 'center' },
              gap: 2
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CurrencyIcon sx={{ fontSize: 48, color: 'success.main' }} />
              <Box>
                <Typography variant="h3" component="h1">
                  Currency Management
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                  Manage game currencies, denominations, and exchange rates
                </Typography>
              </Box>
            </Box>
          </Box>
        </Paper>

        {/* Alerts */}
        {message && (
          <Alert 
            severity={message.includes('successfully') ? 'success' : 'error'} 
            sx={{ mb: 3 }}
          >
            {message}
          </Alert>
        )}

        {/* Currencies Table */}
        <Paper sx={{ mb: 3 }}>
          <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6" gutterBottom>
              All Currencies & Exchange Rates
            </Typography>
            <Typography variant="body2" color="text.secondary">
              All currencies support flexible pegging to USD, other currencies, metals, or materials
            </Typography>
          </Box>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Currency</strong></TableCell>
                  <TableCell align="right"><strong>Peg Type & Target</strong></TableCell>
                  <TableCell align="right"><strong>Peg Value</strong></TableCell>
                  <TableCell align="right"><strong>USD Equivalent</strong></TableCell>
                  <TableCell align="right"><strong>Gold Equivalent (oz)</strong></TableCell>
                  <TableCell><strong>Denominations</strong></TableCell>
                  <TableCell align="center"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {/* Gold Row (Base Currency) */}
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body1" fontWeight="bold">
                        🥇 Gold (oz)
                      </Typography>
                      <Chip 
                        label="BASE" 
                        size="small" 
                        color="primary" 
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      METAL → Gold
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      (Base metal)
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      1.000 oz
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="success.main">
                      ${goldPriceUSD.toFixed(2)} USD
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="warning.main">
                      1.000000 oz
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      (1 oz Gold)
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      Base unit (no denominations)
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body2" color="text.secondary">
                      -
                    </Typography>
                  </TableCell>
                </TableRow>

                {/* Other Currencies */}
                {currencies.map((currency) => {
                  const hasGoldPrice = goldPriceUSD > 0;

                  const valuation = currencyValuations[currency.id] || {};
                  const computedGold = valuation.gold;
                  const computedUsd = valuation.usd;

                  const rawFallbackGold = currency.base_unit_value_oz_gold;
                  const numericFallbackGold = typeof rawFallbackGold === 'number'
                    ? rawFallbackGold
                    : Number(rawFallbackGold);
                  const fallbackGoldValue = Number.isFinite(numericFallbackGold) ? numericFallbackGold : null;

                  const goldValue = Number.isFinite(computedGold)
                    ? computedGold
                    : fallbackGoldValue;

                  const usdValue = Number.isFinite(computedUsd)
                    ? computedUsd
                    : (goldValue != null && hasGoldPrice ? goldValue * goldPriceUSD : null);

                  const hasGoldValue = typeof goldValue === 'number' && Number.isFinite(goldValue);
                  const hasUsdValue = typeof usdValue === 'number' && Number.isFinite(usdValue);
                  const isUsdCurrency = (currency.name || '').toUpperCase() === 'USD';

                  return (
                    <TableRow key={currency.id}>
                      <TableCell>
                        <Typography variant="body1" fontWeight="medium">
                          {currency.name}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          {currency.peg_type || 'CURRENCY'} → {currency.peg_target || 'USD'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ({currency.peg_type || 'Currency'} pegged)
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          {(currency.base_unit_value || 0).toFixed(6)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          (1 {currency.name} = {(currency.base_unit_value || 0).toFixed(6)} {currency.peg_target || 'USD'})
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="success.main">
                          {hasUsdValue ? `$${usdValue.toFixed(2)} USD` : 'N/A'}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="warning.main">
                          {hasGoldValue ? `${goldValue.toFixed(6)} oz` : 'N/A'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {hasGoldPrice
                            ? `${goldPriceUSD.toFixed(2)} USD / oz`
                            : 'Gold price unavailable'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {currency.denominations && currency.denominations.length > 0 ? (
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, maxWidth: 300 }}>
                            {currency.denominations.map((denom, index) => (
                              <Chip
                                key={index}
                                label={`${denom.name} (${denom.value_in_base_units})`}
                                size="small"
                                variant="outlined"
                                sx={{ fontSize: '0.75rem' }}
                              />
                            ))}
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            No denominations
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(currency)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => requestDeleteCurrency(currency.id, currency.name)}
                          color="error"
                          disabled={isUsdCurrency}
                          title={isUsdCurrency ? 'USD is the base currency and cannot be deleted.' : 'Delete currency'}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Empty State */}
        {currencies.length === 0 && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <CurrencyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No currencies found
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Create your first currency to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              Add Currency
            </Button>
          </Paper>
        )}

        {/* Floating Action Button */}
        <Fab
          color="primary"
          aria-label="add currency"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={() => handleOpenDialog()}
        >
          <AddIcon />
        </Fab>

        {/* Currency Dialog */}
        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>
            {editingCurrency ? 'Edit Currency' : 'Add New Currency'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Currency Name"
                  value={currencyForm.name}
                  onChange={(e) => setCurrencyForm(prev => ({ ...prev, name: e.target.value }))}
                  disabled={!!editingCurrency}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel id="peg-type-label">Peg Type</InputLabel>
                  <Select
                    labelId="peg-type-label"
                    value={normalizedPegType}
                    label="Peg Type"
                    onChange={handlePegTypeChange}
                  >
                    <MenuItem value="CURRENCY">Currency</MenuItem>
                    <MenuItem value="METAL">Metal</MenuItem>
                    <MenuItem value="MATERIAL">Material</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth disabled={!hasPegTargets}>
                  <InputLabel id="peg-target-label">Peg Target</InputLabel>
                  <Select
                    labelId="peg-target-label"
                    value={currencyForm.peg_target || ''}
                    label="Peg Target"
                    onChange={handlePegTargetChange}
                  >
                    {!hasPegTargets ? (
                      <MenuItem value="" disabled>
                        No targets available
                      </MenuItem>
                    ) : (
                      pegTargetOptions.map((option) => (
                        <MenuItem key={option} value={option}>
                          {option}
                        </MenuItem>
                      ))
                    )}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label={effectivePegTarget ? `Value per Unit (${effectivePegTarget})` : 'Value per Unit'}
                  type="number"
                  value={currencyForm.base_unit_value}
                  onChange={(e) => setCurrencyForm(prev => ({ 
                    ...prev, 
                    base_unit_value: Number.isNaN(parseFloat(e.target.value)) ? 0 : parseFloat(e.target.value)
                  }))}
                  inputProps={{ min: 0, step: 0.000001 }}
                  helperText={normalizedPegType === 'CURRENCY'
                    ? `How many ${effectivePegTarget || 'target units'} equal one unit of this currency.`
                    : `Amount of ${effectivePegTarget || 'target'} that equals one unit of this currency.`}
                />
              </Grid>
            </Grid>

            {/* Denominations Section */}
            <Box sx={{ mt: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Denominations</Typography>
                <Button
                  startIcon={<AddIcon />}
                  onClick={handleAddDenomination}
                  sx={{ ml: 2 }}
                >
                  Add Denomination
                </Button>
              </Box>

              {currencyForm.denominations.map((denomination, index) => (
                <Grid container spacing={2} key={index} sx={{ mb: 2 }}>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Denomination Name"
                      value={denomination.name}
                      onChange={(e) => handleDenominationChange(index, 'name', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <TextField
                      fullWidth
                      label="Value in Base Units"
                      type="number"
                      value={denomination.value_in_base_units}
                      onChange={(e) => handleDenominationChange(index, 'value_in_base_units', parseFloat(e.target.value) || 0)}
                      inputProps={{ min: 0, step: 0.001 }}
                    />
                  </Grid>
                  <Grid item xs={2}>
                    <IconButton
                      color="error"
                      onClick={() => handleRemoveDenomination(index)}
                      sx={{ mt: 1 }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Grid>
                </Grid>
              ))}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={handleSaveCurrency} 
              variant="contained"
              disabled={isSaveDisabled}
            >
              {editingCurrency ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={Boolean(deleteTarget)} onClose={cancelDeleteCurrency}>
          <DialogTitle>Delete Currency</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete the currency
              {deleteTarget?.name ? ` "${deleteTarget.name}"` : ''}? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={cancelDeleteCurrency} disabled={deleteSubmitting}>
              Cancel
            </Button>
            <Button
              color="error"
              onClick={handleDeleteCurrency}
              disabled={deleteSubmitting}
            >
              {deleteSubmitting ? 'Deleting…' : 'Delete'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
}

export default GMCurrencies;