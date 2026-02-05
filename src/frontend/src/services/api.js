import axios from 'axios';

// API base URL
// Development: Use '/api' which gets proxied to backend (see vite.config.js)
// Production: Use '' (empty) since frontend and backend are served from same origin
const API_BASE_URL = import.meta.env.MODE === 'development' ? '/api' : '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data.detail || error.response.data.message || 'An error occurred');
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

// API methods
export const authAPI = {
  /**
   * Verify employee PIN
   * @param {string} name - Employee name
   * @param {string} pin - 4-digit PIN
   * @returns {Promise<{success: boolean, message: string, employee_name: string}>}
   */
  verify: async (name, pin) => {
    const response = await api.post('/auth/verify', { name, pin });
    return response.data;
  },
};

export const hoursAPI = {
  /**
   * Submit hours worked
   * @param {Object} data - Hours submission data
   * @param {string} data.employee_name - Employee name
   * @param {string} data.date - Date in YYYY-MM-DD format
   * @param {string} data.start_time - Start time in HH:MM format
   * @param {string} data.end_time - End time in HH:MM format
   * @returns {Promise<{success: boolean, message: string, hours_worked: number, date: string}>}
   */
  submit: async (data) => {
    const response = await api.post('/submit-hours', data);
    return response.data;
  },
};

export const managerAPI = {
  /**
   * Authenticate manager with password
   * @param {string} password - Manager password
   * @returns {Promise<{success: boolean, message: string, token: string}>}
   */
  login: async (password) => {
    const response = await api.post('/manager/auth', { password });
    return response.data;
  },
  
  /**
   * Submit daily tips
   * @param {Object} data - Tip submission data
   * @param {string} data.date - Date in YYYY-MM-DD format
   * @param {number} data.total_tips - Total tips amount
   * @returns {Promise<{success: boolean, message: string, date: string, total_tips: number, formulas_injected: boolean}>}
   */
  submitTips: async (data) => {
    const response = await api.post('/manager/submit-daily-tip', data);
    return response.data;
  },
  
  /**
   * Get employee list from Settings
   * This would require a new backend endpoint
   * For now, we'll return mock data or implement it
   */
  getEmployees: async () => {
    // TODO: Implement backend endpoint for this
    // For now, return empty array
    // const response = await api.get('/manager/employees');
    // return response.data;
    return [];
  },
};

export const healthAPI = {
  /**
   * Check API health
   * @returns {Promise<{status: string, spreadsheet_id: string, message: string}>}
   */
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;


