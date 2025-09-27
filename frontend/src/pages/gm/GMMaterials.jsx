import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  TextField,
  Alert,
  CircularProgress,
  Container,
  Breadcrumbs,
  Link,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Build as MaterialsIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { materialService, metalService, sessionService } from '../../services';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`materials-tabpanel-${index}`}
      aria-labelledby={`materials-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function GMMaterials() {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [materials, setMaterials] = useState([]);
  const [metals, setMetals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [editDialog, setEditDialog] = useState({ open: false, item: null, type: null });
  const [editValues, setEditValues] = useState({ minMultiplier: 0.8, maxMultiplier: 1.2 });
  const [createDialog, setCreateDialog] = useState({ open: false, type: null });
  const [createValues, setCreateValues] = useState({ name: '', unit: '', basePrice: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Get current session first
      const session = await sessionService.getState();
      const currentSession = session.current_session;
      
      const [materialsRanges, metalsRanges, currentMaterialPrices, currentMetalPrices] = await Promise.all([
        materialService.getPriceRanges(),
        metalService.getPriceRanges(),
        materialService.getCurrentPrices(currentSession, true),
        metalService.getCurrentPrices(true, currentSession)
      ]);
      
      // Create lookup maps for current prices
      const materialPriceMap = {};
      if (currentMaterialPrices.prices) {
        currentMaterialPrices.prices.forEach(price => {
          materialPriceMap[price.material_name] = price;
        });
      }
      
      const metalPriceMap = {};
      if (currentMetalPrices.prices) {
        currentMetalPrices.prices.forEach(price => {
          metalPriceMap[price.metal_name] = price;
        });
      }
      
      // Transform materials data with current prices
      const materialsData = materialsRanges.materials.map(material => {
        const currentPrice = materialPriceMap[material.name];
        return {
          ...material,
          minMultiplier: material.min_multiplier || 0.8,
          maxMultiplier: material.max_multiplier || 1.2,
          currentPrice: currentPrice?.price_per_unit_usd || material.base_price,
          currentMinPrice: currentPrice ? currentPrice.price_per_unit_usd * (material.min_multiplier || 0.8) : material.base_price * 0.8,
          currentMaxPrice: currentPrice ? currentPrice.price_per_unit_usd * (material.max_multiplier || 1.2) : material.base_price * 1.2
        };
      });

      // Transform metals data with current prices
      const metalsData = metalsRanges.metals.map(metal => {
        const currentPrice = metalPriceMap[metal.name];
        return {
          ...metal,
          minMultiplier: metal.min_multiplier || 0.8,
          maxMultiplier: metal.max_multiplier || 1.2,
          currentPrice: currentPrice?.price_per_unit_usd || metal.base_price,
          currentMinPrice: currentPrice ? currentPrice.price_per_unit_usd * (metal.min_multiplier || 0.8) : metal.base_price * 0.8,
          currentMaxPrice: currentPrice ? currentPrice.price_per_unit_usd * (metal.max_multiplier || 1.2) : metal.base_price * 1.2
        };
      });

      setMaterials(materialsData);
      setMetals(metalsData);
    } catch (error) {
      console.error('Failed to load materials and metals data:', error);
      setMessage('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleEditClick = (item, type) => {
    setEditDialog({ 
      open: true, 
      item, 
      type 
    });
    setEditValues({
      minMultiplier: item.minMultiplier,
      maxMultiplier: item.maxMultiplier
    });
  };

  const handleEditSave = async () => {
    try {
      setSaving(true);
      
      // Call the appropriate API to update the price range
      if (editDialog.type === 'material') {
        await materialService.updatePriceRange(
          editDialog.item.name,
          editValues.minMultiplier,
          editValues.maxMultiplier
        );
      } else {
        await metalService.updatePriceRange(
          editDialog.item.name,
          editValues.minMultiplier,
          editValues.maxMultiplier
        );
      }
      
      // Update local state
      const updatedItem = {
        ...editDialog.item,
        minMultiplier: editValues.minMultiplier,
        maxMultiplier: editValues.maxMultiplier,
        currentMinPrice: editDialog.item.base_price * editValues.minMultiplier,
        currentMaxPrice: editDialog.item.base_price * editValues.maxMultiplier
      };

      if (editDialog.type === 'material') {
        setMaterials(prev => prev.map(m => 
          m.name === editDialog.item.name ? updatedItem : m
        ));
      } else {
        setMetals(prev => prev.map(m => 
          m.name === editDialog.item.name ? updatedItem : m
        ));
      }

      setMessage(`Successfully updated ${editDialog.item.name} price range`);
      setEditDialog({ open: false, item: null, type: null });
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Failed to update price range:', error);
      setMessage('Failed to update price range');
    } finally {
      setSaving(false);
    }
  };

  const handleEditCancel = () => {
    setEditDialog({ open: false, item: null, type: null });
    setEditValues({ minMultiplier: 0.8, maxMultiplier: 1.2 });
  };

  const handleCreateClick = (type) => {
    setCreateDialog({ open: true, type });
    setCreateValues({ name: '', unit: '', basePrice: '' });
  };

  const handleCreateSave = async () => {
    try {
      setSaving(true);
      const { name, unit, basePrice } = createValues;
      
      if (!name || !unit || !basePrice) {
        setMessage('Please fill in all fields');
        return;
      }

      const price = parseFloat(basePrice);
      if (isNaN(price) || price <= 0) {
        setMessage('Please enter a valid price');
        return;
      }

      let result;
      if (createDialog.type === 'material') {
        result = await materialService.create(name, unit, price);
      } else {
        result = await metalService.create(name, unit, price);
      }

      setMessage(result.message);
      setCreateDialog({ open: false, type: null });
      setCreateValues({ name: '', unit: '', basePrice: '' });
      
      // Reload data to show the new item
      await loadData();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Failed to create item:', error);
      setMessage(error.response?.data?.detail || 'Failed to create item');
    } finally {
      setSaving(false);
    }
  };

  const handleCreateCancel = () => {
    setCreateDialog({ open: false, type: null });
    setCreateValues({ name: '', unit: '', basePrice: '' });
  };

  const renderItemsTable = (items, type) => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>{type === 'material' ? 'Material' : 'Metal'}</TableCell>
            <TableCell>Unit</TableCell>
            <TableCell align="right">Base Price</TableCell>
            <TableCell align="right">Current Price</TableCell>
            <TableCell align="right">Min Price</TableCell>
            <TableCell align="right">Max Price</TableCell>
            <TableCell align="right">Price Range</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {items.map((item) => (
            <TableRow key={item.name}>
              <TableCell component="th" scope="row">
                <Typography variant="body2" fontWeight="medium">
                  {item.name}
                </Typography>
              </TableCell>
              <TableCell>{item.unit}</TableCell>
              <TableCell align="right">
                ${item.base_price?.toFixed(2) || 'N/A'}
              </TableCell>
              <TableCell align="right">
                <Typography color="primary.main" fontWeight="medium">
                  ${item.currentPrice?.toFixed(2) || 'N/A'}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Typography color="error.main">
                  ${item.currentMinPrice?.toFixed(2) || 'N/A'}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Typography color="success.main">
                  ${item.currentMaxPrice?.toFixed(2) || 'N/A'}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Typography variant="body2" color="text.secondary">
                  {((item.minMultiplier || 0.8) * 100).toFixed(0)}% - {((item.maxMultiplier || 1.2) * 100).toFixed(0)}%
                </Typography>
              </TableCell>
              <TableCell align="center">
                <IconButton
                  size="small"
                  onClick={() => handleEditClick(item, type)}
                  color="primary"
                >
                  <EditIcon />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

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
          <Typography color="text.primary">Materials Management</Typography>
        </Breadcrumbs>

        {/* Page Header */}
        <Paper sx={{ p: 3, mb: 4, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <MaterialsIcon sx={{ fontSize: 48, color: 'primary.main', mr: 2 }} />
            <Typography variant="h3" component="h1">
              Materials & Metals Management
            </Typography>
          </Box>
          <Typography variant="h6" color="text.secondary">
            Configure price ranges for materials and metals
          </Typography>
        </Paper>

        {/* Alerts */}
        {message && (
          <Alert 
            severity={message.includes('Successfully') ? 'success' : 'error'} 
            sx={{ mb: 3 }}
          >
            {message}
          </Alert>
        )}

        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange}
            variant="fullWidth"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab label={`Materials (${materials.length})`} />
            <Tab label={`Metals (${metals.length})`} />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <Box sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Material Price Ranges
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => handleCreateClick('material')}
                  sx={{ ml: 2 }}
                >
                  Add New Material
                </Button>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Configure the minimum and maximum price multipliers for each material. 
                These ranges determine how much prices can fluctuate during gameplay.
              </Typography>
              {renderItemsTable(materials, 'material')}
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Metal Price Ranges
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => handleCreateClick('metal')}
                  sx={{ ml: 2 }}
                >
                  Add New Metal
                </Button>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Configure the minimum and maximum price multipliers for each metal. 
                These ranges determine how much prices can fluctuate during gameplay.
              </Typography>
              {renderItemsTable(metals, 'metal')}
            </Box>
          </TabPanel>
        </Paper>

        {/* Edit Dialog */}
        <Dialog open={editDialog.open} onClose={handleEditCancel} maxWidth="sm" fullWidth>
          <DialogTitle>
            Edit Price Range for {editDialog.item?.name}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Base Price: ${editDialog.item?.base_price?.toFixed(2) || 'N/A'}
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Minimum Multiplier"
                    type="number"
                    value={editValues.minMultiplier}
                    onChange={(e) => setEditValues(prev => ({ 
                      ...prev, 
                      minMultiplier: parseFloat(e.target.value) || 0 
                    }))}
                    inputProps={{ step: 0.1, min: 0.1, max: 1.0 }}
                    helperText={`Min Price: $${((editDialog.item?.base_price || 0) * editValues.minMultiplier).toFixed(2)}`}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Maximum Multiplier"
                    type="number"
                    value={editValues.maxMultiplier}
                    onChange={(e) => setEditValues(prev => ({ 
                      ...prev, 
                      maxMultiplier: parseFloat(e.target.value) || 0 
                    }))}
                    inputProps={{ step: 0.1, min: 1.0, max: 3.0 }}
                    helperText={`Max Price: $${((editDialog.item?.base_price || 0) * editValues.maxMultiplier).toFixed(2)}`}
                  />
                </Grid>
              </Grid>
              
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Price Range: {(editValues.minMultiplier * 100).toFixed(0)}% - {(editValues.maxMultiplier * 100).toFixed(0)}% of base price
                </Typography>
              </Alert>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleEditCancel} disabled={saving}>
              <CancelIcon sx={{ mr: 1 }} />
              Cancel
            </Button>
            <Button 
              onClick={handleEditSave} 
              variant="contained" 
              disabled={saving || editValues.minMultiplier >= editValues.maxMultiplier}
            >
              {saving ? <CircularProgress size={20} sx={{ mr: 1 }} /> : <SaveIcon sx={{ mr: 1 }} />}
              Save Changes
            </Button>
          </DialogActions>
        </Dialog>

        {/* Create Dialog */}
        <Dialog open={createDialog.open} onClose={handleCreateCancel} maxWidth="sm" fullWidth>
          <DialogTitle>
            Add New {createDialog.type === 'material' ? 'Material' : 'Metal'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <TextField
                fullWidth
                label="Name"
                value={createValues.name}
                onChange={(e) => setCreateValues(prev => ({ ...prev, name: e.target.value }))}
                sx={{ mb: 2 }}
                placeholder={`Enter ${createDialog.type} name`}
              />
              <TextField
                fullWidth
                label="Unit"
                value={createValues.unit}
                onChange={(e) => setCreateValues(prev => ({ ...prev, unit: e.target.value }))}
                sx={{ mb: 2 }}
                placeholder="e.g., lb, oz, kg, ton"
                helperText="The unit of measurement for this item"
              />
              <TextField
                fullWidth
                label="Base Price (USD)"
                type="number"
                value={createValues.basePrice}
                onChange={(e) => setCreateValues(prev => ({ ...prev, basePrice: e.target.value }))}
                sx={{ mb: 2 }}
                placeholder="0.00"
                helperText="The base price in USD per unit"
                inputProps={{ min: 0, step: 0.01 }}
              />
              {message && (
                <Alert 
                  severity={message.includes('Successfully') ? 'success' : 'error'} 
                  sx={{ mt: 2 }}
                >
                  {message}
                </Alert>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCreateCancel} disabled={saving}>
              <CancelIcon sx={{ mr: 1 }} />
              Cancel
            </Button>
            <Button 
              onClick={handleCreateSave} 
              variant="contained" 
              disabled={saving || !createValues.name || !createValues.unit || !createValues.basePrice}
            >
              {saving ? <CircularProgress size={20} sx={{ mr: 1 }} /> : <SaveIcon sx={{ mr: 1 }} />}
              Create {createDialog.type === 'material' ? 'Material' : 'Metal'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
}

export default GMMaterials;