import React from 'react';
import { Typography, Box, Paper, Grid, Button } from '@mui/material';
import { AccountBalance, TrendingUp, Receipt } from '@mui/icons-material';
import { PageHeader } from '../../components/Common';

const BankingPage = () => {
  return (
    <Box>
      <PageHeader
        title="Banking & Finance"
        subtitle="Manage accounts, loans, and financial transactions"
      />

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <AccountBalance sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Bank Account
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Deposit, withdraw, and exchange currencies with configurable fees.
            </Typography>
            <Button variant="outlined" fullWidth>
              Access Account
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Receipt sx={{ fontSize: 48, color: 'warning.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Loan Office
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              View loan offers, submit petitions, and manage payment schedules.
            </Typography>
            <Button variant="outlined" fullWidth>
              View Loans
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Banking Features (Coming Soon)
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Account Management
            </Typography>
            <Box component="ul">
              <li>Multi-currency account support</li>
              <li>Transaction history tracking</li>
              <li>Automated exchange rate calculations</li>
              <li>Balance alerts and notifications</li>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Loan Services
            </Typography>
            <Box component="ul">
              <li>Loan application system</li>
              <li>Interest rate calculators</li>
              <li>Payment scheduling</li>
              <li>Credit history tracking</li>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default BankingPage;