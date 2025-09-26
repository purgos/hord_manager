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
  InputAdornment
} from '@mui/material';
import { AccountCircle, Shield, Visibility, VisibilityOff } from '@mui/icons-material';

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState('player');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [hidePasswordTimer, setHidePasswordTimer] = useState(null);

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
      // Simulate authentication - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate network delay

      // Simple authentication logic - replace with real authentication
      const isValidPlayer = userType === 'player' && password === 'player123';
      const isValidGM = userType === 'gm' && password === 'gm123';

      if (isValidPlayer || isValidGM) {
        // Store authentication in localStorage
        localStorage.setItem('hord_auth', JSON.stringify({
          username: username.trim(),
          userType,
          loginTime: new Date().toISOString()
        }));

        // Call parent component's onLogin function
        onLogin({
          username: username.trim(),
          userType,
          isAuthenticated: true
        });
      } else {
        setError('Invalid credentials. Use "player123" for players or "gm123" for GM.');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleUserTypeChange = (event, newUserType) => {
    if (newUserType !== null) {
      setUserType(newUserType);
      setError(''); // Clear errors when switching user type
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
                {/* User Type Toggle */}
                <Box sx={{ mb: 3, textAlign: 'center' }}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Login as:
                  </Typography>
                  <ToggleButtonGroup
                    value={userType}
                    exclusive
                    onChange={handleUserTypeChange}
                    aria-label="user type"
                    fullWidth
                  >
                    <ToggleButton value="player" aria-label="player">
                      <AccountCircle sx={{ mr: 1 }} />
                      Player
                    </ToggleButton>
                    <ToggleButton value="gm" aria-label="gm">
                      <Shield sx={{ mr: 1 }} />
                      Game Master
                    </ToggleButton>
                  </ToggleButtonGroup>
                </Box>

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
                    <strong>Demo Credentials:</strong>
                  </Typography>
                  <Typography variant="caption" display="block">
                    Player: any username + password "player123"
                  </Typography>
                  <Typography variant="caption" display="block">
                    GM: any username + password "gm123"
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
              </Box>
            </CardContent>
          </Card>
        </Paper>
      </Box>
    </Container>
  );
}

export default LoginPage;