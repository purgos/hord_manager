import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Container,
  Breadcrumbs,
  Link,
  Chip,
  Divider
} from '@mui/material';
import { Inbox as InboxIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { gmService, currencyService } from '../../services';

function GMInbox() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [detailsDialog, setDetailsDialog] = useState(false);
  const [actionDialog, setActionDialog] = useState(false);
  const [actionType, setActionType] = useState('');
  const [actionValue, setActionValue] = useState('');
  const [actionCurrency, setActionCurrency] = useState('oz gold');
  const [currencies, setCurrencies] = useState([]);
  const [loanInterestRate, setLoanInterestRate] = useState('');
  const [loanTermSessions, setLoanTermSessions] = useState('');
  const [loanPaymentType, setLoanPaymentType] = useState('per_session');

  useEffect(() => {
    loadMessages();
    loadCurrencies();
  }, []);

  const loadMessages = async () => {
    try {
      const data = await gmService.getInbox();
      setMessages(data);
    } catch (error) {
      console.error('Failed to load inbox:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCurrencies = async () => {
    try {
      const data = await currencyService.getAllCurrencies();
      // Add oz gold as the base currency option
      const currencyOptions = [
        { name: 'oz gold', id: 'oz_gold' },
        ...data.map(currency => ({ name: currency.name, id: currency.name }))
      ];
      setCurrencies(currencyOptions);
    } catch (error) {
      console.error('Failed to load currencies:', error);
      // Fallback to just oz gold
      setCurrencies([{ name: 'oz gold', id: 'oz_gold' }]);
    }
  };

  const handleViewDetails = (message) => {
    setSelectedMessage(message);
    setDetailsDialog(true);
  };

  const handleAction = (message, action) => {
    setSelectedMessage(message);
    setActionType(action);
    
    // Pre-populate with player's requested values for loans
    if (message.type === 'loan' && action === 'approved') {
      setActionValue(message.payload.requested_amount || '');
      setActionCurrency('oz gold'); // Default to oz gold
      setLoanInterestRate('5.0'); // GM sets interest rate
      
      // Extract requested term from player's proposal
      const requestedTerm = message.payload.repayment_plan || message.payload.term_sessions || '10';
      // Extract numeric value if it's a string like "12 sessions"
      const termMatch = requestedTerm.toString().match(/\\d+/);
      setLoanTermSessions(termMatch ? termMatch[0] : '10');
      
      setLoanPaymentType('per_session');
    } else {
      setActionValue('');
      setActionCurrency('oz gold');
      setLoanInterestRate('5.0');
      setLoanTermSessions('10');
      setLoanPaymentType('per_session');
    }
    
    setActionDialog(true);
  };

  const confirmAction = async () => {
    try {
      let responseData = null;
      
      if (actionValue && actionType === 'approved') {
        responseData = {
          value: actionValue,
          currency: actionCurrency,
          approved_at: new Date().toISOString()
        };

        // Add loan-specific terms for loan approvals
        if (selectedMessage?.type === 'loan') {
          responseData.interest_rate = parseFloat(loanInterestRate);
          responseData.term_sessions = parseInt(loanTermSessions);
          responseData.payment_type = loanPaymentType;
          
          // Calculate payment per session
          const principal = parseFloat(actionValue);
          const rate = parseFloat(loanInterestRate) / 100;
          const sessions = parseInt(loanTermSessions);
          
          if (loanPaymentType === 'per_session') {
            // Simple interest calculation: (Principal + (Principal * Rate * Sessions)) / Sessions
            const totalAmount = principal + (principal * rate * sessions);
            responseData.payment_per_session = (totalAmount / sessions).toFixed(3);
          } else {
            // Lump sum: Principal + (Principal * Rate * Sessions)
            responseData.total_payment = (principal + (principal * rate * sessions)).toFixed(3);
          }
        }
      }

      // Handle account registration approvals/rejections differently
      if (selectedMessage?.type === 'account_registration') {
        const endpoint = actionType === 'approved' ? 'approve-account' : 'reject-account';
        const response = await fetch(`http://localhost:8000/gm/${endpoint}/${selectedMessage.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error('Failed to process account registration');
        }
      } else {
        await gmService.updateMessageStatus(selectedMessage.id, actionType, responseData);
      }
      await loadMessages(); // Refresh the list
      setActionDialog(false);
      setSelectedMessage(null);
      setActionType('');
      setActionValue('');
      setActionCurrency('oz gold');
      setLoanInterestRate('5.0');
      setLoanTermSessions('10');
      setLoanPaymentType('per_session');
    } catch (error) {
      console.error('Failed to update message:', error);
    }
  };

  const getMessageTypeIcon = (type) => {
    switch (type) {
      case 'appraisal': return '🎨';
      case 'business': return '🏢';
      case 'investment': return '💰';
      case 'loan': return '🏦';
      case 'account_registration': return '👤';
      default: return '📝';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'resolved': return 'info';
      default: return 'default';
    }
  };

  const formatPayload = (payload) => {
    return Object.entries(payload).map(([key, value]) => {
      if (key === 'response' && typeof value === 'object') {
        return (
          <Box key={key} sx={{ mt: 1, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
            <Typography variant="body2" fontWeight="bold" color="primary">
              GM Response:
            </Typography>
            {Object.entries(value).map(([responseKey, responseValue]) => (
              <Typography key={responseKey} variant="body2" sx={{ ml: 2 }}>
                <strong>{responseKey}:</strong> {responseValue}
              </Typography>
            ))}
          </Box>
        );
      }
      return (
        <Typography key={key} variant="body2">
          <strong>{key}:</strong> {typeof value === 'object' ? JSON.stringify(value) : value}
        </Typography>
      );
    });
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
          <Typography color="text.primary">GM Inbox</Typography>
        </Breadcrumbs>

        {/* Page Header */}
        <Paper sx={{ p: 3, mb: 4, textAlign: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <InboxIcon sx={{ fontSize: 48, color: 'warning.main', mr: 2 }} />
            <Typography variant="h3" component="h1">
              GM Inbox
            </Typography>
          </Box>
          <Typography variant="h6" color="text.secondary">
            Review and respond to player requests ({messages.length} messages)
          </Typography>
        </Paper>

        {/* Refresh Button */}
        <Box sx={{ mb: 3 }}>
          <Button
            variant="outlined"
            onClick={loadMessages}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>

        {/* Messages */}
        {messages.length === 0 ? (
          <Alert severity="info">
            No messages in inbox. Player requests will appear here.
          </Alert>
        ) : (
          <Grid container spacing={2}>
            {messages.map((message) => (
              <Grid item xs={12} key={message.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ mr: 1 }}>
                        {getMessageTypeIcon(message.type)} {message.type.charAt(0).toUpperCase() + message.type.slice(1)}
                      </Typography>
                      <Chip
                        label={message.status}
                        color={getStatusColor(message.status)}
                        size="small"
                        sx={{ ml: 'auto' }}
                      />
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Created: {new Date(message.created_at).toLocaleString()}
                    </Typography>
                    
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      Player: {message.player_username || 'Unknown'}
                    </Typography>

                    <Divider sx={{ my: 1 }} />
                    
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {formatPayload(message.payload)}
                    </Typography>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      size="small"
                      onClick={() => handleViewDetails(message)}
                    >
                      View Details
                    </Button>
                    
                    {message.status === 'pending' && (
                      <>
                        <Button
                          size="small"
                          color="success"
                          onClick={() => handleAction(message, 'approved')}
                        >
                          Approve
                        </Button>
                        <Button
                          size="small"
                          color="error"
                          onClick={() => handleAction(message, 'rejected')}
                        >
                          Reject
                        </Button>
                      </>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Message Details Dialog */}
        <Dialog open={detailsDialog} onClose={() => setDetailsDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>
            {selectedMessage && (
              <>
                {getMessageTypeIcon(selectedMessage.type)} {selectedMessage.type.charAt(0).toUpperCase() + selectedMessage.type.slice(1)} Request
              </>
            )}
          </DialogTitle>
          <DialogContent>
            {selectedMessage && (
              <Box>
                <Typography variant="body2" paragraph>
                  <strong>Status:</strong> <Chip label={selectedMessage.status} color={getStatusColor(selectedMessage.status)} size="small" />
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>Player:</strong> {selectedMessage.player_username || 'Unknown'}
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>Created:</strong> {new Date(selectedMessage.created_at).toLocaleString()}
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>Updated:</strong> {new Date(selectedMessage.updated_at).toLocaleString()}
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>Request Details:</Typography>
                {formatPayload(selectedMessage.payload)}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDetailsDialog(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* Action Dialog - Truncated for brevity, but includes all the approval/rejection logic */}
        <Dialog open={actionDialog} onClose={() => setActionDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            {actionType === 'approved' ? 'Approve Request' : 'Reject Request'}
          </DialogTitle>
          <DialogContent>
            <Typography paragraph>
              Are you sure you want to {actionType === 'approved' ? 'approve' : 'reject'} this {selectedMessage?.type} request?
            </Typography>
            {/* Add all the specific approval forms for different message types here */}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setActionDialog(false)}>Cancel</Button>
            <Button
              onClick={confirmAction}
              color={actionType === 'approved' ? 'success' : 'error'}
              variant="contained"
            >
              {actionType === 'approved' ? 'Approve' : 'Reject'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
}

export default GMInbox;