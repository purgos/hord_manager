import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', background: '#f5f5f5', minHeight: '100vh' }}>
          <h2>Something went wrong.</h2>
          <details style={{ whiteSpace: 'pre-wrap', background: 'white', padding: '10px', border: '1px solid #ccc' }}>
            <summary>Error details (click to expand)</summary>
            <strong>Error:</strong> {this.state.error && this.state.error.toString()}
            <br />
            <strong>Stack trace:</strong>
            {this.state.errorInfo.componentStack}
            <br />
            <strong>Full error info:</strong>
            {JSON.stringify(this.state.errorInfo, null, 2)}
          </details>
          <button 
            onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
            style={{ marginTop: '10px', padding: '10px', background: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;