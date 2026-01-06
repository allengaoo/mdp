/**
 * API client configuration.
 */
import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;

