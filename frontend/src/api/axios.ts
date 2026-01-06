/**
 * Axios client with interceptors for request/response logging.
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Track request start times
const requestTimers = new Map<string, number>();

// Request Interceptor
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const timestamp = Date.now();
    const requestKey = `${config.method?.toUpperCase()}-${config.url}-${timestamp}`;
    requestTimers.set(requestKey, timestamp);
    
    // Log request
    console.log(`>> [Req] ${config.method?.toUpperCase()} ${config.url}`);
    
    return config;
  },
  (error: AxiosError) => {
    console.error('>> [Req Error]', error);
    return Promise.reject(error);
  }
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    const config = response.config;
    const method = config.method?.toUpperCase() || 'UNKNOWN';
    const url = config.url || '';
    
    // Find matching timer (search for partial match)
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
      `<< [Res] ${response.status} ${url} (${processTime}ms) [Request-ID: ${requestId}]`
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
      console.error(`<< [Res Error] ${status} ${url} - ${message} [Request-ID: ${requestId}]`);
      
      // Log full error response data for debugging
      if (error.response?.data) {
        console.error('Error Response Data:', JSON.stringify(error.response.data, null, 2));
      }
      
      // Check if traceback exists in response (DEBUG mode)
      if (error.response?.data && typeof error.response.data === 'object') {
        const responseData = error.response.data as any;
        if (responseData.traceback) {
          console.error('🔥 BACKEND TRACEBACK:\n', responseData.traceback);
          if (responseData.error_msg) {
            console.error('Error Message:', responseData.error_msg);
          }
          if (responseData.error_type) {
            console.error('Error Type:', responseData.error_type);
          }
        }
        // Log validation errors (422)
        if (status === 422 && Array.isArray(responseData.detail)) {
          console.error('Validation Errors:');
          responseData.detail.forEach((err: any, index: number) => {
            console.error(`  ${index + 1}. ${err.loc?.join('.')}: ${err.msg} (type: ${err.type})`);
          });
        }
      }
    } else {
      console.error('<< [Res Error]', error);
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;

