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
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Container,
  Breadcrumbs,
  Link
} from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { gmService } from '../../services';

function GMPasswordChange() {
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '', 
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleChange = (field, value) => {
    setPasswordData(prev => ({
      ...prev,
      [field]: value
    }));
    setMessage(''); // Clear message when user types
  };

  const handleSubmit = async () => {
    if (!passwordData.newPassword || !passwordData.confirmPassword) {
      setMessage('Please fill in all required fields');
      return;
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage('New passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      setMessage('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);
    try {
      const response = await gmService.changePassword({
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
        confirm_password: passwordData.confirmPassword
      });

      setMessage('Password changed successfully!');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Change GM Password
        </Typography>
        
        {message && (
          <Alert 
            severity={message.includes('successfully') ? 'success' : 'error'} 
            sx={{ mb: 2 }}
          >
            {message}
          </Alert>
        )}

        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Current Password"
              type={showCurrentPassword ? 'text' : 'password'}
              value={passwordData.currentPassword}
              onChange={(e) => handleChange('currentPassword', e.target.value)}
              InputProps={{
                endAdornment: (
                  <Button
                    size="small"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  >
                    {showCurrentPassword ? 'Hide' : 'Show'}
                  </Button>
                )
              }}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="New Password"
              type={showNewPassword ? 'text' : 'password'}
              value={passwordData.newPassword}
              onChange={(e) => handleChange('newPassword', e.target.value)}
              InputProps={{
                endAdornment: (
                  <Button
                    size="small"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                  >
                    {showNewPassword ? 'Hide' : 'Show'}
                  </Button>
                )
              }}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Confirm New Password"
              type={showConfirmPassword ? 'text' : 'password'}
              value={passwordData.confirmPassword}
              onChange={(e) => handleChange('confirmPassword', e.target.value)}
              InputProps={{
                endAdornment: (
                  <Button
                    size="small"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    {showConfirmPassword ? 'Hide' : 'Show'}
                  </Button>
                )
              }}
            />
          </Grid>
        </Grid>

        <Button
          variant="contained"
          color="secondary"
          onClick={handleSubmit}
          disabled={loading}
          sx={{ mt: 2 }}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Changing Password...' : 'Change Password'}
        </Button>
      </CardContent>
    </Card>
  );
}

function GMSettings() {
  const navigate = useNavigate();
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await gmService.getSettings();
      setSettings(data);
    } catch (error) {
      console.error('Failed to load GM settings:', error);
      setMessage('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await gmService.updateSettings(settings);
      setMessage('Settings saved successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
      setMessage('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
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
          <Typography color="text.primary">Economic Settings</Typography>
        </Breadcrumbs>

        {/* Page Header */}
        <Paper sx={{ p: 3, mb: 4, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <SettingsIcon sx={{ fontSize: 48, color: 'secondary.main', mr: 2 }} />
            <Typography variant="h3" component="h1">
              Economic Settings
            </Typography>
          </Box>
          <Typography variant="h6" color="text.secondary">
            Configure economic parameters and security settings
          </Typography>
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

        <Grid container spacing={3}>
          {/* Economic Controls */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Economic Controls
                </Typography>
                <TextField
                  fullWidth
                  label="Exchange Fee (%)"
                  type="number"
                  value={settings?.exchange_fee_percent || 0}
                  onChange={(e) => handleChange('exchange_fee_percent', parseFloat(e.target.value) || 0)}
                  inputProps={{ min: 0, max: 100, step: 0.1 }}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Interest Rate (%)"
                  type="number"
                  value={settings?.interest_rate_percent || 0}
                  onChange={(e) => handleChange('interest_rate_percent', parseFloat(e.target.value) || 0)}
                  inputProps={{ min: 0, max: 100, step: 0.1 }}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Growth Factor (%)"
                  type="number"
                  value={settings?.growth_factor_percent || 0}
                  onChange={(e) => handleChange('growth_factor_percent', parseFloat(e.target.value) || 0)}
                  inputProps={{ min: -100, max: 100, step: 0.1 }}
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Player Visibility */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Player Visibility
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings?.hide_dollar_from_players || false}
                      onChange={(e) => handleChange('hide_dollar_from_players', e.target.checked)}
                    />
                  }
                  label="Hide USD from Players"
                />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  When enabled, players will not see USD values in the currency page
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Password Change */}
          <Grid item xs={12}>
            <GMPasswordChange />
          </Grid>

          {/* Save Button */}
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSave}
              disabled={saving}
              startIcon={saving ? <CircularProgress size={20} /> : <SettingsIcon />}
              size="large"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
}

export default GMSettings;