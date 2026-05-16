import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export const startAnalysis = (inputType, content) =>
  api.post('/api/v1/analyze', { input_type: inputType, content });

export const getResult = (jobId) =>
  api.get(`/api/v1/analyze/${jobId}`);

export const getHistory = () =>
  api.get('/api/v1/jobs');

export default api;
