/**
 * V3 API Module - MDP Platform V3.1
 * Export all V3 API functions and types.
 */

// Client
export { default as v3Client } from './client';

// Types
export * from './types';

// API Functions
export * from './ontology';
export * from './search';
export * from './chat';

// Adapters (V3 → V1 compatibility)
export * from './adapters';
