import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import TreasurePage from './pages/TreasurePage';
import BankingPage from './pages/BankingPage';
import CurrenciesPage from './pages/CurrenciesPage';
import { sessionService } from './services';

// Placeholder components for routes not yet implemented
const BusinessPage = () => <div>Business page coming soon...</div>;
const NetWorthPage = () => <div>Net Worth page coming soon...</div>;
const GMPage = () => <div>GM Screen coming soon...</div>;

// Protected Route component
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2
        }}
      >
        <CircularProgress size={60} />
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

// Main App Content (after authentication)
function AppContent() {
  const { user, login, isAuthenticated } = useAuth();
  const [sessionNumber, setSessionNumber] = useState(null);

  useEffect(() => {
    // Fetch current session on app load (only if authenticated)
    if (isAuthenticated()) {
      const fetchSession = async () => {
        try {
          const session = await sessionService.getState();
          setSessionNumber(session.current_session);
        } catch (error) {
          console.error('Failed to fetch session:', error);
          setSessionNumber(1); // Fallback session number
        }
      };

      fetchSession();
    }
  }, [isAuthenticated]);

  // Show login page if not authenticated
  if (!isAuthenticated()) {
    return <LoginPage onLogin={login} />;
  }

  return (
    <Layout sessionNumber={sessionNumber} user={user}>
      <Routes>
        <Route path="/login" element={<Navigate to="/" replace />} />
        <Route 
          path="/" 
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/treasure" 
          element={
            <ProtectedRoute>
              <TreasurePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/banking" 
          element={
            <ProtectedRoute>
              <BankingPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/business" 
          element={
            <ProtectedRoute>
              <BusinessPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/net-worth" 
          element={
            <ProtectedRoute>
              <NetWorthPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/currencies" 
          element={
            <ProtectedRoute>
              <CurrenciesPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/gm" 
          element={
            <ProtectedRoute>
              <GMPage />
            </ProtectedRoute>
          } 
        />
        {/* Redirect any unknown routes to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
