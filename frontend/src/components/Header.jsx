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
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountBalance,
  Business,
  Diamond,
  Gavel,
  Home,
  Settings,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Header = ({ sessionNumber, onNavigate }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNavigation = (path) => {
    navigate(path);
    handleMenuClose();
    if (onNavigate) onNavigate(path);
  };

  const menuItems = [
    { label: 'Home', path: '/', icon: <Home /> },
    { label: 'Treasure Horde', path: '/treasure', icon: <Diamond /> },
    { label: 'Banking', path: '/banking', icon: <AccountBalance /> },
    { label: 'Business', path: '/business', icon: <Business /> },
    { label: 'Net Worth', path: '/net-worth', icon: <Gavel /> },
    { label: 'Currencies', path: '/currencies', icon: <AccountBalance /> },
    { label: 'GM Screen', path: '/gm', icon: <Settings /> },
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
          Hord Manager
        </Typography>

        {sessionNumber && (
          <Box sx={{ mr: 2 }}>
            <Typography variant="body2">
              Session: {sessionNumber}
            </Typography>
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