# Hord Manager Frontend

A modern React frontend for the Hord Manager treasure tracking system, built with Vite, Material-UI, and React Router.

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and development server
- **Material-UI (MUI)** - Comprehensive React component library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API communication
- **Recharts** - Chart library for data visualization

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Header.jsx      # Navigation header with menu
│   ├── Layout.jsx      # Main layout wrapper
│   └── Common.jsx      # Common UI components
├── pages/              # Page components
│   ├── HomePage.jsx    # Dashboard/home page
│   ├── CurrenciesPage.jsx  # Metal prices and currencies
│   ├── TreasurePage.jsx    # Treasure management
│   └── BankingPage.jsx     # Banking and finance
├── services/           # API service layer
│   ├── api.js         # Axios configuration
│   └── index.js       # Service functions
├── hooks/             # Custom React hooks
├── contexts/          # React contexts
├── utils/            # Utility functions
└── assets/           # Static assets
```

## Features

### Implemented
- ✅ **Dashboard** - Overview of session data, system status, and metal prices
- ✅ **Metal Prices** - Real-time price tracking with charts and tables
- ✅ **Navigation** - Responsive header with menu system
- ✅ **API Integration** - Full backend communication layer
- ✅ **Responsive Design** - Mobile-friendly Material-UI components

### Coming Soon
- 🔄 **Treasure Management** - Gemstones, art, and real estate tracking
- 🔄 **Banking System** - Account management and loan services
- 🔄 **Business Management** - Investment and business tracking
- 🔄 **GM Screen** - Admin interface (password protected)
- 🔄 **Authentication** - User login and session management

## Development

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Getting Started

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

4. **Preview production build**
   ```bash
   npm run preview
   ```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## API Integration

The frontend communicates with the FastAPI backend through a service layer:

- **Health Service** - System status checks
- **Session Service** - Game session management  
- **Metal Service** - Price data and scraping
- **Currency Service** - Currency management
- **GM Service** - Admin functionality

## Contributing

1. Follow the existing code structure
2. Use Material-UI components when possible
3. Keep API calls in the service layer
4. Add proper error handling
5. Test with the backend running on port 8000

## Backend Integration

The frontend expects the FastAPI backend to be running on `http://localhost:8000`. Key endpoints used:

- `GET /health/ping` - Health check
- `GET /sessions/state` - Current session
- `POST /sessions/increment` - Increment session
- `GET /metals/supported` - Supported metals
- `GET /metals/prices/current` - Current prices
- `POST /metals/scrape` - Trigger price scraping
