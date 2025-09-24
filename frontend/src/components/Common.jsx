import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Box,
} from '@mui/material';

const LoadingSpinner = ({ size = 40 }) => (
  <Box display="flex" justifyContent="center" alignItems="center" p={3}>
    <CircularProgress size={size} />
  </Box>
);

const ErrorAlert = ({ error, onRetry }) => (
  <Alert 
    severity="error" 
    action={onRetry && <button onClick={onRetry}>Retry</button>}
    sx={{ mb: 2 }}
  >
    {error?.message || 'An error occurred'}
  </Alert>
);

const PageHeader = ({ title, subtitle, action }) => (
  <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        {title}
      </Typography>
      {subtitle && (
        <Typography variant="subtitle1" color="text.secondary">
          {subtitle}
        </Typography>
      )}
    </Box>
    {action && <Box>{action}</Box>}
  </Box>
);

const InfoCard = ({ title, value, subtitle, icon, color = 'primary' }) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h5" component="div" color={`${color}.main`}>
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
        {icon && (
          <Box color={`${color}.main`}>
            {icon}
          </Box>
        )}
      </Box>
    </CardContent>
  </Card>
);

export { LoadingSpinner, ErrorAlert, PageHeader, InfoCard };