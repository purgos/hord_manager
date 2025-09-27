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
  increment: async () => {
    return await api.post('/sessions/increment');
  },
};

// Currency Service
export const currencyService = {
  async getAllCurrencies() {
    const timestamp = Date.now();
    return await api.get(`/currencies/?_=${timestamp}`);
  },

  async getCurrency(name) {
    return await api.get(`/currencies/${name}`);
  },

  async createCurrency(currency) {
    return await api.post('/currencies/', currency);
  },

  async updateCurrency(currencyId, payload) {
    return await api.patch(`/currencies/${currencyId}`, payload);
  },

  async deleteCurrency(currencyId) {
    return await api.delete(`/currencies/${currencyId}`);
  },

  async convertCurrency(amount, fromCurrency, toCurrency) {
    return await api.post('/currencies/convert', {
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency
    });
  },

  async convertFromGold(ozGold, currency) {
    return await api.post(`/currencies/convert/from-gold?oz_gold=${ozGold}&currency=${currency}`);
  },

  async convertToGold(amount, currency) {
    return await api.post(`/currencies/convert/to-gold?amount=${amount}&currency=${currency}`);
  },

  async convertUSD(amount, toCurrency = null, fromCurrency = null, sessionNumber = null) {
    const params = new URLSearchParams({ amount: amount.toString() });
    if (toCurrency) params.append('to_currency', toCurrency);
    if (fromCurrency) params.append('from_currency', fromCurrency);
    if (sessionNumber) params.append('session_number', sessionNumber.toString());
    
    return await api.post(`/currencies/convert/usd?${params}`);
  },

  async getConversionRates(baseCurrency = 'USD') {
    return await api.get(`/currencies/rates/${baseCurrency}`);
  },

  async displayValueInCurrencies(ozGoldValue, targetCurrencies = null) {
    return await api.post('/currencies/display', {
      oz_gold_value: ozGoldValue,
      target_currencies: targetCurrencies
    });
  },

  async getCurrencyBreakdown(currencyName, amount) {
    return await api.get(`/currencies/breakdown/${currencyName}?amount=${amount}`);
  },

  async getMetalValue(metalName, amount, unit, sessionNumber = null, targetCurrencies = null) {
    const params = new URLSearchParams({
      metal_name: metalName,
      amount: amount.toString(),
      unit
    });
    if (sessionNumber) params.append('session_number', sessionNumber.toString());
    if (targetCurrencies) {
      targetCurrencies.forEach(currency => params.append('target_currencies', currency));
    }
    
    return await api.get(`/currencies/metals/value?${params}`);
  },

  async getGemstoneValue(gemstoneName, carats, targetCurrencies = null) {
    const params = new URLSearchParams({
      gemstone_name: gemstoneName,
      carats: carats.toString()
    });
    if (targetCurrencies) {
      targetCurrencies.forEach(currency => params.append('target_currencies', currency));
    }
    
    return await api.get(`/currencies/gemstones/value?${params}`);
  }
};

// Metal prices service
export const metalService = {
  getSupportedMetals: async () => {
    return await api.get('/metals/supported');
  },
  getCurrentPrices: async (useMockData = false, sessionNumber = 1) => {
    const params = { 
      use_mock_data: useMockData,
      session_number: sessionNumber
    };
    return await api.get('/metals/prices/current', { params });
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
  getPriceRanges: async () => {
    return await api.get('/metals/price-ranges');
  },
  updatePriceRange: async (metalName, minMultiplier, maxMultiplier) => {
    return await api.put(`/metals/price-range/${metalName}`, null, {
      params: {
        min_multiplier: minMultiplier,
        max_multiplier: maxMultiplier
      }
    });
  },
  create: async (name, unit, basePrice) => {
    return await api.post('/metals/create', null, {
      params: {
        name: name,
        unit: unit,
        base_price: basePrice
      }
    });
  },
};

// Material prices service
export const materialService = {
  getAvailableMaterials: async () => {
    return await api.get('/materials/list');
  },
  getCurrentPrices: async (sessionNumber = 1, useMockData = true) => {
    return await api.get('/materials/prices/current', {
      params: { 
        session_number: sessionNumber,
        use_mock_data: useMockData 
      }
    });
  },
  getPriceHistory: async (materialName = null, sessionNumber = null, limit = 100) => {
    return await api.get('/materials/prices/history', {
      params: {
        material_name: materialName,
        session_number: sessionNumber,
        limit: limit
      }
    });
  },
  triggerUpdate: async (sessionNumber = 1, useMockData = true) => {
    return await api.post('/materials/scrape', null, {
      params: { 
        session_number: sessionNumber,
        use_mock_data: useMockData 
      }
    });
  },
  getPriceRanges: async () => {
    return await api.get('/materials/price-ranges');
  },
  updatePriceRange: async (materialName, minMultiplier, maxMultiplier) => {
    return await api.put(`/materials/price-range/${materialName}`, null, {
      params: {
        min_multiplier: minMultiplier,
        max_multiplier: maxMultiplier
      }
    });
  },
  create: async (name, unit, basePrice) => {
    return await api.post('/materials/create', null, {
      params: {
        name: name,
        unit: unit,
        base_price: basePrice
      }
    });
  },
};

// GM service
export const gmService = {
  getSettings: async () => {
    return await api.get('/gm/settings');
  },
  updateSettings: async (settings) => {
    return await api.patch('/gm/settings', settings);
  },
  getInbox: async () => {
    return await api.get('/gm/inbox');
  },
  getInboxMessage: async (messageId) => {
    return await api.get(`/gm/inbox/${messageId}`);
  },
  updateMessageStatus: async (messageId, status, responseData = null) => {
    return await api.patch(`/gm/inbox/${messageId}/status`, null, {
      params: { status },
      data: responseData ? { response_data: responseData } : {}
    });
  },
  createInboxMessage: async (messageType, payload, playerId = null) => {
    return await api.post('/gm/inbox', null, {
      params: { 
        message_type: messageType,
        player_id: playerId
      },
      data: { payload }
    });
  },
  changePassword: async (passwordData) => {
    return await api.post('/gm/change-password', passwordData);
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
  // Pricing methods
  getSupportedGemstones: async () => {
    return await api.get('/metals/gemstones/supported');
  },
  getCurrentPrices: async (useMockData = false) => {
    return await api.get('/metals/gemstones/prices/current', {
      params: { use_mock_data: useMockData }
    });
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

// Data Management Service
export { dataManagementService } from './dataManagementService';