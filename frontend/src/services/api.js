import axios from 'axios';

// URL de base de l'API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Service API
const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Scans
  getScans: () => api.get('/scans'),
  getScan: (scanId) => api.get(`/scans/${scanId}`),
  startScan: (scanData) => api.post('/scans/start', scanData),
  deleteScan: (scanId) => api.delete(`/scans/${scanId}`),
  getStats: () => api.get('/scans/stats'),
  downloadReport: (scanId, format) => {
    return api.get(`/scans/${scanId}/download/${format}`, {
      responseType: 'blob'
    });
  },

  // AD Test
  testADConnection: (adData) => api.post('/ad/test-connection', adData),
  getADUsers: (adData) => api.post('/ad/users', adData),
  getPrivilegedUsers: (adData) => api.post('/ad/privileged-users', adData),
};

export default apiService;
