/**
 * V3 API Client - MDP Platform V3.1
 * Axios instance configured for V3 API endpoints.
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// Create axios instance for V3 API
const v3Client: AxiosInstance = axios.create({
  baseURL: '/api/v3',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Track request start times for performance logging
const requestTimers = new Map<string, number>();

// Request Interceptor
v3Client.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const timestamp = Date.now();
    const requestKey = `${config.method?.toUpperCase()}-${config.url}-${timestamp}`;
    requestTimers.set(requestKey, timestamp);
    
    // Log request with V3 tag
    console.log(`>> [V3 Req] ${config.method?.toUpperCase()} ${config.url}`);
    
    return config;
  },
  (error: AxiosError) => {
    console.error('>> [V3 Req Error]', error);
    return Promise.reject(error);
  }
);

// Response Interceptor
v3Client.interceptors.response.use(
  (response: AxiosResponse) => {
    const config = response.config;
    const method = config.method?.toUpperCase() || 'UNKNOWN';
    const url = config.url || '';
    
    // Find matching timer
    let processTime = 0;
    for (const [key, startTime] of requestTimers.entries()) {
      if (key.includes(method) && key.includes(url)) {
        processTime = Date.now() - startTime;
        requestTimers.delete(key);
        break;
      }
    }
    
    // Log response
    const requestId = response.headers['x-request-id'] || 'N/A';
    console.log(
      `<< [V3 Res] ${response.status} ${url} (${processTime}ms) [Request-ID: ${requestId}]`
    );
    
    return response;
  },
  (error: AxiosError) => {
    const config = error.config;
    if (config) {
      const method = config.method?.toUpperCase() || 'UNKNOWN';
      const url = config.url || '';
      
      // Clean up timer
      for (const [key] of requestTimers.entries()) {
        if (key.includes(method) && key.includes(url)) {
          requestTimers.delete(key);
          break;
        }
      }
      
      // Log error response
      const status = error.response?.status || 'ERROR';
      const message = error.message || 'Unknown error';
      const requestId = error.response?.headers['x-request-id'] || 'N/A';
      console.error(`<< [V3 Res Error] ${status} ${url} - ${message} [Request-ID: ${requestId}]`);
      
      // Log full error response data for debugging
      if (error.response?.data) {
        console.error('[V3] Error Response Data:', JSON.stringify(error.response.data, null, 2));
      }
      
      // Check if traceback exists in response (DEBUG mode)
      if (error.response?.data && typeof error.response.data === 'object') {
        const responseData = error.response.data as Record<string, unknown>;
        if (responseData.traceback) {
          console.error('[V3] BACKEND TRACEBACK:\n', responseData.traceback);
          if (responseData.error_msg) {
            console.error('[V3] Error Message:', responseData.error_msg);
          }
        }
        // Log validation errors (422)
        if (status === 422 && Array.isArray(responseData.detail)) {
          console.error('[V3] Validation Errors:');
          (responseData.detail as Array<{ loc?: string[]; msg: string; type: string }>).forEach(
            (err, index) => {
              console.error(`  ${index + 1}. ${err.loc?.join('.')}: ${err.msg} (type: ${err.type})`);
            }
          );
        }
      }
    } else {
      console.error('<< [V3 Res Error]', error);
    }
    
    return Promise.reject(error);
  }
);

export default v3Client;
