import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Avatar,
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountBalance,
  Business,
  Diamond,
  Gavel,
  Home,
  Settings,
  AccountCircle,
  Shield,
  Logout,
  AttachMoney,
  Inbox,
  DeleteForever,
  Build,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Header = ({ sessionNumber, user, onNavigate }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, isGM } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [userMenuAnchor, setUserMenuAnchor] = React.useState(null);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleUserMenuClick = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = () => {
    logout();
    handleUserMenuClose();
    navigate('/login');
  };

  const handleNavigation = (path) => {
    navigate(path);
    handleMenuClose();
    if (onNavigate) onNavigate(path);
  };

  const menuItems = isGM() ? [
  // GM-only navigation menu
  { label: 'Home', path: '/', icon: <Home /> },
  { label: 'Settings', path: '/gm/settings', icon: <Settings /> },
  { label: 'Currencies', path: '/gm/currencies', icon: <AttachMoney /> },
  { label: 'Materials', path: '/gm/materials', icon: <Build /> },
  { label: 'Inbox', path: '/gm/inbox', icon: <Inbox /> },
  { label: 'Gemstones', path: '/gm/gemstones', icon: <Diamond /> },
  { label: 'Data', path: '/gm/data', icon: <DeleteForever /> },
  ] : [
    // Player navigation menu
    { label: 'Home', path: '/', icon: <Home /> },
    { label: 'Treasure Horde', path: '/treasure', icon: <Diamond /> },
    { label: 'Banking', path: '/banking', icon: <AccountBalance /> },
    { label: 'Business', path: '/business', icon: <Business /> },
    { label: 'Net Worth', path: '/net-worth', icon: <Gavel /> },
    { label: 'Currencies', path: '/currencies', icon: <AttachMoney /> },
  ];

  return (
    <AppBar position="static" sx={{ mb: 2 }}>
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={handleMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          🏰 Hord Manager
        </Typography>

        {sessionNumber && (
          <Box sx={{ mr: 2 }}>
            <Typography variant="body2">
              Session: {sessionNumber}
            </Typography>
          </Box>
        )}

        {/* User Info and Menu */}
        {user && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              icon={isGM() ? <Shield /> : <AccountCircle />}
              label={`${user.username} (${isGM() ? 'GM' : 'Player'})`}
              color={isGM() ? 'secondary' : 'primary'}
              variant="outlined"
              onClick={handleUserMenuClick}
              sx={{ color: 'white', borderColor: 'white' }}
            />
            <Menu
              anchorEl={userMenuAnchor}
              open={Boolean(userMenuAnchor)}
              onClose={handleUserMenuClose}
            >
              <MenuItem onClick={handleLogout}>
                <Logout sx={{ mr: 1 }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        )}

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          {menuItems.map((item) => (
            <MenuItem
              key={item.path}
              onClick={() => handleNavigation(item.path)}
              selected={location.pathname === item.path}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mr: 1 }}>
                {item.icon}
              </Box>
              {item.label}
            </MenuItem>
          ))}
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;