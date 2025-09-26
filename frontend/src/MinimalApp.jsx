import React from 'react';

function MinimalApp() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Hord Manager</h1>
      <p>Minimal app is working!</p>
      <p>Current time: {new Date().toLocaleString()}</p>
    </div>
  );
}

export default MinimalApp;