import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const documentApi = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () => api.get('/documents'),
  get: (id) => api.get(`/documents/${id}`),
  process: (id) => api.post(`/documents/${id}/process`),
};

export const evaluationApi = {
  list: () => api.get('/evaluations'),
  get: (id) => api.get(`/evaluations/${id}`),
  run: (docId) => api.post(`/evaluations/document/${docId}/run`),
  generateReport: (evalId) => api.post(`/evaluations/${evalId}/generate-report`),
};

export const certifierApi = {
  getPending: () => api.get('/certifier/pending'),
  getAll: (status) => api.get(`/certifier/all${status ? '?status=' + status : ''}`),
  getHistory: () => api.get('/certifier/history'),
  approve: (evalId, notes = '') => api.post(`/certifier/${evalId}/approve`, { action: 'APPROVE', notes }),
  requestReview: (evalId, notes = '') => api.post(`/certifier/${evalId}/request-review`, { action: 'REQUEST_REVIEW', notes }),
  returnToReviewer: (evalId, notes = '') => api.post(`/certifier/${evalId}/return-to-reviewer`, { action: 'RETURN_TO_REVIEWER', notes }),
};

export const standardsApi = {
  listStandards: () => api.get('/standards'),
  listDeviceTypes: () => api.get('/standards/device-types'),
  listRequirements: () => api.get('/standards/requirements'),
};

export const reportsApi = {
  list: () => api.get('/reports'),
  getDownloadUrl: (filename) => `${API_BASE}/reports/${filename}/download`,
};

export const samplesApi = {
  list: () => api.get('/samples'),
  getDownloadUrl: (filename) => `${API_BASE}/samples/download/${filename}`,
  runSample: (filename) => api.post(`/samples/run-sample/${filename}`),
};

export const settingsApi = {
  getStatus: () => api.get('/settings/status'),
  verifyGroq: () => api.get('/settings/verify-groq'),
  reseedDb: () => api.post('/settings/reseed-db'),
};

export default api;
