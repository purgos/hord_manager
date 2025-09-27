import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  ToggleButton,
  ToggleButtonGroup,
  Container,
  Paper,
  IconButton,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Link
} from '@mui/material';
import { AccountCircle, Shield, Visibility, VisibilityOff, PersonAdd } from '@mui/icons-material';

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [hidePasswordTimer, setHidePasswordTimer] = useState(null);
  
  // Registration dialog state
  const [showRegistration, setShowRegistration] = useState(false);
  const [regUsername, setRegUsername] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');
  const [regError, setRegError] = useState('');
  const [regLoading, setRegLoading] = useState(false);
  const [regSuccess, setRegSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Basic validation
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password');
      setLoading(false);
      return;
    }

    try {
      // Use backend authentication for both GM and players
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          password: password
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Determine user type based on username
        const userType = username.trim().toUpperCase() === 'GM' ? 'gm' : 'player';
        
        // Store authentication in localStorage
        localStorage.setItem('hord_auth', JSON.stringify({
          username: data.username,
          userType: userType,
          playerId: data.player_id,
          loginTime: new Date().toISOString()
        }));

        // Call parent component's onLogin function
        onLogin({
          username: data.username,
          userType: userType,
          playerId: data.player_id,
          isAuthenticated: true
        });
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };



  const handlePasswordVisibilityToggle = () => {
    setShowPassword(!showPassword);
    
    // Clear any existing timer
    if (hidePasswordTimer) {
      clearTimeout(hidePasswordTimer);
    }
    
    // If showing password, set a timer to hide it after 5 seconds
    if (!showPassword) {
      const timer = setTimeout(() => {
        setShowPassword(false);
        setHidePasswordTimer(null);
      }, 5000);
      setHidePasswordTimer(timer);
    } else {
      setHidePasswordTimer(null);
    }
  };

  const handleRegistrationSubmit = async (e) => {
    e.preventDefault();
    setRegError('');
    setRegSuccess('');
    setRegLoading(true);

    // Basic validation
    if (!regUsername.trim() || !regPassword.trim() || !regConfirmPassword.trim()) {
      setRegError('Please fill in all fields');
      setRegLoading(false);
      return;
    }

    if (regPassword !== regConfirmPassword) {
      setRegError('Passwords do not match');
      setRegLoading(false);
      return;
    }

    if (regPassword.length < 6) {
      setRegError('Password must be at least 6 characters long');
      setRegLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: regUsername.trim(),
          password: regPassword,
          confirm_password: regConfirmPassword
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setRegSuccess('Registration successful! Your account is pending GM approval. You will be notified when it\'s ready.');
        // Clear form
        setRegUsername('');
        setRegPassword('');
        setRegConfirmPassword('');
        // Close dialog after a delay
        setTimeout(() => {
          setShowRegistration(false);
          setRegSuccess('');
        }, 3000);
      } else {
        setRegError(data.detail || 'Registration failed');
      }
    } catch (err) {
      setRegError('Network error. Please try again.');
    } finally {
      setRegLoading(false);
    }
  };

  const handleCloseRegistration = () => {
    setShowRegistration(false);
    setRegError('');
    setRegSuccess('');
    setRegUsername('');
    setRegPassword('');
    setRegConfirmPassword('');
  };

  // Cleanup timer on component unmount
  useEffect(() => {
    return () => {
      if (hidePasswordTimer) {
        clearTimeout(hidePasswordTimer);
      }
    };
  }, [hidePasswordTimer]);

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4
        }}
      >
        <Paper elevation={8} sx={{ p: 4, width: '100%', maxWidth: 400 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h3" component="h1" gutterBottom>
              🏰 Hord Manager
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Adventure & Wealth Management
            </Typography>
          </Box>

          <Card>
            <CardContent>
              <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                {/* Username */}
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="username"
                  label="Username"
                  name="username"
                  autoComplete="username"
                  autoFocus
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={loading}
                />

                {/* Password */}
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={handlePasswordVisibilityToggle}
                          disabled={loading}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />

                {/* Error Alert */}
                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}

                {/* Demo Credentials Info */}
                <Box sx={{ mt: 2, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
                  <Typography variant="caption" display="block">
                    <strong>Login Information:</strong>
                  </Typography>
                  <Typography variant="caption" display="block">
                    Game Master: username "GM" + password "gm1234"
                  </Typography>
                  <Typography variant="caption" display="block">
                    Players: Use your registered account or create a new one
                  </Typography>
                  <Typography variant="caption" display="block">
                    Legacy players: "Aragorn", "Legolas", or "Gimli" (any password)
                  </Typography>
                </Box>

                {/* Submit Button */}
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{ mt: 3, mb: 2 }}
                  disabled={loading}
                  size="large"
                >
                  {loading ? 'Logging in...' : 'Login'}
                </Button>

                {/* Registration Button */}
                {username.trim().toUpperCase() !== 'GM' && (
                  <Box sx={{ textAlign: 'center', mt: 1 }}>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      Don't have an account?
                    </Typography>
                    <Link
                      component="button"
                      variant="body2"
                      onClick={() => setShowRegistration(true)}
                      sx={{ cursor: 'pointer' }}
                    >
                      Create Player Account
                    </Link>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>

          {/* Registration Dialog */}
          <Dialog open={showRegistration} onClose={handleCloseRegistration} maxWidth="sm" fullWidth>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PersonAdd sx={{ mr: 1 }} />
                Create Player Account
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box component="form" onSubmit={handleRegistrationSubmit} sx={{ mt: 1 }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  label="Username"
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  disabled={regLoading}
                  autoFocus
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  label="Password"
                  type="password"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  disabled={regLoading}
                  helperText="Password must be at least 6 characters long"
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  label="Confirm Password"
                  type="password"
                  value={regConfirmPassword}
                  onChange={(e) => setRegConfirmPassword(e.target.value)}
                  disabled={regLoading}
                />

                {regError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {regError}
                  </Alert>
                )}

                {regSuccess && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    {regSuccess}
                  </Alert>
                )}

                <Box sx={{ mt: 2, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
                  <Typography variant="caption" display="block">
                    <strong>Account Approval Process:</strong>
                  </Typography>
                  <Typography variant="caption" display="block">
                    • Your registration will be sent to the Game Master for approval
                  </Typography>
                  <Typography variant="caption" display="block">
                    • You'll be notified when your account is ready
                  </Typography>
                  <Typography variant="caption" display="block">
                    • This usually takes 1-2 business days
                  </Typography>
                </Box>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseRegistration} disabled={regLoading}>
                Cancel
              </Button>
              <Button
                onClick={handleRegistrationSubmit}
                variant="contained"
                disabled={regLoading}
                startIcon={regLoading ? null : <PersonAdd />}
              >
                {regLoading ? 'Creating Account...' : 'Create Account'}
              </Button>
            </DialogActions>
          </Dialog>
        </Paper>
      </Box>
    </Container>
  );
}

export default LoginPage;