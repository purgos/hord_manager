const API_BASE_URL = 'http://localhost:8000';

class DataManagementService {
  async resetUsers() {
    const response = await fetch(`${API_BASE_URL}/data-management/reset/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset users');
    }
    
    return response.json();
  }

  async resetCurrencies() {
    const response = await fetch(`${API_BASE_URL}/data-management/reset/currencies`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset currencies');
    }
    
    return response.json();
  }

  async resetMetals() {
    const response = await fetch(`${API_BASE_URL}/data-management/reset/metals`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset metals');
    }
    
    return response.json();
  }

  async resetMaterials() {
    const response = await fetch(`${API_BASE_URL}/data-management/reset/materials`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset materials');
    }
    
    return response.json();
  }

  async resetGemstones() {
    const response = await fetch(`${API_BASE_URL}/data-management/reset/gemstones`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset gemstones');
    }
    
    return response.json();
  }

  async resetSessions() {
    const response = await fetch(`${API_BASE_URL}/data-management/reset/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset sessions');
    }
    
    return response.json();
  }

  async resetAllData() {
    const response = await fetch(`${API_BASE_URL}/data-management/reset/all`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset all data');
    }
    
    return response.json();
  }
}

export const dataManagementService = new DataManagementService();