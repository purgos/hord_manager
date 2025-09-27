import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  InputAdornment,
  ToggleButton,
  ToggleButtonGroup,
  FormControl,
  FormLabel
} from '@mui/material';
import {
  Diamond as GemstoneIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { gemstoneService, currencyService } from '../../services';

function GMGemstones() {
  const navigate = useNavigate();
  const [gemstones, setGemstones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingGemstone, setEditingGemstone] = useState(null);
  const [message, setMessage] = useState('');
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteSubmitting, setDeleteSubmitting] = useState(false);
  
  // Form state
  const [gemstoneForm, setGemstoneForm] = useState({
    name: '',
    value_per_carat_oz_gold: 0.0,
    value_per_carat_usd: 0.0
  });
  const [inputMode, setInputMode] = useState('oz_gold'); // 'oz_gold' or 'usd'
  const [converting, setConverting] = useState(false);

  const loadGemstones = useCallback(async () => {
    try {
      const data = await gemstoneService.getAll();
      // Add USD values to each gemstone
      const gemstonesWithUSD = await Promise.all(
        data.map(async (gemstone) => {
          try {
            const usdValue = await currencyService.convertFromGold(
              gemstone.value_per_carat_oz_gold, 
              'USD'
            );
            return {
              ...gemstone,
              value_per_carat_usd: usdValue.amount || 0
            };
          } catch (error) {
            console.error('Failed to convert gold to USD for gemstone:', gemstone.name, error);
            return {
              ...gemstone,
              value_per_carat_usd: 0
            };
          }
        })
      );
      setGemstones(gemstonesWithUSD);
    } catch (error) {
      console.error('Failed to load gemstones:', error);
      setMessage('Failed to load gemstones');
    } finally {
      setLoading(false);
    }
  }, []);

  const convertCurrency = useCallback(async (value, fromMode) => {
    if (!value || value <= 0) return;
    
    setConverting(true);
    try {
      if (fromMode === 'oz_gold') {
        // Convert from oz gold to USD
        const result = await currencyService.convertFromGold(value, 'USD');
        setGemstoneForm(prev => ({
          ...prev,
          value_per_carat_usd: result.amount || 0
        }));
      } else {
        // Convert from USD to oz gold
        const result = await currencyService.convertToGold(value, 'USD');
        setGemstoneForm(prev => ({
          ...prev,
          value_per_carat_oz_gold: result.oz_gold || 0
        }));
      }
    } catch (error) {
      console.error('Currency conversion failed:', error);
      setMessage('Failed to convert currency');
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setConverting(false);
    }
  }, []);

  useEffect(() => {
    loadGemstones();
  }, [loadGemstones]);

  const handleOpenDialog = (gemstone = null) => {
    if (gemstone) {
      setEditingGemstone(gemstone);
      setGemstoneForm({
        name: gemstone.name,
        value_per_carat_oz_gold: gemstone.value_per_carat_oz_gold || 0.0,
        value_per_carat_usd: gemstone.value_per_carat_usd || 0.0
      });
    } else {
      setEditingGemstone(null);
      setGemstoneForm({
        name: '',
        value_per_carat_oz_gold: 0.0,
        value_per_carat_usd: 0.0
      });
    }
    setInputMode('oz_gold');
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingGemstone(null);
    setGemstoneForm({
      name: '',
      value_per_carat_oz_gold: 0.0,
      value_per_carat_usd: 0.0
    });
    setInputMode('oz_gold');
  };

  const handleSaveGemstone = async () => {
    const trimmedName = gemstoneForm.name?.trim() || '';
    const value = Number(gemstoneForm.value_per_carat_oz_gold);

    if (!trimmedName) {
      setMessage('Gemstone name is required');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    if (Number.isNaN(value) || value < 0) {
      setMessage('Value per carat must be a valid non-negative number');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    try {
      if (editingGemstone) {
        // Update existing gemstone
        await gemstoneService.update(editingGemstone.id, {
          name: trimmedName,
          value_per_carat_oz_gold: value
        });
        setMessage('Gemstone updated successfully!');
      } else {
        // Create new gemstone
        await gemstoneService.create({
          name: trimmedName,
          value_per_carat_oz_gold: value
        });
        setMessage('Gemstone created successfully!');
      }
      
      await loadGemstones();
      handleCloseDialog();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Failed to save gemstone:', error);
      const detail = error?.response?.data?.detail;
      setMessage(detail ? `Failed to save gemstone: ${detail}` : 'Failed to save gemstone');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const requestDeleteGemstone = (gemstoneId, gemstoneName) => {
    const targetId = Number(gemstoneId);
    const originalName = (gemstoneName ?? '').trim();

    if (Number.isNaN(targetId)) {
      setMessage('Invalid gemstone reference. Please refresh and try again.');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    setDeleteTarget({ id: targetId, name: originalName || gemstoneName || 'Unnamed Gemstone' });
  };

  const cancelDeleteGemstone = () => {
    if (deleteSubmitting) {
      return;
    }
    setDeleteTarget(null);
  };

  const handleDeleteGemstone = async () => {
    if (!deleteTarget) {
      return;
    }

    const { id: targetId, name } = deleteTarget;

    if (Number.isNaN(targetId)) {
      setMessage('Invalid gemstone reference. Please refresh and try again.');
      setTimeout(() => setMessage(''), 3000);
      setDeleteTarget(null);
      return;
    }

    setDeleteSubmitting(true);

    try {
      await gemstoneService.delete(targetId);
      setGemstones((prev) => prev.filter((item) => Number(item.id) !== targetId));
      await loadGemstones();
      setMessage(`Gemstone "${name || 'Unnamed Gemstone'}" deleted successfully!`);
      setTimeout(() => setMessage(''), 3000);
      setDeleteTarget(null);
    } catch (error) {
      console.error('Failed to delete gemstone:', error);
      const detail = error?.response?.data?.detail;
      setMessage(detail ? `Failed to delete gemstone: ${detail}` : 'Failed to delete gemstone');
      setTimeout(() => setMessage(''), 3000);
    } finally {
      setDeleteSubmitting(false);
    }
  };

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
          <Typography color="text.primary">Gemstone Management</Typography>
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
              <GemstoneIcon sx={{ fontSize: 48, color: 'primary.main' }} />
              <Box>
                <Typography variant="h3" component="h1">
                  Gemstone Management
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                  Manage gemstone types and their values per carat in gold
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

        {/* Gemstones Table */}
        <Paper sx={{ mb: 3 }}>
          <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6" gutterBottom>
              All Gemstones
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Configure gemstone types and their base values per carat in oz gold
            </Typography>
          </Box>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Gemstone Name</strong></TableCell>
                  <TableCell align="right"><strong>Value per Carat (oz Gold)</strong></TableCell>
                  <TableCell align="right"><strong>Value per Carat (USD)</strong></TableCell>
                  <TableCell align="center"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {gemstones.map((gemstone) => (
                  <TableRow key={gemstone.id}>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {gemstone.name}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {(gemstone.value_per_carat_oz_gold || 0).toFixed(6)} oz
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        ${(gemstone.value_per_carat_usd || 0).toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(gemstone)}
                        color="primary"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => requestDeleteGemstone(gemstone.id, gemstone.name)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Empty State */}
        {gemstones.length === 0 && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <GemstoneIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No gemstones found
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Create your first gemstone to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              Add Gemstone
            </Button>
          </Paper>
        )}

        {/* Floating Action Button */}
        <Fab
          color="primary"
          aria-label="add gemstone"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={() => handleOpenDialog()}
        >
          <AddIcon />
        </Fab>

        {/* Gemstone Dialog */}
        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingGemstone ? 'Edit Gemstone' : 'Add New Gemstone'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Gemstone Name"
                  value={gemstoneForm.name}
                  onChange={(e) => setGemstoneForm(prev => ({ ...prev, name: e.target.value }))}
                  disabled={!!editingGemstone}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <FormLabel component="legend" sx={{ mb: 1 }}>
                    Currency Input Mode
                  </FormLabel>
                  <ToggleButtonGroup
                    value={inputMode}
                    exclusive
                    onChange={(e, newMode) => {
                      if (newMode) setInputMode(newMode);
                    }}
                    size="small"
                    sx={{ mb: 2 }}
                  >
                    <ToggleButton value="oz_gold">oz Gold</ToggleButton>
                    <ToggleButton value="usd">USD</ToggleButton>
                  </ToggleButtonGroup>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Value per Carat (oz Gold)"
                  type="number"
                  value={gemstoneForm.value_per_carat_oz_gold}
                  onChange={(e) => {
                    const value = parseFloat(e.target.value) || 0;
                    setGemstoneForm(prev => ({ ...prev, value_per_carat_oz_gold: value }));
                    if (inputMode === 'oz_gold' && value > 0) {
                      convertCurrency(value, 'oz_gold');
                    }
                  }}
                  disabled={inputMode !== 'oz_gold' || converting}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">oz</InputAdornment>,
                    inputProps: { min: 0, step: 0.000001 }
                  }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Value per Carat (USD)"
                  type="number"
                  value={gemstoneForm.value_per_carat_usd}
                  onChange={(e) => {
                    const value = parseFloat(e.target.value) || 0;
                    setGemstoneForm(prev => ({ ...prev, value_per_carat_usd: value }));
                    if (inputMode === 'usd' && value > 0) {
                      convertCurrency(value, 'usd');
                    }
                  }}
                  disabled={inputMode !== 'usd' || converting}
                  InputProps={{
                    endAdornment: <InputAdornment position="end">$</InputAdornment>,
                    inputProps: { min: 0, step: 0.01 }
                  }}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={handleSaveGemstone} 
              variant="contained"
              disabled={!gemstoneForm.name?.trim()}
            >
              {editingGemstone ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={Boolean(deleteTarget)} onClose={cancelDeleteGemstone}>
          <DialogTitle>Delete Gemstone</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete the gemstone
              {deleteTarget?.name ? ` "${deleteTarget.name}"` : ''}? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={cancelDeleteGemstone} disabled={deleteSubmitting}>
              Cancel
            </Button>
            <Button
              color="error"
              onClick={handleDeleteGemstone}
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

export default GMGemstones;