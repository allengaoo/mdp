/**
 * V3 Health API Functions - MDP Platform V3.1
 * API client for index health monitoring and observability.
 */
import v3Client from './client';

// ==========================================
// Types - Metrics
// ==========================================

export interface IJobMetrics {
  pk_collisions: number;
  ai_latency_avg_ms: number;
  ai_inference_count: number;
  ai_low_confidence_count: number;
  vector_dim_mismatch: number;
  corrupt_media_files: number;
  transform_errors: number;
}

// ==========================================
// Types - Object Health
// ==========================================

export type HealthStatus = 'HEALTHY' | 'DEGRADED' | 'FAILED';

export interface IObjectHealthSummary {
  object_def_id: string;
  object_name: string | null;
  status: HealthStatus;
  last_run_time: string | null;
  lag_seconds: number | null;
  rows_processed: number;
  rows_indexed: number;
  success_rate: number;
  metrics: Partial<IJobMetrics>;
}

export interface ISystemHealthSummary {
  total_objects: number;
  healthy_count: number;
  degraded_count: number;
  failed_count: number;
  overall_success_rate: number;
  avg_ai_latency_ms: number | null;
  total_corrupt_files: number;
  objects: IObjectHealthSummary[];
}

// ==========================================
// Types - Job Run
// ==========================================

export type JobStatus = 'SUCCESS' | 'PARTIAL_SUCCESS' | 'FAILED';

export interface IIndexJobRun {
  id: string;
  mapping_id: string;
  object_def_id: string;
  start_time: string;
  end_time: string | null;
  status: JobStatus;
  rows_processed: number;
  rows_indexed: number;
  metrics_json: Partial<IJobMetrics>;
  created_at: string | null;
}

export interface IJobHistoryResponse {
  object_def_id: string;
  runs: IIndexJobRun[];
}

// ==========================================
// Types - Error Sample
// ==========================================

export type ErrorCategory = 'SEMANTIC' | 'AI_INFERENCE' | 'MEDIA_IO' | 'SYSTEM';

export interface IIndexErrorSample {
  id: string;
  job_run_id: string;
  raw_row_id: string;
  error_category: ErrorCategory;
  error_message: string;
  stack_trace: string | null;
  created_at: string | null;
}

// ==========================================
// Types - Reindex Response
// ==========================================

export interface IReindexResponse {
  message: string;
  object_def_id: string;
  mapping_id: string;
}

// ==========================================
// API Functions
// ==========================================

/**
 * Get system health summary with all object statuses.
 */
export const fetchHealthSummary = async (): Promise<ISystemHealthSummary> => {
  const response = await v3Client.get('/health/summary');
  return response.data;
};

/**
 * Get historical job runs for an object type.
 */
export const fetchObjectHistory = async (
  objectDefId: string,
  days: number = 7,
  limit: number = 50
): Promise<IJobHistoryResponse> => {
  const response = await v3Client.get(`/health/objects/${objectDefId}/history`, {
    params: { days, limit }
  });
  return response.data;
};

/**
 * Get details of a specific job run.
 */
export const fetchJobRun = async (runId: string): Promise<IIndexJobRun> => {
  const response = await v3Client.get(`/health/jobs/${runId}`);
  return response.data;
};

/**
 * Get error samples for a specific job run.
 */
export const fetchJobErrors = async (
  runId: string,
  category?: ErrorCategory,
  limit: number = 100
): Promise<IIndexErrorSample[]> => {
  const params: Record<string, any> = { limit };
  if (category) {
    params.category = category;
  }
  const response = await v3Client.get(`/health/jobs/${runId}/errors`, { params });
  return response.data || [];
};

/**
 * Trigger immediate re-indexing for an object type.
 */
export const triggerReindex = async (objectDefId: string): Promise<IReindexResponse> => {
  const response = await v3Client.post(`/health/objects/${objectDefId}/reindex`);
  return response.data;
};

// ==========================================
// Helper Functions
// ==========================================

/**
 * Format lag time to human-readable string.
 */
export const formatLag = (lagSeconds: number | null): string => {
  if (lagSeconds === null) return 'N/A';
  
  if (lagSeconds < 60) return `${lagSeconds}s ago`;
  if (lagSeconds < 3600) return `${Math.floor(lagSeconds / 60)}m ago`;
  if (lagSeconds < 86400) return `${Math.floor(lagSeconds / 3600)}h ago`;
  return `${Math.floor(lagSeconds / 86400)}d ago`;
};

/**
 * Get status color for Ant Design Badge.
 */
export const getStatusColor = (status: HealthStatus): string => {
  switch (status) {
    case 'HEALTHY': return 'success';
    case 'DEGRADED': return 'warning';
    case 'FAILED': return 'error';
    default: return 'default';
  }
};

/**
 * Get error category color.
 */
export const getErrorCategoryColor = (category: ErrorCategory): string => {
  switch (category) {
    case 'SEMANTIC': return 'orange';
    case 'AI_INFERENCE': return 'purple';
    case 'MEDIA_IO': return 'red';
    case 'SYSTEM': return 'volcano';
    default: return 'default';
  }
};
