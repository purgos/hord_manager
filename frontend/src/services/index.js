import api from './api';

// Health check service
export const healthService = {
  ping: async () => {
    return await api.get('/health/ping');
  },
};

// Session management service
export const sessionService = {
  getState: async () => {
    return await api.get('/sessions/state');
  },
  incrementSession: async () => {
    return await api.post('/sessions/increment');
  },
};

// Currency service
export const currencyService = {
  getAll: async () => {
    return await api.get('/currencies');
  },
  getById: async (id) => {
    return await api.get(`/currencies/${id}`);
  },
  create: async (currency) => {
    return await api.post('/currencies', currency);
  },
  update: async (id, currency) => {
    return await api.put(`/currencies/${id}`, currency);
  },
  delete: async (id) => {
    return await api.delete(`/currencies/${id}`);
  },
};

// Metal prices service
export const metalService = {
  getSupportedMetals: async () => {
    return await api.get('/metals/supported');
  },
  getCurrentPrices: async (useMockData = false) => {
    return await api.get('/metals/prices/current', {
      params: { use_mock_data: useMockData }
    });
  },
  getPriceHistory: async (metalName = null, sessionNumber = null, limit = 100) => {
    return await api.get('/metals/prices/history', {
      params: {
        metal_name: metalName,
        session_number: sessionNumber,
        limit: limit
      }
    });
  },
  triggerScraping: async (useMockData = false) => {
    return await api.post('/metals/scrape', null, {
      params: { use_mock_data: useMockData }
    });
  },
};

// GM service
export const gmService = {
  getSettings: async () => {
    return await api.get('/gm/settings');
  },
  updateSettings: async (settings) => {
    return await api.put('/gm/settings', settings);
  },
  getInbox: async () => {
    return await api.get('/gm/inbox');
  },
};

// Gemstone service
export const gemstoneService = {
  getAll: async () => {
    return await api.get('/gemstones');
  },
  create: async (gemstone) => {
    return await api.post('/gemstones', gemstone);
  },
  update: async (id, gemstone) => {
    return await api.put(`/gemstones/${id}`, gemstone);
  },
  delete: async (id) => {
    return await api.delete(`/gemstones/${id}`);
  },
};

// Business service
export const businessService = {
  getAll: async () => {
    return await api.get('/businesses');
  },
  create: async (business) => {
    return await api.post('/businesses', business);
  },
  update: async (id, business) => {
    return await api.put(`/businesses/${id}`, business);
  },
  delete: async (id) => {
    return await api.delete(`/businesses/${id}`);
  },
};

// Art service
export const artService = {
  getAll: async () => {
    return await api.get('/art');
  },
  create: async (artItem) => {
    return await api.post('/art', artItem);
  },
  update: async (id, artItem) => {
    return await api.put(`/art/${id}`, artItem);
  },
  delete: async (id) => {
    return await api.delete(`/art/${id}`);
  },
};

// Real Estate service
export const realEstateService = {
  getAll: async () => {
    return await api.get('/real_estate');
  },
  create: async (property) => {
    return await api.post('/real_estate', property);
  },
  update: async (id, property) => {
    return await api.put(`/real_estate/${id}`, property);
  },
  delete: async (id) => {
    return await api.delete(`/real_estate/${id}`);
  },
};