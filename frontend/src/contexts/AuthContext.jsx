import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing authentication on app load
    const checkAuth = () => {
      try {
        const authData = localStorage.getItem('hord_auth');
        if (authData) {
          const parsedAuth = JSON.parse(authData);
          // Check if login is still valid (optional: add expiration logic)
          setUser({
            ...parsedAuth,
            isAuthenticated: true
          });
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        localStorage.removeItem('hord_auth'); // Clear invalid data
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = (userData) => {
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('hord_auth');
    setUser(null);
  };

  const isPlayer = () => user?.userType === 'player';
  const isGM = () => user?.userType === 'gm';
  const isAuthenticated = () => user?.isAuthenticated === true;

  const value = {
    user,
    login,
    logout,
    isPlayer,
    isGM,
    isAuthenticated,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;