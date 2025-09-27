import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Snackbar,
  CircularProgress
} from '@mui/material';
import {
  Delete,
  Warning,
  RestartAlt,
  People,
  AttachMoney,
  Category,
  Diamond,
  Schedule,
  DeleteSweep
} from '@mui/icons-material';
import { PageHeader } from '../../components/Common';
import { dataManagementService } from '../../services/dataManagementService';

const GMDataManagement = () => {
  const [loading, setLoading] = useState({});
  const [confirmDialog, setConfirmDialog] = useState({ open: false, action: null, title: '', message: '' });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleConfirmAction = (action, title, message) => {
    setConfirmDialog({
      open: true,
      action,
      title,
      message
    });
  };

  const handleCloseDialog = () => {
    setConfirmDialog({ open: false, action: null, title: '', message: '' });
  };

  const executeAction = async () => {
    const { action } = confirmDialog;
    if (!action) return;

    setLoading({ ...loading, [action]: true });
    handleCloseDialog();

    try {
      let result;
      switch (action) {
        case 'users':
          result = await dataManagementService.resetUsers();
          break;
        case 'currencies':
          result = await dataManagementService.resetCurrencies();
          break;
        case 'metals':
          result = await dataManagementService.resetMetals();
          break;
        case 'materials':
          result = await dataManagementService.resetMaterials();
          break;
        case 'gemstones':
          result = await dataManagementService.resetGemstones();
          break;
        case 'sessions':
          result = await dataManagementService.resetSessions();
          break;
        case 'all':
          result = await dataManagementService.resetAllData();
          break;
        default:
          throw new Error('Unknown action');
      }
      
      showSnackbar(result.message || 'Operation completed successfully', 'success');
    } catch (error) {
      console.error(`Error in ${action} reset:`, error);
      showSnackbar(error.message || 'Operation failed', 'error');
    } finally {
      setLoading({ ...loading, [action]: false });
    }
  };

  const resetActions = [
    {
      key: 'users',
      title: 'Reset Users',
      description: 'Reset all users to default GM and Player accounts',
      icon: <People />,
      color: 'primary',
      confirmTitle: 'Reset User Data?',
      confirmMessage: 'This will delete all existing users and restore default GM and Player accounts. This action cannot be undone.'
    },
    {
      key: 'currencies',
      title: 'Reset Currencies',
      description: 'Reset all currencies to default (USD only)',
      icon: <AttachMoney />,
      color: 'primary',
      confirmTitle: 'Reset Currency Data?',
      confirmMessage: 'This will delete all existing currencies and restore only USD as the default currency. This action cannot be undone.'
    },
    {
      key: 'metals',
      title: 'Reset Metals',
      description: 'Reset to 20 default metals with price history',
      icon: <Category />,
      color: 'primary',
      confirmTitle: 'Reset Metal Data?',
      confirmMessage: 'This will delete all existing metals and price history, then restore 20 default metals (including Gold, Silver, Platinum, Steel, Lithium, Iron, Lead, and others) with session 1 prices. This action cannot be undone.'
    },
    {
      key: 'materials',
      title: 'Reset Materials',
      description: 'Reset to 20 default materials with price history',
      icon: <Category />,
      color: 'primary',
      confirmTitle: 'Reset Material Data?',
      confirmMessage: 'This will delete all existing materials and price history, then restore 20 default materials (including Wood, Carbon, Cotton, Flax, Sulfur, Stone, Silicon, Gallium, and others) with session 1 prices. This action cannot be undone.'
    },
    {
      key: 'gemstones',
      title: 'Reset Gemstones',
      description: 'Reset all gemstones to default 20 stones with realistic prices',
      icon: <Diamond />,
      color: 'primary',
      confirmTitle: 'Reset Gemstone Data?',
      confirmMessage: 'This will reset all gemstones to the default 20 stones with realistic prices. This action cannot be undone.'
    },
    {
      key: 'sessions',
      title: 'Reset Sessions',
      description: 'Reset session counter back to 1',
      icon: <Schedule />,
      color: 'warning',
      confirmTitle: 'Reset Session Data?',
      confirmMessage: 'This will reset the session counter back to 1. This action cannot be undone.'
    }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <PageHeader 
        title="Data Management" 
        subtitle="Reset various data categories to their default values"
        icon={<RestartAlt />}
      />

      <Alert severity="warning" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Warning:</strong> All reset operations are permanent and cannot be undone. 
          Make sure you understand the consequences before proceeding.
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        {resetActions.map((action) => (
          <Grid item xs={12} md={6} key={action.key}>
            <Paper elevation={2} sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box sx={{ mr: 2, color: `${action.color}.main` }}>
                  {action.icon}
                </Box>
                <Typography variant="h6" component="h3">
                  {action.title}
                </Typography>
              </Box>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3, flexGrow: 1 }}>
                {action.description}
              </Typography>
              
              <Button
                variant="outlined"
                color={action.color}
                startIcon={loading[action.key] ? <CircularProgress size={20} /> : <Delete />}
                disabled={loading[action.key]}
                onClick={() => handleConfirmAction(action.key, action.confirmTitle, action.confirmMessage)}
                fullWidth
              >
                {loading[action.key] ? 'Resetting...' : action.title}
              </Button>
            </Paper>
          </Grid>
        ))}

        {/* Reset All Data - Special card */}
        <Grid item xs={12}>
          <Paper 
            elevation={3} 
            sx={{ 
              p: 3, 
              border: 2, 
              borderColor: 'error.main',
              bgcolor: 'error.50'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Box sx={{ mr: 2, color: 'error.main' }}>
                <DeleteSweep fontSize="large" />
              </Box>
              <Box>
                <Typography variant="h5" component="h3" color="error.main">
                  Reset All Data
                </Typography>
                <Typography variant="body2" color="error.dark">
                  Nuclear option: Reset everything to factory defaults
                </Typography>
              </Box>
            </Box>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              This will reset ALL data categories: users, currencies, metals, materials, gemstones, and sessions. 
              This is equivalent to a complete database reset to initial state.
            </Typography>
            
            <Button
              variant="contained"
              color="error"
              size="large"
              startIcon={loading.all ? <CircularProgress size={20} color="inherit" /> : <Warning />}
              disabled={loading.all}
              onClick={() => handleConfirmAction(
                'all',
                'Reset ALL Data?',
                'This will permanently delete ALL data and restore everything to default values. This action cannot be undone and will affect users, currencies, metals, materials, gemstones, and sessions.'
              )}
              fullWidth
            >
              {loading.all ? 'Resetting All Data...' : 'Reset All Data'}
            </Button>
          </Paper>
        </Grid>
      </Grid>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialog.open}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center' }}>
          <Warning color="warning" sx={{ mr: 1 }} />
          {confirmDialog.title}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {confirmDialog.message}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Cancel
          </Button>
          <Button 
            onClick={executeAction}
            color="error" 
            variant="contained"
            autoFocus
          >
            Confirm Reset
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default GMDataManagement;