import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import TreasurePage from './pages/TreasurePage';
import BankingPage from './pages/BankingPage';
import CurrenciesPage from './pages/CurrenciesPage';
import { sessionService } from './services';

// Placeholder components for routes not yet implemented
const BusinessPage = () => <div>Business page coming soon...</div>;
const NetWorthPage = () => <div>Net Worth page coming soon...</div>;
const GMPage = () => <div>GM Screen coming soon...</div>;

function App() {
  const [sessionNumber, setSessionNumber] = useState(null);

  useEffect(() => {
    // Fetch current session on app load
    const fetchSession = async () => {
      try {
        const session = await sessionService.getState();
        setSessionNumber(session.current_session);
      } catch (error) {
        console.error('Failed to fetch session:', error);
      }
    };

    fetchSession();
  }, []);

  return (
    <Router>
      <Layout sessionNumber={sessionNumber}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/treasure" element={<TreasurePage />} />
          <Route path="/banking" element={<BankingPage />} />
          <Route path="/business" element={<BusinessPage />} />
          <Route path="/net-worth" element={<NetWorthPage />} />
          <Route path="/currencies" element={<CurrenciesPage />} />
          <Route path="/gm" element={<GMPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
